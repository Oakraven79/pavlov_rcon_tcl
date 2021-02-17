"""
This dict used in the switch map server action.

The left side is the display name, the right side is what is sent via RCON

the ones that start with --- are ignored and just for spacing.

Feel free to customise this and add your own. You just need to make sure the names on the left are unique

"""

# Map Ids, Keys MUST be Unique as they ge translated into a list!
MAP_IDS = {
    '--- New' : '', #Spacer
    'station' : 'station',
    'stalingrad' : 'stalingrad',
    'santorini':'santorini',
    'industry' : 'industry',
    '--- Originals': '',
    'Data Center': 'datacenter',
    'Sand': 'sand',
    'Bridge': 'bridge',
    'Container Yard': 'containeryard',
    'Siberia': 'prisonbreak',
    'Hospital (Zombies)': 'hospital',
    'Kill House': 'killhouse',
    'Shooting Range': 'range',
    'Tutorial': 'tutorial',
    '--- Counter Strike Maps' : ' ', # Spacer
    'DUST II': "UGC1664873782",
    "Mirage": "UGC1661803933",
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