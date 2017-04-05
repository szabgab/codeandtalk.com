import scrapy

# scrapy runspider bin/fetch_dev.py

class FullStackRadioSpider(scrapy.Spider):
    name = "full-stack-radio"

    start_urls = ['http://www.fullstackradio.com/episodes']

    def parse(self, response):
        print("parse_main")
        #print(response.url)
        # links = response.xpath('//a[contains(@href, "podcast")]')
        # for a in links.extract():
        #     print(a)
        #rs = []
        for a in response.css('a::attr(href)').extract():
            print(a)
            #yield scrapy.Request(self.base_url + a, callback=self.parse_episode)

        #self.pages = response.css('a[href*=podcast]::attr(href)').extract()

    # def parse_episode(self, response):
    #     print("parse episode")
    #     print(response.url)

