import socket
import os, sys
import json
import pickle
import random
import time
import sqlite3
import datetime
import binascii

from modules.colorhash import ColorHash

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
    if data["content"][0] == "/": # Command
        c.execute("SELECT * FROM admin_ips")
        admins = c.fetchall()
        flags = ""
        for admin in admins:
            if admin[0] == user["addr"][0]:
                flags = admin[1]
        split_command = data["content"].split()
        if split_command[0] == "/pm": # Private Message
            found = False
            for cl in clients:
                if cl["username"] == split_command[1]:
                    found = True
                    targetCl = cl
                    pmContent = " ".join(split_command[2:])
                    currentDT = datetime.datetime.now()
                    dt = str(currentDT.strftime("%d-%m-%Y %H:%M:%S"))                    
                    colour = ColorHash(user["username"])

                    message = {
                        "username": "",
                        "channel": "",
                        "content": [dt, user["username"], ("[PM] " + pmContent), colour.hex],
                        "messagetype": "outboundMessage"
                        }
                    data = encode(message)
                    targetCl["conn"].send(data)
                    print("Sent " + message["messagetype"] + " to client " + targetCl["username"] + "(" + str(user["addr"]) + ")")
                    conn.send(data)
                    print("Sent " + message["messagetype"] + " to client " + user["username"] + "(" + str(user["addr"]) + ")")

            if found == False:
                message = {
                    "username": "",
                    "channel": "",
                    "content": ["","system","[SERVER] User not found", ""],                                                                                        
                    "messagetype": "outboundMessage",
                    }
                data = encode(message)
                conn.send(data)
                print("Sent " + message["messagetype"] + " to client " + user["username"] + "(" + str(user["addr"]) + ")")
        else: # Admin command
            if flags == "":
                message = {
                        "username": "",
                        "channel": "",
                        "content": ["","system","[SERVER] Insufficient Permissions", ""],
                        "messagetype": "outboundMessage"
                        }
                data = encode(message)
                conn.send(data)
                print("Sent " + message["messagetype"] + " to client " + user["username"] + "(" + str(user["addr"]) + ")")
            elif split_command[0] == "/a":
                if "x" in flags or "M" in flags or "a" in flags:
                    #colour = ColorHash(user["username"])
                    message = {
                            "username": "",
                            "channel": "",
                            "content": ["", "system", "[ANNOUNCEMENT] "+" ".join(split_command[1:]), ""],
                            "messagetype": "outboundMessage"
                        }
                    data = encode(message)
                    for cl in clients:
                        cl["conn"].send(data)
                        print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")

                else:
                    message = {
                        "username": "",
                        "channel": "",
                        "content": ["","system","[SERVER] Insufficient Permissions", ""],
                        "messagetype": "outboundMessage"
                        }
                    data = encode(message)
                    conn.send(data)
                    print("Sent " + message["messagetype"] + " to client " + user["username"] + "(" + str(cl["addr"]) + ")")
            elif split_command[0] == "/whois":
                if "x" in flags or "w" in flags:
                    targetUser = ""
                    for cl in clients:
                        if cl["username"] == split_command[1]:
                            targetUser = cl
                    if targetUser == "":
                        message = {
                            "username": "",
                            "channel": "",
                            "content": ["","system","[WHOIS] User could not be found", ""],
                            "messagetype": "outboundMessage"
                            }
                        data = encode(message)
                        conn.send(data)
                        print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
                    else:
                        message = {
                            "username": "",
                            "channel": "",
                            "content": ["","system", "[WHOIS] " + str(targetUser["addr"]), ""],
                            "messagetype": "outboundMessage"
                            }
                        data = encode(message)
                        conn.send(data)
                        print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
                else:
                    message = {
                        "username": "",
                        "channel": "",
                        "content": ["","system","[SERVER] Insufficient Permissions", ""],
                        "messagetype": "outboundMessage"
                        }
                    data = encode(message)
                    conn.send(data)
                    print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
            elif split_command[0] == "/kick":
                if "x" in flags or "M" in flags or "k" in flags:
                    for cl in clients:
                        if cl["username"] == split_command[1]:
                            for cl2 in clients:
                                if cl2["channel"] == cl["channel"]:
                                    message = {
                                        "username": "",
                                        "channel": "",
                                        "content": ["","system","[SERVER] "+cl["username"]+" was kicked from the server", ""],
                                        "messagetype": "outboundMessage"
                                        }
                                    data = encode(message)
                                    cl2["conn"].send(data)
                            kickReason = " ".join(split_command[2:])
                            message = {
                                "username": "",
                                "channel": "",
                                "content": kickReason,
                                "messagetype": "userKicked"
                                }
                            data = encode(message)
                            cl["conn"].send(data)
                            cl["check"] = False
                            oldChannel = cl["channel"]
                            clients.remove(cl)
                            oldChannelCls = []
                            for cl in clients:
                                if cl["channel"] == oldChannel: # If the client is in the old channel
                                    found = False
                                    for a in admins:
                                        if a[0] == cl["addr"][0]:
                                            oldChannelCls.append(cl["username"]  + " \u2606")
                                            found = True
                                    if found == False:
                                        oldChannelCls.append(cl["username"])
                            for cl in clients:
                                if cl["channel"] == oldChannel:                                
                                    message = {
                                        "username": "",
                                        "channel": cl["channel"],
                                        "content": oldChannelCls,
                                        "messagetype": "channelMembers"
                                        }
                                    data = encode(message)
                                    cl["conn"].send(data)
                            
            elif split_command[0] == "/modify":
                if "x" in flags or "m" in flags:
                    targetUser = ""
                    for cl in clients:
                        if cl["username"] == split_command[1]:
                            targetUser = cl
                    if targetUser == "":
                        message = {
                            "username": "",
                            "channel": "",
                            "content": ["","system","[MODIFY] User could not be found", ""],
                            "messagetype": "outboundMessage"
                            }
                        data = encode(message)
                        conn.send(data)
                        print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
                    else:
                        try:
                            c.execute("UPDATE admin_ips SET flags='"+split_command[2]+"' WHERE ip='"+targetUser["addr"][0]+"'")
                            sqlite3_conn.commit()
                        except IndexError:
                            c.execute("UPDATE admin_ips SET flags='' WHERE ip='"+targetUser["addr"][0]+"'")
                            sqlite3_conn.commit()
                        message = {
                            "username": "",
                            "channel": "",
                            "content": ["","system","[MODIFY] User permissions updated", ""],
                            "messagetype": "outboundMessage"
                            }
                        data = encode(message)
                        conn.send(data)
                        print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
                        c.execute("SELECT * FROM admin_ips")
                        admins = c.fetchall()
                        ChannelCls = []
                        clients.remove(user)
                        for cl in clients:
                            if cl["channel"] == user["channel"]:
                                found = False
                                for a in admins:
                                    if a[0] == cl["addr"][0]:
                                        ChannelCls.append(cl["username"] + " \u2606")
                                        found = True
                                if found == False:
                                    ChannelCls.append(cl["username"])
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
                                
                                
                else:
                    message = {
                        "username": "",
                        "channel": "",
                        "content": ["","system","[SERVER] Insufficient Permissions", ""],
                        "messagetype": "outboundMessage"
                        }
                    data = encode(message)
                    conn.send(data)
                    print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
                
            
    else: # Regular Message
        currentDT = datetime.datetime.now()
        dt = str(currentDT.strftime("%d-%m-%Y %H:%M:%S"))
        msgContent = data["content"]
        #colour = str((binascii.hexlify(user["username"].encode('utf-8'))).decode('utf-8'))[:6]
        colour = ColorHash(user["username"])
        message = {
            "username": "",
            "channel": data["channel"],
            "content": [str(dt), user["username"], data["content"], colour.hex],
            "messagetype": "outboundMessage"
            }
        data = encode(message)
        for cl in clients:
            if cl["channel"] == user["channel"]:
                cl["conn"].send(data)
                print("Sent " + message["messagetype"] + " to client " + cl["username"] + str(cl["addr"]))
        c.execute("INSERT INTO chatlogs (ip, username, channel, date, message) values (?,?,?,?,?)",[str(user["addr"]), user["username"], user["channel"], dt, msgContent])
        sqlite3_conn.commit()
        c.execute("INSERT INTO tempchatlogs (username, channel, date, message, colour, realtime) values (?,?,?,?,?,?)",[user["username"], user["channel"], dt, msgContent, colour.hex, time.time()])
        sqlite3_conn.commit()