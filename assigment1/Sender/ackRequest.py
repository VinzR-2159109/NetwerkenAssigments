import requests

class AckRequest:
    def __init__(self, url):
        self.url = url
    
    def send_request(self, method='GET', params=None, data=None, headers=None):
        try:
            response = requests.request(method, self.url, params=params, data=data, headers=headers)
            response.raise_for_status()
            return response.json() if response.status_code != 204 else None
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"