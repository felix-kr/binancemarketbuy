from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
import math
import time
import telegrambot as tbot
# import win32api

class Order():

    ########################################################################
    # setting up args

    def __init__(self, message):
        apikey = ""
        secretkey = ""
        self.client = Client(apikey, secretkey)
        self.getargs(message)
        self.checksymbol()

        # gt = self.client.get_server_time()
        # tt=time.gmtime(int((gt["serverTime"])/1000))
        # win32api.SetSystemTime(tt[0],tt[1],0,tt[2],tt[3],tt[4],tt[5],0) # fix local time, find other fix

    def getargs(self, message): # basic check for number of arguments
        args = message.split(" ")
        if (len(args) != 2):
            raise FormatError()
        else:
            self.symbol = args[0].upper()
            self.usdamount = float(args[1].replace(",","."))

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
        return self.client.order_market(symbol=ticker,side="BUY", quantity=quantity, newOrderRespType="FULL")

    def detourorder(self, ticker):
        detourorder = self.directorder("BTCUSDT", self.usdamount) # min buy for BTCUSDT pair is 10$ -> triggers BinanceAPIException automatically, followuporder is not executed
        print(detourorder)
        quantity = float(detourorder["executedQty"]) # reset amount for followup order
        time.sleep(3)
        return self.directorder(self.ticker, quantity)

    ########################################################################
    # stoploss

    def setsl(self, resp):
        try:

            def roundprice(price):
                stepsize = self.client.get_symbol_info(self.ticker)["filters"][0]["tickSize"].find("1") - 1
                return round(price, stepsize)

            def updatesl(price, sl):
                while True:
                    time.sleep(20)
                    order = self.client.get_order(symbol=self.ticker, orderId=sl["orderId"])
                    currprice = float(self.client.get_symbol_ticker(symbol = self.ticker)["price"])
                    if (order["executedQty"] == order["origQty"] or order["status"] == "CANCELED"):
                        tbot.sendmsg("SL was canceled or filled")
                        if (self.ticker.endswith("BTC") and order["status"] != "CANCELED"):
                            tbot.sendmsg("selling btc for usdt")
                            print(self.client.order_market_sell(symbol="BTCUSDT", quantity=round(float(order["executedQty"]) * currprice, 6), newOrderRespType="FULL"))
                        break
                    elif currprice > price:
                        price = currprice
                        self.client.cancel_order(symbol=self.ticker, orderId=sl["orderId"])
                        time.sleep(1)
                        sl = self.client.create_order (symbol=self.ticker, type="STOP_LOSS_LIMIT", quantity=quantity , stopPrice=roundprice(price * 0.97), side="SELL", price=roundprice(price * 0.96), timeInForce="GTC")
                        updatesl(price, sl)
                    else: continue

            price = float(resp["fills"][0]["price"])
            quantity = float(resp["executedQty"])
            sl = self.client.create_order(symbol=self.ticker, type="STOP_LOSS_LIMIT", quantity=quantity , stopPrice=roundprice(price * 0.97), side="SELL", price=roundprice(price * 0.96), timeInForce="GTC")
            print(sl)
            updatesl(price, sl)

        except BinanceAPIException as e: # main loop doesn't catch exceptions in thread
            tbot.sendmsg(e)

class FormatError(Exception): pass

class TickerError(Exception): pass
