# -*- coding: utf-8 -*-
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider,Rule
from news.items import NewsItem
from .extractor import Extractor

class NewsSpider(CrawlSpider):
   name = "newscrawl"
   #allowed_domains = ["tech.163.com"]
   #start_urls = ["http://tech.163.com/"]
   #rules = [Rule(LinkExtractor(allow=("/17/04\d+/\d+/*")),'parse_item')]
   allowed_domains = ["news.sohu.com"]
   start_urls = ["http://news.sohu.com/"]
   rules = [Rule(LinkExtractor(allow=("201704\d+/")),'parse_item')]

   def parse_item(self,response):
     items = []
     item = NewsItem()
     item['url'] = response.url
     ext = Extractor(response,blockSize=5, image=False)
     #ext = Extractor(response)
     item['desc'] = ext.getContext()
     #print(item['desc'])
     items.append(item)
     return items