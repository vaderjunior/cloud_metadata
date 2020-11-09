from flask_pymongo import PyMongo
import server as s

s.app.config['MONGO_DBNAME'] = 'mydb'
s.app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydb'
mongo = PyMongo(s.app)
