import requests
import json
import time

class Telegrambot:

    def __init__(self):
        self.token = ""
        self.chatid = ""
        self.last_update_id = 0

    def getupdates(self):
        url = "https://api.telegram.org/bot" + self.token + "/getUpdates"
        values = {"offset": self.last_update_id}
        r = requests.get(url, params=values)
        data = r.content.decode("utf-8") # convert bytes to str
        answer = json.loads(data) # convert string that represents dict to dict

        if answer["result"]:
            self.last_update_id = answer["result"][0]["update_id"] + 1 # answer["result"] can never have more than one item (after an instance was created) because Telegram API only sends back messages with update_id > self.last_update_id

        return answer

    def sendmsg(self, message):
        url = "https://api.telegram.org/bot" + self.token + "/sendMessage"
        values = {"chat_id" : self.chatid, "text" : message}
        requests.get(url, params=values)

if __name__ == "__main__":
    tbot = Telegrambot()
    while True:
        print(tbot.getupdates())
        time.sleep(0.5)
