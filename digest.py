import itertools
import requests
import sys
from bs4 import BeautifulSoup
from cafeAd import CafeAd
from datetime import datetime
from typing import List
from database import Database

ADS_URL = 'https://www.mandolincafe.com/ads/Mandolins'

CONFIG_FILE = 'config.mas'

def get_link(ad_id: int):
    return 'https://www.mandolincafe.com/' + str(ad_id) + '#' + str(ad_id)

def generate_email_content(ads: List[CafeAd], start_date: datetime) -> str:
    if not ads:
        return 'No new mandolins for sale since last email!'
    
    content = f'New mandolins for sale as of {start_date.strftime("%H:%M")}:<br><br>'

    for ad in ads:
        content.append(f'<a href="{get_link(ad.id)}">{ad.name}</a><br>')
    
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
        date_str = (''.join(list(itertools.dropwhile(lambda x: x != 'P', div_replyarea.p.text))))[8:]
        ad_date = datetime.strptime(date_str, '%b %d, %Y %I:%M %p %Z')
        ad = CafeAd(ad_id, ad_name, ad_date)
        ad_list.append(ad)

    ad_list.sort(key=lambda a: a.date_posted, reverse=True)
    return ad_list

def main():
    db = Database()

    ads = parse_html()

    if db.is_empty():
        for ad in ads:
            db.add_ad(ad)
        sys.exit(0)
    
    start_date = db.most_recent_date_posted()
    recent_ads = list(filter(lambda a: a.date_posted > start_date, ads))
    email_content = generate_email_content(ads, start_date)



if __name__ == '__main__':
    main()