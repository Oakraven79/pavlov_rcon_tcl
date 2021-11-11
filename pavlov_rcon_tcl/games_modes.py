"""
This file is imported and used for menus, the left side of the dict (key) is used in the drop down, the right side is what
is sent to the server.

It will try to load from games_modes.json first but in the face of any error it will swap back to the default one

"""

import json

import logging
logger = logging.getLogger(__name__)


DEFAULT_GAME_MODES = {
    'Search And Destroy' : 'SND',
    'Team Death Match' : 'TDM',
    'Deathmatch' : 'DM',
    'Gun Game' : 'GUN',
    'TTT' : 'TTT',
    'Zombie Wave' : 'ZWV',
    "Tank TDM": "TANKTDM",
    "WW2GUN" : "WW2GUN",
    "King of the Hill":"KOTH",
    "One In The Chamber" : "OITC",
    "HIDDEN" : "HIDDEN", 
    "INFECTION" : "INFECTION",
}

GAME_MODES = None

try:
    # load the file and convert
    with open('game_modes.json', 'r') as reader:
        GAME_MODES = json.loads(reader.read())
    logger.info("loaded games_modes.json!")
    # quick check to see if it is a dict and that all the keys/vals are strings
    if not isinstance(GAME_MODES, dict):
        logger.error("First element of game_modes.json must be a dictionary/map starting '{' - defaulting to internal list")
        raise Exception("Bad game modes.json!")
    logger.info("Game modes found in file: {}".format(GAME_MODES))
except:
    logger.info("Unable to load game_modes.json, reverting to internal default. Please check file and format. ")
    GAME_MODES = DEFAULT_GAME_MODES