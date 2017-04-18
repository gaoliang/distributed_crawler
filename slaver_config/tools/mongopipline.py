import pymongo

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log

class MongoPipeline(object):
    '''
        Saves the scraped item to mongodb.
    '''
    def __init__(self, mongo_server, mongo_port, mongo_db, mongo_collection):
        self.mongo_server = mongo_server
        self.mongo_port = int(mongo_port)
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_server=crawler.settings.get('MONGO_HOST'),
            mongo_port=crawler.settings.get('MONGO_PORT'),
            mongo_db="items",
            mongo_collection=crawler.settings.get('PACKAGE'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_server, self.mongo_port)
        self.db = self.client[self.mongo_db]
        self.col = self.db[self.mongo_collection]
    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        print
        self.col.insert(dict(item))
        return item