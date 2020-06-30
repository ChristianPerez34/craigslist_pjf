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
        return self.cities[:num_cities]

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
                    gig_link_page = requests.get(gig_link)
                    gig_link_soup = BeautifulSoup(gig_link_page.content, 'html.parser')
                    gig_description = gig_link_soup.find("section", id="postingbody")
                    self.gigs.append((gig_link, gig.text, gig_description))
            print(post)

            # TODO: Only get gigs that have been posted in the last 3 days. 
            print(gig_soup)
        pass

    def output_to_excel(self):
        pass

    def scrape_jobs(self):
        pass


pjf = CraigslistPJF(url="https://www.craigslist.org/about/sites#US")
pjf.get_us_cities_links()
links = pjf.select_rand_cities(num_cities=5)
pjf.scrape_gigs()
print(links)
