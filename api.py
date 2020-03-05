import requests


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
        for yes in self._yes:
            yield Offer(yes)

    @property
    def no_offers(self):
        for no in self._no:
            yield Offer(no)


class Market:
    def __init__(self, market_dict):
        pass


class API:
    def __init__(self, username, password):
        login_info = {'email': username, 'password': password, 'grant_type': 'password',
                      'rememberMe': 'false'}
        r = requests.post('https://www.predictit.org/api/Account/token', login_info)
        self.token = r.json()['access_token']
        self.username = username
        self.password = password

    def get_auth(self):
        login_info = {'email': self.username, 'password': self.password, 'grant_type': 'password',
                      'rememberMe': 'false'}
        r = requests.post('https://www.predictit.org/api/Account/token', login_info)
        self.token = r.json()['access_token']

    def get_markets(self):
        pass

    def get_market(self, market_id=None, market_str=None):
        assert market_id or market_str
        markets = self.get_markets()
