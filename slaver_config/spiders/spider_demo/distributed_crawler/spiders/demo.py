# -*- coding: utf-8 -*-
import scrapy
import re

from scrapy import Request
from scrapy_splash import SplashRequest as Request


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["http://jd.com"]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, self.parse)

    def parse(self, response):
        print response.text