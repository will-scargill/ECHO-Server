import configparser
import json

def GetSetting(setting, section):
	parser = configparser.ConfigParser()
	parser.read(r"configs/config.ini")
	try:
		data = json.loads(parser.get(section, setting))
		return data
	except:
		data = parser.get(section, setting)
		if data == '""':
			return ""
		else:
			return data

def GetBlacklist():
	wordBlacklist = []

	with open(r'configs/wordblacklist.json', 'r') as f:
		blacklistData = json.load(f)

	for word in blacklistData:
		wordBlacklist.append(word)
	return wordBlacklist