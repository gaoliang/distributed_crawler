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
    """
    预处理下载器成功下载的response
    """

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
    """
    处理下载器下载response时引发的异常
    """

    def process_exception(self, request, exception, spider):
        # 这个方法可以处理的异常来自于下载器下载request时引发的异常
        # 或者是其他下载中间件引发的异常

        # 如果在下载器下载的时候引发了下列的异常，就重新返回这个请求，后面继续下载
        if isinstance(exception, (DNSLookupError, TimeoutError, TCPTimedOutError)):
            return request
