import time

import requests
import auths
from utils import optShares
import math
import re
from fuzzywuzzy import fuzz
import threading
from discord import Embed
import numpy as np
import random


class Offer:
    def __init__(self, offer_dict):
        self.costPerShareNo = offer_dict['costPerShareNo']
        self.costPerShareYes = offer_dict['costPerShareYes']
        self.pricePerShare = offer_dict['pricePerShare']
        self.quantity = offer_dict['quantity']
        self.tradeType = offer_dict['tradeType']


class Contract:
    def __init__(self, orderbook_dict, contract_dict, market, token):
        self.timestamp = orderbook_dict['timestamp']
        self._yes = orderbook_dict['yesOrders']
        self._no = orderbook_dict['noOrders']
        self.name = contract_dict['name']
        self.id = contract_dict['id']
        self.image = contract_dict['image']
        self.shortName = contract_dict['shortName']
        self.status = contract_dict['status']
        self.market = market
        self.token = token

    @property
    def yes_offers(self):
        if not self._yes:
            empty_offer = {
                "costPerShareNo": 0,
                "costPerShareYes": 1,
                "pricePerShare": 0,
                "quantity": 0,
                "tradeType": 0
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
                "tradeType": 1
            }
            yield Offer(empty_offer)
        else:
            for no in self._no:
                yield Offer(no)

    @property
    def best_no(self):
        return list(self.no_offers)[0]

    def _make_trade(self, num_shares, price, long):
        print(num_shares, price, int(long), self.id)
        response = requests.post("https://www.predictit.org/api/Trade/SubmitTrade",
                                 data="quantity=" + str(num_shares) + "&pricePerShare=" + str(
                                     price) + "&contractId=" + str(
                                     self.id) + "&tradeType=" + str(int(long)),
                                 headers={'Authorization': 'Bearer ' + self.token,
                                          'Content-Type': 'application/x-www-form-urlencoded'})
        print(response)
        return response.status_code == 200

    def buy_no(self, num_shares, price=None):
        if price is None:
            price = int(self.best_no.pricePerShare * 100)
        return self._make_trade(num_shares, price, False)

    def buy_yes(self, num_shares, price):
        if price is None:
            price = int(self.best_yes.pricePerShare * 100)
        return self._make_trade(num_shares, price, True)


class Market:
    def __init__(self, market_dict, orderbook, token):
        self.id = market_dict['id']
        self.name = market_dict['name']
        self.short_name = market_dict['shortName']
        self.image = market_dict['image']
        self.url = market_dict['url']
        self._contracts = market_dict['contracts']
        self._orderbook = orderbook
        self.token = token

    @property
    def contracts(self):
        for contract in self._contracts:
            orderbook = self._orderbook[str(contract['id'])]
            yield Contract(orderbook, contract, self, self.token)

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
        share_multiplier = (max_shares / costliest) / optShares(costliest)
        best_holds = []
        for contract in contracts:
            if contract.best_no.quantity:
                best_holds.append(math.floor(share_multiplier * optShares(contract.best_no.pricePerShare)))
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
            guess = re.sub(r'[^\w\s]', '', bin_name).lower()
            guess_words = guess.split()
            most_matches = 0
            best_diff = 0
            best_diff_contract = 0
            for contract in self.contracts:
                short_name = re.sub(r'[^\w\s]', '', contract.name).lower()
                matches = sum([word in short_name or word in short_name for word in guess_words])
                diff1 = fuzz.token_sort_ratio(guess, short_name)
                if matches > most_matches or (matches >= most_matches and (diff1 > best_diff)):
                    best_diff = diff1
                    best_diff_contract = contract
                if matches > most_matches:
                    most_matches = matches
            return best_diff_contract
        elif bin_exact is not None:
            for contract in self.contracts:
                if contract.shortName == bin_exact:
                    return contract

    def buy_spread(self, spread):
        for i, num in enumerate(spread):
            if num:
                res = self.get_contract(bin_num=i).buy_no(num)
                time.sleep(.25)


class PredictIt:
    def __init__(self, username, password):
        login_info = {'email': username, 'password': password, 'grant_type': 'password',
                      'rememberMe': 'false'}
        r = requests.post('https://www.predictit.org/api/Account/token', login_info)
        self.session = requests.session()
        self.token = r.json()['access_token']
        self.username = username
        self.password = password
        self._markets = requests.get('https://www.predictit.org/api/marketdata/all').json()
        self._orderbook = requests.get('https://predictit-f497e.firebaseio.com/contractOrderBook.json').json()

    def reload_markets(self):
        self._markets = self.session.get('https://www.predictit.org/api/marketdata/all').json()

    def reload_orderbook(self):
        r = self.session.get('https://predictit-f497e.firebaseio.com/contractOrderBook.json')
        print(r)
        self._orderbook = r.json()

    def get_max_invested(self, market_id):
        contracts = self.session.get("https://www.predictit.org/api/Market/{}/Contracts".format(market_id),
                                 headers={'Authorization': 'Bearer ' + self.token,
                                          'Content-Type': 'application/x-www-form-urlencoded'}).json()
        invested = []
        prices = []
        for contract in contracts:
            invested += [contract['userQuantity']]
            prices += [contract['bestNoPrice']]
        return max(invested), prices

    def get_auth(self):
        login_info = {'email': self.username, 'password': self.password, 'grant_type': 'password',
                      'rememberMe': 'false'}
        r = self.session.post('https://www.predictit.org/api/Account/token', login_info)
        self.token = r.json()['access_token']

    def get_markets(self):
        for market in self._markets['markets']:
            yield Market(market, self._orderbook, self.token)

    def _get_market_id(self, market_str):
        guess = re.sub(r'[^\w\s]', '', market_str).lower()
        guess_words = guess.split()
        most_matches = 0
        best_diff = 0
        best_diff_id = 0
        for market in self.get_markets():
            short_name = re.sub(r'[^\w\s]', '', market.short_name).lower()
            long_name = re.sub(r'[^\w\s]', '', market.name).lower()
            matches = sum([word in short_name or word in long_name for word in guess_words])
            diff1 = fuzz.token_sort_ratio(guess, short_name)
            diff2 = fuzz.token_sort_ratio(guess, long_name)
            if matches > most_matches or (matches >= most_matches and (diff1 > best_diff or diff2 > best_diff)):
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
        reload_markets_thread = threading.Thread(target=self.reload_markets_thread, daemon=True)
        reload_markets_thread.start()
        reload_orderbook_thread = threading.Thread(target=self.reload_orderbook_thread, daemon=True)
        reload_orderbook_thread.start()
        reload_auth_thread = threading.Thread(target=self.reload_auth_thread, daemon=True)
        reload_auth_thread.start()
        self.old_markets = {}

    def reload_auth_thread(self):
        while True:
            time.sleep(60*60*3+random.randrange(0, 60*60*2))
            self.pi_api.get_auth()

    def reload_markets_thread(self):
        while True:
            time.sleep(60 * 10)
            self.pi_api.reload_markets()

    def reload_orderbook_thread(self):
        while True:
            time.sleep(27.5 + random.randrange(0, 5))
            self.pi_api.reload_orderbook()
            self.buy_risk(50)

    def buy_risk(self, share_max):
        for market in self.pi_api.optimize_all():
            print("buying neg risk in " + str(market.id))
            max_invested, prices = self.pi_api.get_max_invested(market.id)
            correct = True
            for i, contract in enumerate(market.contracts):
                if contract.best_no.pricePerShare and contract.best_no.pricePerShare != prices[i]:
                    correct = False
            if not correct:
                print('discrepancy detected')
                print(market.short_name)
                print([c.id for c in market.contracts])
                print([c.best_no.quantity for c in market.contracts])
                print([c.best_no.pricePerShare for c in market.contracts])
                print(prices)
                continue
            if max_invested > 800:
                continue
            spread, profit = market.optimize_spread()
            if min([i for i in spread if i != 0]) > share_max:
                spread, profit = market.optimize_spread(share_max)
            if profit > 0:
                market.buy_spread(spread)

    def check_swings(self):
        messages = []
        for market in self.pi_api.get_markets():
            try:
                old_prices = self.old_markets[market.id]
                for contract in market.contracts:
                    if abs(contract.best_no.costPerShareYes - old_prices[contract.id]) >= .25:
                        change = int(contract.best_no.costPerShareYes - old_prices[contract.id] * 100)
                        title = "Price swing detected in {}".format(market.short_name)
                        msg = "```\n"
                        msg += "\nContract '{}' has moved {}¢ in the past 30 seconds\n".format(contract.name, change)
                        msg += "```"
                        messages.append(Embed(title=title, description=msg, url=market.url, color=2206669))
                        old_prices[contract.id] = contract.best_no.costPerShareYes
            except KeyError:
                self.old_markets[market.id] = {}
                for contract in market.contracts:
                    self.old_markets[market.id][contract.id] = contract.best_no.costPerShareYes
        return messages

    def orderbook(self, market):
        market = self.pi_api.get_market(market)
        title = 'Orderbook for "' + market.name + '"\n'
        offers = list(market.contracts)
        max_len = 0
        for contract in offers:
            if len(contract.name) > max_len:
                max_len = len(contract.name)
        msg = '```\n'
        msg += ' ' * (max_len + 2) + 'YES  OFFERS  NO  OFFERS\n'
        for contract in offers:
            if contract.best_no.quantity:
                msg += ' ' * (max_len - len(contract.name)) + str(contract.name)
                msg += '  ' + str(int(contract.best_yes.pricePerShare * 100)) + (
                        ' ' * (3 - len(str(int(contract.best_yes.pricePerShare * 100))))) + '  ' + str(
                    contract.best_yes.quantity) + ' ' * (6 - len(str(contract.best_yes.quantity)))
                msg += '  ' + str(int(contract.best_no.pricePerShare * 100)) + (
                        ' ' * (3 - len(str(int(contract.best_no.pricePerShare * 100))))) + '  ' + str(
                    contract.best_no.quantity) + '\n'
        msg += '```'
        return Embed(title=title, description=msg, url=market.url, color=2206669)

    def risk_market(self, market, max_shares=None, minimize=False):
        market = self.pi_api.get_market(market)
        if max_shares is None:
            max_shares = market.lowest_no_quantity
        title = 'Market risk for "' + market.short_name + '"\n'
        msg = ''
        spread, profit = market.optimize_spread(max_shares, minimize)
        if profit > 0:
            msg += 'Negative risk found!!!\n'
            spread = list(filter(lambda x: x != 0, spread))
            msg += 'Sum of 1 minus no is ' + str(market.sum_return()) + '\n'
            msg += 'Potential profit w/ below spread is ' + str(profit) + '\n'
            msg += 'Ideal spread is ' + str(spread) + '\n'
        else:
            msg += 'No negative risk available at ' + str(max_shares) + ' shares :('

        return Embed(title=title, description=msg, url=market.url, color=2206669)

    def risk_all(self, max_shares=None):
        title = 'There are {} markets with negative risk\n'
        msg = '```\n'
        n = 0
        for market in self.pi_api.optimize_all(max_shares):
            n += 1
            spread, profit = market.optimize_spread(max_shares)
            if max_shares:
                msg += "Market " + str(market.id) + ' (' + str(market.sum_return()) + ' / $' + str(profit) + ')\n'
            else:
                msg += "Market " + str(market.id) + ' (' + str(market.sum_return()) + ' / $' + str(
                    profit) + ' / ' + str(market.lowest_no_quantity) + ')\n'
        if n == 0:
            msg += ':('
        msg += '```'
        return Embed(title=title.format(n), description=msg, color=2206669)

    def bins(self, market):
        market = self.pi_api.get_market(market)
        title = 'Market bins for "' + market.short_name + '"\n'
        offers = list(market.contracts)
        max_len = 0
        for contract in offers:
            if len(contract.name) > max_len:
                max_len = len(contract.name)
        msg = '```\n'
        msg += ' ' * (max_len + 2) + 'YES  NO\n'
        for contract in offers:
            if contract.best_no.quantity:
                msg += ' ' * (max_len - len(contract.name)) + str(contract.name)
                msg += '  ' + str(int(contract.best_yes.pricePerShare * 100)) + (
                        ' ' * (3 - len(str(int(contract.best_yes.pricePerShare * 100)))))
                msg += '  ' + str(int(contract.best_no.pricePerShare * 100)) + (
                        ' ' * (3 - len(str(int(contract.best_no.pricePerShare * 100))))) + '\n'
        msg += '```'
        return Embed(title=title, description=msg, url=market.url, color=2206669)

    def related_markets_bin(self, bin_name):
        title = 'Looking for markets containing "' + bin_name + '" as a bin\n'
        msg = '```\n'
        n = 0
        m = 1
        for letter in bin_name:
            if letter == '+':
                m += 1
        bin_name = bin_name.strip('+').lower()
        bin_name_words = bin_name.split()
        for market in self.pi_api.get_markets():
            for contract in market.contracts:
                if all([bin_name in contract.name.lower() for bin_name in bin_name_words]):
                    if (20 * m) > n >= (20 * (m - 1)):
                        msg += market.short_name + ' (' + str(market.id) + ') ' + str(
                            int(contract.best_yes.pricePerShare * 100)) + '¢\n'
                    n += 1
        if n == 0:
            msg += "No markets found!"
        elif n >= 20 * m:
            msg += "Only displaying the first twenty markets, to get twenty more, run ,. " + bin_name + "+" * m
        msg += '```'
        return Embed(title=title, description=msg, color=2206669)

    def related_markets_title(self, name_frag):
        name_frag = name_frag.lower()
        title = 'Looking for markets containing "' + name_frag + '" in the title\n'
        msg = '```\n'
        n = 0
        m = 1
        for letter in name_frag:
            if letter == '+':
                m += 1
        name_frag = name_frag.strip('+').lower()
        name_frag_words = name_frag.split()
        for market in self.pi_api.get_markets():
            if all([name_frag in market.name.lower() or name_frag in market.short_name.lower() for name_frag in
                    name_frag_words]):
                if (20 * m) > n >= (20 * (m - 1)):
                    msg += market.short_name + ' (' + str(market.id) + ')\n'
                n += 1
        if n == 0:
            msg += "No markets found!"
        elif n >= 20 * m:
            msg += "Only displaying the first twenty markets, to get twenty more, run ,- " + name_frag + "+" * m
        msg += '```'
        return Embed(title=title, description=msg, color=2206669)

    def value_buy(self, market, bin):
        market = self.pi_api.get_market(market)
        title = 'Value buy for "' + market.short_name + '"\n'
        msg = '```\n'
        if len(list(market.contracts)) <= 1:
            msg += "This market only has one bin"
        else:
            msg += "Buying B" + str(bin) + " Yes costs " + str(
                int(list(market.contracts)[bin - 1].best_yes.pricePerShare * 100)) + '¢\n'
            risk = market.calc_risk_bin(bin - 1)
            msg += "Buying No on everything else would cost " + str(int(risk * 100)) + '¢\n'
        msg += '```'
        return Embed(title=title, description=msg, url=market.url, color=2206669)

    def divide_bins(self, market1, market2):
        market1 = self.pi_api.get_market(market1)
        market2 = self.pi_api.get_market(market2)
        divided_prices = {}
        for contract in market1.contracts:
            try:
                if contract.best_yes.costPerShareYes >= 0.02:
                    divided_prices[contract.shortName] = int(contract.best_yes.costPerShareYes / market2.get_contract(bin_exact=contract.shortName).best_yes.costPerShareYes * 100)
            except AttributeError:
                pass
        print('Getting Difference')
        title = "Implied odds"
        msg = ""
        for name, div in divided_prices.items():
            msg += name + ": " + str(div) + "%\n"
        return Embed(title=title, description=msg, color=2206669)
