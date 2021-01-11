"""

RefreshList
{
        "PlayerList": [
                {
                        "Username": "Oakraven",
                        "UniqueId": "76561198040783597"
                }
        ]
}
Help
{
        "Help": "Kick UniqueID, Kill UniqueID, Ban UniqueID, Unban UniqueId, BlackList, RotateMap, MapList, SwitchMap MapId, SwitchTeam UniqueID TeamID, ItemList, GiveItem UniqueID ItemID, SetCash UniqueID CashAmt, GiveCash UniqueID CashAmt, GiveTeamCash TeamId CashAmt, InspectPlayer UniqueID, RefreshList, ServerInfo, ResetSND, SetLimitedAmmoType AmmoType, SetPlayerSkin UniqueID SkinID, Disconnect"
}

InspectPlayer 76561198040783597
{
        "PlayerInfo":
        {
                "PlayerName": "Oakraven",
                "UniqueId": "76561198040783597",
                "KDA": "0/4/0",
                "Cash": "9400",
                "TeamId": "0"
        }
}
ServerInfo
{
        "ServerInfo":
        {
                "MapLabel": "UGC1929882349",
                "GameMode": "ZWV",
                "ServerName": "Great Leap To Zombies",
                "RoundState": "Started",
                "PlayerCount": "1/16"
        }
}
"""


import platform
import asyncio
import random

import tkinter as tk
from tkinter import ttk


import logging
import sys

import pavlovrcon

# SEt up the logger, just push to STDOUT
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)



GAME_MODES = {
    'Seek And Destroy':'SND',
    'Team Death Match': 'TDM',
    'Deathmatch' : 'DM',
    'Gun Game' : 'GUN',
    'Zombie Wave' : 'ZWV',
}

# Map Ids, Keys MUST be Unique!
MAP_IDS = {
    'Data Center':'datacenter',
    'Sand':'sand',
    'Bridge' : 'bridge',
    'Container Yard': 'containeryard',
    'Siberia' : 'prisonbreak',
    'Hospital (Zombies)': 'hospital',
    'Kill House' : 'killhouse',
    'Shooting Range' : 'range',
    'Tutorial' : 'tutorial',
    '--- PropHunt' : '', # Spacer
    'PH Warehouse' : 'UGC1810463805',
    'PH Hotel' : 'UGC1825578429',
    '--- CS Maps' : ' ', # Spacer
    'DUST II' : "UGC1664873782",
    "Mirage" : "UGC1661803933",
    '--- Zombies' : '  ', # Spacer
    "NachtDerUntoten (CODz)": "UGC1836053818",
    "Der Riese (CODz)" : "UGC1890699727",
    "Kino Der Toten (CODz)" : "UGC1929882349",
    "Call of the Dead (CODz)" : "UGC1948201228",
    "Oasis: Minecraft Zombies":"UGC1931739042",
    "Zombies - Subway - End Days" : "UGC1741218360",
    "Zombies - Three Islands - END DAYS" : "UGC1804442427",
}

# If the name of the item has a human friendly version, add it here.
KNOWN_ITEM_NAME_MAP = {}

# Simple thing to get an Rcon connection, TODO: Make this a decorator
def get_rcon():
    return pavlovrcon.PavlovRCON("192.168.0.15", 9102, 'password')

# Send a command
async def send_rcon(command):

    # if command == "RefreshList":
    #
    #     if random.randint(0,9) > 4:
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
    #
    #                     ]
    #             }
    #     else:
    #         data = {
    #             "PlayerList": [
    #                 {
    #                     "Username": "Oakraven",
    #                     "UniqueId": "76561198040783597"
    #                 },
    #
    #             ]
    #         }
    #
    # elif command == "InspectPlayer 76561198040783597":
    #     data = {
    #                     "PlayerInfo":
    #                     {
    #                             "PlayerName": "Oakraven",
    #                             "UniqueId": "76561198040783597",
    #                             "KDA": "0/4/0",
    #                             "Cash": "9400",
    #                             "TeamId": "0"
    #                     }
    #             }
    # elif command == "InspectPlayer 76561198040783598":
    #     data = {
    #                     "PlayerInfo":
    #                     {
    #                             "PlayerName": "Oakraven2",
    #                             "UniqueId": "76561198040783598",
    #                             "KDA": "0/4/0",
    #                             "Cash": "9400",
    #                             "TeamId": "0"
    #                     }
    #             }
    # elif command == "ItemList":
    #     data = {'ItemList': ['ak', 'vanas', 'AUG', 'awp', 'smg', 'shotgun', 'AR', 'sock', 'm9', 'cet9', 'Armour', 'kevlarhelmet', 'Grenade', 'grenade_ru', 'AK47', 'AK12', 'DE', '1911', 'mp5', 'p90', 'Smoke', 'smoke_ru', 'flash', 'flash_ru', 'sawedoff', 'Pliers', 'LMGA', 'AutoShotgun', 'AntiTank', 'kar98', 'AutoSniper', '57', 'uzi', 'Knife', 'DrumShotgun', 'Revolver', 'supp_pistol', 'supp_rifle', 'scope', 'Grip_Angled', 'Grip_Vertical', 'acog', 'holo', 'reddot', 'painkillers', 'ammo_rifle', 'ammo_sniper', 'ammo_smg', 'ammo_pistol', 'ammo_shotgun', 'ammo_special', 'taser', 'crowbar', 'boltcutters', 'lockpick', 'handcuffs', 'repairtool', 'pickaxe', 'keycard', 'syringe', 'luger', 'mp40', 'G43', 'Tokarev', 'webley', 'm1garand', 'svt40', 'grenade_us', 'smoke_us', 'grenade_ger', 'smoke_ger', 'grenade_svt', 'smoke_svt', 'bar', 'bren', 'ppsh', 'sten', 'mosin', 'springfield', 'thompson', 'mg42', 'leeenfield', 'RL_M1A1', 'RL_PIAT', 'rl_panzer', 'stg44', 'dp27', 'kross', 'vss', 'tankmg', 'tankturret', 'backblast', 'runover', 'Fire', 'fall', 'scar', 'skinhelmet_us', 'skinhelmet_ger', 'skinhelmet_svt', 'FlashLight', 'Katana', 'AdminSword', 'DiamondSword', 'OneHandedSword', 'BlueRoseSword', 'ContributorSword', 'ContributorSwordSecond', 'ContributorSwordThird', 'ContributorSwordFour', 'ContributorSwordFifth', 'Torch', 'AncientSWORD', 'TwitchSword', 'DarkAncientSword', 'NetherScythe', 'PerkBottleBase', 'juggernautbottle', 'staminupbottle', 'ExcaliburSword', 'TestingBow', 'MCBow', 'PatreonBow', 'Enderpearl', 'SnakeBow', 'PatreonSword', 'DiamondAxe']}

    # elif command == "ServerInfo":
    #     data = {'ServerInfo': {'MapLabel': 'UGC1741218360', 'GameMode': 'ZWV', 'ServerName': 'Great Leap To Zombies', 'RoundState': 'Started', 'PlayerCount': '0/16'}}

    # else:
    rcon_obj = get_rcon()
    data = await rcon_obj.send(command)
    # close the rcon connection
    await rcon_obj.close()
    logger.info(data)

    return data

def button_hi():
    logger.info("Button")

def button_give_money(unique_id, amount):
    """


    :param unique_id:
    :param amount:
    :return:
    """

    logger.info("Give {} ${}".format(unique_id, amount))
    asyncio.run(send_rcon("GiveCash {} {}".format(unique_id, amount)))

def button_give_item(unique_id, item):
    """

    :param unique_id:
    :param item:
    :return:
    """

    logger.info("Give {} {}".format(unique_id, item))
    asyncio.run(send_rcon("GiveItem {} {}".format(unique_id, item)))


def button_rotate_map():
    asyncio.run(send_rcon("RotateMap"))

def button_switch_map():
    """
    Calling this inspects the apps state for the selections

    :return:
    """
    logger.info("SwitchMap!")
    selections = app.get_current_map_selection_values()
    logger.info(selections)

    mapped_game_mode = GAME_MODES.get(selections['game_mode'], None)
    if mapped_game_mode is None:
        logger.info("Game mode: {} is unknown".format(selections['game_mode']))
        return
    # now to check the MAP name against the list. Since it is possible to specify workshop maps
    # we need to allow for maps that are in the MAP_IDS dict and if they are not we make sure they have
    # UGC in front before we send to the server.
    raw_map_id = selections['map']
    if not raw_map_id.strip():
        logger.info("Unable to switch map, no map specified")
        return
    mapped_map_id = MAP_IDS.get(raw_map_id, None)
    if mapped_map_id is None:
        # The user has dropped something in the text box that we don't know about so we need to do a few quick checks
        # before submitting to the server
        # if the map start with UGC, we strip that out for now and put it back in later
        raw_map_id = raw_map_id.lower().replace('ugc', '')
        if raw_map_id.isdigit():
            mapped_map_id = "UGC{}".format(raw_map_id)
        else:
            logger.info("Map ID is not a number so i'm skipping it")
            return
    if mapped_map_id.startswith("---"):
        # This is the just the spacer, don't select this!
        return
    # mapped_map_id is ready to submit to the server
    switch_str = "SwitchMap {} {}".format(mapped_map_id, mapped_game_mode)
    logger.info(switch_str)
    asyncio.run(send_rcon(switch_str))


class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self,master=master,**kw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        #logger.info("Enter")
        if platform.system() == "Darwin":  ### if its a Mac
            self['highlightbackground'] = "green"
        else:
            self['bg'] = "green"


    def on_leave(self, e):
        #logger.info("leave")
        if platform.system() == "Darwin":  ### if its a Mac
            self['highlightbackground'] = "SystemButtonFace"
        else:
            self['bg'] = "SystemButtonFace"


class PlayerListFrame:

    def __init__(self, parent_frame):
        """

        :param parent_frame:
        """
        self.parent_frame = parent_frame
        self.player_frame_dict = dict()



    def update_player_frame(self, data, items_list):
        """
        Given a data dict which is direct from the API, this interprets and updates the currnet player frame as needed

        :param data_dict:
        :return:
        """
        logger.info("Updating the players with {}".format(data))


        # Each player has a Unique ID, so we build a list of those as each frame, if the user dissappears so does the frame
        # and all its child widgets.

        # The list is sorted according to who arrived first. If you want a leaderboard, be in the game.

        # Create or update as needed
        current_player_ids_list = list(self.player_frame_dict.keys())
        seen_unique_ids_list = list()
        for refresh_item_dict in data:
            player_info = refresh_item_dict['PlayerInfo']
            unique_id = player_info['UniqueId']
            if unique_id in current_player_ids_list:
                self.update_single_player_frame(self.player_frame_dict[unique_id], player_info, items_list)
            else:
                self.player_frame_dict[unique_id] = self.create_single_player_frame(player_info, items_list)
            seen_unique_ids_list.append(unique_id)
        # now check to see if any have gone missing
        for unique_id in current_player_ids_list:
            if unique_id not in seen_unique_ids_list:
                self.delete_single_player_frame(self.player_frame_dict[unique_id])
                del(self.player_frame_dict[unique_id])

        # Update the current items list
        self.current_items_list = items_list


    def create_single_player_frame(self, data_dict, items_list):
        """

        Given a dict like {'PlayerInfo': {'PlayerName': 'Oakraven', 'UniqueId': '76561198040783597', 'KDA': '0/4/0', 'Cash': '9400', 'TeamId': '0'}}

        This will return a LabelFrame Object with all the sub items for a single player in it

        It will also pack it into the window manger using the parent_frame.

        :param data_dict:
        :return:
        """
        logger.info("Creating Frame: {}".format(data_dict))
        main_frame = tk.LabelFrame(self.parent_frame, text=data_dict['UniqueId'], bd=5)

        main_frame.pack(fill='x')


        main_frame.player_name_label = tk.Label(main_frame, text=data_dict['PlayerName'])
        main_frame.player_name_label.config(font=("Impact", 44))
        main_frame.player_name_label.pack(side='left')

        main_frame.player_kda_label = tk.Label(main_frame, text="K/D/A: {}".format(data_dict['KDA']))
        main_frame.player_kda_label.pack(side='left')

        main_frame.player_cash_label = tk.Label(main_frame, text="Cash: ${}".format(data_dict['Cash']))
        main_frame.player_cash_label.pack(side='left')

        main_frame.player_team_label = tk.Label(main_frame, text="Team: {}".format(data_dict['TeamId']))
        main_frame.player_team_label.pack(side='left')

        # Give money button
        main_frame.give_money_label_frame = tk.LabelFrame(main_frame, text="Give Money", bd=5, borderwidth=3)
        main_frame.give_money_label_frame.pack(side='left')

        main_frame.give_money_label_frame.give_money_button = HoverButton(main_frame.give_money_label_frame, text="+$1000", command=lambda: button_give_money(data_dict['UniqueId'], 1000), padx=5, pady=0)
        main_frame.give_money_label_frame.give_money_button.pack(side="left")
        main_frame.give_money_label_frame.give_more_money_button = HoverButton(main_frame.give_money_label_frame,
                                                                          text="+$5000", command=lambda: button_give_money(data_dict['UniqueId'], 5000), padx=2,
                                                                          pady=0)
        main_frame.give_money_label_frame.give_more_money_button.pack(side="left")

        # Item Selector
        main_frame.give_item_label_frame = tk.LabelFrame(main_frame, text="Give Item", bd=5, borderwidth=3)
        main_frame.give_item_label_frame.pack(side='left')

        main_frame.give_item_label_frame.choice_var = tk.StringVar()

        if len(items_list) > 0:
            main_frame.give_item_label_frame.choice_var.set(items_list[0])


        main_frame.give_item_label_frame.selected_item = ttk.OptionMenu(
            main_frame.give_item_label_frame,
            main_frame.give_item_label_frame.choice_var,
            *items_list
        )
        main_frame.give_item_label_frame.selected_item.configure(width=20)
        main_frame.give_item_label_frame.selected_item.pack(side='left')

        main_frame.give_item_label_frame.give_item_money_button = HoverButton(main_frame.give_item_label_frame,
                                                                               text="Give Item", command=lambda: button_give_item(data_dict['UniqueId'], main_frame.give_item_label_frame.choice_var.get()), padx=2,
                                                                               pady=0)
        main_frame.give_item_label_frame.give_item_money_button.pack(side="left")

        # Kill Player

        # Kick player
        # TBD




        return main_frame


    def update_single_player_frame(self, label_frame_obj, data_dict, items_list):
        """
        Given a player frame and data dict, it will update the contents of that players window

        :param label_frame_obj:
        :param data_dict:
        :return:
        """
        logger.info("updating Frame: {}".format(data_dict))

        label_frame_obj.player_name_label['text'] = data_dict['PlayerName']
        label_frame_obj.player_kda_label['text'] = "K/D/A: {}".format(data_dict['KDA'])
        label_frame_obj.player_cash_label['text'] = "Cash: ${}".format(data_dict['Cash'])
        label_frame_obj.player_team_label['text'] = "Team: {}".format(data_dict['TeamId'])

        # If the items list has changed at all, then we overwrite the list of items
        # if nothing has changed, then we do nothing and leave it where it is.

        if hasattr(self, 'current_items_list'):
            if self.current_items_list != items_list:
                logger.info("Updating items list to: {}".format(items_list))
                label_frame_obj.give_item_label_frame.selected_item.set_menu(*items_list)
                if len(items_list) > 0:
                    label_frame_obj.give_item_label_frame.choice_var.set(items_list[0])

        else:
            logger.info("Initial current_items_list set: {}".format(items_list))
            label_frame_obj.give_item_label_frame.selected_item.set_menu(*items_list)
            if len(items_list) > 0:
                label_frame_obj.give_item_label_frame.choice_var.set(items_list[0])


    def delete_single_player_frame(self, label_frame_obj):
        """
        Given an instance of LabelFrame it will delete it and all the child frames

        :param label_frame_obj:
        :return:
        """
        logger.info("Deleting frame!")

        label_frame_obj.destroy()






class Application(tk.Frame):


    def __init__(self, master=None):
        super().__init__(master, width=1200, height=1200)
        self.master = master
        self.pack()
        self.create_menu()
        self.create_frames()



    def create_menu(self):
        """
        Draws the File Menu

        :return:
        """
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=filemenu)

    def create_frames(self):
        """
        :return:
        """
        # Server Info Frame
        self.server_info_frame = tk.LabelFrame(self, text="Server Info", relief="raised", borderwidth=3)
        self.server_info_frame.place(relx=0, rely=0, relheight=0.3, relwidth=0.5)
        self.create_server_info_items()
        # Server Actions Frame
        self.server_actions_frame = tk.LabelFrame(self, relief="raised", borderwidth=3, text="Server Actions")
        self.server_actions_frame.place(relx=0.5, rely=0, relheight=0.3, relwidth=0.5)
        self.create_server_action_buttons()
        # Server Players Frame
        self.server_players_frame = tk.LabelFrame(self, relief="raised", borderwidth=3, text="Current Players")
        self.server_players_frame.place(relx=0, rely=0.3, relheight=0.7, relwidth=1)
        self.create_player_info_items()


    def create_server_info_items(self):
        """
        Create all the items in the server info, These are a state set of windows that get updated

        :return:
        """
        frame = self.server_info_frame
        # ServerInfo

        frame.server_name_label = tk.Label(frame, text="Server name")
        frame.server_name_label.pack()

        frame.server_map_label = tk.Label(frame, text="Current Map")
        frame.server_map_label.pack()

        frame.server_player_count_label = tk.Label(frame, text="Player Count")
        frame.server_player_count_label.pack()



    def update_server_window(self, server_name, current_map, game_mode, game_status, player_count):
        """

        :param server_name:
        :return:
        """
        # Try look up the map from the values to logger.info a better looking one
        map_values_list = list(MAP_IDS.values())
        if current_map in map_values_list:
            current_map = "{} ({})".format(list(MAP_IDS.keys())[map_values_list.index(current_map)], current_map)
        self.server_info_frame.server_name_label['text'] = "Server: {}".format(server_name)
        self.server_info_frame.server_map_label['text'] = "Map: {} (Mode: {}) (Status: {})".format(current_map, game_mode, game_status)
        self.server_info_frame.server_player_count_label['text'] = "{} Players Connected".format(player_count)

    def create_server_action_buttons(self):
        """

        :return:
        """
        frame = self.server_actions_frame

        # Disconnect
        frame.disconnect_button = HoverButton(frame, text="Disconnect", command=button_hi, padx=5, pady=5)
        frame.disconnect_button.pack()
        # ResetSND
        frame.reset_snd_button = HoverButton(frame, text="Reset SnD", command=button_hi, padx=5, pady=5)
        frame.reset_snd_button.pack()
        # RotateMap
        frame.rotate_map_button = HoverButton(frame, text="Rotate Map", command=button_rotate_map, padx=5, pady=5)
        frame.rotate_map_button.pack()

        # SetLimitedAmmoType {0-2}
        frame.set_limited_ammo_type_frame = tk.LabelFrame(frame, relief="raised", borderwidth=3, text="Set Limited Ammo Type", padx=5, pady=5)
        frame.set_limited_ammo_type_frame.pack()

        frame.set_limited_ammo_type_frame.ammo_spin = tk.Spinbox(frame.set_limited_ammo_type_frame, from_=0, to=2, width=1)
        frame.set_limited_ammo_type_frame.ammo_spin.pack(side="left")

        frame.set_limited_ammo_type_frame.apply_button = HoverButton(frame.set_limited_ammo_type_frame, text="Apply Ammo Limit", command=button_hi, padx=5, pady=5)
        frame.set_limited_ammo_type_frame.apply_button.pack(side="right")

        # SwitchMap {MapName/ID} {GameMode}
        frame.set_switch_map_frame = tk.LabelFrame(frame, relief="raised", borderwidth=3,
                                                          text="Switch Map", padx=5, pady=5)
        frame.set_switch_map_frame.pack(fill='x')

        # Map combo box
        frame.set_switch_map_frame.map_id_combo = ttk.Combobox(frame.set_switch_map_frame, values=list(MAP_IDS.keys()))
        frame.set_switch_map_frame.map_id_combo.configure(width=40)
        frame.set_switch_map_frame.map_id_combo.pack(side='left')

        # Game Mode Choice
        frame.set_switch_map_frame.choice_var = tk.StringVar()
        frame.set_switch_map_frame.choice_var.set(list(GAME_MODES.keys())[0])
        frame.set_switch_map_frame.game_mode = tk.OptionMenu( frame.set_switch_map_frame, frame.set_switch_map_frame.choice_var,
            *(list(GAME_MODES.keys())))
        frame.set_switch_map_frame.game_mode.pack(side='left')
        # Apply button
        frame.set_switch_map_frame.apply_button = HoverButton(frame.set_switch_map_frame,
                                                                     text="Switch Map", command=button_switch_map, padx=5,
                                                                     pady=5)
        frame.set_switch_map_frame.apply_button.pack(side="right")

        # GiveTeamCash {TeamId} {CashAmt}


        # Show list of banned players, allows for unbans

        # Give item to all connected players 



    def get_current_map_selection_values(self):
        """
        GEt the current values in the switch map area of the server actions
        :return:
        """
        return {
            'map':self.server_actions_frame.set_switch_map_frame.map_id_combo.get(),
            'game_mode' : self.server_actions_frame.set_switch_map_frame.choice_var.get()
        }


    def create_player_info_items(self):
        """

        This relies on a server connection, so really this only needs to be populated and updated as part of the main loop


        :return:
        """
        logger.info("Creating player frame...")
        # Create the player window (bit of chaining between fucntions though, this needs self.server_players_frame to exist)
        self.player_frame = PlayerListFrame(self.server_players_frame)



    def update_player_window(self, player_dict):
        """
        Given a list of the players currently connected it will

        :param player_dict:
        :return:
        """
        logger.info(player_dict)

        self.player_frame.update_player_frame(player_dict, self.get_available_items())


    def update_server_items(self, items_list):
        """
        Given a list of item codes the current server supports, this list is used by various menu items


        :param player_dict:
        :return:
        """
        logger.info("Setting server items list as: {}".format(items_list))

        self.current_map_items = items_list

    def get_available_items(self):
        """

        :return:
        """
        return self.current_map_items




async def main_update():

    data = await send_rcon("ServerInfo")

    # Update the server details
    server_name = data.get('ServerInfo',{}).get('ServerName','')
    map_name = data.get('ServerInfo', {}).get('MapLabel', '')
    game_mode = data.get('ServerInfo', {}).get('GameMode', '')
    game_status = data.get('ServerInfo', {}).get('RoundState', '')
    player_count = data.get('ServerInfo', {}).get('PlayerCount', '')
    app.update_server_window(server_name, map_name, game_mode, game_status, player_count)
    # Get the Item list from the server Which shows what items the players are allowed to have here
    data = await send_rcon("ItemList")
    app.update_server_items(data.get("ItemList", list()))
    # Get the player info
    data = await send_rcon("RefreshList")
    players_dict = {k:v for k, v in zip([x['Username'] for x in data['PlayerList']] , [x['UniqueId'] for x in data['PlayerList']]) }
    data = await asyncio.gather(*[send_rcon("InspectPlayer {}".format(x)) for x in list(players_dict.values())])
    app.update_player_window(data)




def update_windows():
    logger.info("Running")
    try:
        asyncio.run(main_update())
    except asyncio.exceptions.TimeoutError as exc:
        logger.info("Server took tool long to respond, Will try again shortly...")
    # Add itself back in to the main loop so it runs again.
    root.after(5000, update_windows)


# Main App container
root = tk.Tk()
root.title("Pavlov RCON Helper")
root.iconbitmap("rcon.ico")



app = Application(master=root)
# testing resize handling
# Bind the action to the root container so it gets the event and then let app object sort out the layout

def handle_configure(event):
    logger.info("window geometry:\n" + root.geometry())
#root.bind("<Configure>", handle_configure)

try:
    root.after(20, update_windows)
    # start the app main loop
    app.mainloop()
except Exception as exc:
    logger.info("Exception occurred: {}".format(exc))