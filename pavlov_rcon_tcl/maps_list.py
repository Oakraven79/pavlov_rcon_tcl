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
    '--- New' : '', #Spacer
    'Station' : 'station',
    'Stalingrad' : 'stalingrad',
    'Santorini':'santorini',
    'Santorini at night':'santorini_night',
    'Industry' : 'industry',
    'Industry at night' : 'industry_night',
    '--- Originals': '',
    'Data Center': 'datacenter',
    'Sand': 'sand',
    'Sand at night': 'sand_night',
    'Bridge': 'bridge',
    'Container Yard': 'containeryard',
    'Siberia': 'prisonbreak',
    'Hospital (Zombies)': 'hospital',
    'Kill House': 'killhouse',
    'Shooting Range': 'range',
    'Tutorial': 'tutorial',
    '--- Counter Strike Maps' : ' ', # Spacer
    'DUST II': "UGC1664873782",
    "Mirage": "UGC2405033833",
    "Office": "UGC1080743206",
    "Cache": "UGC1695916905",
    "Inferno":  "UGC1661039078",
    "Tuscan": "UGC2170893566",
    "Overpass": "UGC1676961583",
    "Lake" : "UGC1401905027",
    "--- Call Of Duty": "", # Spacer
    "Rust" : "UGC1739104662",
    "--- Others": '',  # Spacer
    "Outset Island (Zelda)": "UGC1373830364",
    "McDonalds": "UGC1984149656",
    "Oilrig": "UGC1701860633",
    "Elven Ruins" : "UGC2396016789",
    "--- BIG MAPS": "",  # Spacer
    'City War': 'UGC2297877134',
    '--- Zombies': '  ',  # Spacer
    "NachtDerUntoten (CODz)": "UGC1836053818",
    "Der Riese (CODz)": "UGC1890699727",
    "Kino Der Toten (CODz)": "UGC1929882349",
    "Call of the Dead (CODz)": "UGC1948201228",
    "Oasis: Minecraft Zombies": "UGC1931739042",
    "Zombies - Subway - End Days": "UGC1741218360",
    "Zombies - Three Islands - END DAYS": "UGC1804442427",
    "--- TTT" : "",
    "New MC CITY TTT" : "UGC1729478375",
    "TTT Old West" : "UGC2267134313",
    '--- PropHunt': '',  # Spacer
    'PH Warehouse': 'UGC1810463805',
    'PH Hotel': 'UGC1825578429',
}

MAP_IDS = None

try:
    with open('maps.json', 'r') as reader:
        MAP_IDS = json.loads(reader.read())
    logger.info("loaded maps.json!")

    # just do a quick check of all the keys to make sure they are strings
    maps_list_local = []
    for key, value in MAP_IDS.items():
        if type(key) is str and type(value) is str:

            if key.startswith("---"):
                logger.info("Spacer detected: '{}' --> '{}'".format(key, value))
            else:
                logger.info("Map loaded: '{}' --> '{}'".format(key,value))
                maps_list_local.append(key)
        else:
            logger.warning("Map values must be strings, invalid pair: '{}'/'{}'".format(key, value))
            raise Exception("Invalid map supplied: {}/{}".format(key, value))
    logger.info("{} maps loaded from maps.json".format(len(maps_list_local)))

except Exception as exc:
    logger.warning("Unable to load maps.json, error: {}".format(exc))
    logger.info("Using default maps ids. ")
    MAP_IDS = DEFAULT_MAP_IDS