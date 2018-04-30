from telegrambot import Telegrambot
import time
import order

tbot = Telegrambot()

def getupdates():
    while True:
        answer = tbot.getupdates()
        if answer["result"]:
            return answer["result"][0]["message"]["text"]
        time.sleep(1)

while True:
    try:
        message = getupdates()
        try:
            client = order.Order(message) # initialize Order instance
            resp = client.executetransaction()
            print(resp)
        except order.FormatError:
            tbot.sendmsg("wrong format")
        except order.TickerError:
            tbot.sendmsg("wrong ticker")
        except order.BinanceAPIException as e:
            tbot.sendmsg(e.message)


    except Exception as e:
        print(e)
        time.sleep(10)
        continue
