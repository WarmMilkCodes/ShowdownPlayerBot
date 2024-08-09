import pymongo, certifi, config

MongoURL = config.MONGO_URL
ca = certifi.where()
cluster = pymongo.MongoClient(MongoURL, tlsCAFile=ca)

db = cluster[config.DATABASE]
player_collection = db[config.PLAYER_COLLECTION]
teams_collection = db[config.TEAM_COLLECTION]