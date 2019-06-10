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

from modules import aes
from modules import permissions
from modules import config
from modules import blacklist
from modules.encoding import encodeEncrypted, encode, decode

kickOnUse = (config.GetSetting("kickOnUse", "Blacklist"))
blKickReason = config.GetSetting("kickReason", "Blacklist")

if kickOnUse == "True":
    kickOnUse = True
elif kickOnUse == "False":
    kickOnUse = False
else:
    print("Error - incomplete config [kickOnUse setting missing]")

# Permission flags
# x - admin
# M - moderator
# m - modify
# k - kick
# b - ban
# a - announce
# w - whois


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
                    data = encodeEncrypted(message, cl["secret"])
                    targetCl["conn"].send(data)
                    print("Sent " + message["messagetype"] + " to client " + targetCl["username"] + "(" + str(user["addr"]) + ")")
                    data = encodeEncrypted(message, user["secret"])
                    conn.send(data)
                    print("Sent " + message["messagetype"] + " to client " + user["username"] + "(" + str(user["addr"]) + ")")

            if found == False:
                message = {
                    "username": "",
                    "channel": "",
                    "content": ["","system","[SERVER] User not found", ""],                                                                                        
                    "messagetype": "outboundMessage",
                    }
                data = encodeEncrypted(message, user["secret"])
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
                data = encodeEncrypted(message, user["secret"])
                conn.send(data)
                print("Sent " + message["messagetype"] + " to client " + user["username"] + "(" + str(user["addr"]) + ")")
            elif split_command[0] == "/a": # Announcement
                if "x" in flags or "M" in flags or "a" in flags:
                    #colour = ColorHash(user["username"])
                    message = {
                            "username": "",
                            "channel": "",
                            "content": ["", "system", "[ANNOUNCEMENT] "+" ".join(split_command[1:]), ""],
                            "messagetype": "outboundMessage"
                        }               
                    for cl in clients:
                        data = encodeEncrypted(message, cl["secret"])
                        cl["conn"].send(data)
                        print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")

                else:
                    message = {
                        "username": "",
                        "channel": "",
                        "content": ["","system","[SERVER] Insufficient Permissions", ""],
                        "messagetype": "outboundMessage"
                        }
                    data = encodeEncrypted(message, user["secret"])
                    conn.send(data)
                    print("Sent " + message["messagetype"] + " to client " + user["username"] + "(" + str(cl["addr"]) + ")")
            elif split_command[0] == "/whois": # Whois
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
                        data = encodeEncrypted(message, user["secret"])
                        conn.send(data)
                        print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
                    else:
                        if permissions.canBeExecuted(user, targetUser, admins) == True:
                            message = {
                                "username": "",
                                "channel": "",
                                "content": ["","system", "[WHOIS] " + str(targetUser["addr"]), ""],
                                "messagetype": "outboundMessage"
                                }
                            data = encodeEncrypted(message, user["secret"])
                            conn.send(data)
                            print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
                        else:
                            message = {
                                "username": "",
                                "channel": "",
                                "content": ["","system","[SERVER] Insufficient Permissions", ""],
                                "messagetype": "outboundMessage"
                                }
                            data = encodeEncrypted(message, user["secret"])
                            conn.send(data)
                            print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
                else:
                    message = {
                        "username": "",
                        "channel": "",
                        "content": ["","system","[SERVER] Insufficient Permissions", ""],
                        "messagetype": "outboundMessage"
                        }
                    data = encodeEncrypted(message, user["secret"])
                    conn.send(data)
                    print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
            elif split_command[0] == "/kick": # Kick
                if "x" in flags or "M" in flags or "k" in flags:
                    for cl in clients:
                        if cl["username"] == split_command[1]:
                            if permissions.canBeExecuted(user, cl, admins) == True:
                                kickReason = " ".join(split_command[2:])
                                permissions.kickUser(cl, kickReason, clients, False)
                            else:
                                message = {
                                    "username": "",
                                    "channel": "",
                                    "content": ["","system","[SERVER] Insufficient Permissions", ""],
                                    "messagetype": "outboundMessage"
                                    }
                                data = encodeEncrypted(message, user["secret"])
                                conn.send(data)
                                print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
                else:
                    message = {
                        "username": "",
                        "channel": "",
                        "content": ["","system","[SERVER] Insufficient Permissions", ""],
                        "messagetype": "outboundMessage"
                        }
                    data = encodeEncrypted(message, user["secret"])
                    conn.send(data)
                    print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
            elif split_command[0] == "/ban": # Ban
                if "x" in flags or "M" in flags or "b" in flags:
                    for cl in clients:
                        if cl["username"] == split_command[1]:
                            if permissions.canBeExecuted(user, cl, admins) == True:
                                kickReason = " ".join(split_command[2:])
                                currentDT = datetime.datetime.now()
                                dt = str(currentDT.strftime("%d-%m-%Y %H:%M:%S"))

                                c.execute("INSERT INTO banned_ips (ip, date_banned, reason, realtime) VALUES (?,?,?,?)",[str(cl["addr"][0]), dt, kickReason, time.time()])
                                sqlite3_conn.commit()

                                permissions.kickUser(cl, kickReason, clients, True)
                            else:
                                message = {
                                    "username": "",
                                    "channel": "",
                                    "content": ["","system","[SERVER] Insufficient Permissions", ""],
                                    "messagetype": "outboundMessage"
                                    }
                                data = encodeEncrypted(message, user["secret"])
                                conn.send(data)
                                print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
                else:
                    message = {
                        "username": "",
                        "channel": "",
                        "content": ["","system","[SERVER] Insufficient Permissions", ""],
                        "messagetype": "outboundMessage"
                        }
                    data = encodeEncrypted(message, user["secret"])
                    conn.send(data)
                    print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")

            elif split_command[0] == "/modify": # Modify
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
                        data = encodeEncrypted(message, user["secret"])
                        conn.send(data)
                        print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
                    else:
                        if permissions.canBeExecuted(user, targetUser, admins) == True:
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
                            data = encodeEncrypted(message, user["secret"])
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
                                    data = encodeEncrypted(message, cl["secret"])
                                    cl["conn"].send(data)
                                    print("Sent " + message["messagetype"] + " to client " + cl["username"] + str(cl["addr"]))
                        else:
                            message = {
                                "username": "",
                                "channel": "",
                                "content": ["","system","[SERVER] Insufficient Permissions", ""],
                                "messagetype": "outboundMessage"
                                }
                            data = encodeEncrypted(message, user["secret"])
                            conn.send(data)
                            print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")                                      
                else:
                    message = {
                        "username": "",
                        "channel": "",
                        "content": ["","system","[SERVER] Insufficient Permissions", ""],
                        "messagetype": "outboundMessage"
                        }
                    data = encodeEncrypted(message, user["secret"])
                    conn.send(data)
                    print("Sent " + message["messagetype"] + " to client " + cl["username"] + "(" + str(cl["addr"]) + ")")
                
            
    else: # Regular Message
        if blacklist.checkBlacklist(data["content"]) == True:
            print("User " + user["username"] + " used a blacklisted word")
            if kickOnUse == True:
                permissions.kickUser(user, blKickReason, clients, False)
            else:
                message = {
                        "username": "",
                        "channel": "",
                        "content": ["","system","[SERVER] You used a blacklisted word, and your message was not sent.", ""],
                        "messagetype": "outboundMessage"
                        }
                data = encodeEncrypted(message, user["secret"])
                conn.send(data)
        else:
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
            for cl in clients:
                if cl["channel"] == user["channel"]:
                    data = encodeEncrypted(message, cl["secret"])
                    cl["conn"].send(data)
                    print("Sent " + message["messagetype"] + " to client " + cl["username"] + str(cl["addr"]))
            c.execute("INSERT INTO chatlogs (ip, username, channel, date, message) values (?,?,?,?,?)",[str(user["addr"]), user["username"], user["channel"], dt, msgContent])
            sqlite3_conn.commit()
            c.execute("INSERT INTO tempchatlogs (username, channel, date, message, colour, realtime) values (?,?,?,?,?,?)",[user["username"], user["channel"], dt, msgContent, colour.hex, time.time()])
            sqlite3_conn.commit()