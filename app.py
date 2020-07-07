import csv
import os
import random
import time
from datetime import datetime
from pathlib import Path

import requests
import schedule
import yagmail
from bs4 import BeautifulSoup
from yattag import Doc


class CraigslistPJF:

    def __init__(self, *args, **kwargs):
        self.today = datetime.today().date()
        self.url = kwargs.pop('url', None)
        self.cities = []
        self.gigs = []

    def get_us_cities_links(self):
        """
        Gets all us city links from Craigslist and stores it in a list.
        """
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Retrieve first div that contains all US cities
        result = soup.find_all('div', class_='colmask')[0]

        # Get all US cities links
        self.cities = [city['href'] for city in result.find_all('a')]

    def select_rand_cities(self, num_cities):
        """
        Selects random city links to scrape
        :param num_cities: int
            Number of cities to scrape
        """
        random.shuffle(self.cities)
        self.cities = self.cities[:num_cities]

    def scrape_gigs(self):
        """
        Scrapes gigs for visited gig pages
        """
        for link in self.cities:
            # View gigs
            gig_page = requests.get(f'{link}search/ggg?')
            gig_soup = BeautifulSoup(gig_page.content, 'html.parser')

            # Gets all gigs on page
            gig_posts = gig_soup.find_all('p', class_='result-info')

            for post in gig_posts:
                date_str = post.find('time').attrs['datetime']
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M').date()

                # Filters out gigs that have been posted 4+ days ago
                if (self.today - date).days < 4:
                    gig = post.find(class_='result-title')
                    gig_link = gig.attrs['href']

                    # Stores scraped data in a list
                    self.gigs.append({'link': gig_link, 'title': gig.text})
                else:
                    break

    def output_to_excel(self):
        """
        Outputs scraped data to a csv file
        """
        with open('craigslist_gigs.csv', mode='w', encoding='utf-8', newline='') as csv_file:
            fieldnames = ['link', 'title']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.gigs)

    def scrape_jobs(self):
        pass


def send_email(recipients, subject, content):
    """
    Sends email to recipients
    :param recipients: list
        People that will receive email to be sent
    :param subject: str
        Subject of the email
    :param content: list
        Message body and any attachments
    """
    with yagmail.SMTP(GMAIL_USER, GMAIL_PASS) as yag:
        yag.send(recipients, subject, content)


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


GMAIL_USER = os.getenv('GMAIL_USER', None)
GMAIL_PASS = os.getenv('GMAIL_PASS', None)

if not GMAIL_USER or not GMAIL_PASS:
    raise ValueError("'GMAIL_USER'/'GMAIL_PASS' environment variable not set")

schedule.every().day.at("11:30").do(job)
while True:
    schedule.run_pending()
    time.sleep(1)
