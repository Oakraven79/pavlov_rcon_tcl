"""
Main file the executes the app

"""
import logging
import sys
import asyncio
import json

from async_app import AsyncApp


###############################################################
# Set up the logger, just push to STDOUT
###############################################################

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

###############################################################
# Some help if the server.json config goes missing
###############################################################

SERVER_JSON_CONFIG_EXAMPLE = """

Ideally the file looks like this:

[
  {
    "host"      : "192.168.0.15",
    "password"  : "password",
    "port"      : "9102"
  }
]
        
"""


###############################################################
# Main Entry Point
###############################################################
def main():
    # load the server configs
    servers_list = []
    try:
        with open('server.json') as server_conn_json_file:
            servers_data = json.load(server_conn_json_file)
            for data in servers_data:
                servers_list.append({
                    'rcon_host' : data['host'],
                    'rcon_port' : int(data['port']),
                    'rcon_pass' : data['password'],
                    'rcon_name' : data.get("display_name", "No Name")
                })

    except Exception as exc:
        print("There was a problem reading server.json! Error: {}".format(exc))
        print(SERVER_JSON_CONFIG_EXAMPLE)
        sys.exit(1)
    # init the app and run it
    try:
        loop = asyncio.get_event_loop()
        root = AsyncApp(loop)
        root.title("Pavlov RCON Helper V0.01")
        root.iconbitmap("rcon.ico")
        root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
        root.state('zoomed')

        for server_dict in servers_list:
            logger.info("SUPPLIED CREDS: {} {} {}".format(*(list(server_dict.values()))))
            root.add_new_server_frame(**server_dict)
        loop = asyncio.get_event_loop()
        loop.run_forever()
        loop.close()
    except Exception as exc:
        logger.info("Exception occurred during app initialisation: {}".format(exc))


if __name__ == '__main__':
    main()