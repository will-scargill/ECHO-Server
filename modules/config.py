import configparser

def GetSetting(setting):
	parser = configparser.ConfigParser()
	parser.read("config.ini")
	try:
		data = json.loads(parser.get("Server", setting))
		return data
	except:
		data = parser.get("Server", setting)
		if data == '""':
			return ""
		else:
			return data