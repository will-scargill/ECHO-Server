import socket
import os, sys
import json
from _thread import *
import pickle
import random
import time
import sqlite3
import datetime

def encode(data):
    data = json.dumps(data) #Json dump message
    data = data.encode('utf-8') #Encode message in utf-8
    return(data) 
def decode(data):
    try:
        data = data.decode('utf-8') #Decode utf-8 data
        data = data.strip()
        data = json.loads(data) #Load from json
        return(data)
    except json.decoder.JSONDecodeError:
        print("json error")
        print(data)

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
	data = encode(message)
	conn.send(data)

	print("Sent " + message["messagetype"] + " to client " + user["username"] + str(user["addr"]))