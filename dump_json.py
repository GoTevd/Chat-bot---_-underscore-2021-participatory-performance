import json
from pymongo import MongoClient
from datetime import datetime


def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

client = MongoClient()
db = client.database.spectators
dataCursor = db.find()
data = []
for entry in dataCursor:
	data.append(entry)
file = open('dump.json', 'w')
json.dump(data, file, default=datetime_handler)