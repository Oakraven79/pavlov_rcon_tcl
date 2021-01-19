"""
Main file the executes the app

"""

import asyncio
import json

import tkinter as tk
from tkinter import ttk

import logging
import sys


from server_frame import SingleServerFrame
from rcon_connector import send_rcon






###############################################################
# Set up the logger, just push to STDOUT
###############################################################
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

###############################################################
# Some help if the server.json config goes missing
###############################################################

SERVER_JSON_CONFIG_EXAMPLE = """

Ideally the file looks like this:

{
  "host"      : "192.168.0.15",
  "password"  : "password",
  "port"      : "9102"
}
        
"""


###############################################################
# Main App container
###############################################################
def init_app():
    try:
        with open('server.json') as server_conn_json_file:
            data = json.load(server_conn_json_file)
            rcon_host = data['host']
            rcon_port = int(data['port'])
            rcon_pass = data['password']
    except Exception as exc:
        print("There was a problem reading server.json! Error: {}".format(exc))
        print(SERVER_JSON_CONFIG_EXAMPLE)
        sys.exit(1)


    logger.info("SUPPLIED CREDS: {} {} {}".format(rcon_host, rcon_port, rcon_pass))
    root = tk.Tk()
    root.title("Pavlov RCON Helper V0.01")
    root.iconbitmap("rcon.ico")
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.state('zoomed')


    app = SingleServerFrame(master=root, rcon_host=rcon_host, rcon_port=rcon_port, rcon_pass=rcon_pass)
    return root, app





###############################################################
# Functions to be used to update the server contents
###############################################################
async def main_update():

    server_creds = app.get_server_creds()

    data = await send_rcon("ServerInfo", **server_creds, use_persisted_connection=False)

    max_players = 0 # Init this for further down

    if data is not None:
        # Update the server details
        server_name = data.get('ServerInfo',{}).get('ServerName','')
        map_name = data.get('ServerInfo', {}).get('MapLabel', '')
        game_mode = data.get('ServerInfo', {}).get('GameMode', '')
        game_status = data.get('ServerInfo', {}).get('RoundState', '')
        player_count = data.get('ServerInfo', {}).get('PlayerCount', '')
        teams_status = "{}".format(data.get('ServerInfo', {}).get('Teams', ''))
        teams_0_score = "{}".format(data.get('ServerInfo', {}).get('Team0Score', ''))
        teams_1_score = "{}".format(data.get('ServerInfo', {}).get('Team1Score', ''))
        max_players = int(player_count.split("/")[1])
        app.update_server_window(server_name, map_name, game_mode, game_status, player_count, teams_status, teams_0_score, teams_1_score )
    else:
        app.update_server_window_for_error()
    # Get the Item list from the server Which shows what items the players are allowed to have here

    data = await send_rcon("ItemList", **server_creds, use_persisted_connection=False)
    if data is not None:
        app.update_server_items(data.get("ItemList", list()))
    # Get the player info
    data = await send_rcon("RefreshList", **server_creds, use_persisted_connection=False)
    if data is not None:
        players_dict = {k:v for k, v in zip([x['Username'] for x in data['PlayerList']] , [x['UniqueId'] for x in data['PlayerList']]) }
    if data is not None:
        data = await asyncio.gather(*[send_rcon("InspectPlayer {}".format(x),**server_creds) for x in list(players_dict.values())])
        app.update_player_window(data, max_players)

    # TODO: Add a visual flag to the app for a connection problem


def update_windows():
    logger.info("Running")
    try:
        asyncio.run(main_update())
    except asyncio.exceptions.TimeoutError as exc:
        logger.info("Server took tool long to respond, Will try again shortly...")
    # Add itself back in to the main loop so it runs again.
    root.after(5000, update_windows)


###############################################################
# Application kick off stuff
###############################################################



root, app = init_app()



# testing resize handling
# Bind the action to the root container so it gets the event and then let app object sort out the layout

def handle_configure(event):
    logger.info("window geometry:\n" + root.geometry())
#root.bind("<Configure>", handle_configure)


# Now that i have the bulk of the windows working
# I need to do the following
# 1. Handle connects and disconnects
try:
    root.after(20, update_windows)
    # start the app main loop
    app.mainloop()
except Exception as exc:
    logger.info("Exception occurred: {}".format(exc))