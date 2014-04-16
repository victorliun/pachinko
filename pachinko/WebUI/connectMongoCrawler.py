
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import time

class DBCrawlerConnection:
        def __init__(self):
		self.client = MongoClient('localhost', 27017)
		self.db = self.client['pachinko_crawler']

	def setCrawlerData(self,username,password,targetHallocde,targetmachinetype,startFirstCrawlTime,startLastCrawlTime,startingDate,finishingDate):
		collection = self.db['data']
		return collection.insert({"username": username, "password": password, "targetHallocde": targetHallocde, "targetmachinetype": targetmachinetype, "startFirstCrawlTime": startFirstCrawlTime, "startLastCrawlTime": startLastCrawlTime, "startLastCrawlTime": startLastCrawlTime, "startingDate": startingDate, "finishingDate": finishingDate, "time": long(time.time()*1000)})

	def getLatestCrawlerDetails(self):
		collection = self.db['data']
		#return collection.findOne().sort([('time', -1)])
		return collection.find().sort('time', -1).limit(1)

	def getPreviousData(self):
                collection = self.db['data']
                #return collection.findOne().sort([('time', -1)])
                return collection.find().sort('time', -1).limit(2)
