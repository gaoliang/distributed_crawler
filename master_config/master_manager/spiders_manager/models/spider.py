# -*- coding: utf-8 -*-

from datetime import datetime

import bson
from mongokit import Document
from . import connection, DATABASE_NAME


@connection.register
class SpiderDoc(Document):
  __database__ = DATABASE_NAME
  __collection__ = 'spider'
  structure = {
    'name': basestring,
    'status': basestring,
    'created_at': datetime,
    'file': bson.binary.Binary,
    'machines':list
  }
  required_fields = ['name', 'file']


spider_collection = connection[DATABASE_NAME]['spiders']
