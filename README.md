# pavlov_rcon_tcl
Want to manage your Pavlov server(s) (via RCON commands) from within VR?

What does it look like? https://www.youtube.com/watch?v=OrHwuWEGjaA

NEW: Added custom server commands -->  https://youtu.be/nOR2lqD70JQ

<img src="http://www.greatleapskyward.com/pavlov_rcon.jpg" />

This is a small app written in Python Tkinter and asyncio to quickly interface with Pavlov's RCON from within VR.

This is under active development.

## Why does this exist?
I wanted to build a tool that I could use to admin Pavlov from within VR (via Virtual Desktop)but set myself a challenge to use as much vanilla python as possible. So part fun project but also hoping to contribute to what is a really cool game!

There are plenty of more complete tools to manage Pavlov via RCON if you want more depth, check out http://wiki.pavlov-vr.com/index.php?title=Dedicated_server#Tools_available_to_access_Rcon_interface


## Features:

Supports most RCON commands (more to be added)

You can specify the workshop ID of a custom map into the switch map button (as described in the RCON instructions above)

Has a preloaded set of maps in the map list

Supports multiple servers, add seperate entries in the `server.json`

Supports custom server batch commands which allows raw RCON commands to be chained together, applied to all/some players and allows for delays between commands as per video above. See server_custom_commands_example.json for examples 

For fun I added a "give all" button which cycles through all connected players and gives them the selected item.


## Installation
Step 0. Make sure your Pavlov server has RCON set up as per [the Official Pavlov wiki](http://wiki.pavlov-vr.com/index.php?title=Dedicated_server#Rcon_Overview_and_Commands) 

_Note This doesn't work with Arctic as they have their own server tools._

### Option 1:  Stand alone .exe (Windows Only)

Step 1. Download https://github.com/Oakraven79/pavlov_rcon_tcl/releases/download/0.65/pavlov_rcon_tcl-0-65.zip

_Note: Windows may complain about downloading and running an .exe, it is just doing its job on security. If that bothers you, go with option 2._

Step 2. Unzip that file where you want.

Step 3. Edit `server.json` and supply the credentials for your servers or servers ("display_name" is the name of the server in the app )

Step 4. Run `PavlovRcon.exe`

(Optional)

Step 5. Edit maps.json and add your own maps. (will need to close and reopen) 

### Option 2: Run from Python source

Step 1. Go to [the Python website](http://www.python.org/downloads/) and install python 3.8 or above and get it working on your system. 

Step 2. Download the code as a zip (`Code` -> `Download zip`)

Step 3. Unzip that file where you want.

Step 4. edit `server.json` and supply the credentials for your servers or servers ("display_name" is what you want to see it in this app )

Step 5. either `run_win.bat` in the `pavlov_rcon_tcl` folder (for windows machines) or run `python main.py` from the `pavlov_rcon_tcl` folder 

(Optional)

Step 6. Fiddle with maps_list.py to add your own maps.  

## Please Note that it is very new and sometimes crashes and needs a restart. Work in progress! 

## On the TODO List 

- Add ability to list banned players and unban in server actions
- Make the item list easy to read as it is a bit fiddly still. 
- Make the map list easier to read.
- Make the window and fonts scale appropriately to the screen size. 
- Add player avatar pictures

## Feedback?

For feedback and suggestions on this tool contact @Oakraven:3967 on the official Pavlov Discord (https://discord.com/invite/pavlov-vr)

### Please note i'm just a fan writing a tool for the game, not an official member of the team at all. 
### They are much cooler than me.