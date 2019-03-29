import socket
import os, sys
import json
from _thread import *
import pickle
import random
import time
import sqlite3
import datetime
import re
import queue
import binascii

from net import inboundMessage
from net import changedChannel
from net import disconnect
from net import messageReq

sqlite3_conn = sqlite3.connect("database.db", check_same_thread=False)
c = sqlite3_conn.cursor()

tables = [
    {
        "name": "banned_ips",
        "columns": "ip TEXT, date_banned TEXT, reason TEXT"
    },
    {
        "name": "admin_ips",
        "columns": "ip TEXT, flags TEXT, permlevel TEXT, colour TEXT"
    },
    {
        "name": "chatlogs",
        "columns": "ip TEXT, username TEXT, channel TEXT, date TEXT, message TEXT"
    },
    {
        "name": "commandlogs",
        "columns": "ip TEXT, username TEXT, channel TEXT, date TEXT, command TEXT, reason TEXT"
    },
    {
        "name": "pmlogs",
        "columns": "ip TEXT, username TEXT, channel TEXT, date TEXT, message TEXT"
    },
    {
        "name": "tempchatlogs",
        "columns": "username TEXT, channel TEXT, date TEXT, message TEXT, colour TEXT, realtime INTEGER"
    }
]

for table in tables:
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [table["name"]])
    data = c.fetchall()
    if len(data) <= 0:  # If table doesn't exist
        c.execute("CREATE TABLE " + table["name"] + " (" + table["columns"] + ")")

clients = []

channels = ["Channel 1", "Channel 2", "Channel 3", "Spam Channel"]

password = ""

def encode(data):
    data = json.dumps(data) #Json dump message
    data = data.encode('utf-8') #Encode message in utf-8
    return(data) 
def decode(data):
    try:
        data = data.decode('utf-8') #Decode utf-8 data
        data = data.strip()
        data = re.findall('.*?[}]', data)
        #data = json.loads(data) #Load from json
        return(data)
    except json.decoder.JSONDecodeError:
        print("json error")
        print(data)

def client_connection_thread(conn, addr):
    try:
        confirmedDisconnect = False
        data = conn.recv(1024)
        data = decode(data)
        data = json.loads(data[0])
        user = {
            "username": data["content"][0],
            "channel": "",
            "conn": conn,
            "addr": addr
            }
        if data["content"][1] == password:

            check = True
            
            message = {
            "username": "",
            "channel": "",
            "content": channels,
            "messagetype": "connReqAccepted"
            }
            data = encode(message)
            conn.send(data)
            print("Connection request from " + str(addr) + " approved")
            for cl in clients:
                if cl["username"] == user["username"]:
                    user["username"] = (user["username"] + "_" + str(random.randint(1,10)))
                    message = {
                        "username": user["username"],
                        "channel": "",
                        "content": "username",
                        "messagetype": "userUpdate"
                        }
                    data = encode(message)
                    conn.send(data)
                    print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
            clients.append(user)
            mainQueue = queue.Queue()
            while (check == True):
                rawData = conn.recv(4096)
                rawData = decode(rawData)
                for data in rawData:
                    data = json.loads(data)
                    try:
                        print("Recieved " + data["messagetype"] + " from client " + user["username"] + str(user["addr"]))
                        #print(data["content"])
                        if data["messagetype"] == "inboundMessage":
                            inboundMessage.handle(conn, addr, c, sqlite3_conn, data, user, clients)
                        elif data["messagetype"] == "changedChannel":
                            changedChannel.handle(conn, addr, c, sqlite3_conn, data, user, clients)
                        elif data["messagetype"] == "disconnect":
                            disconnect.handle(conn, addr, c ,sqlite3_conn, data, user, clients)
                        elif data["messagetype"] == "messageReq":
                            messageReq.handle(conn, addr, c, sqlite3_conn, data, user, clients)
                    except TypeError:
                        print("Recieved data triggered type error - slowdown")
                    
                    
        else:
            message = {
            "username": "",
            "channel": "",
            "content": "",
            "messagetype": "connReqDenied"
            }
            data = encode(message)
            conn.send()
            print("Connection request from " + str(addr) + " denied")
                         
            conn.close()
    except(ConnectionResetError) as e:
        print("Connection lost to client: " + str(addr))
        try:
            check = False
            clients.remove(user)
            oldChannelCls = []
            for cl in clients:
                if cl["channel"] == user["channel"]:
                    if cl["username"] == user["username"]:
                        pass
                    else:
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
        except() as e:
            print(e)
        conn.close()
    
    
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "127.0.0.1"
port = 16000

try:
    s.bind((host, port))
except socket.error as e:
    print(e)

s.listen(20)

clients = []

print("Listening...")

while True:
    conn, addr = s.accept()

    start_new_thread(client_connection_thread, (conn, addr,))

