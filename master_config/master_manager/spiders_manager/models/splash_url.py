# -*- coding: utf-8 -*-

from mongokit import Document
from . import connection, DATABASE_NAME


@connection.register
class SplashUrlDoc(Document):
    __database__ = DATABASE_NAME
    __collection__ = 'splash_urls'
    structure = {
        'url': basestring
    }
    required_fields = ['url']
    default_values = {
    }

splash_urls_collection = connection[DATABASE_NAME]['splash_urls']
