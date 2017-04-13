import scrapy
from scrapy_splash import SplashRequest


class JdSpider(scrapy.Spider):
    name = "jd"
    start_urls = [
        'https://item.jd.com/3133829.html'
    ]

    def start_requests(self):

        for url in self.start_urls:
            yield SplashRequest(url=url, callback=self.parse,
                                args={
                                    'wait': 0.5,
                                })
        pass

    def parse(self, response):

        fo = open("jd2.html", "wb")
        fo.write(response.body)
        fo.close()
