#coding:utf-8
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider,Rule
from news.items import NewsItem
from .extractor import Extractor
class TechSpider(CrawlSpider):
   name = "tech"
   allowed_domains = ["tech.163.com"]
   start_urls = ["http://tech.163.com/"]
   rules = [Rule(LinkExtractor(allow=("/17/04\d+/\d+/*")),'parse_item')]

   def parse_item(self,response):
     #sites = response.xpath('//div[@class="end-text"]/p')
     items = []
     #content = []
     #for site in sites:
       #content.append(''.join(site.xpath('text()').extract()))
     item = NewsItem()
     item['url'] = response.url
     #item['desc'] = ''.join(content)
     ext = Extractor(response,blockSize=5, image=False)
     item['desc'] = ext.getContext()
     items.append(item)
     return items