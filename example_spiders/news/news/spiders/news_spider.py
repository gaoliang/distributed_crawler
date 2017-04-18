# coding:utf-8
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from ..items import NewsItem
from .extractor import Extractor


class TechSpider(CrawlSpider):
    name = "news"
    allowed_domains = ["tech.163.com"]
    start_urls = ["http://tech.163.com/"]
    rules = [Rule(LinkExtractor(allow=("/17/\d+/\d+/*")), 'parse_item')]

    def parse_item(self, response):
        item = NewsItem()
        item['url'] = response.url
        ext = Extractor(rawPage=response.text, blockSize=5, image=False)
        print ext.getContext()
        item['content'] = ext.getContext()
        yield item
