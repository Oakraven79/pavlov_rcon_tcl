# pavlov_rcon_tcl
A small app written in Python Tkinter and asyncio to interface with Pavlov's RCON from within VR.

This is under active development.

## Why does this exist?
I wanted to build a tool that I could use to admin Pavlov from within VR but set myself a challenge to use as much vanilla python as possible. So part fun project but also hoping to contribute to what is a really cool game!

There are plenty of more complete tools to manage Pavlov via RCON if you want more depth, check out http://wiki.pavlov-vr.com/index.php?title=Dedicated_server#Tools_available_to_access_Rcon_interface

This was my attempt at the simplest way to connect to your server in game and quickly fire off commands.  

## Features:

Supports most RCON commands (more to be added)

You can specify the workshop ID of a custom map into the switch map button (as described in the RCON instructions above)

For fun I added a "give all" button which cycles through all connected players and gives them the selected item.

## Installation
Step 0. Make sure your Pavlov server has RCON set up as per [http://wiki.pavlov-vr.com/index.php?title=Dedicated_server#Rcon_Overview_and_Commands] 

Step 1. Go to www.python.org/downloads/ and install python 3.8 or above and get it working on your system. 

Step 2. Download the code as a zip (`Code` -> `Download zip`)

Step 3. Unzip that file where you want.

Step 4. edit `server.json` and supply the credentials for your server

Step 5. either `run_win.bat` (for windows machines) or run `python main.py` from the `pavlov_rcon_tcl` folder 

Please Note that it is very new and sometimes crashes and needs a restart. Work in progress! 

On the TODO List: 

- Add scroll bars when there are more players than available screen
- Add ability to list banned players and unban in server actions
- Sometimes the background tasks freeze the UI, working to background that properly.



