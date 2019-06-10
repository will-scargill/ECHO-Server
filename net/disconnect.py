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
	        data = encodeEncrypted(message, cl["secret"])
	        cl["conn"].send(data)
	        print("Sent " + message["messagetype"] + " to client " + cl["username"] + str(cl["addr"]))
	conn.close()                   
	user["check"] = False