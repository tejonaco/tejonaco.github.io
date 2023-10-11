import requests
from bs4 import BeautifulSoup
from datetime import datetime
from unidecode import unidecode
from genrss import GenRSS, Enclosure
import time


SITEMAP_URL = 'https://99rabbits.com/post-sitemap.xml'
SITE_URL = 'https://99rabbits.com'
FEED_URL = 'https://tejonaco.github.io/feed.xml'
IMAGE_URL = 'https://99rabbits.com/wp-content/uploads/2023/07/cropped-rabbit-labs-logo.png'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0'
    }



def scrapEntry(url):
    r = requests.get(url, headers=HEADERS)
    html = BeautifulSoup(r.text, 'lxml')


    title = unidecode(html.h1.text)

    #pubDate
    pubDate_text = html.find(class_='post-date').find(class_='meta-text').text.strip()
    pubDate = datetime.strptime(pubDate_text, '%B %d, %Y')

    return title, pubDate


def getEntries(maxEntries=None):
    r = requests.get(SITEMAP_URL)
    xml = BeautifulSoup(r.text, 'xml')

    for i, e in enumerate(xml.findAll('url')[1:]):
        if i == maxEntries:
            return
        url = e.find('loc').text
        lastmod = e.find('lastmod').text
        
        if imageLoc := e.find('image:loc'):
            image = imageLoc.text

        yield {'url': url, 'lastmod': lastmod, 'image': image}


### GENERATE FEED ###

feed = GenRSS(title='99 Rabbits',
              site_url=SITE_URL,
              feed_url=FEED_URL,
              image_url=IMAGE_URL,
              )

for entry in getEntries():
    entry['title'], entry['pubdate'] = scrapEntry(entry['url'])

    # cover image
    if entry['image']:
        extension = entry['image'].split('.')[-1]
        enclosure = Enclosure(
            url = entry['image'],
            type = 'image/' + extension
        )
    else:
        enclosure = None

    feed.item(
            title=entry['title'],
            url=entry['url'],
            pub_date=entry['pubdate'],
            enclosure=enclosure
            )
    time.sleep(0.5)

xml = feed.xml(pretty=True)
with open('feed.xml', 'w') as f:
    f.write(xml)