"""
This is for the section where all the player details live for a single server.

This is imported by SingleServerFrame and used from within it


"""
import webbrowser

import tkinter as tk

from tkinter import ttk

from widgets import HoverButton
from rcon_connector import send_rcon

from items_list import (KNOWN_ITEM_NAME_MAP, KNOWN_ITEM_NAME_MAP_INV)
from skins_list import SKINS_LIST
from config_items import (MENU_FONT_SIZE, MENU_FONT_NAME)

import logging
logger = logging.getLogger(__name__)

class PlayerListFrame:

    def __init__(self, parent_frame, rcon_host, rcon_port, rcon_pass, loop):
        """

        :param parent_frame:
        """
        self.parent_frame = parent_frame # The LabelFrame that contains all of this

        self.player_frame_dict = dict()
        self.loop = loop

        # Pass this in here otherwise we just have to keep reaching back the parent
        self.rcon_host = rcon_host
        self.rcon_port = rcon_port
        self.rcon_pass = rcon_pass

    def get_players_and_teams(self):
        """
        return a list of the tuples that are (UniqueID, TeamID)

        :return:
        """
        ret_list = []
        for unique_id, label_frame_obj in self.player_frame_dict.items():
            team_id = None
            if hasattr(label_frame_obj, "player_team_number"):
                team_id = label_frame_obj.player_team_number
            ret_list.append((unique_id,team_id))
        return ret_list

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
            if refresh_item_dict is None:
                logger.warning("Got None data for a player.. Skipping")
                continue
            player_info = refresh_item_dict.get('PlayerInfo', None)
            if player_info is None:
                logger.warning("Got None data for a player_info.. Skipping")
                continue
            unique_id = player_info.get('UniqueId', None)
            if unique_id is None:
                logger.warning("Got null data for a player.. Skipping")
                continue
            if unique_id in seen_unique_ids_list:
                # Somehow we've got 2+ players steam ids that are exactly the same...
                logger.warning("Saw Unique_ID {} 2+ times in a player list, skipping this player...")
            else:
                if unique_id in current_player_ids_list:

                    player_label_frame_obj = self.player_frame_dict.get(unique_id, None)
                    if player_label_frame_obj is not None:
                        self.update_single_player_frame(player_label_frame_obj, player_info, items_list)
                    else:
                        logger.warning("Tried to update a player frame that has been deleted. Skipping ")
                else:
                    self.player_frame_dict[unique_id] = self.create_single_player_frame(player_info, items_list)
            # Mark this as seen
            seen_unique_ids_list.append(unique_id)
        # now check to see if any have gone missing
        for unique_id in current_player_ids_list:
            if unique_id not in seen_unique_ids_list:
                player_label_frame_obj = self.player_frame_dict.get(unique_id, None)
                if player_label_frame_obj is not None:
                    self.delete_single_player_frame(self.player_frame_dict[unique_id])
                    del(self.player_frame_dict[unique_id])
                else:
                    logger.warning("Tried to delete a player frame that has been already deleted. Skipping ")
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
        main_frame = tk.LabelFrame(self.parent_frame.scrollable_frame, text="{} (Click name to view profile in browser)".format(data_dict['UniqueId']), bd=5)

        main_frame.pack(fill='x', expand=tk.YES)

        main_frame.grid_rowconfigure(0, weight=1) # only 1 row, and it can expand as needed

        main_frame.player_name_label = HoverButton(main_frame,
                                                   text=data_dict['PlayerName'],
                                                   command=lambda: self.loop.create_task(self.view_player_profile(
                                                       data_dict['UniqueId'])), padx=5, pady=2
                                        )




        main_frame.player_name_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE), width=30)
        main_frame.player_name_label.grid(row=0,column=0, sticky="nesw", pady = 2, padx = 5)

        main_frame.grid_columnconfigure(0, weight=1) #We want player name to expand, default weight is 0

        kills, deaths, assists = data_dict.get('KDA', "0/0/0").split("/")

        main_frame.player_kda_label = tk.Label(
            main_frame, text="Kills: {}\nDeaths: {}\nAssists: {}".format(kills, deaths, assists)
        )
        main_frame.player_kda_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE-3), width=20)
        main_frame.player_kda_label.grid(row=0,column=1, sticky="nesw", pady=2, padx = 5)

        main_frame.player_cash_label = tk.Label(main_frame, text="Cash: ${}\nScore: {}".format(data_dict['Cash'],
                                                                                               data_dict['Score']))
        main_frame.player_cash_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3), width=20)
        main_frame.player_cash_label.grid(row=0,column=2, sticky="nesw", pady = 2, padx = 5)

        main_frame.player_team_label = tk.Label(main_frame, text="Team: {}".format(data_dict['TeamId'].replace("0", "Blue").replace("1", "Red")))
        main_frame.player_team_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.player_team_label.grid(row=0,column=3, sticky="nesw", pady = 2, padx = 5)

        # Switch teams
        main_frame.move_player_label_frame = tk.LabelFrame(main_frame, text="Switch Team", bd=5, borderwidth=3)
        main_frame.move_player_label_frame.grid(row=0, column=4, sticky="nesw", pady=2, padx=5)

        main_frame.move_player_label_frame.team_0_button = HoverButton(main_frame.move_player_label_frame, text="Blue",
                                                                       command=lambda: self.loop.create_task(self.button_switch_team(
                                                                           data_dict['UniqueId'], 0)), padx=5, pady=2)
        main_frame.move_player_label_frame.team_0_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.move_player_label_frame.team_0_button.pack(side="left", fill=tk.BOTH, expand=tk.YES)
        main_frame.move_player_label_frame.team_1_button = HoverButton(main_frame.move_player_label_frame, text="Red",
                                                                       command=lambda: self.loop.create_task(self.button_switch_team(
                                                                           data_dict['UniqueId'], 1)), padx=5, pady=2)
        main_frame.move_player_label_frame.team_1_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.move_player_label_frame.team_1_button.pack(side="left", fill=tk.BOTH, expand=tk.YES)

        # Give money button
        main_frame.give_money_label_frame = tk.LabelFrame(main_frame, text="Give Money", bd=5, borderwidth=3)
        main_frame.give_money_label_frame.grid(row=0, column=5, sticky="nesw", pady=2, padx=5)
        main_frame.grid_columnconfigure(5, weight=1)  # We want give money  to expand, default weight is 0

        main_frame.give_money_label_frame.give_money_button = HoverButton(main_frame.give_money_label_frame, button_colour="lime green",
                                                                          text="+$1000",
                                                                          command=lambda: self.loop.create_task(self.button_give_money(
                                                                              data_dict['UniqueId'], 1000)), padx=5,
                                                                          pady=2)
        main_frame.give_money_label_frame.give_money_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.give_money_label_frame.give_money_button.pack(side="left", fill=tk.BOTH, expand=tk.YES)
        main_frame.give_money_label_frame.give_more_money_button = HoverButton(main_frame.give_money_label_frame, button_colour="lime green",
                                                                               text="+$5000",
                                                                               command=lambda: self.loop.create_task(self.button_give_money(
                                                                                   data_dict['UniqueId'], 5000)), padx=2,
                                                                               pady=2)
        main_frame.give_money_label_frame.give_more_money_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.give_money_label_frame.give_more_money_button.pack(side="left", fill=tk.BOTH, expand=tk.YES)

        # Item Selector
        main_frame.give_item_label_frame = tk.LabelFrame(main_frame, text="Give Item", bd=5, borderwidth=3)
        main_frame.give_item_label_frame.grid(row=0,column=6, sticky="nesw", pady = 2, padx = 5)
        main_frame.grid_columnconfigure(6, weight=1)  # We want give item to expand, default weight is 0

        main_frame.give_item_label_frame.choice_var = tk.StringVar()

        selected_give_item = ''
        if len(items_list) > 0:
            main_frame.give_item_label_frame.choice_var.set(items_list[0])
            selected_give_item = "{}".format(items_list[0])


        main_frame.give_item_label_frame.selected_item = ttk.OptionMenu(
            main_frame.give_item_label_frame,
            main_frame.give_item_label_frame.choice_var,
            selected_give_item, *items_list, style = 'player_frame.TMenubutton'
        )
        main_frame.give_item_label_frame.selected_item.configure(width=20)
        main_frame.give_item_label_frame.selected_item["menu"].configure(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        main_frame.give_item_label_frame.selected_item.pack(side='left', fill=tk.BOTH, expand=tk.YES)

        main_frame.give_item_label_frame.give_item_button = HoverButton(main_frame.give_item_label_frame,
                                                                        text="Give Item",
                                                                        command=lambda: self.loop.create_task(self.button_give_item(
                                                                            data_dict['UniqueId'],
                                                                            main_frame.give_item_label_frame.choice_var.get())),
                                                                        padx=2,
                                                                        pady=0)
        main_frame.give_item_label_frame.give_item_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.give_item_label_frame.give_item_button.pack(side="left", fill=tk.BOTH, expand=tk.YES)

        # Switch Skin
        main_frame.switch_skin_label_frame = tk.LabelFrame(main_frame, text="Set Player Skin", bd=5, borderwidth=3)
        main_frame.switch_skin_label_frame.grid(row=0, column=7, sticky="nesw", pady=2, padx=5)
        main_frame.grid_columnconfigure(7, weight=1)  # We want switch skin  to expand, default weight is 0

        main_frame.switch_skin_label_frame.choice_var = tk.StringVar()
        if len(SKINS_LIST) > 0:
            main_frame.switch_skin_label_frame.choice_var.set(SKINS_LIST[0])

        main_frame.switch_skin_label_frame.selected_item = ttk.OptionMenu(
            main_frame.switch_skin_label_frame,
            main_frame.switch_skin_label_frame.choice_var,
            SKINS_LIST[0], *SKINS_LIST, style = 'player_frame.TMenubutton'
        )
        main_frame.switch_skin_label_frame.selected_item.configure(width=10)
        main_frame.switch_skin_label_frame.selected_item["menu"].configure(font=(MENU_FONT_NAME, MENU_FONT_SIZE))

        main_frame.switch_skin_label_frame.selected_item.pack(side='left', fill=tk.BOTH, expand=tk.YES)

        main_frame.switch_skin_label_frame.give_item_button = HoverButton(main_frame.switch_skin_label_frame,
                                                                          text="Switch!",
                                                                          command=lambda: self.loop.create_task(self.button_switch_skins(
                                                                              data_dict['UniqueId'],
                                                                              main_frame.switch_skin_label_frame.choice_var.get())),
                                                                          padx=2,
                                                                          pady=0)
        main_frame.switch_skin_label_frame.give_item_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.switch_skin_label_frame.give_item_button.pack(side="left", fill=tk.BOTH, expand=tk.YES)

        # Kill Player
        main_frame.kill_button = HoverButton(main_frame, text="Kill Player", button_colour="pale green",
                                             command=lambda: self.loop.create_task(self.button_kill_player(data_dict['UniqueId'])), padx=5, pady=0)
        main_frame.kill_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.kill_button.grid(row=0, column=8, sticky="nesw", pady=2, padx=5)

        # Kick player
        main_frame.kick_button = HoverButton(main_frame, text="Kick Player", button_colour="orange",
                                             command=lambda: self.loop.create_task(self.button_kick_player(data_dict['UniqueId'])), padx=5, pady=0)
        main_frame.kick_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.kick_button.grid(row=0, column=9, sticky="nesw", pady=2, padx=5)

        # Ban player
        main_frame.ban_button = HoverButton(main_frame, text="BAN PLAYER", button_colour="red",
                                            command=lambda: self.loop.create_task(self.button_ban_player(data_dict['UniqueId'])), padx=5, pady=0)
        main_frame.ban_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 5))
        main_frame.ban_button.grid(row=0, column=10, sticky="nesw", pady=2, padx=5)


        return main_frame


    def update_single_player_frame(self, label_frame_obj, data_dict, items_list):
        """
        Given a player frame and data dict, it will update the contents of that players window

        :param label_frame_obj:
        :param data_dict:
        :return:
        """
        if data_dict is None:
            logger.warning("Update frame for player is None, no update performed")
            return

        logger.info("updating Frame: {}".format(data_dict))


        label_frame_obj.player_name_label['text'] = data_dict.get('PlayerName', "Unknown")

        kills, deaths, assists = data_dict.get('KDA', "0/0/0").split("/")

        label_frame_obj.player_kda_label['text'] = "Kills: {}\nDeaths: {}\nAssists: {}".format(kills, deaths, assists)
        label_frame_obj.player_cash_label['text'] = "Cash: ${}\nScore: {}".format(data_dict['Cash'],data_dict['Score'])
        label_frame_obj.player_team_label['text'] = "Team: {}".format(data_dict['TeamId'].replace("0", "Blue").replace("1", "Red"))
        label_frame_obj.player_team_number = int(data_dict['TeamId'])

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

    async def button_kill_player(self, unique_id):
        """

        :param unique_id:
        :return:
        """
        logger.info("Kill {}".format(unique_id))
        await send_rcon("Kill {}".format(unique_id), self.rcon_host, self.rcon_port, self.rcon_pass)

    async def button_kick_player(self, unique_id):
        """

        :param unique_id:
        :return:
        """
        logger.info("Kick {}".format(unique_id))
        await send_rcon("Kick {}".format(unique_id), self.rcon_host, self.rcon_port, self.rcon_pass)

    async def button_ban_player(self, unique_id):
        """

        :param unique_id:
        :return:
        """
        logger.info("Ban {}".format(unique_id))
        await send_rcon("Ban {}".format(unique_id), self.rcon_host, self.rcon_port, self.rcon_pass)

    async def button_give_money(self, unique_id, amount):
        """


        :param unique_id:
        :param amount:
        :return:
        """

        logger.info("Give {} ${}".format(unique_id, amount))
        await send_rcon("GiveCash {} {}".format(unique_id, amount), self.rcon_host, self.rcon_port, self.rcon_pass)

    async def button_switch_team(self, unique_id, team_id):
        """

        :param unique_id:
        :param team_id:
        :return:
        """
        logger.info("SwitchTeam {} {}".format(unique_id, team_id))
        await send_rcon("SwitchTeam {} {}".format(unique_id, team_id), self.rcon_host, self.rcon_port, self.rcon_pass)

    async def button_switch_skins(self, unique_id, skin_name):
        """


        :param unique_id:
        :param skin_name:
        :return:
        """
        logger.info("SetPlayerSkin {} {}".format(unique_id, skin_name))
        await send_rcon("SetPlayerSkin {} {}".format(unique_id, skin_name), self.rcon_host, self.rcon_port, self.rcon_pass)

    async def button_give_item(self, unique_id, item):
        """
        Give a single player an item from the list of items.

        :param unique_id:
        :param item:
        :return:
        """

        logger.info("Give {} {}".format(unique_id, item))
        # maybe repalce the human readable one with the mapped one
        replace_item = KNOWN_ITEM_NAME_MAP.get(item, None)
        if replace_item is not None:
            item = replace_item
        await send_rcon("GiveItem {} {}".format(unique_id, item), self.rcon_host, self.rcon_port, self.rcon_pass)


    async def view_player_profile(self, unique_id):
        """
        When called, opens a browser to that players profile

        :param unique_id:
        :return:
        """
        webbrowser.open("https://steamcommunity.com/profiles/{}".format(unique_id))



