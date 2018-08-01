#from gevent import monkey
#monkey.patch_all()
from pymongo import MongoClient
from remotelogger.settings import STORAGE_URL



class Log(object):

    def __init__(self, exchange, queue, routing_key, logger):
        self._info          = {"exchange":exchange, "queue":queue, "routing_key": routing_key}
        self._client        = MongoClient(STORAGE_URL)
        self._collection    = self._client[exchange][routing_key]
        self.logger         = logger

    def create(self):
        log = self._collection.find_one(self._info)
        if log is None:
            self.logger.info('Create document %s', str(self._info))
            log = self._collection.insert_one(self._info)
            self._collection.update_one(self._info, {"$set": {"logs":[]} })
            
    def append(self, value):
        self.logger.debug('Storing {%s} to %s', value, str(self._info))
        self._collection.update_one(self._info, {"$push": {"logs":value} })

    def get(self):
        log = self._collection.find_one(self._info)
        return log

class StorageInfo(object):

    def __init__(self, logger):
        self._client = MongoClient(STORAGE_URL)
        self.logger  = logger

    def list_databases(self):
        self.logger.debug('List databases')
        return [db for db in self._client.database_names() if db not in  ['admin', 'config', 'local']]

    def list_collections(self, database):
        self.logger.debug('List collections in database: "%s"', database)
        db = self._client[database]
        return db.collection_names()

    def list_documents(self, database, collection):
        self.logger.debug('List documents in database: "%s", collection: "%s"', database, collection)
        db = self._client[database]
        collection = db[collection]
        return [doc['queue'] for doc in collection.find()]


