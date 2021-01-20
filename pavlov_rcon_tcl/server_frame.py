"""
This class is for a single server connection

"""
import asyncio
import tkinter as tk
from tkinter import ttk

import logging
logger = logging.getLogger(__name__)

from widgets import HoverButton
from rcon_connector import send_rcon
from playerlist_frame import PlayerListFrame

from config_items import (MENU_FONT_SIZE, MENU_FONT_NAME)
from items_list import (KNOWN_ITEM_NAME_MAP, KNOWN_ITEM_NAME_MAP_INV)
from games_modes import GAME_MODES
from maps_list import MAP_IDS



class SingleServerFrame(tk.Frame):


    def __init__(self, master=None, rcon_host=None, rcon_port=None, rcon_pass=None):
        super().__init__(master, width=master.winfo_screenwidth(), height=master.winfo_screenheight())
        self.master = master
        self.rcon_host = rcon_host
        self.rcon_port = rcon_port
        self.rcon_pass = rcon_pass

        self.pack(fill='both')
        self.create_frames()

    def get_server_creds(self):
        """

        :return:
        """
        return {
            'rcon_host' : self.rcon_host,
            'rcon_port' : self.rcon_port,
            'rcon_pass' : self.rcon_pass
        }

    async def exec_rcon_update(self):
        """
        Method that triggers the update of the current server frame and all its components

        TODO: Add some visual flag to mark connection issues

        :return:
        """

        server_creds = self.get_server_creds()

        data = await send_rcon("ServerInfo", **server_creds, use_persisted_connection=False)

        max_players = 0  # Init this for further down

        if data is not None:
            # Update the server details
            server_name = data.get('ServerInfo', {}).get('ServerName', '')
            map_name = data.get('ServerInfo', {}).get('MapLabel', '')
            game_mode = data.get('ServerInfo', {}).get('GameMode', '')
            game_status = data.get('ServerInfo', {}).get('RoundState', '')
            player_count = data.get('ServerInfo', {}).get('PlayerCount', '')
            teams_status = "{}".format(data.get('ServerInfo', {}).get('Teams', ''))
            teams_0_score = "{}".format(data.get('ServerInfo', {}).get('Team0Score', ''))
            teams_1_score = "{}".format(data.get('ServerInfo', {}).get('Team1Score', ''))
            max_players = int(player_count.split("/")[1])
            self.update_server_window(server_name, map_name, game_mode, game_status, player_count, teams_status,
                                     teams_0_score, teams_1_score)
        else:
            self.update_server_window_for_error()
        # Get the Item list from the server Which shows what items the players are allowed to have here
        data = await send_rcon("ItemList", **server_creds, use_persisted_connection=False)
        if data is not None:
            self.update_server_items(data.get("ItemList", list()))
        # Get the player info
        data = await send_rcon("RefreshList", **server_creds, use_persisted_connection=False)
        if data is not None:
            players_dict = {k: v for k, v in zip([x['Username'] for x in data['PlayerList']],
                                                 [x['UniqueId'] for x in data['PlayerList']])}
        if data is not None:
            data = await asyncio.gather(
                *[send_rcon("InspectPlayer {}".format(x), **server_creds) for x in list(players_dict.values())])
            self.update_player_window(data, max_players)




    def create_frames(self):
        """
        :return:
        """
        # Server Info Frame
        self.server_info_frame = tk.LabelFrame(self, text="Server Info", relief="raised", borderwidth=3)
        self.server_info_frame.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE-3))
        self.server_info_frame.place(relx=0, rely=0, relheight=0.3, relwidth=0.35)
        self.create_server_info_items()
        # Server Actions Frame
        self.server_actions_frame = tk.LabelFrame(self, relief="raised", borderwidth=3, text="Server Actions")
        self.server_actions_frame.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE-3))
        self.server_actions_frame.place(relx=0.35, rely=0, relheight=0.3, relwidth=0.65)
        self.create_server_action_buttons()
        # Server Players Frame
        self.server_players_frame = tk.LabelFrame(self, relief="raised", borderwidth=3, text="Current Players")
        self.server_players_frame.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE-3))
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

        frame.server_teams_label = tk.Label(frame, text="Teams Status")
        frame.server_teams_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.server_teams_label.pack(fill=tk.BOTH, expand=tk.YES)

        frame.server_player_count_label = tk.Label(frame, text="Player Count")
        frame.server_player_count_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE+2))
        frame.server_player_count_label.pack(fill=tk.BOTH, expand=tk.YES)



    def update_server_window(self, server_name, current_map, game_mode, game_status, player_count, teams_status, teams_0_score, teams_1_score ):
        """

        :param server_name:
        :return:
        """
        # Try look up the map from the values to convert it an easier to read one. 
        map_values_list = list(MAP_IDS.values())
        if current_map in map_values_list:
            current_map = "{} - {}".format(list(MAP_IDS.keys())[map_values_list.index(current_map)], current_map)
        self.server_info_frame.server_name_label['text'] = "Server: {}".format(server_name)

        self.server_info_frame.server_teams_label['text'] = "Teams: {}\nTeam 0 Score: {}\nTeam 1 Score:{}".format(teams_status, teams_0_score, teams_0_score)

        self.server_info_frame.server_map_label['text'] = "Map: {}\nMode: {}\nStatus: {}".format(current_map, game_mode, game_status)
        self.server_info_frame.server_player_count_label['text'] = "{} Players Connected".format(player_count)

    def update_server_window_for_error(self):
        """
        Call this when there is a connection problem and it will mark the Server info as disconnected

        :return:
        """
        self.server_info_frame.server_name_label['text'] = "ERROR: Unable to connect to server listed in server.json - {}:{}".format(self.rcon_host, self.rcon_port)
        self.server_info_frame.server_map_label['text'] = "Please see logs."
        self.server_info_frame.server_teams_label['text'] = ""
        self.server_info_frame.server_player_count_label['text'] = "Retrying shortly..."

    def create_server_action_buttons(self):
        """

        :return:
        """
        frame = self.server_actions_frame

        # Disconnect (COmmented out as we don't really need this at the moment)
        # Perhaps use this to disconnect and remove a server from a multi server config?
        # frame.disconnect_button = HoverButton(frame, text="Disconnect RCON", command=button_hi, padx=5, pady=2)
        # frame.disconnect_button.config(font=("Helvetica", MENU_FONT_SIZE))
        # frame.disconnect_button.pack(fill='x')

        # ResetSND
        frame.reset_snd_button = HoverButton(frame, text="Reset Seek and Destroy",
                                             command=lambda: self.master.loop.create_task(self.button_reset_snd()),
                                             padx=5, pady=2)
        frame.reset_snd_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.reset_snd_button.grid(row=0,column=0, sticky="nsew", pady = 5, padx = 5)
        # RotateMap
        frame.rotate_map_button = HoverButton(frame, text="Rotate Map",
                                              command=lambda: self.master.loop.create_task(self.button_rotate_map()),
                                              padx=5, pady=2)
        frame.rotate_map_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.rotate_map_button.grid(row=1,column=0,columnspan=2, sticky="nsew", pady = 5, padx = 5)

        # SetLimitedAmmoType {0-2}
        frame.set_limited_ammo_type_frame = tk.LabelFrame(frame, relief="raised", borderwidth=3, text="Set Limited Ammo Type", padx=5, pady=2)
        frame.set_limited_ammo_type_frame.grid(row=0,column=1, sticky="nsew", pady = 5, padx = 5)

        frame.set_limited_ammo_type_frame.ammo_spin = tk.Spinbox(frame.set_limited_ammo_type_frame, from_=0, to=2, width=2)
        frame.set_limited_ammo_type_frame.ammo_spin.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.set_limited_ammo_type_frame.ammo_spin.pack(side="left")

        frame.set_limited_ammo_type_frame.apply_button = HoverButton(frame.set_limited_ammo_type_frame,
                                                                     text="Apply Ammo Limit",
                                                                     command=lambda: self.master.loop.create_task(self.button_set_ammo_limit_type(
                                                                         frame.set_limited_ammo_type_frame.ammo_spin.get())),
                                                                     padx=5, pady=2)
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
                                                              text="Switch Map", command=lambda: self.master.loop.create_task(self.button_switch_map(
                                                                    self.get_current_map_selection_values())), padx=5,
                                                              pady=2)
        frame.set_switch_map_frame.apply_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.set_switch_map_frame.apply_button.pack(side="right")

        # GiveTeamCash {TeamId} {CashAmt}
        frame.give_team_cash_frame = tk.LabelFrame(frame, relief="raised", borderwidth=3,
                                                          text="Give Team Cash", padx=5, pady=2)
        frame.give_team_cash_frame.grid(row=1, column=2, columnspan=2, sticky="nsew", pady=5, padx=5)

        frame.give_team_cash_frame.team_0_1000_button = HoverButton(frame.give_team_cash_frame, button_colour="lime green", text="Team 0\n+$1000",
                                                                    command=lambda: self.master.loop.create_task(self.button_give_team_cash(0, 1000)),
                                                                    padx=15,
                                                                    pady=2)
        frame.give_team_cash_frame.team_0_1000_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.give_team_cash_frame.team_0_1000_button.pack(side="left", fill='x', expand=True)

        frame.give_team_cash_frame.team_1_1000_button = HoverButton(frame.give_team_cash_frame, button_colour="lime green", text="Team 1\n+$1000",
                                                                    command=lambda: self.master.loop.create_task(self.button_give_team_cash(1, 1000)),
                                                                    padx=15,
                                                                    pady=2)
        frame.give_team_cash_frame.team_1_1000_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.give_team_cash_frame.team_1_1000_button.pack(side="left", fill='x', expand=True)

        # Show list of banned players, allows for unbans # TODO

        # Give item to all connected players
        frame.give_all_players_item_frame = tk.LabelFrame(frame, relief="raised", borderwidth=3,
                                                          text="Give all players item", padx=5, pady=2)
        frame.give_all_players_item_frame.grid(row=0,column=2, columnspan=2, sticky="nsew", pady = 5, padx = 5)

        frame.give_all_players_item_frame.choice_var = tk.StringVar()

        items_list = []
        frame.give_all_players_item_frame.choice_var.set("")
        selected_give_item = ""
        if hasattr(self, 'current_map_items'):
            items_list = self.current_map_items
            frame.give_all_players_item_frame.choice_var.set(items_list[0])
            selected_give_item = "{}".format(items_list[0])

        frame.give_all_players_item_frame.item_selection = ttk.OptionMenu(
                                                                    frame.give_all_players_item_frame,
                                                                    frame.give_all_players_item_frame.choice_var,
                                                                    selected_give_item, *items_list)
        frame.give_all_players_item_frame.item_selection.configure(width=30)
        frame.give_all_players_item_frame.item_selection.pack(side="left")
        frame.give_all_players_item_frame.apply_button = HoverButton(frame.give_all_players_item_frame,
                                                                text="Give this to all players",
                                                                command=lambda: self.master.loop.create_task(self.button_give_players_item(self.all_player_ids,
                                                                      frame.give_all_players_item_frame.choice_var.get())),
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
        self.player_frame = PlayerListFrame(self.server_players_frame, self.rcon_host, self.rcon_port, self.rcon_pass, loop=self.master.loop )


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
            self.server_actions_frame.give_all_players_item_frame.item_selection.set_menu(new_item_list[0] ,*new_item_list)
            self.server_actions_frame.give_all_players_item_frame.choice_var.set(new_item_list[0])


    def get_available_items(self):
        """

        :return:
        """
        if hasattr(self, "current_map_items"):
            return self.current_map_items
        else:
            return list()

    async def button_rotate_map(self):
        """

        :return:
        """
        await send_rcon("RotateMap", self.rcon_host, self.rcon_port, self.rcon_pass)

    async def button_give_team_cash(self, team_id, cash_amount):
        """

        :param team_id:
        :param cash_amount:
        :return:
        """
        logger.info("GiveTeamCash {} {}".format(team_id, cash_amount))
        await send_rcon("GiveTeamCash {} {}".format(team_id, cash_amount), self.rcon_host, self.rcon_port, self.rcon_pass)

    async def button_reset_snd(self):
        """
        ResetSND

        :return:
        """
        await send_rcon("ResetSND", self.rcon_host, self.rcon_port, self.rcon_pass)

    async def button_set_ammo_limit_type(self, ammo_limit_type):
        """

        SetLimitedAmmoType AmmoType

        :param ammo_limit:
        :return:
        """
        logger.info("SetLimitedAmmoType {}".format(ammo_limit_type))
        await send_rcon("SetLimitedAmmoType {}".format(ammo_limit_type),self.rcon_host, self.rcon_port, self.rcon_pass)

    async def button_switch_map(self, selections):
        """
        Calling this inspects the apps state for the selections

        :return:
        """
        logger.info("SwitchMap!")
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
        await send_rcon(switch_str, self.rcon_host, self.rcon_port, self.rcon_pass)

    async def button_give_players_item(self, unique_id_list, item):
        """

        TODO: Make this use the entries in the player frame

        :param unique_id_list:
        :param item:
        :return:
        """
        # Check to see if the player frame has been drawn
        if hasattr(self, "player_frame"):
            # This executes all the calls to give players this item in parallel. Make it rain guns!
            await asyncio.gather(*[self.player_frame.button_give_item(unique_id, item) for unique_id in unique_id_list])

