
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import logging
from settings import *

class DBConnection:
    def __init__(self):
        # self.client = MongoClient()
        # self.db = self.client['pachinko_data2']
        self.client = MongoClient(MONGOHQ_URI)
        self.db = self.client.pachinko_systems
        self.machine_details = self.db.machine_details

    def getHallCode(self,column):
        collection = self.db['data']
        return collection.distinct(column)

    def getData(self,startDate, endDate, hallcode,machinetype,machinenumber, limit=0):
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
            if limit == 0:
                return collection.find(query).sort([('date', 1),('time_of_win',1)])
            else:
                return collection.find(query).limit(limit).sort([('date', 1),('time_of_win',1)])
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

    def get_collection(self, db_name, collection_name):
        """
        this will return an collection of the db_name:
        """

        return self.client[db_name][collection_name]

    def get_hallcodes(self, ignore=False, start_date="", end_date=""):
        """
        Return all hallcodes in the collection
        if Ingore = true, check if any data within the time period
        """
        if ignore:
            hallcodes = self.db['data'].find({'date':{'$gte':start_date, '$lte':end_date}}).distinct('hallcode')
            return sorted(hallcodes)
        else:
            hallcodes = self.machine_details.find({'ancestors':[]})
            return [hallcode['hallcode'] for hallcode in hallcodes]

    def get_machine_types(self, hallcode, ignore=False, start_date="", end_date=""):
        """
        Return all machine types under the hall code.
        if Ingore = true, check if any data within the time period
        """
        
        if ignore:
            machine_types = self.db['data'].find({'date':{'$gte':start_date, '$lte':end_date}, 
                'hallcode':hallcode}).distinct('machine_type')
            return sorted(machine_types)
        else:
            machine_types = self.machine_details.find({'ancestors':[hallcode]})
            return [mt['machine_type'] for mt in machine_types]

    def get_machines(self, hallcode, machine_type, ignore=False, start_date="", end_date=""):
        """
        Return all machine types under the hall code.
        if Ingore = true, check if any data within the time period
        """
        
        if ignore:
            machines = self.db['data'].find({'hallcode':hallcode, 
                'date':{'$gte':start_date, '$lte':end_date}, 'machine_type': machine_type,}).distinct('machine')
            return sorted(machines)
        else:
            machines = self.machine_details.find({'ancestors':[machine_type, hallcode]})
            return [machine['machine'] for machine in machines]

    def insert_hallcode(self, hallcode):
        """
        Insert hallcode to machine details. return true if success.
        """

        try:
            self.machine_details.insert({"hallcode":hallcode, "ancestors":[]})
        except Exception, err:
            logging.error(err)
            return False
        return True

    def insert_machine_type(self, hallcode, machine_type):
        """
        Insert hallcode to machine details. return true if success.
        """

        try:
            self.machine_details.insert({"machine_type":machine_type, "ancestors":[hallcode]})
        except Exception, err:
            logging.error(err)
            return False
        return True

    def insert_machine(self, hallcode, machine_type, machine):
        """
        Insert hallcode to machine details. return true if success.
        """

        try:
            self.machine_details.insert({"machine":machine, "ancestors":[machine_type, hallcode]})
        except Exception, err:
            logging.error(err)
            return False
        return True