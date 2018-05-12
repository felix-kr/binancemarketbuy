import telegrambot as tbot
import time
import order
import threading

def getupdates():
    while True:
        answer = tbot.getupdates()
        if answer["result"]:
            return answer["result"][0]["message"]["text"]
        time.sleep(1)

def prompt():
    tbot.sendmsg("Start trailing SL? (y/n)")
    resp = getupdates()
    if resp == "y":
        tbot.sendmsg("Starting SL")
        return True
    elif resp == "n":
        tbot.sendmsg("Not starting SL")
        return False
    else:
        print("Wrong answer")
        prompt()

while True:
    try:
        message = getupdates()

        try:
            client = order.Order(message) # initialize Order instance
            resp = client.executetransaction()
            print(resp)
            if prompt():
                t = threading.Thread(target=client.setsl, args=(resp,))
                t.start()
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
