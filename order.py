from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
import math
import time
# import win32api

class InitOrder():

    def __init__(self):
        apikey = ""
        secretkey = ""
        self.client = Client(apikey, secretkey)

        # gt = self.client.get_server_time()
        # tt=time.gmtime(int((gt["serverTime"])/1000))
        # win32api.SetSystemTime(tt[0],tt[1],0,tt[2],tt[3],tt[4],tt[5],0) # fix local time, find other fix

    def getargs(self, message): # basic check for number of arguments
        self.args = message.split(" ")
        if (len(self.args) != 2):
            return False
        else:
            self.symbol = self.args[0].upper()
            self.amount = float(self.args[1])
            return True

    def checksymbol(self):
        if str(self.symbol.upper() + "USDT") in (x["symbol"] for x in self.client.get_ticker()):
            self.detour = False
            self.ticker = str(self.symbol + "USDT")
            return True
        elif str(self.symbol.upper() + "BTC") in (x["symbol"] for x in self.client.get_ticker()):
            self.detour = True
            self.ticker = str(self.symbol + "BTC")
            return True

    ########################################################################

    def executetransaction(self):
        if not self.detour:
            self.directorder(self.ticker)
        else:
            self.detourorder(self.ticker)

    def getquantity(self, ticker): # rounds down the number that will be bought
        self.quantity = self.amount / float(self.price)
        info = self.client.get_symbol_info(ticker)["filters"]
        for x in range(len(info)):
            if "stepSize" in info[x]:
                stepsize = float(info[x]["stepSize"])
        multiplier = stepsize ** -1

        self.quantity = math.floor(self.quantity * multiplier) / multiplier

    def directorder(self, ticker):
        self.price = self.client.get_symbol_ticker(symbol = ticker)["price"]
        self.getquantity(ticker)
        resp = self.client.order_market_buy(symbol= ticker, quantity=self.quantity, newOrderRespType="FULL")
        print(resp)
        return resp

    def detourorder(self, ticker):
        detourorder = self.directorder("BTCUSDT") # min buy for BTCUSDT pair is 10$ -> triggers BinanceAPIException automatically, followuporder is not executed
        self.amount = float(detourorder["executedQty"]) # reset amount for followup order
        time.sleep(3)
        followuporder = self.directorder(self.ticker)
