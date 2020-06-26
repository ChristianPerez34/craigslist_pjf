import random

import requests
from bs4 import BeautifulSoup


class CraigslistPJF:

    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop("url", None)
        self.cities = []

    def get_us_cities_links(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Retrieve first div that contains all US cities
        result = soup.find_all("div", class_="colmask")[0]

        # Get all US cities links
        self.cities = [city["href"] for city in result.find_all("a")]

    def select_rand_cities(self, num_cities):
        for i in range(100):
            random.shuffle(self.cities)
        return self.cities[:num_cities]


pjf = CraigslistPJF(url="https://www.craigslist.org/about/sites#US")
pjf.get_us_cities_links()
links = pjf.select_rand_cities(num_cities=5)
print(links)
