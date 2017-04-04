# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# !/usr/bin/env python
# -*- coding: utf-8 -*-

import platform

from scrapy import signals
from datetime import datetime


from distributed_crawler.models.instance import instances_collection


class InstanceStatusMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        obj = cls()
        crawler.signals.connect(obj.spider_opened, signals.spider_opened)
        crawler.signals.connect(obj.spider_closed, signals.spider_closed)
        crawler.signals.connect(obj.spider_idle, signals.spider_idle)
        crawler.signals.connect(obj.request_scheduled, signals.request_scheduled)

        return obj

    def spider_opened(self, spider):
        self.instance_doc = instances_collection.InstanceDoc()
        self.instance_doc.update({
            'name': spider.name,
            'machine': ",".join(platform.uname()),
            'status': u"已启动",
            'created_at': datetime.now()
        })

    def spider_closed(self, spider):
        self.instance_doc.update({'status': u'已停止', 'closed_at': datetime.now()})
        self.instance_doc.save()

    def spider_idle(self, spider):
        self.instance_doc.update({'status': u'空闲'})
        self.instance_doc.save()

    def request_scheduled(self, spider):
        self.instance_doc.update({'status': u'正在运行'})
        self.instance_doc.save()

# vi: ft=python:tw=0:ts=4:sw=4
