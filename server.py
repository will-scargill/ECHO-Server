import socket
import os, sys
import json
import threading
import pickle
import random
import time
import sqlite3
import datetime
import re
import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES

#os.chdir("/home/echo/")

from modules import aes
from modules import config
from modules.encoding import encodeEncrypted, encode, decode

from net import inboundMessage
from net import changedChannel
from net import disconnect
from net import messageReq
from net import userReq

from net import sendMessage

sqlite3_conn = sqlite3.connect(r"data/database.db", check_same_thread=False) # Connect to the database
c = sqlite3_conn.cursor() # Setup sqlite cursor

try: # Try to read data from RSA keys to check if they exist
    fileIn = open(r"data/public.pem", "rb")
    fileIn.close()
    fileIn = open(r"data/private.pem", "rb")
    fileIn.close()
except: # If they don't, generate RSA keys
    print("Rsa keys not found, generating...")
    exec(open("regenerateRsaKeys.py").read())

tables = [
    {
        "name": "banned_ips",
        "columns": "ip TEXT, date_banned TEXT, reason TEXT"
    },
    {
        "name": "admin_ips",
        "columns": "ip TEXT, flags TEXT, permlevel TEXT"
    },
    {
        "name": "chatlogs",
        "columns": "ip TEXT, username TEXT, channel TEXT, date TEXT, message TEXT"
    },
    {
        "name": "commandlogs",
        "columns": "senderip TEXT, senderusername TEXT, targetip TEXT, targetusername TEXT, channel TEXT, date TEXT, command TEXT, reason TEXT"
    },
    {
        "name": "pmlogs",
        "columns": "senderip TEXT, senderusername TEXT, targetip TEXT, targetusername TEXT, channel TEXT, date TEXT, message TEXT"
    },
    {
        "name": "tempchatlogs",
        "columns": "username TEXT, channel TEXT, date TEXT, message TEXT, colour TEXT, realtime INTEGER"
    }
]

for table in tables: # Create database tables if they don't exist
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [table["name"]])
    data = c.fetchall()
    if len(data) <= 0:  # If table doesn't exist
        c.execute("CREATE TABLE " + table["name"] + " (" + table["columns"] + ")")



channels = config.GetSetting("channels", "Server")

password = config.GetSetting("password", "Server")

port = config.GetSetting("port", "Server")
    
def splitCombinedMessages(data): # Used to seperate messages if multiple messages are sent as one
    messages = []
    dataSplit = data.split("][")
    for d in dataSplit:
        if d[0] != "[":
            tData = "["
            tData += d
            d = tData
        if d[(len(d) - 1)] != "]":
            d += "]"
        messages.append(d)
    return messages
    

def decodeEncrypted(rawData, key): # Decode encrypted network data
    try:
        rawData = rawData.decode('utf-8') #Decode utf-8 data
        rawData = rawData.strip()
        splitData = splitCombinedMessages(rawData)
        for data in splitData:
            data = json.loads(data)
            data = aes.Decrypt(data[0], key, data[1])
            data = data.decode('utf-8')
            data = re.findall('.*?[}]', data)
            dataToReturn = []
            for item in data:
                item = json.loads(item)
                dataToReturn.append(item)
        return dataToReturn
    except json.decoder.JSONDecodeError:
        print("json error")
        print(data)

def client_connection_thread(conn, addr): # Main connection thread for all clients
    try:
        print("Incoming connection from address " + str(addr))
        confirmedDisconnect = False
        data = conn.recv(1024) # Recieve 'keyRequest'
        data = decode(data)

        print("Recieved keyRequest from address " + str(addr))
        
        # Encryption set up start

        fileIn = open(r"data/private.pem", "rb") # Read private key
        bytesIn = fileIn.read()
        private = RSA.import_key(bytesIn)
        fileIn.close()

        fileIn = open(r"data/public.pem", "rb") # Read public key
        bytesIn = fileIn.read()
        public = RSA.import_key(bytesIn) 
        fileIn.close()

        publicToSend = bytesIn.decode('utf-8') # Get string of public key to send to client
        
        encObject = PKCS1_OAEP.new(public) # Setup public key encryption object
        decObject = PKCS1_OAEP.new(private) # Setup private key encryption object
        
        message = {
            "username": "",
            "chanel": "",
            "content": publicToSend,
            "messagetype": "publicKey"
            }
        data = encode(message)
        conn.send(data)

        print("Sent publicKey to address " + str(addr))

        
        data = conn.recv(1024) # Recieve 'secretKey'
        data = data.decode('utf-8')
        data = json.loads(data)
        print("Recieved secretKey from address " + str(addr))
        
        secretKey = decObject.decrypt(base64.b64decode(data["content"])) # Decode the secret key we recieved from the client

        message = {
            "username": "",
            "chanel": "",
            "content": "",
            "messagetype": "confirmed"
            }
        data = encode(message)
        conn.send(data)

        print("Sent confirmed to address " + str(addr))

        # Encryption set up end
        
        data = conn.recv(1024)
        data = decodeEncrypted(data, secretKey)
        
        user = {
            "username": data[0]["content"][0],
            "channel": "",
            "conn": conn,
            "addr": addr,
            "check": False,
            "secret": secretKey
            }
        c.execute("SELECT * FROM banned_ips") # Get all banned IPs from the database
        bannedIpsAllData = c.fetchall()
        bannedIps = []
        for usr in bannedIpsAllData:
            bannedIps.append(usr[0])
        userBanned = False
        for ip in bannedIps:
            if ip == user["addr"][0]:
                userBanned = True
        if (data[0]["content"][1] == password) and (userBanned == False): # If the password is correct & the client isn't banned

            user["check"] = True # user["check"] keeps track of whether the user is connected
            
            message = {
            "username": "",
            "channel": "",
            "content": channels,
            "messagetype": "connReqAccepted"
            }
            data = encodeEncrypted(message, user["secret"])
            #conn.send(data)
            sendMessage.sendMessage(conn, user, data)
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
                    data = encodeEncrypted(message, user["secret"])
                    sendMessage.sendMessage(conn, user, data)
                    print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
            clients.append(user)
            while (user["check"] == True):
                rawData = conn.recv(4096)
                rawData = decodeEncrypted(rawData, user["secret"])
                for data in rawData:
                    print("Recieved " + data["messagetype"] + " from client " + user["username"] + str(user["addr"]))
                    if data["messagetype"] == "inboundMessage":
                        inboundMessage.handle(conn, addr, c, sqlite3_conn, data, user, clients)
                    elif data["messagetype"] == "changedChannel":
                        changedChannel.handle(conn, addr, c, sqlite3_conn, data, user, clients)
                    elif data["messagetype"] == "disconnect":
                        disconnect.handle(conn, addr, c ,sqlite3_conn, data, user, clients)
                    elif data["messagetype"] == "messageReq":
                        messageReq.handle(conn, addr, c, sqlite3_conn, data, user, clients)
                    elif data["messagetype"] == "userReq":
                        userReq.handle(conn, addr, c, sqlite3_conn, data, user, clients)
                    
                    
        else: # One or more joining conditions was not fulfilled
            if (user["addr"][0] in bannedIps): # If the client was banned
                message = {
                "username": "",
                "channel": "",
                "content": "banned",
                "messagetype": "connReqDenied"
                }
                data = encodeEncrypted(message, user["secret"])
                conn.send(data)
                print("Connection request from " + str(addr) + " denied - User is banned")
            elif (data[0]["content"][1] != password): # If the password was incorrect
                message = {
                "username": "",
                "channel": "",
                "content": "password",
                "messagetype": "connReqDenied"
                }
                data = encodeEncrypted(message, user["secret"])
                conn.send(data)
                print("Connection request from " + str(addr) + " denied - Incorrect password")
                         
            conn.close()
    except(ConnectionResetError) as e: # If a connection error occurs
        print("Connection lost to client: " + str(addr))
        try:
            check = False
            clients.remove(user)
            # Code below updates users who were in the same channel
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
                    data = encodeEncrypted(message, cl["secret"])
                    cl["conn"].send(data)
                    print("Sent " + message["messagetype"] + " to client " + cl["username"] + str(cl["addr"]))            
        except() as e:
            print(e)
        conn.close()
    
    
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Setup socket object

host = "127.0.0.1"
#port = 16000

try:
    s.bind(("", int(port))) 
except socket.error as e:
    print(e)

s.listen(20) # Listen for connections

clients = []

print("Listening...")

while True:
    conn, addr = s.accept() # Accept incoming connections

    threading.Thread(target=client_connection_thread, args=(conn,addr)).start() # Start a new thread for the client

