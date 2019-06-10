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
    userList = []
    for cl in clients:
        userList.append(cl["username"])
    message = {
        "username": "",
        "channel": "",
        "content": userList,
        "messagetype": "userList"
        }
    data = encodeEncrypted(message, user["secret"])
    conn.send(data)