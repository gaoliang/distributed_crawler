# -*- coding: utf-8 -*-


from mongokit import Connection

# from datetime import datetime
import ConfigParser

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp(open('custom_settings.conf'))

connection = Connection(host=config.get("mongo_settings", "mongo_host"),
                        port=config.getint("mongo_settings", "mongo_port"))

DATABASE_NAME = "spiders"
