import socket
import os, sys
import json
import pickle
import random
import time
import sqlite3
import datetime

from modules import aes
from modules.encoding import encodeEncrypted, encode, decode

def handle(conn, addr, c, sqlite3_conn, data, user, clients):
	timesRequested = data["content"]
	channel = data["channel"]
	desclimit = timesRequested * 50
	asclimit = (timesRequested - 1) * 50

	c.execute("SELECT * FROM tempchatlogs WHERE channel=?", [channel])
	allMessages = c.fetchall()

	remaining = (len(allMessages) - asclimit)
	if remaining < 50:
	    c.execute("SELECT * FROM (SELECT * FROM (SELECT * FROM tempchatlogs WHERE channel=? ORDER BY realtime DESC LIMIT "+str(desclimit)+") ORDER BY realtime ASC LIMIT "+str(remaining)+") ORDER BY date DESC",[channel])
	else:   
	    c.execute("SELECT * FROM (SELECT * FROM (SELECT * FROM tempchatlogs WHERE channel=? ORDER BY realtime DESC LIMIT "+str(desclimit)+") ORDER BY realtime ASC LIMIT 50) ORDER BY date DESC",[channel])
	channelHistory = c.fetchall()
	message = {
	    "username": "",
	    "channel": user["channel"],
	    "content": channelHistory,
	    "messagetype": "additionalHistory"
	    }
	#print(message)
	data = encodeEncrypted(message, user["secret"])
	conn.send(data)

	print("Sent " + message["messagetype"] + " to client " + user["username"] + str(user["addr"]))