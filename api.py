import math
import re
import threading
import time
import traceback

import numpy as np
import requests
import wolframalpha
from discord import Embed
from fuzzywuzzy import fuzz

import auths
from Polymarket import Poly
from utils import opt_shares, space
from wallets import Bank


class Offer:
    def __init__(self, offer_dict):
        self.costPerShareNo = offer_dict["costPerShareNo"]
        self.costPerShareYes = offer_dict["costPerShareYes"]
        self.pricePerShare = offer_dict["pricePerShare"]
        self.quantity = offer_dict["quantity"]
        self.tradeType = offer_dict["tradeType"]


class Contract:
    def __init__(self, orderbook_dict, contract_dict, market):
        self.timestamp = orderbook_dict["timestamp"]
        self._yes = orderbook_dict["yesOrders"]
        self._no = orderbook_dict["noOrders"]
        self.name = contract_dict["name"]
        self.id = contract_dict["id"]
        self.image = contract_dict["image"]
        self.shortName = contract_dict["shortName"]
        self.status = contract_dict["status"]
        self.market = market

    @property
    def yes_offers(self):
        if not self._yes:
            empty_offer = {
                "costPerShareNo": 0,
                "costPerShareYes": 1,
                "pricePerShare": 0,
                "quantity": 0,
                "tradeType": 0,
            }
            yield Offer(empty_offer)
        else:
            for yes in self._yes:
                yield Offer(yes)

    @property
    def best_yes(self):
        return list(self.yes_offers)[0]

    @property
    def no_offers(self):
        if not self._no:
            empty_offer = {
                "costPerShareNo": 1,
                "costPerShareYes": 0,
                "pricePerShare": 1,
                "quantity": 0,
                "tradeType": 1,
            }
            yield Offer(empty_offer)
        else:
            for no in self._no:
                yield Offer(no)

    @property
    def best_no(self):
        return list(self.no_offers)[0]


class Market:
    def __init__(self, market_dict, orderbook):
        self.id = market_dict["id"]
        self.name = market_dict["name"]
        self.short_name = market_dict["shortName"]
        self.image = market_dict["image"]
        self.url = market_dict["url"]
        self._contracts = market_dict["contracts"]
        self._orderbook = orderbook

    @property
    def contracts(self):
        for contract in self._contracts:
            orderbook = self._orderbook[str(contract["id"])]
            yield Contract(orderbook, contract, self)

    @property
    def lowest_no_quantity(self):
        quantities = []
        for contract in self.contracts:
            if contract.best_no.quantity > 0:
                quantities += [contract.best_no.quantity]
        if not quantities:
            quantities += [0]
        return min(quantities)

    def no_prices(self):
        prices = []
        for contract in self.contracts:
            prices += [contract.best_no.pricePerShare]
        return prices

    def yes_prices(self):
        prices = []
        for contract in self.contracts:
            prices += [contract.best_yes.pricePerShare]
        return prices

    def sum_return(self):
        total = 0
        for price in self.no_prices():
            total += 1 - price
        return round(total, 3)

    def _calc_risk(self, spread):
        prices = self.no_prices()

        num_shares = np.array(spread)
        prices = np.array(prices)

        investments = num_shares * prices

        profits = num_shares * (1.00 - prices)
        adj_profits = np.round(0.9 * profits, 3)

        values = adj_profits + investments

        risks = np.round(np.sum(adj_profits) - values, 3)
        return risks

    def calc_risk_bin(self, bin):
        spread = []
        for i, contract in enumerate(self.contracts):
            if contract.best_no.quantity != 0 and i != bin:
                spread += [1]
            else:
                spread += [0]
        risk = self._calc_risk(spread)
        return 1 - risk[bin]

    def _potential_profit(self, spread):
        return min(self._calc_risk(spread))

    def _best_amount(self, max_shares):
        contracts = list(self.contracts)
        maxed = max(self.no_prices())
        costliest = maxed if maxed != 1 else 0.99
        share_multiplier = (max_shares / costliest) / opt_shares(costliest)
        best_holds = []
        for contract in contracts:
            if contract.best_no.quantity:
                best_holds.append(
                    math.floor(
                        share_multiplier * opt_shares(contract.best_no.pricePerShare)
                    )
                )
            else:
                best_holds.append(0)
        return best_holds

    def optimize_spread(self, max_shares=None, minimize=None):
        if minimize is None:
            minimize = True
            if max_shares is not None:
                minimize = False

        if max_shares is None:
            maximum = self.lowest_no_quantity
            if maximum > 850:
                maximum = 850
            max_shares = maximum
        else:
            maximum = max_shares

        max_profit = 0
        max_spread = []
        while maximum > max_shares - (max_shares // 8.5):
            spread = self._best_amount(maximum)
            maximum -= 1
            if not minimize:
                max_spread = spread
                max_profit = self._potential_profit(spread)
                break
            elif max(spread) <= max_shares:
                if self._potential_profit(spread) > max_profit:
                    max_spread = spread
                    max_profit = self._potential_profit(spread)
        return max_spread, max_profit

    def get_contract(self, bin_num=None, bin_name=None, bin_exact=None):
        if bin_num is not None:
            return list(self.contracts)[bin_num]
        elif bin_name is not None:
            guess = re.sub(r"[^\w\s]", "", bin_name).lower()
            guess_words = guess.split()
            most_matches = 0
            best_diff = 0
            best_diff_contract = 0
            for contract in self.contracts:
                short_name = re.sub(r"[^\w\s]", "", contract.name).lower()
                matches = sum(
                    [word in short_name or word in short_name for word in guess_words]
                )
                diff1 = fuzz.token_sort_ratio(guess, short_name)
                if matches > most_matches or (
                        matches >= most_matches and (diff1 > best_diff)
                ):
                    best_diff = diff1
                    best_diff_contract = contract
                if matches > most_matches:
                    most_matches = matches
            return best_diff_contract
        elif bin_exact is not None:
            for contract in self.contracts:
                if contract.shortName == bin_exact:
                    return contract


class PredictIt:
    def __init__(self):
        self.session = requests.session()
        self._markets = requests.get(
            "https://www.predictit.org/api/marketdata/all"
        ).json()
        self._orderbook = requests.get(
            "https://predictit-f497e.firebaseio.com/contractOrderBook.json"
        ).json()

    def reload_markets(self):
        self._markets = self.session.get(
            "https://www.predictit.org/api/marketdata/all"
        ).json()

    def reload_orderbook(self):
        r = self.session.get(
            "https://predictit-f497e.firebaseio.com/contractOrderBook.json"
        )
        self._orderbook = r.json()

    def get_markets(self):
        for market in self._markets["markets"]:
            yield Market(market, self._orderbook)

    def _get_market_id(self, market_str):
        guess = re.sub(r"[^\w\s]", "", market_str).lower()
        guess_words = guess.split()
        most_matches = 0
        best_diff = 0
        best_diff_id = 0
        for market in self.get_markets():
            short_name = re.sub(r"[^\w\s]", "", market.short_name).lower()
            long_name = re.sub(r"[^\w\s]", "", market.name).lower()
            matches = sum(
                [word in short_name or word in long_name for word in guess_words]
            )
            diff1 = fuzz.token_sort_ratio(guess, short_name)
            diff2 = fuzz.token_sort_ratio(guess, long_name)
            if matches > most_matches or (
                    matches >= most_matches and (diff1 > best_diff or diff2 > best_diff)
            ):
                best_diff = max(diff1, diff2)
                best_diff_id = market.id
            if matches > most_matches:
                most_matches = matches
        return best_diff_id

    def get_market(self, market):
        try:
            int(market)
            market_id = market
        except ValueError:
            market_id = self._get_market_id(market)
        markets = self.get_markets()
        if market_id:
            for market in markets:
                if str(market.id) == str(market_id):
                    return market

    def optimize_all(self, max_shares=None):
        for market in self.get_markets():
            spread, profit = market.optimize_spread(max_shares=max_shares)
            if profit > 0.01:
                yield market


class Discord:
    def __init__(self, pi_api: PredictIt):
        self.pi_api = pi_api
        reload_markets_thread = threading.Thread(
            target=self.reload_markets_thread, daemon=True
        )
        reload_markets_thread.start()
        self.old_markets = {}
        self.bank = Bank.from_file("bank")
        self.poly_api = Poly()
        self.wolfram = wolframalpha.Client(app_id=auths.app_id)

    def reload_markets_thread(self):
        i = 0
        while True:
            time.sleep(10)
            if i == 0:
                try:
                    self.pi_api.reload_markets()
                    self.poly_api.refresh_markets()
                except:
                    pass
            try:
                self.pi_api.reload_orderbook()
            except:
                pass
            i += 1
            if i >= 6:
                i = 0

    def orderbook(self, market):
        msg = "```" + str(market) + "\n"
        market = self.pi_api.get_market(market)
        title = 'Orderbook for "' + market.name + '"\n'
        offers = list(market.contracts)
        max_len = 0
        for contract in offers:
            if len(contract.name) > max_len:
                max_len = len(contract.name)
        msg += " " * (max_len + 2) + "YES  OFFERS  NO  OFFERS\n"
        for contract in offers:
            if contract.best_no.quantity:
                msg += " " * (max_len - len(contract.name)) + str(contract.name)
                msg += (
                        "  "
                        + str(int(contract.best_yes.pricePerShare * 100))
                        + (" " * (3 - len(str(int(contract.best_yes.pricePerShare * 100)))))
                        + "  "
                        + str(contract.best_yes.quantity)
                        + " " * (6 - len(str(contract.best_yes.quantity)))
                )
                msg += (
                        "  "
                        + str(int(contract.best_no.pricePerShare * 100))
                        + (" " * (3 - len(str(int(contract.best_no.pricePerShare * 100)))))
                        + "  "
                        + str(contract.best_no.quantity)
                        + "\n"
                )
        msg += "```"
        return Embed(title=title, description=msg, url=market.url, color=2206669)

    def risk_market(self, market, max_shares=None, minimize=False):
        msg = "```" + market + "." + str(max_shares) + "." + str(minimize) + "\n"
        market = self.pi_api.get_market(market)
        if max_shares is None:
            max_shares = market.lowest_no_quantity
        title = 'Market risk for "' + market.short_name + '"\n'
        spread, profit = market.optimize_spread(max_shares, minimize)
        if profit > 0:
            msg += "Negative risk found!!!\n"
            spread = list(filter(lambda x: x != 0, spread))
            msg += "Sum of 1 minus no is " + str(market.sum_return()) + "\n"
            msg += "Potential profit w/ below spread is " + str(profit) + "\n"
            msg += "Ideal spread is " + str(spread) + "\n"
        else:
            msg += "No negative risk available at " + str(max_shares) + " shares :("
        msg += "```"
        return Embed(title=title, description=msg, url=market.url, color=2206669)

    def risk_all(self, max_shares=None):
        title = "There are {} markets with negative risk\n"
        msg = "```"+str(max_shares)+"\n"
        n = 0
        for market in self.pi_api.optimize_all(max_shares):
            n += 1
            spread, profit = market.optimize_spread(max_shares)
            if max_shares:
                msg += (
                        "Market "
                        + str(market.id)
                        + " ("
                        + str(market.sum_return())
                        + " / $"
                        + str(profit)
                        + ")\n"
                )
            else:
                msg += (
                        "Market "
                        + str(market.id)
                        + " ("
                        + str(market.sum_return())
                        + " / $"
                        + str(profit)
                        + " / "
                        + str(market.lowest_no_quantity)
                        + ")\n"
                )
        if n == 0:
            msg += ":("
        msg += "```"
        return Embed(title=title.format(n), description=msg, color=2206669)

    def bins(self, market):
        msg = "```"+str(market).replace(" ", '.') + "\n"
        market = self.pi_api.get_market(market)
        title = 'Market bins for "' + market.short_name + '"\n'
        offers = list(market.contracts)
        max_len = 0
        for contract in offers:
            if len(contract.name) > max_len:
                max_len = len(contract.name)
        msg += " " * (max_len + 2) + "YES  NO\n"
        for contract in offers:
            if contract.best_no.quantity:
                msg += " " * (max_len - len(contract.name)) + str(contract.name)
                msg += (
                        "  "
                        + str(int(contract.best_yes.pricePerShare * 100))
                        + (" " * (3 - len(str(int(contract.best_yes.pricePerShare * 100)))))
                )
                msg += (
                        "  "
                        + str(int(contract.best_no.pricePerShare * 100))
                        + (" " * (3 - len(str(int(contract.best_no.pricePerShare * 100)))))
                        + "\n"
                )
        msg += "```"
        return Embed(title=title, description=msg, url=market.url, color=2206669).set_thumbnail(url=market.image)

    def related_markets_bin(self, bin_name, page):
        title = 'Looking for markets containing "' + bin_name + '" as a bin\n'
        msg = "```\n"
        bin_name = bin_name.strip("+").lower()
        bin_name_words = bin_name.split()
        messages = []
        for market in self.pi_api.get_markets():
            for contract in market.contracts:
                if all(
                        [bin_name in contract.name.lower() for bin_name in bin_name_words]
                ):
                    messages.append(
                            market.short_name
                            + " ("
                            + str(market.id)
                            + ") "
                            + str(int(contract.best_yes.pricePerShare * 100))
                            + "¢\n"
                    )
        if len(messages) == 0:
            msg += "No markets found!"
        else:
            for m in messages[20*page:20*page+20]:
                msg += m
            msg += (
                    "Displaying page " + str(page + 1) + " of " + str(len(messages)//20 + 1)
            )
        msg += "```"
        return Embed(title=title, description=msg, color=2206669), len(messages)//20 + 1

    def related_markets_title(self, name_frag, page):
        name_frag = name_frag.lower()
        title = 'Looking for markets containing "' + name_frag + '" in the title\n'
        msg = "```\n"
        name_frag = name_frag.strip("+").lower()
        name_frag_words = name_frag.split()
        messages = []
        for market in self.pi_api.get_markets():
            if all(
                    [
                        name_frag in market.name.lower()
                        or name_frag in market.short_name.lower()
                        for name_frag in name_frag_words
                    ]
            ):
                messages.append(market.short_name + " (" + str(market.id) + ")\n")
        if len(messages) == 0:
            msg += "No markets found!"
        else:
            for m in messages[20*page:20*page+20]:
                msg += m
            msg += (
                    "Displaying page " + str(page + 1) + " of " + str(len(messages)//20 + 1)
            )
        msg += "```"
        return Embed(title=title, description=msg, color=2206669), len(messages)//20 + 1

    def value_buy(self, market, bin):
        market = self.pi_api.get_market(market)
        title = 'Value buy for "' + market.short_name + '"\n'
        msg = "```\n"
        if len(list(market.contracts)) <= 1:
            msg += "This market only has one bin"
        else:
            msg += (
                    "Buying B"
                    + str(bin)
                    + " Yes costs "
                    + str(int(list(market.contracts)[bin - 1].best_yes.pricePerShare * 100))
                    + "¢\n"
            )
            risk = market.calc_risk_bin(bin - 1)
            msg += (
                    "Buying No on everything else would cost "
                    + str(int(risk * 100))
                    + "¢\n"
            )
        msg += "```"
        return Embed(title=title, description=msg, url=market.url, color=2206669)

    def divide_bins(self, market1, market2):
        market1 = self.pi_api.get_market(market1)
        market2 = self.pi_api.get_market(market2)
        divided_prices = {}
        for contract in market1.contracts:
            try:
                if contract.best_yes.costPerShareYes >= 0.02:
                    divided_prices[contract.shortName] = int(
                        contract.best_yes.costPerShareYes
                        / market2.get_contract(
                            bin_exact=contract.shortName
                        ).best_yes.costPerShareYes
                        * 100
                    )
            except AttributeError:
                pass
        print("Getting Difference")
        title = "Implied odds"
        msg = ""
        for name, div in divided_prices.items():
            msg += name + ": " + str(div) + "%\n"
        return Embed(title=title, description=msg, color=2206669)

    def buy(self, market, bin, yes, user):
        w = self.bank.get_wallet(user)
        s = Bank.contract_num_to_string(market, bin, self.pi_api)
        if s is None:
            print("None")
            return None
        p = w.buy_contract(market, s, yes, self.pi_api)
        self.bank.save_to_file("bank")
        return p

    def sell(self, market, bin, yes, user):
        w = self.bank.get_wallet(user)
        s = Bank.contract_num_to_string(market, bin, self.pi_api)
        if s is None:
            return False
        profit = w.sell_contract(market, s, yes, self.pi_api)
        self.bank.save_to_file("bank")
        return profit

    def list_bets(self, page, user, sold):
        title = user + "'s bets"
        msg = "```" + str(page + 1) + "\n"
        wallet = self.bank.get_wallet(user)
        msg += wallet.to_string(page, sold, self.pi_api)
        msg += "```" + "\nDisplaying page " + str(page + 1) + " of " + str(len(wallet.bets) // 25 + 1)
        return Embed(title=title, description=msg, color=2206669), len(wallet.bets) // 25 + 1

    def profit(self, user):
        title = user + "'s current profit"
        bets = self.bank.get_wallet(user)
        profit = bets.profit(self.pi_api)
        msg = "If you maxed out each of their bets when they added it, you would have made $" + str(round(profit, 2)) + "! "
        return Embed(title=title, description=msg, color=2206669)

    def leaderboard(self, page):
        title = "Leaderboard"
        msg = "```" + str(page + 1) + "\n"
        msg += self.bank.to_string(page, self.pi_api)
        msg += "```" + "\nDisplaying page " + str(page + 1) + " of " + str(len(self.bank.wallets) // 25 + 1)
        return Embed(title=title, description=msg, color=2206669), len(self.bank.wallets) // 25 + 1

    def project(self, user):
        title = user + "'s bets"
        w = self.bank.get_wallet(user)
        profit = w.project(self.pi_api)
        msg = "If you maxed out each 99% bet at current prices, you would make $" + str(
            round(profit, 2)) + " on $" + str(850*len([i for i in w.bets if i.last_price != 1])) + " principal IF they all resolved in our favor! "
        return Embed(title=title, description=msg, color=2206669)

    def remove(self, user, market, bin, side):
        w = self.bank.get_wallet(user)
        s = Bank.contract_num_to_string(market, bin, self.pi_api)
        if s is not None and w.remove_contract(market, s, side, self.pi_api):
            self.bank.save_to_file("bank")
            return Embed(title="Success")
        return Embed(title="Failure")

    def poly_bins(self, guess):
        q = self.poly_api.search_questions(guess)
        embed = Embed(title=q.name, color=2206669, url="https://www.polymarket.com/market/"+q.slug)
        if len(q.outcomes) == 2:
            max_len = max(len(q.outcomes[0] + q.outcomePrices[0]), len(q.outcomes[1] + q.outcomePrices[1])) + 2
            msg = "```" + "\n"
            msg += space(q.outcomes[0], '', '', "$" + q.outcomePrices[0], max_len) + "\n"
            msg += space(q.outcomes[1], '', '', "$" + q.outcomePrices[1], max_len) + "\n"
            msg += "```"
            embed.add_field(name="Outcomes", value=msg)
        msg = "```" + "\n"
        msg += space("liquidity", '', '', q.liquidity, 35) + "\n"
        msg += space("volume", '', '', q.volume, 35) + "\n"
        category = q.category if q.category else "None"
        msg += space("category", '', '', category, 35) + "\n"
        end = q.end_date if q.end_date else "None"
        msg += space("end date", '', '', end, 35) + "\n"
        closed = "Yes" if q.closed else "No"
        msg += space("closed", '', '', str(closed), 35) + "\n"
        msg += "```"
        embed.add_field(name="Stats", value=msg, inline=False)
        if q.icon:
            embed.set_thumbnail(url=q.icon)
        return embed

    def cat(self):
        embed = Embed(title="cat.")
        embed.set_image(url=requests.get("http://theoldreader.com/kittens/600/400").url)
        return embed

    def dog(self):
        embed = Embed(title="dog.")
        embed.set_image(url=requests.get("https://dog.ceo/api/breeds/image/random").json()["message"])
        return embed

    def calc(self, input):
        try:
            response = self.wolfram.query(input)
            img = next(response.results)["subpod"]["img"]["@src"]
            return Embed(title="Result").set_image(url=img)
        except StopIteration or AttributeError:
            return Embed(title="Result not Found")
        except:
            traceback.print_exc()
            return Embed(title="error :(", description="please try again later")
