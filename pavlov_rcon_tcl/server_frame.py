"""
This class is for a single server connection

"""
import asyncio
import tkinter as tk
from tkinter import ttk

import logging
logger = logging.getLogger(__name__)

import local_utils

from widgets import (HoverButton, ScrollableFrame)
from rcon_connector import send_rcon
from playerlist_frame import PlayerListFrame

from config_items import (MENU_FONT_SIZE, MENU_FONT_NAME)
from items_list import (KNOWN_ITEM_NAME_MAP, KNOWN_ITEM_NAME_MAP_INV)
from games_modes import GAME_MODES
from maps_list import MAP_IDS


class CustomServerCommands:
    """
    Class to parse and hold custom server commands

    Server commands are expected as a list of commands such as

    [
        {
          "command_name"       : "Reset all Money to $1000",
          "command_short_name" : "ResetMoney",
          "delay_before_start" : 0,
          "steps"              : [
            {
              "command"      : "SetCash {UniqueID} 1000",
              "delay_after"  : 0,
              "comment"      : "{UniqueID} will be replaced with the id of each connected player "
            }
          ]
        },
        {
          "command_name" : "50Cal Free for all",
          "steps"        : [
            {
              "command"      : "GiveItem {UniqueID} AntiTank",
            },
            {
              "command"      : "SetCash {UniqueID} 50000",
            }
          ]
        }
      ]

    A Single command is like this. `command_name` and `steps` are mandatory while `command_short_name`
    and `delay_before_start` are optional

    {
      "command_name"       : "Reset all Money to $1000",
      "command_short_name" : "ResetMoney",
      "delay_before_start" : 0,
      "steps"              : [
        {
          "command"      : "SetCash {UniqueID} 1000",
          "delay_after"  : 0,
          "comment"      : "{UniqueID} will be replaced with the id of each player and apply_to_all will mean this will be applied to all players. "
        }
      ]
    }

    Every command has a series of steps expressed as a list. The commands will be executed in that order.

    The only mandatory field is `command` which refers to the exact RCON command that will be sent. Please see the
    Offical wiki for how those commands are meant to work.

    The added keyword {UniqueID} tells the parser that this command is to be applied to all currently connected players
    so for example if there were 20 players connected the command `SetCash {UniqueID} 1000` would be called 20 times
    with the unique_id of each player in place of {UniqueID}

    Additionally {UniqueID:blue} or {UniqueID:red} will look for players in team 0 or 1 respectively.

    Steps can be repeated via the repeat keyword

    The following example will be executed 20 times with a delay of 3 seconds each time.
    NOTE: Do understand that if you click this multiple times they will stack and execute in parallel, maybe that is what you want?
    {
          "command_name"       : "Smoke Grenade PARTY",
          "delay_before_start" : 0,
          "comment"            : "Give everyone a smoke grenade every 3 seconds for 1 minute ",
          "steps"              : [
            {
              "command"      : "GiveItem {UniqueID} smoke",
              "delay_after"  : 3,
              "comment"      : "{UniqueID} will be replaced with the id of each player and will mean this will be applied to all players. 'repeat' will execute this command x times",
              "repeat"       : 20
            }
          ]
        }


    """

    VALID_COMMAND_SPECIALS = ['{UniqueID}', '{UniqueID:blue}', '{UniqueID:red}']

    def __init__(self, server_commands, server_frame_obj):
        """

        :param server_commands: the loaded json data
        :param server_frame_obj: The parent Frame so this can call methods on it to get player info
        """
        self._server_commands_raw = server_commands
        self._valid_command_name_list = []
        self._server_frame_obj = server_frame_obj
        self.validate_server_commands()


    def validate_server_commands(self):
        """
        Goes through each server command and validates if all the required keywords
        are there and warns if it sees anything it doesn't know about.

        :return:
        """
        commands = self._server_commands_raw

        for cmd in commands:
            cmd_valid = True
            print(cmd)
            # looking for required fields
            cmd_name = cmd.get('command_name', None)
            if cmd_name is None:
                logger.error("Couldn't find 'command_name' in entry {}".format(cmd))
                cmd_valid = False
            else:
                logger.info("Loaded custom command: {}".format(cmd_name))
            cmd_delay_before = cmd.get('delay_before_start', None)
            if cmd_delay_before is None:
                logger.info("delay_before_start not specified so {} will start as soon as button is pressed".format(cmd_name))
            else:
                try:
                    cmd_delay_before = int(cmd_delay_before)
                    logger.info("delay_before_start set to {} for command {}".format(cmd_delay_before, cmd_name))
                except ValueError:
                    logger.warning("delay_before_start for command {} is not an integer. value supplied: {} (this will be ignored FYI)".format(cmd_name, cmd_delay_before))
            # now to check each step
            cmd_steps = cmd.get("steps", None)
            if cmd_steps is None:
                logger.error("no command steps defined for command: {}".format(cmd_name))
                cmd_valid = False
            else:
                for i, cmd_step in enumerate(cmd_steps, 1):
                    logger.info("Looking at step {}: {}".format(i, cmd_step))
                    # Examine command
                    step_rcon = cmd_step.get("command", None)
                    if step_rcon is None:
                        logger.error("No 'command' entry defined for {}".format(cmd_step))
                    else:
                        # check the command for special Characters
                        if step_rcon.find("{") != -1:
                            all_words = step_rcon.split(" ")
                            for word in all_words:
                                if word.find("{") != -1:
                                    if word not in CustomServerCommands.VALID_COMMAND_SPECIALS:
                                        logger.error("Keyword '{}' in command '{}' is not a valid special. Valid specials are: {} ".format(
                                            word, step_rcon, CustomServerCommands.VALID_COMMAND_SPECIALS
                                        ))
                                        cmd_valid = False
                    step_delay = cmd_step.get("delay_after", None)
                    if step_delay is None:
                        logger.info("No delay specified for command {}, defaulting to 0".format(step_rcon))
                    else:
                        try:
                            step_delay = int(step_delay)
                            logger.info("Step will delay {} after executing the command: {}".format(step_delay, step_rcon))
                        except ValueError:
                            logger.error("Specified delay for command '{}' is not an Integer in command step:".format(step_delay, cmd_step) )
                            cmd_valid = False
            if cmd_valid is True:
                self._valid_command_name_list.append(cmd_name)
            else:
                logger.warning("Not adding command {} as there was missing data".format(cmd_name))
        logger.info("Valid Commands: {}".format(self._valid_command_name_list))


    def get_command_names(self):
        """
        return a list of strings of the command names

        :return:
        """
        return self._valid_command_name_list

    def get_command_dict_by_name(self, command_name):
        """
        Given a command name it will get the correct dict or return None

        :param command_name:
        :return:
        """
        ret_val = None
        for command in self._server_commands_raw:
            if command.get("command_name", "") == command_name:
                return command
        return ret_val

    async def exec_command_by_name(self, command_name):
        """
        Given the string name of a command, it will try to execute it

        This object has access to the server frame so can call out to it get info
        about the currently connected players etc.

        This assumes that only validated commands will be sent through

        :param command_name:
        :return:
        """
        command_dict = self.get_command_dict_by_name(command_name)
        # Check if the command has a pre delay
        delay = int(command_dict.get('delay_before_start', 0))
        if delay > 0:
            await asyncio.sleep(delay)
        # now to cycle through the steps
        steps_list = command_dict.get("steps")
        for step_dict in steps_list:
            await self.process_command_step(step_dict)

    async def process_command_step(self, step_dict):
        """
        Given a step dict from a custom command, this will execute it.

        :param step_dict:
        :return:
        """
        repeat_count = 0
        target_repeats = step_dict.get('repeat', 1)
        delay_after = step_dict.get('delay_after', 0)
        while repeat_count < target_repeats:
            await self.exec_rcon_command(step_dict.get('command', ""))
            if delay_after > 0:
                await asyncio.sleep(delay_after)
            repeat_count += 1

    async def exec_rcon_command(self, rcon_command):
        """

        :param rcon_command:
        :return:
        """
        if rcon_command.find('{') == -1:
            # The command contains no substititions
            await send_rcon(rcon_command, **self._server_frame_obj.get_server_creds())
        else:
            # now we need to ask the server_frame for its current list of players based on the command
            # At this stage it is only going to be all, red, blue so it is matter of finding which
            player_and_team_list = self._server_frame_obj.player_frame.get_players_and_teams()
            exec_list = []
            # now to build the command list base on these current parameters
            if rcon_command.find("{UniqueID}") != -1:
                for unique_id, team_id in player_and_team_list:
                    exec_list.append(rcon_command.replace("{UniqueID}", unique_id))
            elif rcon_command.find("{UniqueID:blue}") != -1:
                for unique_id, team_id in player_and_team_list:
                    if team_id == 0:
                        exec_list.append(rcon_command.replace("{UniqueID}", unique_id))
            elif rcon_command.find("{UniqueID:red}") != -1:
                for unique_id, team_id in player_and_team_list:
                    if team_id == 1:
                        exec_list.append(rcon_command.replace("{UniqueID}", unique_id))
            # now to exec the list
            chunk_size = 5  # only do 5 players at a time
            for chunked_list in local_utils.chunker(exec_list, chunk_size):
                await asyncio.gather(*[send_rcon(rcon_string, **self._server_frame_obj.get_server_creds()) for rcon_string in chunked_list])

class SingleServerFrame(tk.Frame):


    def __init__(self, master=None, loop=None, rcon_host=None, rcon_port=None, rcon_pass=None, server_commands=None):
        super().__init__(master, width=master.winfo_screenwidth(), height=master.winfo_screenheight())
        self.master = master
        self.rcon_host = rcon_host
        self.rcon_port = rcon_port
        self.rcon_pass = rcon_pass
        self.server_commands_obj = CustomServerCommands(server_commands, self)
        self.loop = loop

        self.pack(fill='both')

        # now with all the data loaded we can create the server frames
        self.create_frames()

    def get_server_creds(self):
        """
        Each Server frame knows its creds, this is a getter method

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

        :return:
        """

        server_creds = self.get_server_creds()

        data = await send_rcon("ServerInfo", **server_creds)

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
        data = await send_rcon("ItemList", **server_creds)
        if data is not None:
            self.update_server_items(data.get("ItemList", list()))
        # Get the player info
        data = await send_rcon("RefreshList", **server_creds)
        if data is not None:
            players_dict = {k: v for k, v in zip([x['Username'] for x in data['PlayerList']],
                                                 [x['UniqueId'] for x in data['PlayerList']])}
        if data is not None:
            player_data_list = []
            chunk_size = 5 # only do 5 players at a time
            for chunked_list in local_utils.chunker(list(players_dict.values()), chunk_size):
                player_data_list.extend(
                    await asyncio.gather(
                        *[send_rcon("InspectPlayer {}".format(x), **server_creds) for x in chunked_list])
                )
            self.update_player_window(player_data_list, max_players)


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
        self.server_players_frame = ScrollableFrame(self, relief="raised", borderwidth=3)
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

        self.server_info_frame.server_teams_label['text'] = "Teams: {}\nTeam 0 (Blue) Score: {}\nTeam 1 (Red) Score:{}".format(teams_status, teams_0_score, teams_1_score)

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
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_columnconfigure(3, weight=1)


        # Disconnect (COmmented out as we don't really need this at the moment)
        # Perhaps use this to disconnect and remove a server from a multi server config?
        # frame.disconnect_button = HoverButton(frame, text="Disconnect RCON", command=button_hi, padx=5, pady=2)
        # frame.disconnect_button.config(font=("Helvetica", MENU_FONT_SIZE))
        # frame.disconnect_button.pack(fill='x')

        # ResetSND
        frame.reset_snd_button = HoverButton(frame, text="Reset Seek and Destroy",
                                             command=lambda: self.loop.create_task(self.button_reset_snd()),
                                             padx=5, pady=2)
        frame.reset_snd_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.reset_snd_button.grid(row=0,column=0, sticky="nsew", pady = 5, padx = 5)



        # RotateMap
        frame.rotate_map_button = HoverButton(frame, text="Rotate Map",
                                              command=lambda: self.loop.create_task(self.button_rotate_map()),
                                              padx=5, pady=2)
        frame.rotate_map_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.rotate_map_button.grid(row=1,column=0,columnspan=2, sticky="nsew", pady = 5, padx = 5)

        # SetLimitedAmmoType {0-5}
        frame.set_limited_ammo_type_frame = tk.LabelFrame(frame, relief="raised", borderwidth=3, text="Set Limited Ammo Type", padx=5, pady=2)
        frame.set_limited_ammo_type_frame.grid(row=0,column=1, sticky="nsew", pady = 5, padx = 5)

        frame.set_limited_ammo_type_frame.ammo_spin = tk.Spinbox(frame.set_limited_ammo_type_frame, from_=0, to=5, width=2)
        frame.set_limited_ammo_type_frame.ammo_spin.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.set_limited_ammo_type_frame.ammo_spin.pack(side="left")

        frame.set_limited_ammo_type_frame.apply_button = HoverButton(frame.set_limited_ammo_type_frame,
                                                                     text="Apply Ammo Limit",
                                                                     command=lambda: self.loop.create_task(self.button_set_ammo_limit_type(
                                                                         frame.set_limited_ammo_type_frame.ammo_spin.get())),
                                                                     padx=5, pady=2)
        frame.set_limited_ammo_type_frame.apply_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.set_limited_ammo_type_frame.apply_button.pack(side="left", fill="x", expand=tk.YES)

        # SwitchMap {MapName/ID} {GameMode}
        frame.set_switch_map_frame = tk.LabelFrame(frame, relief="raised", borderwidth=3,
                                                          text="Switch Map", padx=2, pady=2)
        frame.set_switch_map_frame.grid(row=2,column=0, columnspan=2,sticky="nsew", pady = 5, padx = 5)

        # Map combo box
        frame.set_switch_map_frame.map_id_combo = ttk.Combobox(frame.set_switch_map_frame,
                                                               values=list(MAP_IDS.keys()),
                                                               font = (MENU_FONT_NAME, MENU_FONT_SIZE),
                                                               style='server_frame.TCombobox'
                                                )
        frame.set_switch_map_frame.map_id_combo.configure(width=40)
        frame.set_switch_map_frame.map_id_combo.pack(side="left", fill="both", expand=tk.YES)

        # Game Mode Choice
        frame.set_switch_map_frame.choice_var = tk.StringVar()
        frame.set_switch_map_frame.choice_var.set(list(GAME_MODES.keys())[0])
        frame.set_switch_map_frame.game_mode = tk.OptionMenu( frame.set_switch_map_frame, frame.set_switch_map_frame.choice_var,
            *(list(GAME_MODES.keys())))
        frame.set_switch_map_frame.game_mode.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.set_switch_map_frame.game_mode["menu"].configure(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.set_switch_map_frame.game_mode.pack(side='left', fill="y", expand=tk.YES)
        # Apply button
        frame.set_switch_map_frame.apply_button = HoverButton(frame.set_switch_map_frame,
                                                              text="Switch Map", command=lambda: self.loop.create_task(self.button_switch_map(
                                                                    self.get_current_map_selection_values())), padx=2,
                                                              pady=2)
        frame.set_switch_map_frame.apply_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.set_switch_map_frame.apply_button.pack(side="left", fill="both", expand=tk.YES)

        # GiveTeamCash {TeamId} {CashAmt}
        frame.give_team_cash_frame = tk.LabelFrame(frame, relief="raised", borderwidth=3,
                                                          text="Give Team Cash", padx=5, pady=2)
        frame.give_team_cash_frame.grid(row=1, column=2, columnspan=2, sticky="nsew", pady=5, padx=5)

        frame.give_team_cash_frame.team_0_1000_button = HoverButton(frame.give_team_cash_frame, button_colour="lime green", text="Team Blue(0)\n+$1000",
                                                                    command=lambda: self.loop.create_task(self.button_give_team_cash(0, 1000)),
                                                                    padx=15,
                                                                    pady=2)
        frame.give_team_cash_frame.team_0_1000_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.give_team_cash_frame.team_0_1000_button.pack(side="left", fill='x', expand=True)

        frame.give_team_cash_frame.team_1_1000_button = HoverButton(frame.give_team_cash_frame, button_colour="lime green", text="Team Red(1)\n+$1000",
                                                                    command=lambda: self.loop.create_task(self.button_give_team_cash(1, 1000)),
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
                                                                    selected_give_item, *items_list, style='server_frame.TMenubutton')
        frame.give_all_players_item_frame.item_selection.configure(width=15)
        frame.give_all_players_item_frame.item_selection["menu"].configure(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.give_all_players_item_frame.item_selection.pack(side="left", fill="both", expand=tk.YES)
        frame.give_all_players_item_frame.apply_button = HoverButton(frame.give_all_players_item_frame,
                                                                text="Give to all",
                                                                command=lambda: self.loop.create_task(self.button_give_players_item(self.all_player_ids,
                                                                      frame.give_all_players_item_frame.choice_var.get())),
                                                                padx=5,
                                                                pady=2)
        frame.give_all_players_item_frame.apply_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.give_all_players_item_frame.apply_button.pack(side="left", fill="both", expand=tk.YES)

        # Create the custom server action buttons
        frame.custom_server_command_frame = tk.LabelFrame(frame, relief="raised", borderwidth=3,
                                                          text="Custom Server Commands", padx=5, pady=2)
        frame.custom_server_command_frame.grid(row=2, column=2, columnspan=2, sticky="nsew", pady=5, padx=5)

        # now to add the menu selection
        frame.custom_server_command_frame.choice_var = tk.StringVar()
        frame.custom_server_command_frame.choice_var.set("")
        commands_list = self.server_commands_obj.get_command_names()
        frame.custom_server_command_frame.item_selection = ttk.OptionMenu(
            frame.custom_server_command_frame,
            frame.custom_server_command_frame.choice_var,
            "", *commands_list, style='server_frame.TMenubutton')
        frame.custom_server_command_frame.item_selection.configure(width=25)
        frame.custom_server_command_frame.item_selection["menu"].configure(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.custom_server_command_frame.item_selection.pack(side="left", fill="both", expand=tk.YES)
        # Make an apply button
        frame.custom_server_command_frame.apply_button = HoverButton(frame.custom_server_command_frame,
                                                                     text="Execute\nCommand",
                                                                     command=lambda: self.loop.create_task(
                                                                         self.button_execute_custom_server_command(
                                                                             frame.custom_server_command_frame.choice_var.get()
                                                                         )),
                                                                     padx=5,
                                                                     pady=2)
        frame.custom_server_command_frame.apply_button.config(font=(MENU_FONT_NAME, MENU_FONT_SIZE))
        frame.custom_server_command_frame.apply_button.pack(side="left", fill="both", expand=tk.YES)


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
        self.player_frame = PlayerListFrame(self.server_players_frame, self.rcon_host, self.rcon_port, self.rcon_pass, loop=self.loop )


    def update_player_window(self, player_list_dict, max_players):
        """
        Given a list of the players currently connected it will call the player frame object and give it the details of
        each player.

        :param player_dict:
        :param max_players: Int for th emax number (used to format the window

        :return:
        """
        logger.info("update_player_window: {}".format(player_list_dict))
        # For the ID list iu've been given try to get all the ids, make sure strip out null values
        self.all_player_ids =[y for y in [ int(x.get('PlayerInfo',{}).get('UniqueId', None)) for x in player_list_dict] if y is not None]
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

        Returns a list of the current items the server is advertising

        :return:
        """
        if hasattr(self, "current_map_items"):
            return self.current_map_items
        else:
            return list()

    async def button_execute_custom_server_command(self, command_name):
        """


        :param command_name:
        :return:
        """
        logger.info("Executing custom command: {}".format(command_name))
        await self.server_commands_obj.exec_command_by_name(command_name)


    async def button_rotate_map(self):
        """
        Sends a RotateMap which will rotate to the next map in the sequence

        :return:
        """
        await send_rcon("RotateMap", self.rcon_host, self.rcon_port, self.rcon_pass)

    async def button_give_team_cash(self, team_id, cash_amount):
        """
        Gives a team a specific cash amount

        :param team_id:
        :param cash_amount:
        :return:
        """
        logger.info("GiveTeamCash {} {}".format(team_id, cash_amount))
        await send_rcon("GiveTeamCash {} {}".format(team_id, cash_amount), self.rcon_host, self.rcon_port, self.rcon_pass)

    async def button_reset_snd(self):
        """
        Executes a ResetSND

        Resets the match back to round 1 keeping the same teams

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
            chunk_size = 5  # only do 5 players at a time
            for chunked_list in local_utils.chunker(unique_id_list, chunk_size):
                await asyncio.gather(*[self.player_frame.button_give_item(unique_id, item) for unique_id in chunked_list])