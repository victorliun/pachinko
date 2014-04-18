
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

class DBConnection:
        def __init__(self):
		self.client = MongoClient('localhost', 27017)
		self.db = self.client['pachinko_data2']

	def getHallCode(self,column):
		collection = self.db['data']
		return collection.distinct(column)

	def getData(self,startDate, endDate, hallcode,machinetype,machinenumber):
		try:
			collection = self.db['data']
			if self.checkEmptyValue(hallcode):
				query = {"date":{"$gte": startDate, "$lte": endDate}}
			else:
				if self.checkEmptyValue(machinetype):
					query = {"$and": [{"date":{"$gte": startDate, "$lte": endDate}},{"hallcode": hallcode}]}
				else:
					if self.checkEmptyValue(machinenumber):
						query = {"$and": [{"date":{"$gte": startDate, "$lte": endDate}},{"hallcode": hallcode},{"machine_type":machinetype}]}
					else:
						query = {"$and": [{"date":{"$gte": startDate, "$lte": endDate}},{"hallcode": hallcode},{"machine_type": machinetype},{"machine": machinenumber}]}
			return collection.find(query).sort([('date', 1),('time_of_win',1)])
		except Exception as e:
			print e;
			pass


	def getMachineDetails(self,column,value,column2,value2,distinctcol):
		try:
			if self.checkEmptyValue(column2) or self.checkEmptyValue(value2): 
				query = {column: value}
			else:
				query = {"$and": [{column: value},{column2: value2}]}
			collection = self.db['data']
			print json.dumps(query)
			return collection.find(query).distinct(distinctcol);
		except Exception as e:
                        print e;
                        pass

	def checkEmptyValue(self,column):
		if column == "blank" or  column == " " or column == "":
			return True
		else:
			return False


	def get_collections(self, startDate='', endDate='', hallcode='',machinetype='',machinenumber=''):
		"""
		Query collections from 'data' table.
		if all empty return the whole package.
		"""

		collection = self.db['data']
		query = {}
		if not self.checkEmptyValue(startDate) and not self.checkEmptyValue(endDate):
			query['date'] = {"$gte": startDate, "$lte": endDate}
		if not self.checkEmptyValue(hallcode):
			query['hallcode'] = hallcode
		if not self.checkEmptyValue(machinetype):
			query['machine_type'] = machinetype
		if not self.checkEmptyValue(machinenumber):
			query['machine'] = machinenumber
		#print query

		return list(collection.find(query))
