# -*- coding: utf-8 -*-

from datetime import datetime
from mongokit import Document
from . import connection, DATABASE_NAME


@connection.register
class MachineDoc(Document):
    __database__ = DATABASE_NAME
    __collection__ = 'machines'
    structure = {
        'name': basestring,
        'ip': basestring,
        'status': basestring,
    }
    required_fields = ['ip']


machine_collection = connection[DATABASE_NAME]['machines']
