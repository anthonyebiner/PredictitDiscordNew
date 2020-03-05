import requests
import auths

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
            yield None
        for yes in self._yes:
            yield Offer(yes)

    @property
    def no_offers(self):
        if not self._no:
            return None
        for no in self._no:
            yield Offer(no)

    def buy_no(self, bin, num_shares, price):
        pass

    def buy_yes(self, bin, num_shares, price):
        pass

    def buy_spread(self, spread):
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


class API:
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

    def get_market(self, market_id=None, market_str=None):
        assert market_id or market_str
        markets = self.get_markets()
        if market_id:
            for market in markets:
                if str(market.id) == str(market_id):
                    return market


api = API(auths.username, auths.password)
