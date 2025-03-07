import requests

class Requester:
    def __init__(self):
        self._request = None

    def get(url):
        try:
            content = None
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            }
            req = requests.get(url, headers=headers)
        
            if req.status_code == 200:
                content = req.content

            return content
        except:
            return None
        