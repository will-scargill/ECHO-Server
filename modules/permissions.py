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
from modules.encoding import encodeEncrypted, encode, decode

flagHeirarchy = {}

flagHeirarchy["x"] = config.GetSetting("x", "Permissions Flag Heirarchy")
flagHeirarchy["M"] = config.GetSetting("Mo", "Permissions Flag Heirarchy")
flagHeirarchy["m"] = config.GetSetting("m", "Permissions Flag Heirarchy")
flagHeirarchy["b"] = config.GetSetting("b", "Permissions Flag Heirarchy")
flagHeirarchy["k"] = config.GetSetting("k", "Permissions Flag Heirarchy")
flagHeirarchy["a"] = config.GetSetting("a", "Permissions Flag Heirarchy")
flagHeirarchy["w"] = config.GetSetting("w", "Permissions Flag Heirarchy")

def canBeExecuted(user, target, admins):
	userFlags = ""
	for admin in admins:
		if admin[0] == user["addr"][0]:
		    userFlags = admin[1]
	targetFlags = ""
	for admin in admins:
		if admin[0] == user["addr"][0]:
	   	    targetFlags = admin[1]
	userFlags = userFlags.split()
	targetFlags = targetFlags.split()
	canExecute = False
	for userFlag in userFlags:
		for targetFlag in targetFlags:
			if flagHeirarchy[userFlag] < flagHeirarchy[targetFlag]:
				canExecute = True
	if user == target:
		canExecute = True
	return canExecute

def kickUser(target, reason, clients, ban):
	for cl in clients:
		if cl["channel"] == target["channel"]:
			message = {
		        "username": "",
		        "channel": "",
		        "content": ["","system","[SERVER] "+ target["username"]+" was kicked from the server", ""],
		        "messagetype": "outboundMessage"
		        }
			data = encodeEncrypted(message, cl["secret"])
			cl["conn"].send(data)
	if ban == True:
		message = {
		    "username": "",
		    "channel": "",
		    "content": reason,
		    "messagetype": "userBanned"
		    }
	else:
		message = {
		    "username": "",
		    "channel": "",
		    "content": reason,
		    "messagetype": "userKicked"
		    }
	data = encodeEncrypted(message, target["secret"])
	target["conn"].send(data)
	target["check"] = False
	oldChannel = target["channel"]
	clients.remove(target)
	oldChannelCls = []
	for cl in clients:
	    if cl["channel"] == oldChannel: # If the client is in the old channel
	        found = False
	        for a in admins:
	            if a[0] == cl["addr"][0]:
	                oldChannelCls.append(cl["username"]  + " \u2606")
	                found = True
	        if found == False:
	            oldChannelCls.append(cl["username"])
	for cl in clients:
	    if cl["channel"] == oldChannel:                                
	        message = {
	            "username": "",
	            "channel": cl["channel"],
	            "content": oldChannelCls,
	            "messagetype": "channelMembers"
	            }
	        data = encodeEncrypted(message, cl["secret"])
	        cl["conn"].send(data)