
import platform
import asyncio
import random

import tkinter as tk
from tkinter import ttk

import logging
import sys

import pavlovrcon

###############################################################
# Set up the logger, just push to STDOUT
###############################################################
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

###############################################################
# Main App container
###############################################################
def init_app():
    root = tk.Tk()
    root.title("Pavlov RCON Helper")
    root.iconbitmap("rcon.ico")
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.state('zoomed')
    app = Application(master=root)
    return root, app

###############################################################
# Some helper maps to make things pretty
###############################################################
GAME_MODES = {
    'Seek And Destroy':'SND',
    'Team Death Match': 'TDM',
    'Deathmatch' : 'DM',
    'Gun Game' : 'GUN',
    'Zombie Wave' : 'ZWV',
}

# Map Ids, Keys MUST be Unique as they ge translated into a list!
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
    '--- New' : '', #Spacer
    'station' : 'station',
    'stalingrad' : 'stalingrad',
    'santorini':'santorini',
    'industry' : 'industry',
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
# NOTE: KEYS AN VALUES MUST ALL BE UNIQUE!
KNOWN_ITEM_NAME_MAP = {
    "M249 Light Machine Gun (LMGA)" :"LMGA",
}
# inverted one for lookups
KNOWN_ITEM_NAME_MAP_INV = {v: k for k, v in KNOWN_ITEM_NAME_MAP.items()}

###############################################################
# Fonts
###############################################################

MENU_FONT_SIZE = 14
MENU_FONT_NAME = "Cabin Bold"


###############################################################
# Simple thing to get an Rcon connection, TODO: Make this a decorator
###############################################################
PERSISTED_RCON = None

def get_rcon(use_persisted_connection=False):
    """
    This is responsible for providing an active connection to the desired server connection.

    TODO: Makes this persistent and connection shared instead of creating a new one each time, perhaps merge with send rcon

    :return:
    """
    if use_persisted_connection:
        global PERSISTED_RCON
        if PERSISTED_RCON is None:
            PERSISTED_RCON = pavlovrcon.PavlovRCON("192.168.0.15", 9102, 'password')
        if not PERSISTED_RCON.is_connected():
            PERSISTED_RCON = pavlovrcon.PavlovRCON("192.168.0.15", 9102, 'password')
        return PERSISTED_RCON
    else:
        return pavlovrcon.PavlovRCON("192.168.0.15", 9102, 'password')

# Send a command
async def send_rcon(command, use_persisted_connection=False):

    # if command == "RefreshList":
    #
    #     if random.randint(0,9) > -1:
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
    #
    # elif command == "ServerInfo":
    #     data = {'ServerInfo': {'MapLabel': 'UGC1741218360', 'GameMode': 'ZWV', 'ServerName': 'Great Leap To Zombies', 'RoundState': 'Started', 'PlayerCount': '0/16'}}
    #
    # else:



    rcon_obj = get_rcon(use_persisted_connection)
    data = await rcon_obj.send(command)
    # close the rcon connection
    if not use_persisted_connection:
        await rcon_obj.send("Disconnect")
        await rcon_obj.close()
    logger.info(data)
    return data

###############################################################
# Action button handlers
###############################################################
def button_hi():
    logger.info("Button")

def button_kill_player(unique_id):
    """

    :param unique_id:
    :return:
    """
    logger.info("Kill {}".format(unique_id))
    asyncio.run(send_rcon("Kill {}".format(unique_id)))

def button_kick_player(unique_id):
    """

    :param unique_id:
    :return:
    """
    logger.info("Kick {}".format(unique_id))
    asyncio.run(send_rcon("Kick {}".format(unique_id)))

def button_give_money(unique_id, amount):
    """


    :param unique_id:
    :param amount:
    :return:
    """

    logger.info("Give {} ${}".format(unique_id, amount))
    asyncio.run(send_rcon("GiveCash {} {}".format(unique_id, amount)))

def button_give_players_item(unique_id_list, item):
    """

    :param unique_id_list:
    :param item:
    :return:
    """
    # TODO: Async this call
    for unique_id in unique_id_list:
        button_give_item(unique_id, item)


def button_give_item(unique_id, item):
    """

    :param unique_id:
    :param item:
    :return:
    """

    logger.info("Give {} {}".format(unique_id, item))
    # maybe repalce the human readable one with the mapped one
    replace_item = KNOWN_ITEM_NAME_MAP.get(item, None)
    if replace_item is not None:
        item = replace_item
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

###############################################################
# Class to modify a button so you know when you are hovering
# over it
###############################################################
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

###############################################################
# Tkinter holder and manager for all connected players
###############################################################
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
        main_frame.player_name_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE), width=50)
        main_frame.player_name_label.grid(row=0,column=0, sticky="ns", pady = 5, padx = 5)

        main_frame.player_kda_label = tk.Label(main_frame, text="K/D/A: {}".format(data_dict['KDA']))
        main_frame.player_kda_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE-3))
        main_frame.player_kda_label.grid(row=0,column=1, sticky="nsew", pady = 5, padx = 5)

        main_frame.player_cash_label = tk.Label(main_frame, text="Cash: ${}".format(data_dict['Cash']))
        main_frame.player_cash_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.player_cash_label.grid(row=0,column=2, sticky="nsew", pady = 5, padx = 5)

        main_frame.player_team_label = tk.Label(main_frame, text="Team: {}".format(data_dict['TeamId']))
        main_frame.player_team_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.player_team_label.grid(row=0,column=3, sticky="nsew", pady = 5, padx = 5)

        # Give money button
        main_frame.give_money_label_frame = tk.LabelFrame(main_frame, text="Give Money", bd=5, borderwidth=3)
        main_frame.give_money_label_frame.grid(row=0,column=4, sticky="nsew", pady = 5, padx = 5)

        main_frame.give_money_label_frame.give_money_button = HoverButton(main_frame.give_money_label_frame, text="+$1000", command=lambda: button_give_money(data_dict['UniqueId'], 1000), padx=5, pady=2)
        main_frame.give_money_label_frame.give_money_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.give_money_label_frame.give_money_button.pack(side="left")
        main_frame.give_money_label_frame.give_more_money_button = HoverButton(main_frame.give_money_label_frame,
                                                                          text="+$5000", command=lambda: button_give_money(data_dict['UniqueId'], 5000), padx=2,
                                                                          pady=2)
        main_frame.give_money_label_frame.give_more_money_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.give_money_label_frame.give_more_money_button.pack(side="left")

        # Item Selector
        main_frame.give_item_label_frame = tk.LabelFrame(main_frame, text="Give Item", bd=5, borderwidth=3)
        main_frame.give_item_label_frame.grid(row=0,column=5, sticky="nsew", pady = 5, padx = 5)

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

        main_frame.give_item_label_frame.give_item_button = HoverButton(main_frame.give_item_label_frame,
                                                                               text="Give Item", command=lambda: button_give_item(data_dict['UniqueId'], main_frame.give_item_label_frame.choice_var.get()), padx=2,
                                                                               pady=0)
        main_frame.give_item_label_frame.give_item_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.give_item_label_frame.give_item_button.pack(side="left")

        # Kill Player
        main_frame.kill_button = HoverButton(main_frame, text="Kill Player", command=lambda: button_kill_player(data_dict['UniqueId']), padx=5, pady=0)
        main_frame.kill_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.kill_button.grid(row=0,column=6, sticky="nsew", pady = 5, padx = 5)

        # Kick player
        main_frame.kick_button = HoverButton(main_frame, text="Kick Player", command=lambda: button_kick_player(data_dict['UniqueId']), padx=5, pady=0)
        main_frame.kick_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.kick_button.grid(row=0,column=7, sticky="nsew", pady = 5, padx = 5)

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




###############################################################
# Main Application Frame
###############################################################
class Application(tk.Frame):


    def __init__(self, master=None):
        super().__init__(master, width=master.winfo_screenwidth(), height=master.winfo_screenheight())
        self.master = master
        self.pack(fill='both')
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
        frame.server_name_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE+2))
        frame.server_name_label.pack(fill=tk.BOTH, expand=tk.YES)

        frame.server_map_label = tk.Label(frame, text="Current Map")
        frame.server_map_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.server_map_label.pack(fill=tk.BOTH, expand=tk.YES)

        frame.server_player_count_label = tk.Label(frame, text="Player Count")
        frame.server_player_count_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE+2))
        frame.server_player_count_label.pack(fill=tk.BOTH, expand=tk.YES)



    def update_server_window(self, server_name, current_map, game_mode, game_status, player_count):
        """

        :param server_name:
        :return:
        """
        # Try look up the map from the values to logger.info a better looking one
        map_values_list = list(MAP_IDS.values())
        if current_map in map_values_list:
            current_map = "{} - {}".format(list(MAP_IDS.keys())[map_values_list.index(current_map)], current_map)
        self.server_info_frame.server_name_label['text'] = "Server: {}".format(server_name)


        self.server_info_frame.server_map_label['text'] = "Map: {}\nMode: {}\nStatus: {}".format(current_map, game_mode, game_status)
        self.server_info_frame.server_player_count_label['text'] = "{} Players Connected".format(player_count)

    def create_server_action_buttons(self):
        """

        :return:
        """
        frame = self.server_actions_frame

        # Disconnect (COmmented out as we don't really need this at the moment)
        # frame.disconnect_button = HoverButton(frame, text="Disconnect RCON", command=button_hi, padx=5, pady=2)
        # frame.disconnect_button.config(font=("Helvetica", MENU_FONT_SIZE))
        # frame.disconnect_button.pack(fill='x')
        # ResetSND
        frame.reset_snd_button = HoverButton(frame, text="Reset Seek and Destroy", command=button_hi, padx=5, pady=2)
        frame.reset_snd_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.reset_snd_button.grid(row=0,column=0, sticky="nsew", pady = 5, padx = 5)
        # RotateMap
        frame.rotate_map_button = HoverButton(frame, text="Rotate Map", command=button_rotate_map, padx=5, pady=2)
        frame.rotate_map_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.rotate_map_button.grid(row=1,column=0,columnspan=2, sticky="nsew", pady = 5, padx = 5)

        # SetLimitedAmmoType {0-2}
        frame.set_limited_ammo_type_frame = tk.LabelFrame(frame, relief="raised", borderwidth=3, text="Set Limited Ammo Type", padx=5, pady=2)
        frame.set_limited_ammo_type_frame.grid(row=0,column=1, sticky="nsew", pady = 5, padx = 5)

        frame.set_limited_ammo_type_frame.ammo_spin = tk.Spinbox(frame.set_limited_ammo_type_frame, from_=0, to=2, width=2)
        frame.set_limited_ammo_type_frame.ammo_spin.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.set_limited_ammo_type_frame.ammo_spin.pack(side="left")

        frame.set_limited_ammo_type_frame.apply_button = HoverButton(frame.set_limited_ammo_type_frame, text="Apply Ammo Limit", command=button_hi, padx=5, pady=2)
        frame.set_limited_ammo_type_frame.apply_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.set_limited_ammo_type_frame.apply_button.pack(fill="x")

        # SwitchMap {MapName/ID} {GameMode}
        frame.set_switch_map_frame = tk.LabelFrame(frame, relief="raised", borderwidth=3,
                                                          text="Switch Map", padx=5, pady=2)
        frame.set_switch_map_frame.grid(row=2,column=0, columnspan=2,sticky="nsew", pady = 5, padx = 5)

        # Map combo box
        frame.set_switch_map_frame.map_id_combo = ttk.Combobox(frame.set_switch_map_frame, values=list(MAP_IDS.keys()))
        frame.set_switch_map_frame.map_id_combo.configure(width=40)
        frame.set_switch_map_frame.map_id_combo.pack(side='left')

        # Game Mode Choice
        frame.set_switch_map_frame.choice_var = tk.StringVar()
        frame.set_switch_map_frame.choice_var.set(list(GAME_MODES.keys())[0])
        frame.set_switch_map_frame.game_mode = tk.OptionMenu( frame.set_switch_map_frame, frame.set_switch_map_frame.choice_var,
            *(list(GAME_MODES.keys())))
        frame.set_switch_map_frame.game_mode.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.set_switch_map_frame.game_mode.pack(side='left')
        # Apply button
        frame.set_switch_map_frame.apply_button = HoverButton(frame.set_switch_map_frame,
                                                                     text="Switch Map", command=button_switch_map, padx=5,
                                                                     pady=2)
        frame.set_switch_map_frame.apply_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.set_switch_map_frame.apply_button.pack(side="right")

        # GiveTeamCash {TeamId} {CashAmt}


        # Show list of banned players, allows for unbans

        # Give item to all connected players
        frame.give_all_players_item_frame = tk.LabelFrame(frame, relief="raised", borderwidth=3,
                                                          text="Give all players item", padx=5, pady=2)
        frame.give_all_players_item_frame.grid(row=3,column=0, columnspan=2, sticky="nsew", pady = 5, padx = 5)

        frame.give_all_players_item_frame.choice_var = tk.StringVar()

        items_list = ["None", ]
        frame.give_all_players_item_frame.choice_var.set("")
        if hasattr(self, 'current_map_items'):
            items_list = self.current_map_items
            frame.give_all_players_item_frame.choice_var.set(items_list[0])

        frame.give_all_players_item_frame.item_selection = ttk.OptionMenu(frame.give_all_players_item_frame,
                                                             frame.give_all_players_item_frame.choice_var,
                                                             *items_list)
        frame.give_all_players_item_frame.item_selection.configure(width=20)
        frame.give_all_players_item_frame.item_selection.pack(side="left")
        frame.give_all_players_item_frame.apply_button = HoverButton(frame.give_all_players_item_frame,
                                                                text="Give this to all players",
                                                                command=lambda: button_give_players_item(self.all_player_ids,
                                                                      frame.give_all_players_item_frame.choice_var.get()),
                                                                padx=5,
                                                                pady=2)
        frame.give_all_players_item_frame.apply_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.give_all_players_item_frame.apply_button.pack(fill="x")




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



    def update_player_window(self, player_list_dict, max_players):
        """
        Given a list of the players currently connected it will

        :param player_dict:
        :param max_players: Int for th emax number (used to format the window

        :return:
        """
        logger.info("update_player_window: {}".format(player_list_dict))


        self.all_player_ids = [ int(x['PlayerInfo']['UniqueId']) for x in player_list_dict]
        logger.info("All player IDS: {}".format(self.all_player_ids))


        self.player_frame.update_player_frame(player_list_dict, self.get_available_items())


    def update_server_items(self, items_list):
        """
        Given a list of item codes the current server supports, this list is used by various menu items


        :param player_dict:
        :return:
        """
        logger.info("Setting server items list as: {}".format(items_list))
        new_item_list = []
        known_item_keys = list(KNOWN_ITEM_NAME_MAP_INV.keys())
        for item in items_list:
            if item in known_item_keys:
                new_item_list.append(KNOWN_ITEM_NAME_MAP_INV[item])
                logger.info("Replaced Items '{}' with '{}' for readability".format(item, KNOWN_ITEM_NAME_MAP_INV[item]))
            else:
                new_item_list.append(item)
        new_item_list.sort()

        list_is_new = False

        if hasattr(self, "current_map_items"):
            if new_item_list !=  self.current_map_items:
                list_is_new = True
        else:
            list_is_new = True

        self.current_map_items = new_item_list

        # Now need to update the server actions to include the new items list
        if list_is_new and len(new_item_list) >0:
            self.server_actions_frame.give_all_players_item_frame.item_selection.set_menu(*new_item_list)
            self.server_actions_frame.give_all_players_item_frame.choice_var.set(new_item_list[0])


    def get_available_items(self):
        """

        :return:
        """
        return self.current_map_items


###############################################################
# Functions to be used to update the server contents
###############################################################
async def main_update():

    data = await send_rcon("ServerInfo", use_persisted_connection=False)

    # Update the server details
    server_name = data.get('ServerInfo',{}).get('ServerName','')
    map_name = data.get('ServerInfo', {}).get('MapLabel', '')
    game_mode = data.get('ServerInfo', {}).get('GameMode', '')
    game_status = data.get('ServerInfo', {}).get('RoundState', '')
    player_count = data.get('ServerInfo', {}).get('PlayerCount', '')
    max_players = int(player_count.split("/")[1])
    app.update_server_window(server_name, map_name, game_mode, game_status, player_count)
    # Get the Item list from the server Which shows what items the players are allowed to have here
    data = await send_rcon("ItemList", use_persisted_connection=False)
    app.update_server_items(data.get("ItemList", list()))
    # Get the player info
    data = await send_rcon("RefreshList", use_persisted_connection=False)
    players_dict = {k:v for k, v in zip([x['Username'] for x in data['PlayerList']] , [x['UniqueId'] for x in data['PlayerList']]) }
    data = await asyncio.gather(*[send_rcon("InspectPlayer {}".format(x)) for x in list(players_dict.values())])
    app.update_player_window(data, max_players)




def update_windows():
    logger.info("Running")
    try:
        asyncio.run(main_update())
    except asyncio.exceptions.TimeoutError as exc:
        logger.info("Server took tool long to respond, Will try again shortly...")
    # Add itself back in to the main loop so it runs again.
    root.after(5000, update_windows)


###############################################################
# Application kick off stuff
###############################################################
root, app = init_app()



# testing resize handling
# Bind the action to the root container so it gets the event and then let app object sort out the layout

def handle_configure(event):
    logger.info("window geometry:\n" + root.geometry())
#root.bind("<Configure>", handle_configure)


# Now that i have the bulk of the windows working
# I need to do the following
# 1. Handle connects and disconnects
# 2. Allow the user to specify different connection creds (via command line, config file or from within the app)
try:
    root.after(20, update_windows)
    # start the app main loop
    app.mainloop()
except Exception as exc:
    logger.info("Exception occurred: {}".format(exc))