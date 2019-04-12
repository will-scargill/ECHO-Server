import socket
import os, sys
import json
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
        print(data)

def handle(conn, addr, c, sqlite3_conn, data, user, clients):
    userList = []
    for cl in clients:
        userList.append(cl["username"])
    message = {
        "username": "",
        "channel": "",
        "content": userList,
        "messagetype": "userList"
        }
    data = encode(message)
    conn.send(data)