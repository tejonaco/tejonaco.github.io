import requests
from bs4 import BeautifulSoup
from datetime import datetime
from unidecode import unidecode


SITEMAP_URL = 'https://99rabbits.com/post-sitemap.xml'
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

    category = html.find(rel='category tag').text

    return title, pubDate, category


def getEntries(maxEntries=None):
    r = requests.get(SITEMAP_URL)
    xml = BeautifulSoup(r.text, 'xml')
    
    for i, e in enumerate(xml.findAll('url')[1:]):
        if i == maxEntries:
            return
        link = e.find('loc').text
        lastmod = e.find('lastmod').text # 2023-07-11T16:52:58+00:00
        lastmod = datetime.strptime(lastmod,
                  '%Y-%m-%dT%H:%M:%S%z')
        
        if imageLoc := e.find('image:loc'):
            image = imageLoc.text

        yield {'link': link, 'lastmod': lastmod, 'image': image}
