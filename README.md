# pavlov_rcon_tcl
Want to manage your Pavlov server from within VR?

This is a small app written in Python Tkinter and asyncio to interface with Pavlov's RCON from within VR.

This is under active development.

## Why does this exist?
I wanted to build a tool that I could use to admin Pavlov from within VR (via Virtual Desktop)but set myself a challenge to use as much vanilla python as possible. So part fun project but also hoping to contribute to what is a really cool game!

There are plenty of more complete tools to manage Pavlov via RCON if you want more depth, check out http://wiki.pavlov-vr.com/index.php?title=Dedicated_server#Tools_available_to_access_Rcon_interface

This was my attempt at the simplest way to connect to your servers in game and quickly fire off commands.  

## Features:

Supports most RCON commands (more to be added)

You can specify the workshop ID of a custom map into the switch map button (as described in the RCON instructions above)

Has a preloaded set of maps in the map list

Supports multiple servers, add seperate entries in the `server.json`

For fun I added a "give all" button which cycles through all connected players and gives them the selected item.

See screen shot [here](http://www.greatleapskyward.com/pavlov.jpg) (please note the data is faked to show the layout)


## Installation
Step 0. Make sure your Pavlov server has RCON set up as per [the Official Pavlov wiki](http://wiki.pavlov-vr.com/index.php?title=Dedicated_server#Rcon_Overview_and_Commands) 


### Option 1:  Stand alone .exe (Windows Only)

Step 1. Download https://github.com/Oakraven79/pavlov_rcon_tcl/releases/download/v0.51-alpha/pavlov_rcon_tcl-0-51.zip

Step 2. Unzip that file where you want.

Step 3. Edit `server.json` and supply the credentials for your servers or servers ("display_name" is the name of the server in the app )

Step 4. Run `PavlovRcon.exe`

### Option 2: Run from Python source

Step 1. Go to [the Python website](http://www.python.org/downloads/) and install python 3.8 or above and get it working on your system. 

Step 2. Download the code as a zip (`Code` -> `Download zip`)

Step 3. Unzip that file where you want.

Step 4. edit `server.json` and supply the credentials for your servers or servers ("display_name" is what you want to see it in this app )

Step 5. either `run_win.bat` in the `pavlov_rcon_tcl` folder (for windows machines) or run `python main.py` from the `pavlov_rcon_tcl` folder 


## Please Note that it is very new and sometimes crashes and needs a restart. Work in progress! 

## On the TODO List 

- Add ability to list banned players and unban in server actions
- Ability to add custom batch commands. 
- Make the item list easy to read.
- Make the map list easier to read.
- Make the window and fonts scale appropriately to the screen size. 
- Make a youtube video showing this in action
- Turn this into something that is installable via pip

## Feedback?

For feedback and suggestions on this tool contact @Oakraven on the official Pavlov Discord (https://discord.com/invite/pavlov-vr)

###Please note i'm just a fan writing a tool for the game, not an official member of the team at all. 
###They are much cooler than me.