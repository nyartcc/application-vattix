import requests


class APIClient:
    def __init__(self, url):
        self.url = url

    def get_data(self):
        response = requests.get(self.url)
        response.raise_for_status()  # Raises a HTTPError if the response status code is 4XX or 5XX
        data = response.json()  # Converts the JSON response to a Python dictionary
        return data

