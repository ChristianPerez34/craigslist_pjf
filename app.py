import csv
import random
import time
from datetime import datetime
from pathlib import Path

import requests
import schedule
import yagmail
from bs4 import BeautifulSoup
from yattag import Doc


def send_email(recipients, subject, body):
    with yagmail.SMTP('pymail102') as yag:
        yag.send(recipients, subject, body)


class CraigslistPJF:

    def __init__(self, *args, **kwargs):
        self.today = datetime.today().date()
        self.url = kwargs.pop('url', None)
        self.cities = []
        self.gigs = []

    def get_us_cities_links(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Retrieve first div that contains all US cities
        result = soup.find_all('div', class_='colmask')[0]

        # Get all US cities links
        self.cities = [city['href'] for city in result.find_all('a')]

    def select_rand_cities(self, num_cities):
        for i in range(100):
            random.shuffle(self.cities)
        self.cities = self.cities[:num_cities]

    def scrape_gigs(self):
        for link in self.cities:
            gig_page = requests.get(f'{link}search/ggg?')
            gig_soup = BeautifulSoup(gig_page.content, 'html.parser')
            gig_posts = gig_soup.find_all('p', class_='result-info')

            for post in gig_posts:
                date_str = post.find('time').attrs['datetime']
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M').date()

                if (self.today - date).days < 4:
                    gig = post.find(class_='result-title')
                    gig_link = gig.attrs['href']
                    self.gigs.append({'link': gig_link, 'title': gig.text})
                else:
                    break

    def output_to_excel(self):
        with open('craigslist_gigs.csv', mode='w', encoding='utf-8', newline='') as csv_file:
            fieldnames = ['link', 'title']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(self.gigs)

    def scrape_jobs(self):
        pass


def job():
    pjf = CraigslistPJF(url='https://www.craigslist.org/about/sites#US')
    pjf.get_us_cities_links()
    pjf.select_rand_cities(num_cities=5)
    pjf.scrape_gigs()
    pjf.output_to_excel()

    doc, tag, text, line = Doc().ttl()
    recipients = ['christian.perez34@outlook.com']
    subject = f"Craigslist Gigs {datetime.today().date()}"

    with tag('p'):
        text("Today's list of available gigs")
        line('br', '')
    with tag('table'):
        with tag('tr'):
            with tag('th'):
                text('Link')
            with tag('th'):
                text('Title')
        for gig in pjf.gigs:
            with tag('tr'):
                with tag('td'):
                    with tag('a', href=gig['link']):
                        text(gig['link'])
                with tag('td'):
                    text(gig['title'])

    message = doc.getvalue()
    attachment = Path("craigslist_gigs.csv").resolve()
    content = [message, str(attachment)]
    send_email(recipients, subject, content)


schedule.every().day.at("10:00").do(job)
while True:
    schedule.run_pending()
    time.sleep(1)
