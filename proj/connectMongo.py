
from pymongo import MongoClient
from bson.objectid import ObjectId

class DBConnection:
        def __init__(self):
		self.client = MongoClient('localhost', 27017)
		self.db = self.client['pachinko_data2']

	def getHallCode(self,column):
		collection = self.db['data']
		return collection.distinct(column)

	def getData(self,startDate, endDate):
		collection = self.db['data']
		return collection.find({"date":{"$gte": startDate, "$lte": endDate}}).sort([('date', 1)])

	def getMachineDetails(self,column,value,distinctcol):
		collection = self.db['data']
		return collection.find({column: value}).distinct(distinctcol);
