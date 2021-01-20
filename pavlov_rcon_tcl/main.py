"""
Main file the executes the app

"""
import logging
import sys
import asyncio
import json

import tkinter as tk

from server_frame import SingleServerFrame
from rcon_connector import send_rcon


###############################################################
# Set up the logger, just push to STDOUT
###############################################################

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
# Overridden class for blending tkinter event loop with asyncio
###############################################################

class AsyncApp(tk.Tk):

    def __init__(self, loop, interval=1/120):
        super().__init__()
        self.loop = loop
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.tasks = []

        # create these tasks so i can destory them later.
        self.tasks.append(loop.create_task(self.run_rcon_updates()))
        self.tasks.append(loop.create_task(self.updater(interval)))

    # This is core to the tkinter update
    async def updater(self, interval):
        """
        This run the tkinter updates

        :param interval:
        :return:
        """
        while True:
            self.update()
            await asyncio.sleep(interval)

    async def run_rcon_updates(self, interval=5):
        """
        This runs the

        :param interval:
        :return:
        """
        logger.info("Starting Initial update")
        await main_update()

        while await asyncio.sleep(interval, True):
            logger.info("Running update")
            await main_update()
            logger.info("Finishing update")


    # This is for the closed
    def close(self):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.destroy()


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
    loop = asyncio.get_event_loop()
    root = AsyncApp(loop)
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


###############################################################
# Application kick off stuff
###############################################################
root, app = init_app()

try:
    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
except Exception as exc:
    logger.info("Exception occurred: {}".format(exc))