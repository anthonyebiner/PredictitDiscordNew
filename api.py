import requests
import auths
from utils import optShares
import math
import re
from fuzzywuzzy import fuzz


class Offer:
    def __init__(self, offer_dict):
        self.costPerShareNo = offer_dict['costPerShareNo']
        self.costPerShareYes = offer_dict['costPerShareYes']
        self.pricePerShare = offer_dict['pricePerShare']
        self.quantity = offer_dict['quantity']
        self.tradeType = offer_dict['tradeType']


class Contract:
    def __init__(self, contract_dict):
        self.timestamp = contract_dict['timestamp']
        self._yes = contract_dict['yesOrders']
        self._no = contract_dict['noOrders']

    @property
    def yes_offers(self):
        if not self._yes:
            empty_offer = {
                "costPerShareNo": 1,
                "costPerShareYes": 0,
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
                "costPerShareNo": 0,
                "costPerShareYes": 1,
                "pricePerShare": 0,
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

    def buy_no(self, bin, num_shares, price):
        pass

    def buy_yes(self, bin, num_shares, price):
        pass


class Market:
    def __init__(self, market_dict, orderbook):
        self.id = market_dict['id']
        self.name = market_dict['name']
        self.short_name = market_dict['shortName']
        self.image = market_dict['image']
        self.url = market_dict['url']
        self._contracts = market_dict['contracts']
        self._orderbook = orderbook

    @property
    def contracts(self):
        for contract in self._contracts:
            yield Contract(self._orderbook[str(contract['id'])])

    def no_prices(self):
        prices = []
        for contract in self.contracts:
            if contract.best_no.pricePerShare != 0:
                prices += [contract.best_no.pricePerShare]
        return prices

    def yes_prices(self):
        prices = []
        for contract in self.contracts:
            if contract.best_yes.pricePerShare != 0:
                prices += [contract.best_yes.pricePerShare]
        return prices

    def sum_return(self):
        total = 0
        for price in self.no_prices():
            total += 1 - price
        return round(total, 3)

    def _calc_risk(self, spread):
        prices = [contract.best_no.pricePerShare for contract in list(self.contracts)]
        share_value = [spread[i] * prices[i] for i in range(len(prices))]
        if_no = [round((spread[i] - share_value[i]) - 0.1 * (spread[i] - share_value[i]), 3) for i in
                 range(len(prices))]
        if_yes = [-(share_value[i]) for i in range(len(prices))]
        risk = [round(if_yes[i] + sum(if_no[0:i]) + sum(if_no[i + 1:]), 3) for i in range(len(prices))]
        return risk

    def _calc_risk_bin(self, bin):
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
        costliest = max(self.no_prices())
        share_multiplier = (max_shares / costliest) / optShares(costliest)
        best_holds = []
        for contract in contracts:
            if contract.best_no.quantity:
                best_holds.append(math.floor(share_multiplier * optShares(contract.best_no.pricePerShare)))
            else:
                best_holds.append(0)
        return best_holds

    def optimize_spread(self, max_shares, minimize=True):
        maximum = max_shares
        max_profit = 0
        max_spread = []
        while maximum > 0:
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

    def buy_spread(self, spread):
        pass


class PredictIt:
    def __init__(self, username, password):
        # login_info = {'email': username, 'password': password, 'grant_type': 'password',
        #               'rememberMe': 'false'}
        # r = requests.post('https://www.predictit.org/api/Account/token', login_info)
        # self.token = r.json()['access_token']
        # self.username = username
        # self.password = password
        self._markets = requests.get('https://www.predictit.org/api/marketdata/all').json()
        self._orderbook = requests.get('https://predictit-f497e.firebaseio.com/contractOrderBook.json').json()

    def reload_markets(self):
        self._markets = requests.get('https://www.predictit.org/api/marketdata/all').json()

    def reload_orderbook(self):
        self._orderbook = requests.get('https://predictit-f497e.firebaseio.com/contractOrderBook.json').json()

    def get_auth(self):
        login_info = {'email': self.username, 'password': self.password, 'grant_type': 'password',
                      'rememberMe': 'false'}
        r = requests.post('https://www.predictit.org/api/Account/token', login_info)
        self.token = r.json()['access_token']

    def get_markets(self):
        for market in self._markets['markets']:
            yield Market(market, self._orderbook)

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


class Discord:
    def __init__(self, pi_api: PredictIt):
        self.pi_api = pi_api

    def orderbook(self, market):
        market = self.pi_api.get_market(market)
        pass

    def risk(self):
        pass

    def bins(self):
        pass

    def related_markets_bin(self):
        pass

    def related_markets_title(self):
        pass

    def divide_bins(self):
        pass

    def value_buy(self):
        pass


api = PredictIt(auths.username, auths.password)
print(api.get_market(market_str='Dem Nom').name)


