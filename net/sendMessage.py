import socket
import os, sys
import json
import pickle
import random
import time
import sqlite3
import datetime

def chunkstring(string, length):
    return list(string[0+i:length+i] for i in range(0, len(string), length))

def sendMessage(socket, user, data):
    datalist = chunkstring(data, 1024)
    for d in datalist:
        socket.send(d)
