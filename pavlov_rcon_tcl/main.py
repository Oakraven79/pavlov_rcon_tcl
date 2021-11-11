"""
Main file that sets up the app and runs it. 

"""
APP_VERSION = "0.75"
APP_NAME = "Pavlov RCON Helper"

###############################################################
# Set up the logger FIRST, just push to STDOUT
###############################################################
import logging
import sys
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(filename)s:%(lineno)d %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


###############################################################
# Do the rest of the base library imports
###############################################################
import os
import asyncio
import json

# This is the actual import for the app itself, all the magic happens here
from async_app import AsyncApp

###############################################################
# Some help if the server.json config goes missing
###############################################################

MULTIPLE_SERVER_EXAMPLE = """
[
    {
        "display_name"  : "My Server",
        "host"          : "1.1.1.1",
        "password"      : "password",
        "port"          : "9100"
    },{
        "display_name"  : "My Server 2",
        "host"          : "2.2.2.2",
        "password"      : "password",
        "port"          : "9100"
    }
]
"""

SERVER_JSON_CONFIG_EXAMPLE = """

Ideally the file looks like this for one server(JSON):

[
    {
        "display_name"  : "My Server",
        "host"          : "1.1.1.1",
        "password"      : "password",
        "port"          : "910"
    }
]

For multiple servers:
        
"""+ MULTIPLE_SERVER_EXAMPLE


###############################################################
# Main Entry Point
###############################################################
def main():
    # The tool can manage multiple servers, so we load each seperate config into a list of dicts that are 
    # passed into individual server containers 
    servers_list = []
    try:
        with open('server.json') as server_conn_json_file:
            servers_data = json.load(server_conn_json_file)
            for data in servers_data:
                servers_list.append({
                    'rcon_host'       : data['host'],
                    'rcon_port'       : int(data['port']),
                    'rcon_pass'       : data['password'],
                    'rcon_name'       : data.get("display_name", "No Name"),
                    'server_commands' : data.get("custom_server_cmds", [])
                })
    except FileNotFoundError as exc:
        # Exception condition for when the config file has gone missing, write a sample and then quit
        print("Could not find server.json. I created a sample one for you to edit.")
        f = open("server.json", "w")
        f.write(MULTIPLE_SERVER_EXAMPLE)
        f.close()
        sys.exit(1)
    except Exception as exc:
        # Someone has messed up the server.json, print out a sample and then exit
        print("There was a problem reading server.json! {}: {}".format(exc.__class__.__name__,exc))
        print(SERVER_JSON_CONFIG_EXAMPLE)
        sys.exit(1)
    # init the app and run it
    try:
        # This surfaces the async loop manager in asyncio so we can use it. 
        loop = asyncio.get_event_loop()
        # AsyncApp is the main container class for the the entire application, everything here is just getting it ready to go. 
        root = AsyncApp(loop)
        # root is the default variable convention name for tcl/tkinter UI apps. 
        root.title("{} V{}".format(APP_NAME, APP_VERSION)) # This changes the display name at run time, just to make it pretty
        # Set the icon file for the app if there is one, just for added flair
        if os.path.isfile('rcon.ico'):
            root.iconbitmap("rcon.ico")
        # When a TCL/Tkinter app starts it kind of guesses what size it is supposed to be unless you are explicit, this says:
        # "Be the same size as the screen you opened on '{0}x{1}' and do not be offset from the top left '+0+0' "
        root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
        # and go full screen as the application starts
        root.state('zoomed')
        # As this can connect to multiple servers we take the servers_list
        # and load each one
        for server_dict in servers_list:
            logger.info("SUPPLIED CREDS: {} {} {}".format(*(list(server_dict.values()))))
            root.add_new_server_frame(**server_dict)
        # Get the event loop again but as a different variable so as not to interrupt the pointer we passed to the app
        loop = asyncio.get_event_loop()
        # This stars the infinte loop until an exit action is called. 
        loop.run_forever()
        # Close the asyncio tasks otherwise the application will hang until force closed
        loop.close()
    except Exception as exc:
        logger.info("Exception occurred during app initialisation: {}".format(exc))


if __name__ == '__main__':
    main()
    # Insert a pause so you can read the terminal :)
    input("Press Enter to exit...")