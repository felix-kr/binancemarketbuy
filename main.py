from telegrambot import Telegrambot
import time
import order

tbot = Telegrambot()

while True:
    try:
        answer = tbot.getupdates()
        if answer["result"]:
            initorder = order.InitOrder() # initialize Order instance
            if initorder.getargs(answer["result"][0]["message"]["text"]): # args is only not nontype if message format is correct
                if initorder.checksymbol():
                    try:
                        initorder.executetransaction()
                        tbot.sendmsg("order executed")
                    except order.BinanceAPIException as e:
                        tbot.sendmsg(e.message)
                else:
                    print("wrong symbol")
            else:
                print("wrong format")

        time.sleep(0.5)
    except Exception as e:
        print(e)
        time.sleep(10)
        continue
