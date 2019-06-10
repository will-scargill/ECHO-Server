import socket
import os, sys
import json
import pickle
import random
import time
import sqlite3
import datetime
import binascii

from modules import aes
from modules import config

useBlacklist = (config.GetSetting("useBlacklist", "Blacklist"))

def checkBlacklist(message):
	usingNaughtyWord = False
	bannedWords = config.GetBlacklist()
	if useBlacklist == "True":
		for word in message.split():
			if word.lower() in bannedWords[0]["blacklistedWords"]:
				usingNaughtyWord = True
	return usingNaughtyWord
