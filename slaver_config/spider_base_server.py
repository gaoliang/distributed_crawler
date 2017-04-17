# coding=utf-8
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request
import os
import zipfile

app = Flask(__name__)
# file_dir = '/Users/gaoliang/Desktop'
file_dir = "/app/spider_cli/spiders"  # 实际部署时使用的文件夹
app.config['UPLOAD_FOLDER'] = file_dir
ALLOWED_EXTENSIONS = {'zip'}

config_dir = '/etc/supervisor/conf.d/'

scrapy_conf_templates = """[program:{0}]
directory=/app/spider_cli/spiders/{0}
command=scrapy crawl {0}
stdout_logfile=/var/log/supervisor/{0}_stdout.log
redirect_stderr=true
autostart=false
"""
portia_conf_tempaltes = """
[program:{0}]
directory=/app/spider_cli/spiders
command=portiacrawl {0} {0}
stdout_logfile=/var/log/supervisor/{0}_stdout.log
redirect_stderr=true
autostart=false
"""

init_py_template = """

import ConfigParser

import settings

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp(open('custom_settings.conf'))

# settings for anti_ban
settings.COOKIES_ENABLED = config.getboolean("spider_custom_settings", "enable_cookies")
settings.DOWNLOAD_DELAY = config.getfloat("spider_custom_settings", "download_delay")

# setting dbs
settings.REDIS_HOST = config.get("redis_setting", "redis_host")
settings.REDIS_PORT = config.get("redis_setting", "redis_port")
settings.ROBOTSTXT_OBEY = False
settings.SCHEDULER = "scrapy_redis.scheduler.Scheduler"
settings.DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
settings.SCHEDULER_PERSIST = True
settings.ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 300
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
    package = "%s"
    settings.DOWNLOADER_MIDDLEWARES[package + ".middlewares.downloadmiddlewares.MySplashMetaMiddlewares"] = 500
    settings.DOWNLOADER_MIDDLEWARES[
        package + '.middlewares.downloadmiddlewares.MyProcessResponseDownloadMiddleware'] = 900
    settings.DOWNLOADER_MIDDLEWARES[
        package + '.middlewares.downloadmiddlewares.MyProcessExceptionDownloadMiddleware'] = 920
"""

middleware_template = """
# -*-coding:utf-8-*-
import random
import urlparse
import scrapy_splash
from scrapy import Request
from scrapy.exceptions import IgnoreRequest
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError


class MySplashMetaMiddlewares(object):
    # 使用这个下载中间件，设置request.meta['splash']这个字典
    def __init__(self, splash_url):
        self.splash_url = splash_url

    @classmethod
    def from_crawler(cls, crawler):
        instance = cls(crawler.settings.get('SPLASH_URL'))
        return instance

    def process_request(self, request, spider):
        request.meta['splash'] = {
            'args': {
                #     # set rendering arguments here
                'html': 1,
                # 0表示不下载图片
                'png': 0,
                'wait': 0.5,
                #     # 'resource_timeout ': 0,
                'url': request.url,
                'http_method': request.method,
            },
            # # optional parameters
            'endpoint': 'render.html',
            # # 'splash_url': <>,      # optional; overrides SPLASH_URL
            # 'slot_policy': scrapy_splash.SlotPolicy.PER_DOMAIN,
            # 'splash_headers': {},  # optional; a dict with headers sent to Splash
            'dont_process_response': True,  # optional, default is False
            'dont_send_headers': True,  # optional, default is False
            'magic_response': False,  # optional, default is True
        }


class MyCustomHeadersDownLoadMiddleware(object):
    def __init__(self, user_agent_list):
        self.user_agent = user_agent_list

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        middleware = cls(crawler.settings.get('MY_USER_AGENT'))
        return middleware

    def process_request(self, request, spider):
        # 随机选择一个user-agent
        # 添加host头部
        custom_headers = {'user-agent': random.choice(self.user_agent),
                          'host': urlparse.urlparse(request.url).netloc}
        request.headers.update(custom_headers)

        # 禁止重试与重定向，设置超时
        custom_config = {'dont_redirect': True,
                         'dont_retry': True,
                         'download_timeout': 2.0,
                         'handle_httpstatus_all': True}
        request.meta.update(custom_config)


class MyProcessResponseDownloadMiddleware(object):

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def process_response(self, request, response, spider):
        # 处理下载完成的response
        http_code = response.status
        if http_code // 100 == 2:
            return response

        # 排除状态码不是304的所有以3为开头的响应
        if http_code // 100 == 3 and http_code != 304:
            self.stats.inc_value('response/%d' % http_code, spider=spider)
            # 获取重定向的url
            url = response.headers['location']
            domain = urlparse.urlparse(url).netloc
            # 判断重定向的url的domain是否在allowed_domains中
            if domain in spider.allowed_domains:
                return Request(url=url, meta=request.meta)
            else:
                raise IgnoreRequest(u'not allowed to crawl')

        if http_code // 100 == 4 and http_code != 403:
            self.stats.inc_value('response/%d' % http_code, spider=spider)
            # 需要注意403不是响应错误，是无权访问
            raise IgnoreRequest(u'404')

        if http_code // 100 == 5:
            self.stats.inc_value('response/%d' % http_code, spider=spider)
            return request


class MyProcessExceptionDownloadMiddleware(object):

    def process_exception(self, request, exception, spider):
        # 这个方法可以处理的异常来自于下载器下载request时引发的异常
        # 或者是其他下载中间件引发的异常

        # 如果在下载器下载的时候引发了下列的异常，就重新返回这个请求，后面继续下载
        if isinstance(exception, (DNSLookupError, TimeoutError, TCPTimedOutError)):
            return request

"""


def create_conf(spider_name, spider_type):
    file_path = os.path.join(config_dir, spider_name + ".conf")
    with open(file_path, "w") as f:
        if spider_type == "scrapy":
            f.write(scrapy_conf_templates.format(spider_name))
        elif spider_type == "portia":
            f.write(portia_conf_tempaltes.format(spider_name))


def un_zip(file_name):
    """unzip zip file"""
    zip_file = zipfile.ZipFile(file_name)
    if os.path.isdir(file_name.split(".")[0]):
        pass
    else:
        os.mkdir(file_name.split(".")[0])
    for names in zip_file.namelist():
        zip_file.extract(names, file_name.split(".")[0])
    zip_file.close()


# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 用于测试上传
@app.route('/test/upload')
def upload_test():
    return render_template('upload.html')


# 上传文件
@app.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['file']  # 从表单的file字段获取文件，myfile为该表单的name值
    spider_type = request.form['type']
    custom_settings = request.form['custom_settings']
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        filename = secure_filename(f.filename)
        create_conf(filename.split('.')[0], spider_type)
        f.save(os.path.join(file_dir, filename))  # 保存文件到upload目录
        un_zip(os.path.join(file_dir, filename))
        os.system("supervisorctl update")
        with open(os.path.join(file_dir, filename.split('.')[0] + "/custom_settings.conf"), "w+") as f:
            f.write(custom_settings)
        with open(os.path.join(file_dir, filename.split('.')[0] + "/" + filename.split('.')[0] + "/__init__.py"),
                  "w+") as f:
            f.write(init_py_template % filename.split('.')[0])

        if not os.path.exists(
                os.path.join(file_dir, filename.split('.')[0] + "/" + filename.split('.')[0] + '/middlewares')):
            os.makedirs(os.path.join(file_dir, filename.split('.')[0] + "/" + filename.split('.')[0] + '/middlewares'))
        with open(os.path.join(file_dir, filename.split('.')[0] + "/" + filename.split('.')[
            0] + "/middlewares/downloadmiddlewares.py"), "w+") as f:
            f.write(middleware_template)

        with open(os.path.join(file_dir,
                               filename.split('.')[0] + "/" + filename.split('.')[0] + "/middlewares/__init__.py"),
                  "w+") as f:
            pass
        with open(os.path.join(file_dir, filename.split('.')[0] + "/" + filename.split('.')[0] + "/__init__.py"),
                  "w+") as f:
            f.write(init_py_template % filename.split('.')[0])

        return jsonify({"success": True, "errmsg": ""})
    else:
        return jsonify({"success": False, "errmsg": "上传失败"})


# 上传文件
@app.route('/api/delete', methods=['POST'], strict_slashes=False)
def delete():
    name = request.form['name']
    try:
        os.remove(os.path.join(config_dir, name + '.conf'))
        os.system("supervisorctl update")
        return jsonify({"success": True})
    except:
        return jsonify({'success': False})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
