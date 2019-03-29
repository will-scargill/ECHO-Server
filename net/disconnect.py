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
	oldChannelCls = []
	clients.remove(user)
	for cl in clients:
	    if cl["channel"] == user["channel"]:
	        if cl["conn"] == conn:
	            pass
	        else:
	            found = False
	            for a in admins:
	                if a[0] == cl["addr"][0]:
	                    oldChannelCls.append(cl["username"] + " \u2606")
	                    found = True
	            if found == False:
	                oldChannelCls.append(cl["username"])
	                
	for cl in clients: # Have to do this again :(
	    if cl["channel"] == user["channel"]: # If client is in old channel
	        message = {
	            "username": "",
	            "channel": user["channel"],
	            "content": oldChannelCls,
	            "messagetype": "channelMembers"
	            }
	        data = encode(message)
	        cl["conn"].send(data)
	        print("Sent " + message["messagetype"] + " to client " + cl["username"] + str(cl["addr"]))
	conn.close()                   
	check = False