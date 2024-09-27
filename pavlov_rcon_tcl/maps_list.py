"""
This dict used in the switch map server action.

The left side is the display name, the right side is what is sent via RCON

the ones that start with --- are ignored and just for spacing.

Feel free to customise this and add your own. You just need to make sure the names on the left are unique

"""

import json

import logging

logger = logging.getLogger(__name__)

# Map Ids, Keys MUST be Unique as they ge translated into a list!
# This list is used if the load lower fails
DEFAULT_MAP_IDS = {
    "--- Official": "",  # Spacer
    "Station": "station",
    "Stalingrad": "stalingrad",
    "Santorini": "santorini",
    "Santorini at night": "santorini_night",
    "Industry": "industry",
    "Industry at night": "industry_night",
    "Data Center": "datacenter",
    "Sand": "sand",
    "Sand at night": "sand_night",
    "Bridge": "bridge",
    "Container Yard": "containeryard",
    "Siberia": "prisonbreak",
    "Hospital (Zombies)": "hospital",
    "Kill House": "killhouse",
    "Shooting Range": "range",
    "Tutorial": "tutorial",
    "--- Counter Strike Maps": " ",  # Spacer
    "DUST II": "UGC2804502",
    "Mirage": "UGC3020535",
    "Office": "UGC3051820",
    "Inferno": "UGC2996823",
    "Militia": "UGC2844898",
    "Overpass": "UGC2867687",
    "Assault": "UGC2812444",
    "Italy": "UGC2879562",
    "Train": "UGC2871454",
    "DUST": "UGC3113703",
    "Lake": "UGC2841131",
    "Zoo": "UGC3002208",
    "CSGO McDonalds": "UGC3229032",
    "--- Call Of Duty": "",  # Spacer
    "Rust": "UGC3210963",
    "Nuke Town": "UGC2970978",
    "--- Modern Warfare": "",
    "Dome": "UGC2804210",
    "--- Others": "",  # Spacer
    "McDonalds": "UGC2804322",
    "McDonalds at Night": "UGC2819934",
    "7-11": "UGC3246562",
    "Inconvenience Store": "UGC2886706",
    "--- Zombies": "  ",  # Spacer
    "Kino Der Toten (CODz)": "UGC2809826",
    "Killer Jim's Der Riese": "UGC4056425",
    "Oasis: Minecraft Zombies": "UGC3116397",
    "--- PropHunt": "",  # Spacer
    "PH Dunder Mifflin": "UGC2802826",
    "PH Inc.": "UGC2806952",
    "PH Inc. 2": "UGC2816873",
    "PH Burger King": "UGC2812878",
    "PH Restaurant": "UGC2810539",
    "--- Swat 4": "",
    "Fairfax Residence": "UGC2815354",
}

MAP_IDS = None

try:
    with open("maps.json", "r") as reader:
        MAP_IDS = json.loads(reader.read())
    logger.info("loaded maps.json!")

    # just do a quick check of all the keys to make sure they are strings
    maps_list_local = []
    for key, value in MAP_IDS.items():
        if type(key) is str and type(value) is str:

            if key.startswith("---"):
                logger.info("Spacer detected: '{}' --> '{}'".format(key, value))
            else:
                logger.info("Map loaded: '{}' --> '{}'".format(key, value))
                maps_list_local.append(key)
        else:
            logger.warning(
                "Map values must be strings, invalid pair: '{}'/'{}'".format(key, value)
            )
            raise Exception("Invalid map supplied: {}/{}".format(key, value))
    logger.info("{} maps loaded from maps.json".format(len(maps_list_local)))

except Exception as exc:
    logger.warning("Unable to load maps.json, error: {}".format(exc))
    logger.info("Using default maps ids. ")
    MAP_IDS = DEFAULT_MAP_IDS
