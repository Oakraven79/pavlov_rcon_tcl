import asyncio
import pavlovrcon
import logging
import random
import uuid

logger = logging.getLogger(__name__)


SUCCESS_KEY = "Successful"


class RconCommandQueue:
    """
    Object that houses an processes queues of RconCommand's, handles the server connection

    """

    def __init__(self, rcon_host, rcon_port, rcon_pass):
        """ """

        self.rcon_host = rcon_host
        self.rcon_port = rcon_port
        self.rcon_pass = rcon_pass

        self.command_queue = []
        self.command_hash = {}
        self.server_connection = get_rcon(
            rcon_host=self.rcon_host, rcon_port=self.rcon_port, rcon_pass=self.rcon_pass
        )

    def submit_command(self, command, keep_reply_time):
        """
        Adds a command in for processing
        """
        command_obj = RconCommand(command=command, keep_reply_time=keep_reply_time)

        self.command_queue.append(command_obj)
        self.command_hash[command_obj.get_command_id()] = command_obj
        return command_obj.get_command_id()

    def get_command_by_command_id(self, command_id):
        return self.command_hash.get(command_id, None)

    def purge_completed_commands(self):
        """
        goes through and removes completed commands from the queue
        """
        command_ids_to_delete = []

        for command_obj in self.command_queue:
            if command_obj.is_complete() and command_obj._keep_reply_time == 0:
                command_ids_to_delete.append(command_obj.get_command_id())
            elif (
                command_obj.is_complete()
                and command_obj._keep_reply_time == -1
                and command_obj._command_result_extracted
            ):
                command_ids_to_delete.append(command_obj.get_command_id())

        current_index = 0

        command_queue_length = len(self.command_queue)

        for _ in range(command_queue_length):
            current_command_id = self.command_queue[current_index].get_command_id()
            if current_command_id in command_ids_to_delete:
                logger.debug("Purging command {}".format(current_command_id))
                del self.command_hash[current_command_id]
                del self.command_queue[current_index]
            else:
                logger.debug(
                    "NOT Purging command {} as incomplete".format(current_command_id)
                )
                current_index += 1

    async def process_command_queue(self):
        """
        Work though any unfinished tasks on the current connection

        """
        logger.debug(
            "There are {} items in the queue: {}".format(
                len(self.command_queue), self.command_queue
            )
        )

        current_queue_len = len(
            self.command_queue
        )  # Current lenth as queue might be async added to

        for index in range(current_queue_len):
            command = self.command_queue[index]

            logger.info(
                "Loading command {}:{} for processing...".format(index, command)
            )
            asyncio.sleep(1)
            if not command.is_complete():
                logger.debug(
                    "Command {} is NOT finished, sending it...".format(command)
                )
                data = await self.server_connection.send(command.get_command())
                command.set_reply(data)
                if data.get(SUCCESS_KEY, False) is True:
                    command.set_reply(data)
            else:
                logger.debug("SKIPPING Command {} as is finished.".format(command))

    async def send_command_for_processing(
        self, command_str, keep_reply_time=-1, retry_count=0
    ):
        """

        command_str: The raw command to pass to the server

        keep_reply_time: How many miliiseconds to keep the reply for, 0 = dont bother, -1 keep until cleared manually


        :return: returns a unique_string if the keep_reply_time is > 0


        """
        command_id = self.submit_command(
            command=command_str, keep_reply_time=keep_reply_time
        )

        logger.info("Command {} submitted with ID: {}".format(command_str, command_id))

        command_obj = self.get_command_by_command_id(command_id)
        while not command_obj.is_complete():
            logger.debug(
                "************** WAITING FOR TASK {}   (Queue.... {})".format(
                    command_obj, self.command_queue
                )
            )
            await asyncio.sleep(0.5)
        command_obj.mark_data_extracted()
        logger.debug("+++++++++++++++++++ Command {} completed!".format(command_obj))
        return command_obj.get_reply()


class RconCommand:
    """
    Object to be added to queues and processed

    """

    def __init__(self, command, keep_reply_time=0):
        """ """
        self._command = command
        self._keep_reply_time = keep_reply_time
        self._command_id = str(uuid.uuid4())  # make an identifier string
        self._reply = {}  # blank reply
        self._command_executed = False  # Has the command been run yet?
        self._command_result_extracted = False  # Did the caller get the data out?

    def get_command(self):
        return self._command

    def get_command_id(self):
        return self._command_id

    def is_complete(self):
        return self._command_executed == True

    def set_reply(self, reply):
        """
        Sets the reply and marks as done
        """
        self._reply = reply
        self._command_executed = True

    def mark_data_extracted(self):
        self._command_result_extracted = True

    def get_reply(self):
        return self._reply

    def __repr__(self):
        return "<'{}',ttl:{},complete:{},ack:{},id:{}>".format(
            self._command,
            self._keep_reply_time,
            self._command_executed,
            self._command_result_extracted,
            self._command_id,
        )


def get_rcon(rcon_host=None, rcon_port=None, rcon_pass=None):
    """
    This is responsible for providing an active connection to the desired server connection.

    :return:
    """
    return pavlovrcon.PavlovRCON(rcon_host, rcon_port, rcon_pass)


# Send a command
async def send_rcon(
    command, rcon_host=None, rcon_port=None, rcon_pass=None, mock_replies=False
):
    """
    Send the RCON command to the supplied server.

    This will open a connection, send the command, collect the reply, close the connection
    and return reply

    :param command: The RCON command string you want to send
    :param rcon_host: The IP/DNS name of the Pavlov server
    :param rcon_port: The server port
    :param rcon_pass: The password in plain text
    :param mock_replies: True or False. True will use pre-canned replies for testing
    :return:
    """
    if mock_replies:
        return test_replies(command)
    try:
        rcon_obj = get_rcon(
            rcon_host=rcon_host, rcon_port=rcon_port, rcon_pass=rcon_pass
        )
        data = await rcon_obj.send(command, auto_close=True)
    except Exception as exc:
        logger.error("Unable to Send RCON COMMAND: {} (Returning None)".format(exc))
        return None
    logger.info("Data returned from {}:{} - {}".format(rcon_host, rcon_port, data))
    return data


def test_replies(command):
    """
    Use this for mocking replies from the Pavlov server


    :param command:
    :return:
    """
    if command == "RefreshList":
        if random.randint(0, 10) > -1:
            data = {
                "PlayerList": [
                    {"Username": "Oakraven", "UniqueId": "76561198040783597"},
                    {"Username": "Oakraven2", "UniqueId": "76561198040783598"},
                    {"Username": "Oakraven3", "UniqueId": "76561198040783599"},
                    {"Username": "Oakraven4", "UniqueId": "76561198040783510"},
                    {"Username": "Oakraven5", "UniqueId": "76561198040783511"},
                    {"Username": "Oakraven6", "UniqueId": "76561198040783512"},
                    {"Username": "Oakraven7", "UniqueId": "76561198040783513"},
                    {"Username": "Oakraven8", "UniqueId": "76561198040783517"},
                    {"Username": "Oakraven9", "UniqueId": "76561198040783514"},
                    {"Username": "Oakraven10", "UniqueId": "76561198040783515"},
                    {"Username": "Oakraven11", "UniqueId": "76561198040783516"},
                ]
            }
        else:
            data = {
                "PlayerList": [
                    {"Username": "Oakraven", "UniqueId": "76561198040783597"},
                    {"Username": "Oakraven2", "UniqueId": "76561198040783598"},
                ]
            }
    elif command.startswith("InspectPlayer"):
        unique_id = command.split(" ")[1]

        data = {
            "PlayerInfo": {
                "PlayerName": "Oakraven{}".format(unique_id[-4:]),
                "UniqueId": "{}".format(unique_id),
                "KDA": "0/4/0",
                "Score": "0",
                "Cash": "9400",
                "TeamId": "0",
            }
        }
    elif command == "ItemList":
        data = {
            "ItemList": [
                "ak",
                "vanas",
                "AUG",
                "awp",
                "smg",
                "shotgun",
                "AR",
                "sock",
                "m9",
                "cet9",
                "Armour",
                "kevlarhelmet",
                "Grenade",
                "grenade_ru",
                "AK47",
                "AK12",
                "DE",
                "1911",
                "mp5",
                "p90",
                "Smoke",
                "smoke_ru",
                "flash",
                "flash_ru",
                "sawedoff",
                "Pliers",
                "LMGA",
                "AutoShotgun",
                "AntiTank",
                "kar98",
                "AutoSniper",
                "57",
                "uzi",
                "Knife",
                "DrumShotgun",
                "Revolver",
                "supp_pistol",
                "supp_rifle",
                "scope",
                "Grip_Angled",
                "Grip_Vertical",
                "acog",
                "holo",
                "reddot",
                "painkillers",
                "ammo_rifle",
                "ammo_sniper",
                "ammo_smg",
                "ammo_pistol",
                "ammo_shotgun",
                "ammo_special",
                "taser",
                "crowbar",
                "boltcutters",
                "lockpick",
                "handcuffs",
                "repairtool",
                "pickaxe",
                "keycard",
                "syringe",
                "luger",
                "mp40",
                "G43",
                "Tokarev",
                "webley",
                "m1garand",
                "svt40",
                "grenade_us",
                "smoke_us",
                "grenade_ger",
                "smoke_ger",
                "grenade_svt",
                "smoke_svt",
                "bar",
                "bren",
                "ppsh",
                "sten",
                "mosin",
                "springfield",
                "thompson",
                "mg42",
                "leeenfield",
                "RL_M1A1",
                "RL_PIAT",
                "rl_panzer",
                "stg44",
                "dp27",
                "kross",
                "vss",
                "tankmg",
                "tankturret",
                "backblast",
                "runover",
                "Fire",
                "fall",
                "scar",
                "skinhelmet_us",
                "skinhelmet_ger",
                "skinhelmet_svt",
                "FlashLight",
                "Katana",
                "AdminSword",
                "DiamondSword",
                "OneHandedSword",
                "BlueRoseSword",
                "ContributorSword",
                "ContributorSwordSecond",
                "ContributorSwordThird",
                "ContributorSwordFour",
                "ContributorSwordFifth",
                "Torch",
                "AncientSWORD",
                "TwitchSword",
                "DarkAncientSword",
                "NetherScythe",
                "PerkBottleBase",
                "juggernautbottle",
                "staminupbottle",
                "ExcaliburSword",
                "TestingBow",
                "MCBow",
                "PatreonBow",
                "Enderpearl",
                "SnakeBow",
                "PatreonSword",
                "DiamondAxe",
            ]
        }

    elif command == "ServerInfo":
        data = {
            "ServerInfo": {
                "MapLabel": "UGC1741218360",
                "GameMode": "ZWV",
                "ServerName": "Great Leap To Zombies",
                "Teams": True,
                "Team0Score": "0",
                "Team1Score": "0",
                "RoundState": "Started",
                "PlayerCount": "0/16",
            }
        }

    return data
