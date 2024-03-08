import base64
import itertools
import requests
import os
import smtplib
import sys
from bs4 import BeautifulSoup
from cafeAd import CafeAd
from datetime import datetime
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List
from database import Database

ADS_URL = 'https://www.mandolincafe.com/ads/Mandolins'
APP_EMAIL = 'mandolindigest@gmail.com'
APP_PASS = os.environ.get('DIGEST_KEY', 'default')
SCOPES = [
    'https://https://www.googleapis.com/auth/gmail.send'
]


def get_link(ad_id: int):
    return 'https://www.mandolincafe.com/ads/' + str(ad_id) + '#' + str(ad_id)

def generate_email_content(ads: List[CafeAd], start_date: datetime) -> str:    
    content = f'New mandolins for sale as of {start_date.strftime("%H:%M")}:<br><br>'

    for ad in ads:
        content += (f'<a href="{get_link(ad.id)}">{ad.name}</a><br><br>')
    
    return content

def parse_html() -> List[CafeAd]:
    ad_list = []

    ads_html = requests.get(ADS_URL).text
    soup = BeautifulSoup(ads_html, 'html.parser')

    divs = soup.find_all('div', id=lambda x: x is not None and x.isnumeric())

    for div in divs:
        _, div_classtitle, _, _, div_replyarea = itertools.islice(div.next_siblings, 5)
        ad_id = int(div.attrs['id'])
        ad_name = div_classtitle.string
        date_str = (''.join(list(itertools.dropwhile(lambda x: x != 'P', div_replyarea.p.text))))[8:-4]
        ad_date = datetime.strptime(date_str, '%b %d, %Y %I:%M %p')
        ad = CafeAd(ad_id, ad_name, ad_date)
        ad_list.append(ad)

    ad_list.sort(key=lambda a: a.date_posted, reverse=True)
    return ad_list

def main():
    db = Database()

    ads = parse_html()

    if db.is_empty():
        db.add_ads(ads)
        sys.exit(0)
    
    start_date = db.most_recent_date_posted()
    recent_ads = list(filter(lambda a: a.date_posted > start_date, ads))

    if not recent_ads:
        sys.exit(0)
        
    email_content = generate_email_content(recent_ads, start_date)
    
    html_message = MIMEText(email_content, 'html')
    html_message['Subject'] = f'{datetime.now().strftime("%H:%M")} Digest'

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(APP_EMAIL, APP_PASS)
        for sub_email in db.get_sub_emails():
            server.sendmail(APP_EMAIL, sub_email, html_message.as_string())

    db.add_ads(recent_ads)

if __name__ == '__main__':
    main()