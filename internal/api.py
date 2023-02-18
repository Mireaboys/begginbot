import requests
import threading

def GET(url):
        try:
            requests.get(url)
        except Exception as err:
            print(err)
    
def POST(url, data):
    try:
        requests.post(url, json=data)
    except Exception as err:
        print(err)

class FakeAsyncApi:
    def __init__(self, url, port=9001):
        self.url = url
        self.port = port
        self.full_url = f"{self.url}:{self.port}"

    def post(self, data):
        threading.Thread(target=POST, args=(self.full_url, data)).start()

    def get(self):
        threading.Thread(target=GET, args=(self.full_url)).start()