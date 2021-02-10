"""
Main file the executes the app

"""
import logging
import sys
import os
import asyncio
import json

from async_app import AsyncApp


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
    # load the server configs
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
        print("Could not find server.json. I created a sample one for you to edit.")
        f = open("server.json", "w")
        f.write(MULTIPLE_SERVER_EXAMPLE)
        f.close()
        sys.exit(1)
    except Exception as exc:
        print("There was a problem reading server.json! {}: {}".format(exc.__class__.__name__,exc))
        print(SERVER_JSON_CONFIG_EXAMPLE)
        sys.exit(1)
    # init the app and run it
    try:
        loop = asyncio.get_event_loop()
        root = AsyncApp(loop)
        root.title("Pavlov RCON Helper V0.51")
        if os.path.isfile('rcon.ico'):
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
    # Insert a pause so you can read the terminal :)
    input("Press Enter to exit...")