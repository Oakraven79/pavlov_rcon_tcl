"""
This is for the section where all the player details live for a single server.

This is imported by SingleServerFrame and used from within it


"""
import asyncio
import tkinter as tk

from tkinter import ttk

from widgets import HoverButton
from rcon_connector import send_rcon

from items_list import (KNOWN_ITEM_NAME_MAP, KNOWN_ITEM_NAME_MAP_INV)
from skins_list import SKINS_LIST
from config_items import (MENU_FONT_SIZE, MENU_FONT_NAME)

import logging
logger = logging.getLogger()

class PlayerListFrame:

    def __init__(self, parent_frame, rcon_host, rcon_port, rcon_pass):
        """

        :param parent_frame:
        """
        self.parent_frame = parent_frame
        self.player_frame_dict = dict()

        # Pass this in here otherwise we just have to keep reaching back the parent
        self.rcon_host = rcon_host
        self.rcon_port = rcon_port
        self.rcon_pass = rcon_pass


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
                player_label_frame_obj = self.player_frame_dict.get(unique_id, None)
                if player_label_frame_obj is not None:
                    self.update_single_player_frame(player_label_frame_obj, player_info, items_list)
                else:
                    logger.warning("Tried to update a player frame that has been deleted. Skipping ")
            else:
                self.player_frame_dict[unique_id] = self.create_single_player_frame(player_info, items_list)
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
        main_frame = tk.LabelFrame(self.parent_frame, text=data_dict['UniqueId'], bd=5)

        # Main Frame for all the player info to live in
        main_frame.pack(fill='x')

        main_frame.player_name_label = tk.Label(main_frame, text=data_dict['PlayerName'])
        main_frame.player_name_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE), width=30)
        main_frame.player_name_label.grid(row=0,column=0, sticky="ns", pady = 5, padx = 5)

        kills, deaths, assists = data_dict.get('KDA', "0/0/0").split("/")

        main_frame.player_kda_label = tk.Label(
            main_frame, text="Kills: {}\nDeaths: {}\nAssists: {}".format(kills, deaths, assists)
        )
        main_frame.player_kda_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE-3))
        main_frame.player_kda_label.grid(row=0,column=1, sticky="nsew", pady = 5, padx = 5)

        main_frame.player_cash_label = tk.Label(main_frame, text="Cash: ${}\nScore: {}".format(data_dict['Cash'],
                                                                                               data_dict['Score']))
        main_frame.player_cash_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3), width=20)
        main_frame.player_cash_label.grid(row=0,column=2, sticky="nsew", pady = 5, padx = 5)

        main_frame.player_team_label = tk.Label(main_frame, text="Team: {}".format(data_dict['TeamId']))
        main_frame.player_team_label.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.player_team_label.grid(row=0,column=3, sticky="nsew", pady = 5, padx = 5)

        # Switch teams
        main_frame.move_player_label_frame = tk.LabelFrame(main_frame, text="Switch Team", bd=5, borderwidth=3)
        main_frame.move_player_label_frame.grid(row=0, column=4, sticky="nsew", pady=5, padx=5)

        main_frame.move_player_label_frame.team_0_button = HoverButton(main_frame.move_player_label_frame, text="0",
                                                                       command=lambda: self.button_switch_team(
                                                                           data_dict['UniqueId'], 0), padx=5, pady=2)
        main_frame.move_player_label_frame.team_0_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.move_player_label_frame.team_0_button.pack(side="left", fill=tk.BOTH, expand=tk.YES)
        main_frame.move_player_label_frame.team_1_button = HoverButton(main_frame.move_player_label_frame, text="1",
                                                                       command=lambda: self.button_switch_team(
                                                                           data_dict['UniqueId'], 1), padx=5, pady=2)
        main_frame.move_player_label_frame.team_1_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.move_player_label_frame.team_1_button.pack(side="left", fill=tk.BOTH, expand=tk.YES)

        # Give money button
        main_frame.give_money_label_frame = tk.LabelFrame(main_frame, text="Give Money", bd=5, borderwidth=3)
        main_frame.give_money_label_frame.grid(row=0, column=5, sticky="nsew", pady=5, padx=5)

        main_frame.give_money_label_frame.give_money_button = HoverButton(main_frame.give_money_label_frame,
                                                                          text="+$1000",
                                                                          command=lambda: self.button_give_money(
                                                                              data_dict['UniqueId'], 1000), padx=5,
                                                                          pady=2)
        main_frame.give_money_label_frame.give_money_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.give_money_label_frame.give_money_button.pack(side="left")
        main_frame.give_money_label_frame.give_more_money_button = HoverButton(main_frame.give_money_label_frame,
                                                                               text="+$5000",
                                                                               command=lambda: self.button_give_money(
                                                                                   data_dict['UniqueId'], 5000), padx=2,
                                                                               pady=2)
        main_frame.give_money_label_frame.give_more_money_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.give_money_label_frame.give_more_money_button.pack(side="left")

        # Item Selector
        main_frame.give_item_label_frame = tk.LabelFrame(main_frame, text="Give Item", bd=5, borderwidth=3)
        main_frame.give_item_label_frame.grid(row=0,column=6, sticky="nsew", pady = 5, padx = 5)

        main_frame.give_item_label_frame.choice_var = tk.StringVar()

        selected_give_item = ''
        if len(items_list) > 0:
            main_frame.give_item_label_frame.choice_var.set(items_list[0])
            selected_give_item = "{}".format(items_list[0])


        main_frame.give_item_label_frame.selected_item = ttk.OptionMenu(
            main_frame.give_item_label_frame,
            main_frame.give_item_label_frame.choice_var,
            selected_give_item, *items_list
        )
        main_frame.give_item_label_frame.selected_item.configure(width=20)
        main_frame.give_item_label_frame.selected_item.pack(side='left')

        main_frame.give_item_label_frame.give_item_button = HoverButton(main_frame.give_item_label_frame,
                                                                        text="Give Item",
                                                                        command=lambda: self.button_give_item(
                                                                            data_dict['UniqueId'],
                                                                            main_frame.give_item_label_frame.choice_var.get()),
                                                                        padx=2,
                                                                        pady=0)
        main_frame.give_item_label_frame.give_item_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.give_item_label_frame.give_item_button.pack(side="left")

        # Switch Skin
        main_frame.switch_skin_label_frame = tk.LabelFrame(main_frame, text="Set Player Skin", bd=5, borderwidth=3)
        main_frame.switch_skin_label_frame.grid(row=0, column=7, sticky="nsew", pady=5, padx=5)

        main_frame.switch_skin_label_frame.choice_var = tk.StringVar()
        if len(SKINS_LIST) > 0:
            main_frame.switch_skin_label_frame.choice_var.set(SKINS_LIST[0])

        main_frame.switch_skin_label_frame.selected_item = tk.OptionMenu(
            main_frame.switch_skin_label_frame,
            main_frame.switch_skin_label_frame.choice_var,
            *SKINS_LIST
        )
        main_frame.switch_skin_label_frame.selected_item.configure(width=10)
        main_frame.switch_skin_label_frame.selected_item.pack(side='left')

        main_frame.switch_skin_label_frame.give_item_button = HoverButton(main_frame.switch_skin_label_frame,
                                                                          text="Switch!",
                                                                          command=lambda: self.button_switch_skins(
                                                                              data_dict['UniqueId'],
                                                                              main_frame.switch_skin_label_frame.choice_var.get()),
                                                                          padx=2,
                                                                          pady=0)
        main_frame.switch_skin_label_frame.give_item_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.switch_skin_label_frame.give_item_button.pack(side="left")

        # Kill Player
        main_frame.kill_button = HoverButton(main_frame, text="Kill Player",
                                             command=lambda: self.button_kill_player(data_dict['UniqueId']), padx=5, pady=0)
        main_frame.kill_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.kill_button.grid(row=0, column=8, sticky="nsew", pady=5, padx=5)

        # Kick player
        main_frame.kick_button = HoverButton(main_frame, text="Kick Player",
                                             command=lambda:self.button_kick_player(data_dict['UniqueId']), padx=5, pady=0)
        main_frame.kick_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 3))
        main_frame.kick_button.grid(row=0, column=9, sticky="nsew", pady=5, padx=5)

        # Ban player
        main_frame.ban_button = HoverButton(main_frame, text="BAN PLAYER",
                                            command=lambda: self.button_ban_player(data_dict['UniqueId']), padx=5, pady=0)
        main_frame.ban_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE - 5))
        main_frame.ban_button.grid(row=0, column=10, sticky="nsew", pady=5, padx=5)


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

        kills, deaths, assists = data_dict.get('KDA', "0/0/0").split("/")

        label_frame_obj.player_kda_label['text'] = "Kills: {}\nDeaths: {}\nAssists: {}".format(kills, deaths, assists)
        label_frame_obj.player_cash_label['text'] = "Cash: ${}\nScore: {}".format(data_dict['Cash'],data_dict['Score'])
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

    def button_kill_player(self, unique_id):
        """

        :param unique_id:
        :return:
        """
        logger.info("Kill {}".format(unique_id))
        asyncio.run(send_rcon("Kill {}".format(unique_id), self.rcon_host, self.rcon_port, self.rcon_pass))

    def button_kick_player(self, unique_id):
        """

        :param unique_id:
        :return:
        """
        logger.info("Kick {}".format(unique_id))
        asyncio.run(send_rcon("Kick {}".format(unique_id), self.rcon_host, self.rcon_port, self.rcon_pass))

    def button_ban_player(self, unique_id):
        """

        :param unique_id:
        :return:
        """
        logger.info("Ban {}".format(unique_id))
        asyncio.run(send_rcon("Ban {}".format(unique_id), self.rcon_host, self.rcon_port, self.rcon_pass))

    def button_give_money(self, unique_id, amount):
        """


        :param unique_id:
        :param amount:
        :return:
        """

        logger.info("Give {} ${}".format(unique_id, amount))
        asyncio.run(send_rcon("GiveCash {} {}".format(unique_id, amount), self.rcon_host, self.rcon_port, self.rcon_pass))

    def button_switch_team(self, unique_id, team_id):
        """

        :param unique_id:
        :param team_id:
        :return:
        """
        logger.info("SwitchTeam {} {}".format(unique_id, team_id))
        asyncio.run(send_rcon("SwitchTeam {} {}".format(unique_id, team_id), self.rcon_host, self.rcon_port, self.rcon_pass))

    def button_switch_skins(self, unique_id, skin_name):
        """


        :param unique_id:
        :param skin_name:
        :return:
        """
        logger.info("SetPlayerSkin {} {}".format(unique_id, skin_name))
        asyncio.run(send_rcon("SetPlayerSkin {} {}".format(unique_id, skin_name), self.rcon_host, self.rcon_port, self.rcon_pass))

    def button_give_item(self, unique_id, item):
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
        asyncio.run(send_rcon("GiveItem {} {}".format(unique_id, item), self.rcon_host, self.rcon_port, self.rcon_pass))




