from datetime import datetime
import scrapy
import re

# scrapy runspider --nolog fetch_changelog.py

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
    ]

    for ep in range(25, 26):
        start_urls.append('https://changelog.com/podcast/' + str(ep))

    def parse(self, response):
        data = {
            'keywords' : [],
            'guests'   : {},
            'hosts'    : {},
        }
        #print(response)
        data['permalink'] = response.url
        full_title = response.css('title::text').extract_first()
        print(full_title)   # The Changelog #23: The Ruby Racer with Charles Lowell | Changelog
        m = re.search(r'The Changelog #(\d+):\s+(.*?)\s+with\s+(.*?)\s+\| Changelog', full_title)
        if m:
            data['ep'] = m.group(1)
            data['title'] = m.group(2)
            guest_name = m.group(3)
            guest_code = re.sub(r'\s+', '-', guest_name.lower())
            data['guests'] = {
                guest_code : {}
            }

        published  = response.css('time::text').extract_first()
        print(published) # Apr 25 2012
        dt = datetime.strptime(published, '%b %d %Y')
        print(dt)
        data['date'] = dt.strftime('%Y-%m-%d')

        print(data)

# vim: expandtab
