# -*- coding: utf-8 -*-

# Scrapy settings for distributed_crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'distributed_crawler'

SPIDER_MODULES = ['distributed_crawler.spiders']
NEWSPIDER_MODULE = 'distributed_crawler.spiders'

MY_USER_AGENT = [
    "Mozilla/5.0+(Windows+NT+6.2;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/45.0.2454.101+Safari/537.36",
    "Mozilla/5.0+(Windows+NT+5.1)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/28.0.1500.95+Safari/537.36+SE+2.X+MetaSr+1.0",
    "Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/50.0.2657.3+Safari/537.36",
    "Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/51.0.2704.106+Safari/537.36",
    "Mozilla/5.0+(Windows+NT+6.1)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/47.0.2526.108+Safari/537.36+2345Explorer/7.1.0.12633",
    "Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_11_4)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/49.0.2623.110+Safari/537.36",
    "Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_9_5)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/42.0.2311.152+Safari/537.36",
    "Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/42.0.2311.152+Safari/537.36",
    "Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_10_2)+AppleWebKit/600.3.18+(KHTML,+like+Gecko)+Version/8.0.3+Safari/600.3.18",
    "Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/49.0.2623.22+Safari/537.36+SE+2.X+MetaSr+1.0",
    "Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_11_4)+AppleWebKit/601.5.17+(KHTML,+like+Gecko)+Version/9.1+Safari/601.5.17",
    "Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/48.0.2564.103+Safari/537.36",
    "Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/47.0.2526.80+Safari/537.36+Core/1.47.640.400+QQBrowser/9.4.8309.400",
    "Mozilla/5.0+(Macintosh;+Intel+Mac+OS+X+10_10_5)+AppleWebKit/600.8.9+(KHTML,+like+Gecko)+Version/8.0.8+Safari/600.8.9",
    "Mozilla/5.0+(Windows+NT+6.3;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/39.0.2171.99+Safari/537.36+2345Explorer/6.4.0.10356",
    "Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/45.0.2454.87+Safari/537.36+QQBrowser/9.2.5584.400",
    "Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/47.0.2526.111+Safari/537.36",
    "Mozilla/5.0+(Windows+NT+6.1;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/33.0.1750.146+BIDUBrowser/6.x+Safari/537.36",
    "Mozilla/5.0+(Windows+NT+6.1)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/39.0.2171.99+Safari/537.36+2345Explorer/6.5.0.11018",
    "Mozilla/5.0+(Windows+NT+6.2;+WOW64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/42.0.2311.154+Safari/537.36+LBBROWSER"
]

ROBOTSTXT_OBEY = False
# Enables scheduling storing requests queue in redis.
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# Ensure all spiders share same duplicates filter through redis.
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

SCHEDULER_PERSIST = True

ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 300
}

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
}

SPLASH_LOG_400 = True
SPLASH_URL = 'http://127.0.0.1:8050'