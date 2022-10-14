import random
from datetime import datetime
from pymongo import MongoClient

client = MongoClient()
db = client.database.spectators

class Mongo():
	@staticmethod
	def countInRoom(navId):
		return db.count_documents({'location': navId})

	@staticmethod
	def appendClue(chatId, clue):
		user = Mongo.getOrCreateUser(chatId)
		if not 'clues' in user:
			user['clues'] = []
		user['clues'].append({
			'time': datetime.now(),
			'clue': clue
			})
		Mongo.updateData(chatId, 'clues', user['clues'])

	@staticmethod
	def updateNavigation(chatId, navId):
		user = Mongo.getOrCreateUser(chatId)
		if not 'navigation' in user:
			user['navigation'] = []
		user['navigation'].append({
			'time': datetime.now(),
			'location': navId
			})
		query = {'_id': chatId}
		newValue = { '$set': {'location': navId, 'navigation': user['navigation']}}
		db.update_one(query, newValue)

	@staticmethod
	def appendTrack(chatId, track):
		user = Mongo.getOrCreateUser(chatId)
		if not 'tracks' in user:
			user['tracks'] = []
		user['tracks'].append(track)
		Mongo.updateData(chatId, 'tracks', user['tracks'])

	@staticmethod
	def appendQuestion(chatId, text):
		user = Mongo.getOrCreateUser(chatId)
		if not 'questions' in user:
			user['questions'] = []
		user['questions'].append(text)
		Mongo.updateData(chatId, 'questions', user['questions'])

	@staticmethod
	def readData(chatId):
		data = db.find_one({'_id': chatId})
		return '\n'.join(data['messages'])

	@staticmethod
	def updateData(chatId, key, data):
		query = {'_id': chatId}
		newValue = { '$set': {key: data}}
		db.update_one(query, newValue)

	@staticmethod
	def getOrCreateUser(chatId):
		user = db.find_one({'_id': chatId})
		if user is None:
			user = {"_id": chatId, "location": "main_menu"}
			db.insert_one(user)
			print("user {0} was created".format(chatId))
		return user

	@staticmethod
	def askQuestion(chatId, message):
		Mongo.appendQuestion(chatId, message)
		allIds = db.find({}, {"_id": 1})
		idSet = []
		for x in allIds:
			id = x["_id"]
			if id != chatId:
				idSet.append(id)
		if len(idSet) == 0:
			return None
		randomId = random.choice(idSet)
		print("selected id is {0}".format(randomId))
		return randomId

	@staticmethod
	def getRandomTrack(chatId):
		allTracks = db.find({}, {"_id": 1, "tracks": 1})
		tracks = []
		for x in allTracks:
			id = x["_id"]
			# !!! временно закомментировано для тестов
			if id != chatId and 'tracks' in x:
				for t in x["tracks"]:
					tracks.append(t)
		if len(tracks) == 0:
			return None
		randomTrack = random.choice(tracks)
		print("selected track is {0}".format(randomTrack))
		return randomTrack