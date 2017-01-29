from flask_pymongo import PyMongo
from flask import Flask
from datetime import datetime
app = Flask(__name__)
mongo = PyMongo(app)


class Database(object):
    @staticmethod
    def insert_new_user(account_id):
        return mongo.db.users.insert({"account_id": account_id})

    @staticmethod
    def retreive_account():
        pass

    @staticmethod
    def mean(numbers):
        return float(sum(numbers)) / max(len(numbers), 1)


    @staticmethod
    def process_raw_temp_data(data_dump):
        """
        count number of negativity and how negative, percentage of negative / positive / neutral
        average rating for negative and for positive
        """
        if data_dump is None:
            return
        # mongo = PyMongo(app)
        list_data = data_dump["list"]
        result = {}
        pos = []
        neg = []
        neu = []
        
        for d in list_data:
            if d>0.3:
                pos.append(d)
            elif d< -0.3:
                neg.append(d)
            else:
                neu.append(d)
        result["posLen"] = len(pos)
        result["negLen"] = len(neg)
        result["neuLen"] = len(neu)
        result["totalDataLen"] = len(list_data)
        result["pos"] = Database.mean(pos)
        result["neg"] = Database.mean(neg)
        result["neu"] = Database.mean(neu)
        result["total"] = Database.mean(list_data)
        return result


    @staticmethod
    def update_temp_list(number, account_id):
        """
        update the array that stores the temp list (< 6 hours)
        """
        # mongo = PyMongo(app)
        account_id = int(account_id)
        temp_data = mongo.db.users.find_one({"account_id": account_id})

        if "temp" in temp_data.keys():
            past = datetime.strptime(temp_data["temp"]["time"], "%Y-%m-%d %H:%M:%S.%f")
            now = datetime.now()

            #if it's 1 hour since the temp data dump started, then compress it and start new temp data dump
            if (now-past).total_seconds() > 60:
                #start new temp fuck me and compress data duck me
                data_dump = Database.process_raw_temp_data(temp_data["temp"])
                if data_dump is not None:
                    data_dump["time"] = temp_data["temp"]["time"]
                    if "compressed_data" not in temp_data.keys():
                        temp_data["compressed_data"] = []
                    temp_data["compressed_data"].append(data_dump)
                    #mongo.db.users.update({"account_id": account_id}, {"$push": {"compressed_data": data_dump}})
                
                dp = {}
                dp["time"] = str(datetime.now())
                dp["list"] = []
                dp["list"].append(number)
                print(temp_data)
                temp_data["temp"] = dp
                print(temp_data)


                mongo.db.users.update({"account_id": 123}, {"$set": temp_data})
            


            else:
                mongo.db.users.update({"account_id": account_id}, {"$push":{"temp.list": number}})
            return temp_data["temp"]
        
        else:
            data = {}
            data["time"] = str(datetime.now())
            data["list"] = []
            data["list"].append(number)


            mongo.db.users.update({"account_id": account_id}, {"$set": {"temp": data}})

            return "updated"


        return temp_data
    
    @staticmethod
    def am_i_depressed(account_id):
        mongo.db.users.find_one({"account_id": account_id}, {"_id":0, "compressed_data": 1, "temp_data": 1})





