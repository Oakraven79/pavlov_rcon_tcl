"""
Used to map item names to friendly names for display.

Please note that this dict gets flipped for reverse lookups so make sure everything is unique

"""

KNOWN_ITEM_NAME_MAP = {
    "M249 Light Machine Gun (LMGA)" :"LMGA",
}

# inverted this list for lookup items
# If you edit KNOWN_ITEM_NAME_MAP you don't need to edit this
KNOWN_ITEM_NAME_MAP_INV = {v: k for k, v in KNOWN_ITEM_NAME_MAP.items()}