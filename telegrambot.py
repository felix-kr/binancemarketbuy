import requests
import json

token = ""
chatid = ""
last_update_id = 0

def getupdates():
    global last_update_id
    url = "https://api.telegram.org/bot" + token + "/getUpdates"
    values = {"offset": last_update_id}
    r = requests.get(url, params=values)
    data = r.content.decode("utf-8") # convert bytes to str
    answer = json.loads(data) # convert string that represents dict to dict

    if answer["result"]:
        last_update_id = answer["result"][0]["update_id"] + 1 # answer["result"] can never have more than one item (after an instance was created) because Telegram API only sends back messages with update_id > self.last_update_id

    return answer

def sendmsg(message):
    url = "https://api.telegram.org/bot" + token + "/sendMessage"
    values = {"chat_id" : chatid, "text" : message}
    requests.get(url, params=values)

if __name__ == "__main__":
    ans = getupdates()
    print(ans)
    sendmsg("abc")
