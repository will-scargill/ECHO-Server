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
	c.execute("SELECT * FROM admin_ips")
	admins = c.fetchall()
	oldChannel = user["channel"] # Stores channel user WAS in, so as to update people in said channel
	user["channel"] = data["content"] # Updates user["channel"] with new recieved channel
	newChannelCls = [] # List of clients in the new channel
	oldChannelCls = [] # List of clients in the old channel
	for cl in clients:
	    if cl["channel"] == "":
	        pass
	    else:
	        if cl["channel"] == oldChannel: # If the client is in the old channel
	            found = False
	            for a in admins:
	                if a[0] == cl["addr"][0]:
	                    oldChannelCls.append(cl["username"]  + " \u2606")
	                    found = True
	            if found == False:
	                oldChannelCls.append(cl["username"])
	        elif cl["channel"] == user["channel"]: # If the client is in the new channel
	            found = False
	            for a in admins:
	                if a[0] == cl["addr"][0]:
	                        newChannelCls.append(cl["username"] + " \u2606")
	                        found = True
	            if found == False:
	                newChannelCls.append(cl["username"])
	for cl in clients: # Have to do this again :(
	    if cl["channel"] == oldChannel: # If client is in old channel
	        message = {
	            "username": "",
	            "channel": user["channel"],
	            "content": oldChannelCls,
	            "messagetype": "channelMembers"
	            }
	        data = encode(message)
	        cl["conn"].send(data)
	        print("Sent " + message["messagetype"] + " to client " + cl["username"] + str(cl["addr"]))
	    elif cl["channel"] == user["channel"]: # If client is in new channel
	        message = {
	            "username": "",
	            "channel": user["channel"],
	            "content": newChannelCls,
	            "messagetype": "channelMembers"
	            }
	        data = encode(message)
	        cl["conn"].send(data)
	        print("Sent " + message["messagetype"] + " to client " + cl["username"] + str(cl["addr"]))

	c.execute("SELECT * FROM (SELECT * FROM tempchatlogs WHERE channel=? ORDER BY realtime DESC LIMIT 50) ORDER BY realtime ASC", [user["channel"]])
	channelHistory = c.fetchall()
	message = {
	    "username": "",
	    "channel": user["channel"],
	    "content": channelHistory,
	    "messagetype": "channelHistory"
	    }
	data = encode(message)
	conn.send(data)
	print("Sent " + message["messagetype"] + " to client " + cl["username"] + str(cl["addr"]))