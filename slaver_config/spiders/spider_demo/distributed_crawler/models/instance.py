# -*- coding: utf-8 -*-

from datetime import datetime
from mongokit import Document
from . import connection, DATABASE_NAME


@connection.register
class InstanceDoc(Document):
    __database__ = DATABASE_NAME
    __collection__ = 'instances'
    structure = {
        'name': basestring,
        'machine': basestring,
        'status': basestring,
        'created_at': datetime,
        'closed_at': datetime,
    }
    required_fields = ['name']


instances_collection = connection[DATABASE_NAME]['instances']
