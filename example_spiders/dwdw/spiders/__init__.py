import ConfigParser

import settings

package = "jingdong"

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp(open('custom_settings.conf'))

# settings for anti_ban
settings.COOKIES_ENABLED = config.getboolean("spider_custom_settings", "enable_cookies")
settings.DOWNLOAD_DELAY = config.getfloat("spider_custom_settings", "download_delay")

# setting dbs
settings.REDIS_HOST = config.get("redis_setting","redis_host")
settings.REDIS_PORT = config.get("redis_setting","redis_port")
settings.MONGO_HOST = config.get("mongo_settings","mongo_host")
settings.MONGO_PORT = config.get("mongo_settings","mongo_port")
settings.ROBOTSTXT_OBEY = False
settings.SCHEDULER = "scrapy_redis.scheduler.Scheduler"
settings.DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
settings.SCHEDULER_PERSIST = True
settings.ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 300,
    package + ".mongopipline.MongoPipeline": 400
}


# settings splash
SPLASH_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}
if config.getboolean("splash_setting", "enable_splash"):
    settings.SPLASH_URL = "http://splash:8050"
    if hasattr(settings, "DOWNLOADER_MIDDLEWARES"):
        settings.DOWNLOADER_MIDDLEWARES = dict(settings.DOWNLOADER_MIDDLEWARES.items() + SPLASH_MIDDLEWARES.items())
    else:
        settings.DOWNLOADER_MIDDLEWARES = SPLASH_MIDDLEWARES
    settings.DOWNLOADER_MIDDLEWARES[package + ".middlewares.downloadmiddlewares.MySplashMetaMiddlewares"] = 500
    settings.DOWNLOADER_MIDDLEWARES[
        package + '.middlewares.downloadmiddlewares.MyProcessResponseDownloadMiddleware'] = 900
    settings.DOWNLOADER_MIDDLEWARES[
        package + '.middlewares.downloadmiddlewares.MyProcessExceptionDownloadMiddleware'] = 920