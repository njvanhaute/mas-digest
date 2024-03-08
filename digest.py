import itertools
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from cafeAd import CafeAd

ADS_URL = 'https://www.mandolincafe.com/ads/Mandolins'

CONFIG_FILE = 'config.mas'


def main():

    ads_html = requests.get(ADS_URL).text
    soup = BeautifulSoup(ads_html, 'html.parser')

    divs = soup.find_all('div', id=lambda x: x is not None and x.isnumeric())

    ad_list = []

    for div in divs:
        _, div_classtitle, _, _, div_replyarea = itertools.islice(div.next_siblings, 5)
        ad_name = div_classtitle.string
        date_str = (''.join(list(itertools.dropwhile(lambda x: x != 'P', div_replyarea.p.text))))[8:]
        ad_date = datetime.strptime(date_str, '%b %d, %Y %I:%M %p %Z')
        ad_link = 'https://www.mandolincafe.com' + div_replyarea.findAll('a')[2].attrs['href']
        ad = CafeAd(ad_name, ad_date, ad_link)
        ad_list.append(ad)

    ad_list.sort(key=lambda a: a.date_posted, reverse=True)

    print(ad_list)
    try:
        f = open(CONFIG_FILE)

    except FileNotFoundError:
        print('error')
    
    else:
        with f:
            print(f.readlines())

if __name__ == '__main__':
    main()