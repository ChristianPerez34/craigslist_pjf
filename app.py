import csv
import random
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class CraigslistPJF:

    def __init__(self, *args, **kwargs):
        self.today = datetime.today().date()
        self.url = kwargs.pop("url", None)
        self.cities = []
        self.gigs = []

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
        self.cities = self.cities[:num_cities]

    def scrape_gigs(self):
        for link in self.cities:
            gig_page = requests.get(f"{link}search/ggg?")
            gig_soup = BeautifulSoup(gig_page.content, 'html.parser')
            gig_posts = gig_soup.find_all("p", class_="result-info")

            for post in gig_posts:
                date_str = post.find("time").attrs["datetime"]
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M").date()

                if (self.today - date).days < 4:
                    gig = post.find(class_="result-title")
                    gig_link = gig.attrs["href"]
                    self.gigs.append({'link': gig_link, 'title': gig.text})
                else:
                    break

    def output_to_excel(self):
        with open('craigslist_gigs.csv', mode='w', encoding='utf-8') as csv_file:
            fieldnames = ['link', 'title']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(self.gigs)

    def scrape_jobs(self):
        pass


pjf = CraigslistPJF(url="https://www.craigslist.org/about/sites#US")
pjf.get_us_cities_links()
pjf.select_rand_cities(num_cities=5)
pjf.scrape_gigs()
pjf.output_to_excel()
