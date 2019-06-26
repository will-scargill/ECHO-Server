# Echo Server
### Version 1.01
### The python server for [Echo](https://github.com/will-scargill/Echo) 

## Dependancies
* To install all required dependancies, run the following command:

`python3 -m pip install -r requirements.txt`

## Server Configuration

* Extract the files to a suitable folder
* Navigate to configs/config.ini and open it in a text editor
### Server Settings
##### Channels
* Additional channels can be added by adding an extra item to the list
> ["Channel 1", "Channel 2"]
* To add a new channel, you can paste `,""` before the final square bracket, and write the name of the channel you wish to add in-between the quote marks
> ["Channel 1", "Channel 2", "Channel 3"]
##### Password
* If you wish to add a password to your server, simply type the password you wish to use after the equals sign
> password = [password goes here]
* If you do not wish to use a password you can simply leave this blank
##### port
* This is the port that people will connect to your server through
* You can change this by simply changing the number after the equals sign
> port = 16000
* Can become
> port = 16001
### Permissions Flag Heirarchy
* The permission flag heirarchy is used to determine which flags have higher priority when executing commands. Someone with the `x` flag (admin), can always execute commands on other flags (`Mo`, and below). However, someone with the `b` flag (ban), will not be able to execute commands on anyone equal to or higher in the heirarchy than themselves.
##### Flag meanings
* x - admin - Has the ability to run all commands
* Mo - moderator - Has the ability to run `b`, `k`, and `a` commands
* m - modify - Grants the ability to modify other users flags
* w - whois - Grants the ability to view the IP address of any connected user
* b - ban - Grants the ability to ban a user from the server
* k - kick - Grants the ability to kick a user from the server
* a - announce - Grants the ability to post announcements which can be viewed in all channels
##### Changing the heirarchy
* The heirarchy can be changed by simply editing the numbers next to the flags. Smaller numbers have more priority than larger numbers. 

### Blacklist
##### useBlacklist & kickOnUse
* The `useBlacklist` setting (True/False) determines whether the server should use the blacklist to block certain words from being used in a message
* The `kickOnUse` setting (True/False) determines whether a user should be kicked if they use a word in the blacklist
##### kickReason
* This string determines what the user will see as the reason if they are kicked via the blacklist

### Records
* This is a placeholder config setting for a feature that is not yet implemented

## Setup using PM2

> I recommend using [PM2](http://pm2.keymetrics.io/) to manage the server process

* Navigate to the root folder of the server
* Run the command `pm2 start server.py`
* The server should now be running, you can run `pm2 status` to view the condition of all active processes
* `pm2 start server` and `pm2 stop server` can be used to start and stop the server, respectively
