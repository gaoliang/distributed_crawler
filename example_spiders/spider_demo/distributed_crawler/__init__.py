"""
this is the init file for automatically set spiders settings from a conf file
"""

import ConfigParser

import settings

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp(open('custom_settings.conf'))

# settings for anti_ban
settings.COOKIES_ENABLED = config.getboolean("spider_custom_settings", "enable_cookies")
settings.DOWNLOAD_DELAY = config.getint("spider_custom_settings", "download_delay")

# setting dbs
settings.REDIS_HOST = config.get("redis_setting", "redis_host")
settings.REDIS_PORT = config.get("redis_setting", "redis_port")

# settings splash
SPLASH_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}
if config.get("splash_setting", "enable_splash"):
    SPLASH_URL = config.get("splash_setting", "splash_url")
    print SPLASH_URL
    settings.DOWNLOADER_MIDDLEWARES = dict(settings.DOWNLOADER_MIDDLEWARES.items() + SPLASH_MIDDLEWARES.items())


# for custom middlewares
package = settings.BOT_NAME
settings.DOWNLOADER_MIDDLEWARES[package + ".middlewares.downloadmiddlewares.MySplashMetaMiddlewares"] = 500
settings.DOWNLOADER_MIDDLEWARES[
    package + '.middlewares.downloadmiddlewares.MyProcessResponseDownloadMiddleware'] = 900
settings.DOWNLOADER_MIDDLEWARES[
    package + '.middlewares.downloadmiddlewares.MyProcessExceptionDownloadMiddleware'] = 920
