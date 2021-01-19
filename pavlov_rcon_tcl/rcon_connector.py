

import pavlovrcon
import logging
logger = logging.getLogger(__name__)

PERSISTED_RCON = None

def get_rcon(rcon_host=None, rcon_port=None, rcon_pass=None, use_persisted_connection=False):
    """
    This is responsible for providing an active connection to the desired server connection.

    TODO: Makes this persistent and connection shared instead of creating a new one each time, perhaps merge with send rcon

    :return:
    """
    if use_persisted_connection:
        global PERSISTED_RCON
        if PERSISTED_RCON is None:
            PERSISTED_RCON = pavlovrcon.PavlovRCON(rcon_host, rcon_port, rcon_pass)
        if not PERSISTED_RCON.is_connected():
            PERSISTED_RCON = pavlovrcon.PavlovRCON(rcon_host, rcon_port, rcon_pass)
        return PERSISTED_RCON
    else:
        return pavlovrcon.PavlovRCON(rcon_host, rcon_port, rcon_pass)

# Send a command
async def send_rcon(command, rcon_host=None, rcon_port=None, rcon_pass=None, use_persisted_connection=False):

    # if command == "RefreshList":
    #
    #         data = {
    #                     "PlayerList": [
    #                             {
    #                                     "Username": "Oakraven",
    #                                     "UniqueId": "76561198040783597"
    #                             },
    #                         {
    #                             "Username": "Oakraven2",
    #                             "UniqueId": "76561198040783598"
    #                         },
    #                         {
    #                             "Username": "Oakraven3",
    #                             "UniqueId": "76561198040783599"
    #                         },
    #                         {
    #                             "Username": "Oakraven4",
    #                             "UniqueId": "76561198040783510"
    #                         },
    #                         {
    #                             "Username": "Oakraven5",
    #                             "UniqueId": "76561198040783511"
    #                         },
    #                         {
    #                             "Username": "Oakraven6",
    #                             "UniqueId": "76561198040783512"
    #                         },
    #                         {
    #                             "Username": "Oakraven7",
    #                             "UniqueId": "76561198040783513"
    #                         },
    #                         {
    #                             "Username": "Oakraven8",
    #                             "UniqueId": "76561198040783513"
    #                         },
    #                         {
    #                             "Username": "Oakraven9",
    #                             "UniqueId": "76561198040783514"
    #                         },
    #                         {
    #                             "Username": "Oakraven10",
    #                             "UniqueId": "76561198040783515"
    #                         },
    #                         {
    #                             "Username": "Oakraven11",
    #                             "UniqueId": "76561198040783516"
    #                         },
    #
    #                     ]
    #             }
    #
    # elif command.startswith("InspectPlayer"):
    #     unique_id = command.split(" ")[1]
    #
    #     data = {
    #                     "PlayerInfo":
    #                     {
    #                             "PlayerName": "Oakraven{}".format(unique_id[-4:]),
    #                             "UniqueId": "{}".format(unique_id),
    #                             "KDA": "0/4/0",
    #                             "Score": "0",
    #                             "Cash": "9400",
    #                             "TeamId": "0"
    #                     }
    #             }
    #
    # elif command == "ItemList":
    #     data = {'ItemList': ['ak', 'vanas', 'AUG', 'awp', 'smg', 'shotgun', 'AR', 'sock', 'm9', 'cet9', 'Armour', 'kevlarhelmet', 'Grenade', 'grenade_ru', 'AK47', 'AK12', 'DE', '1911', 'mp5', 'p90', 'Smoke', 'smoke_ru', 'flash', 'flash_ru', 'sawedoff', 'Pliers', 'LMGA', 'AutoShotgun', 'AntiTank', 'kar98', 'AutoSniper', '57', 'uzi', 'Knife', 'DrumShotgun', 'Revolver', 'supp_pistol', 'supp_rifle', 'scope', 'Grip_Angled', 'Grip_Vertical', 'acog', 'holo', 'reddot', 'painkillers', 'ammo_rifle', 'ammo_sniper', 'ammo_smg', 'ammo_pistol', 'ammo_shotgun', 'ammo_special', 'taser', 'crowbar', 'boltcutters', 'lockpick', 'handcuffs', 'repairtool', 'pickaxe', 'keycard', 'syringe', 'luger', 'mp40', 'G43', 'Tokarev', 'webley', 'm1garand', 'svt40', 'grenade_us', 'smoke_us', 'grenade_ger', 'smoke_ger', 'grenade_svt', 'smoke_svt', 'bar', 'bren', 'ppsh', 'sten', 'mosin', 'springfield', 'thompson', 'mg42', 'leeenfield', 'RL_M1A1', 'RL_PIAT', 'rl_panzer', 'stg44', 'dp27', 'kross', 'vss', 'tankmg', 'tankturret', 'backblast', 'runover', 'Fire', 'fall', 'scar', 'skinhelmet_us', 'skinhelmet_ger', 'skinhelmet_svt', 'FlashLight', 'Katana', 'AdminSword', 'DiamondSword', 'OneHandedSword', 'BlueRoseSword', 'ContributorSword', 'ContributorSwordSecond', 'ContributorSwordThird', 'ContributorSwordFour', 'ContributorSwordFifth', 'Torch', 'AncientSWORD', 'TwitchSword', 'DarkAncientSword', 'NetherScythe', 'PerkBottleBase', 'juggernautbottle', 'staminupbottle', 'ExcaliburSword', 'TestingBow', 'MCBow', 'PatreonBow', 'Enderpearl', 'SnakeBow', 'PatreonSword', 'DiamondAxe']}
    #
    # elif command == "ServerInfo":
    #     data = {'ServerInfo': {'MapLabel': 'UGC1741218360', 'GameMode': 'ZWV', 'ServerName': 'Great Leap To Zombies', "Teams": True, "Team0Score": "0", "Team1Score": "0",'RoundState': 'Started', 'PlayerCount': '0/16'}}
    #
    #
    # else:


    try:
        rcon_obj = get_rcon(rcon_host=rcon_host, rcon_port=rcon_port, rcon_pass=rcon_pass, use_persisted_connection=use_persisted_connection)

        data = await rcon_obj.send(command)
    except Exception as exc:
        logger.error("Unable to Send RCON COMMAND: {}".format(exc))
        return None
    # close the rcon connection
    if not use_persisted_connection:
        await rcon_obj.send("Disconnect")
        await rcon_obj.close()

    logger.info(data)
    return data
