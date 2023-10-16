from genrss import GenRSS, Enclosure
import xmltodict, os
from scrapping import scrapEntry, getEntries
from datetime import datetime, timezone


SITE_URL = 'https://99rabbits.com'
FEED_URL = 'https://tejonaco.github.io/feed.xml'
IMAGE_URL = 'https://99rabbits.com/wp-content/uploads/2023/07/cropped-rabbit-labs-logo.png'


### READ CURRENT LOCAL FEED ###
if isUpudate := os.path.isfile('feed.xml'):
    with open('feed.xml', 'rb') as f:
        rssDict = xmltodict.parse(f.read())

    buildDate = datetime.strptime(rssDict['rss']['channel']['lastBuildDate'],
                    '%a, %d %b %Y %H:%M:%S %Z')

    oldEntries = rssDict['rss']['channel']['item']

### GENERATE FEED ###

feed = GenRSS(title='99 Rabbits',
              site_url=SITE_URL,
              feed_url=FEED_URL,
              image_url=IMAGE_URL,
              )

for entry in getEntries():
    if isUpudate and buildDate.timestamp() > entry['lastmod'].timestamp(): # if that entry already was here on last build
        for oldEntry in oldEntries:
            if entry['link'] == oldEntry['link']:
                entry['title'], entry['pubDate'], entry['categories'] = oldEntry['title'], oldEntry['pubDate'], oldEntry['categories']
                entry['image'] = oldEntry.get('enclosure', {}).get('@url')
                break

    else: # a new entry
        print(entry['link'])
        entry['title'], entry['pubDate'], entry['categories'] = scrapEntry(entry['link']) #scrap entry only if it's new


    # cover image
    if entry['image']:
        extension = entry['image'].split('.')[-1]
        entry['enclosure'] = Enclosure(
            url = entry['image'],
            type = 'image/' + extension
        )
    else:
        entry['enclosure'] = None


    feed.item(
            title=entry['title'],
            url=entry['link'],
            pub_date=entry['pubDate'],
            enclosure=entry['enclosure'],
            categories=entry['categories'],
            )


xml = feed.xml(pretty=True)
with open('feed.xml', 'w') as f:
    f.write(xml)