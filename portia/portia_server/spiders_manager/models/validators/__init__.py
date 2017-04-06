# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import urlparse

from mongokit import ValidationError
from apscheduler.triggers.cron import CronTrigger


class StringLengthRangeValidator(object):
    def __init__(self, min_length, max_length):
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value):
        l = len(value)
        if l >= self.min_length and l <= self.max_length:
            return True
        else:
            raise ValidationError("%s(值：" + unicode(value) + ") 的长度需要在 " + unicode(self.min_length) + " 和 " + unicode(self.max_length) + " 之间")


class NumeralValueRangeValidator(object):
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, value):
        if value >= self.min_value and value <= self.max_value:
            return True
        else:
            raise ValidationError("%s(值：" + unicode(value) + ") 的取值需要在 " + unicode(self.min_value) + " 和 " + unicode(self.max_value) + " 之间")


class UrlListValidator(object):
    def __call__(self, value):
        for i,v in enumerate(value):
            parsed = urlparse.urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError(unicode("%s 列表内第 " + unicode(i) + " 项: " + v + " 不是合法URL"))
        return True


class CronValidator(object):
    def __call__(self, value):
        if value == "":
            return True

        try:
            split_values = value.split()
            for i in range(0, 8):
                if (i == 0):
                    if (split_values[0] == '?'):
                        year = None
                    else:
                        year = split_values[0]
                if (i == 1):
                    if (split_values[1] == '?'):
                        month = None
                    else:
                        month = split_values[1]
                if (i == 2):
                    if (split_values[2] == '?'):
                        day = None
                    else:
                        day = split_values[2]
                if (i == 3):
                    if (split_values[3] == '?'):
                        week = None
                    else:
                        week = split_values[3]
                if (i == 4):
                    if (split_values[4] == '?'):
                        day_of_week = None
                    else:
                        day_of_week = split_values[4]
                if (i == 5):
                    if (split_values[5] == '?'):
                        hour = None
                    else:
                        hour = split_values[5]
                if (i == 6):
                    if (split_values[6] == '?'):
                        minute = None
                    else:
                        minute = split_values[6]
                if (i == 7):
                    if (split_values[7] == '?'):
                        second = None
                    else:
                        second = split_values[7]
            CronTrigger(year, month, day, week, day_of_week, hour, minute, second)
        except Exception, e:
            raise ValidationError("%s(值：" + value + ")格式不正确")

        return True


# vi: ft=python:tw=0:ts=4:sw=4
