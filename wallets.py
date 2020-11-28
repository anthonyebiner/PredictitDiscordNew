import pickle
import utils


class Purchase:
    def __init__(self, market: int, contract: str, side: bool, pi_api: "PredictIt"):
        self.market = market
        self.contract = contract
        self.side = side
        self.sell_price = None

        self.last_price = 1
        self.purchase_price = self.current_price(pi_api)
        self.last_price = self.purchase_price

    def verify(self, pi_api: "PredictIt") -> bool:
        m = pi_api.get_market(self.market)
        if m is None:
            return False
        c = m.get_contract(bin_exact=self.contract)
        if c is None:
            return False
        return True

    def current_price(self, pi_api: "PredictIt") -> float:
        try:
            c = pi_api.get_market(self.market).get_contract(bin_exact=self.contract)
            self.last_price = c.best_yes.costPerShareYes if self.side else c.best_no.costPerShareNo
        except AttributeError:
            if self.last_price > .5:
                self.last_price = 1
            else:
                self.last_price = 0
        return self.last_price

    def profit(self, pi_api: "PredictIt") -> float:
        if self.sell_price is not None:
            current_price = self.sell_price
        else:
            current_price = self.current_price(pi_api)
        fee = (current_price - self.purchase_price) * .1 if current_price - self.purchase_price > 0 else 0
        return 850 * (current_price - self.purchase_price - fee)

    def project(self, pi_api: "PredictIt") -> float:
        if self.sell_price is not None:
            current_price = self.current_price(pi_api)
            fee = (1 - current_price) * .1 if 1 - current_price > 0 else 0
            return 850 * (1 - current_price - fee)
        else:
            return self.profit(pi_api)

    def sell(self, pi_api: "PredictIt") -> bool:
        if self.sell_price is None:
            self.sell_price = self.current_price(pi_api)
            return True
        else:
            return False

    def to_string(self, sold_view: bool, pi_api: "PredictIt"):
        if self.side:
            s = "YES"
        else:
            s = "NO"
        if sold_view:
            current_price = self.sell_price if self.sell_price is not None else self.current_price(pi_api)
            m = "¢ s> " if self.sell_price is not None else "¢ -> "
            return utils.space(str(self.market) + "[",
                               self.contract,
                               " " + s + "]",
                               str(int(self.purchase_price * 100)) + m + str(int(current_price * 100)) + "¢",
                               48)
        else:
            return utils.space(str(self.market) + "[",
                               self.contract,
                               " " + s + "]",
                               str(int(self.current_price(pi_api) * 100)) + "¢",
                               48)


class Wallet:
    def __init__(self, user: str):
        self.user = user
        self.bets = []

    def buy_contract(self, market: int, contract: str, side: bool, pi_api: "PredictIt") -> Purchase:
        for bet in self.bets:
            if bet.market == market and bet.contract == contract and bet.side == side:
                return 0
        p = Purchase(market, contract, side, pi_api)
        self.bets.append(p)
        return p

    def sell_contract(self, market: int, contract: str, side: bool, pi_api: "PredictIt") -> float:
        for bet in self.bets:
            if bet.market == market and bet.contract == contract and bet.side == side:
                if not bet.sell(pi_api):
                    return None
                return bet.profit(pi_api)
        return None

    def remove_contract(self, market: int, contract: str, side: bool, pi_api: "PredictIt") -> bool:
        for bet in self.bets:
            if bet.market == market and bet.contract == contract and bet.side == side:
                self.bets.remove(bet)
                return True
        return False

    def get_purchase(self, market: int, contract: str, side: bool) -> Purchase:
        for bet in self.bets:
            if bet.market == market and bet.contract == contract and bet.side == side:
                return bet
        return None

    def profit(self, pi_api: "PredictIt") -> float:
        profit = 0
        for bet in self.bets:
            profit += bet.profit(pi_api)
        return profit

    def project(self, pi_api: "PredictIt") -> float:
        profit = 0
        for bet in self.bets:
            profit += bet.project(pi_api)
        return profit

    def save_to_file(self, filename: str):
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def from_file(filename: str) -> "Wallet":
        with open(filename, "rb") as f:
            return pickle.load(f)

    def to_string(self, page: int, sold_view: bool, pi_api: "PredictIt"):
        if not sold_view:
            self.bets.sort(key=lambda x: x.current_price(pi_api))
        msg = ""
        for bet in self.bets[page * 25:25 + page * 25]:
            msg += bet.to_string(sold_view, pi_api) + "\n"
        return msg


class Bank:
    def __init__(self):
        self.wallets = []

    def get_wallet(self, user: str) -> Wallet:
        for wallet in self.wallets:
            if wallet.user == user:
                return wallet
        wallet = Wallet(user)
        self.wallets.append(wallet)
        return wallet

    def remove_wallet(self, user: str) -> bool:
        for wallet in self.wallets:
            if wallet.user == user:
                self.wallets.remove(wallet)
                return True
        return False

    def profits(self, pi_api: "PredictIt") -> list:
        profits = []
        for wallet in self.wallets:
            profits.append([wallet.user, wallet.profit(pi_api)])
        return profits

    @staticmethod
    def contract_num_to_string(market: int, num: int, pi_api: "PredictIt") -> str:
        num -= 1
        m = pi_api.get_market(market)
        if m is None:
            return None
        c = m.get_contract(bin_num=num)
        if c is None:
            return None
        return c.shortName

    def save_to_file(self, filename: str):
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def from_file(filename: str) -> "Bank":
        with open(filename, "rb") as f:
            return pickle.load(f)

    def to_string(self, page: int, pi_api: "PredictIt"):
        self.wallets.sort(key=lambda x: x.profit(pi_api), reverse=True)
        msg = ""
        for leader in self.wallets[page * 25:25 + page * 25]:
            start = leader.user
            msg += utils.space(start, '', '', "$" + str(round(leader.profit(pi_api), 2)), 48) + "\n"
        return msg
