
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import time
from settings import *

class DBCrawlerConnection:
    def __init__(self):
        # self.client = MongoClient()
        # self.db = self.client['pachinko_data2']
        self.client = MongoClient(MONGOHQ_URI)
        self.db = self.client['pachinko_systems']

    def setCrawlerData(self,username,password,targetHallocde,targetmachinetype,startFirstCrawlTime,startLastCrawlTime,startingDate,finishingDate):
        collection = self.db['crawler_settings']
        return collection.insert({"username": username, "password": password, "targetHallocde": targetHallocde, "targetmachinetype": targetmachinetype, "startFirstCrawlTime": startFirstCrawlTime, "startLastCrawlTime": startLastCrawlTime, "startLastCrawlTime": startLastCrawlTime, "startingDate": startingDate, "finishingDate": finishingDate, "time": long(time.time()*1000)})

    def getLatestCrawlerDetails(self):
        collection = self.db['crawler_settings']
        #return collection.findOne().sort([('time', -1)])
        return collection.find().sort('time', -1).limit(1)    

    def getPreviousData(self):   
        collection = self.db['crawler_settings']
        #return collection.findOne().sort([('time', -1)])
        return collection.find().sort('time', -1).limit(2)


    def save_crawler_data(self, username, password, targetHallocde, targetmachinetype):
        """
        save crawler_settings to db.
        """
        collection = self.db['crawler_settings']
        return collection.insert({"username": username, 
            "password": password, 
            "targetHallocde": targetHallocde, 
            "targetmachinetype": targetmachinetype,
            "time": long(time.time()*1000)})

