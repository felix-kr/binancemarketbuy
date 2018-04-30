from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
import math
import time

class Order():

    ########################################################################
    # setting up args

    def __init__(self, message):
        apikey = ""
        secretkey = ""
        self.client = Client(apikey, secretkey)
        self.getargs(message)
        self.checksymbol()

    def getargs(self, message): # basic check for number of arguments
        args = message.split(" ")
        if (len(args) != 2):
            raise FormatError()
        else:
            self.symbol = args[0].upper()
            self.usdamount = float(args[1])

    def checksymbol(self):
        if str(self.symbol.upper() + "USDT") in (x["symbol"] for x in self.client.get_ticker()):
            self.detour = False
            self.ticker = str(self.symbol + "USDT")
        elif str(self.symbol.upper() + "BTC") in (x["symbol"] for x in self.client.get_ticker()):
            self.detour = True
            self.ticker = str(self.symbol + "BTC")
        else:
            raise TickerError()

    ########################################################################
    # order execution

    def executetransaction(self):
        if not self.detour:
            resp = self.directorder(self.ticker, self.usdamount)
        else:
            resp = self.detourorder(self.ticker)
        return resp

    def directorder(self, ticker, amount):

        def getquantity(ticker, amount=amount):
            price = self.client.get_symbol_ticker(symbol = ticker)["price"]
            info = self.client.get_symbol_info(ticker)["filters"]
            for x in range(len(info)):
                if "stepSize" in info[x]:
                    stepsize = float(info[x]["stepSize"])
            multiplier = stepsize ** -1
            return math.floor((amount / float(price)) * multiplier) / multiplier

        quantity = getquantity(ticker)
        return self.client.order_market_buy(symbol=ticker, quantity=quantity, newOrderRespType="FULL")

    def detourorder(self, ticker):
        detourorder = self.directorder("BTCUSDT", self.usdamount) # min buy for BTCUSDT pair is 10$ -> triggers BinanceAPIException automatically, followuporder is not executed
        print(detourorder)
        quantity = float(detourorder["executedQty"]) # reset amount for followup order
        time.sleep(3)
        return self.directorder(self.ticker, quantity)

    ########################################################################
    # sending info

class FormatError(Exception): pass

class TickerError(Exception): pass
