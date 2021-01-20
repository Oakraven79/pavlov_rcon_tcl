import tkinter as tk
from tkinter import ttk
import asyncio

from server_frame import SingleServerFrame
from config_items import (MENU_FONT_SIZE, MENU_FONT_NAME)

import logging
logger = logging.getLogger(__name__)

class AsyncApp(tk.Tk):
    """
    This class takes the Tkinter base class and replaces the
    Tkinter event loop (used for click, menus, resizing etc)
    with the asyncio one.

    Why? When executing calls to Rcon the Tkinter one will
    wait for the calls to return so I wanted to have these done
    in the background.

    The results is that asyncio handles both the RCON calls
    and the Tkinter updates as part of its event loop and runs them
    all async as it needs to.

    I poached and adapted this solution from
    https://stackoverflow.com/questions/47895765/use-asyncio-and-tkinter-or-another-gui-lib-together-without-freezing-the-gui

    """

    def __init__(self, loop, interval=1 / 120):
        super().__init__()
        self.loop = loop
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.tasks = []
        self.create_menu()
        # Create the tabs for multiple servers
        self.create_server_tabs()
        # Where all server frames live
        self.rcon_server_frames = []
        # create these tasks so i can destory them later for a clean exit
        self.tasks.append(loop.create_task(self.run_rcon_updates()))
        self.tasks.append(loop.create_task(self.updater(interval)))

    def create_menu(self):
        """
        Draws the File Menu

        :return:
        """
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.close)
        menubar.add_cascade(label="File", menu=filemenu)

    def create_server_tabs(self):
        """
        Create the Notebook tab

        :return:
        """
        self.tabbed_server = ttk.Notebook(self)
        s = ttk.Style()
        s.configure('TNotebook.Tab',
                    font=(MENU_FONT_NAME, '{}'.format(MENU_FONT_SIZE- 3), 'normal'),
                    width = 1000,
                    padding = 15
        )
        self.tabbed_server.pack(expand = 1, fill ="both")

    # This is core to the tkinter update
    async def updater(self, interval):
        """
        This run the tkinter updates for screen element events.

        :param interval:
        :return:
        """
        while True:
            self.update()
            await asyncio.sleep(interval)

    async def run_rcon_updates(self, interval=5):
        """
        This runs the

        :param interval:
        :return:
        """
        logger.info("Starting Initial update")
        await asyncio.gather(*[rcon_server_frame.exec_rcon_update() for rcon_server_frame in self.rcon_server_frames])

        while await asyncio.sleep(interval, True):
            logger.info("Running update")
            await asyncio.gather(
                *[rcon_server_frame.exec_rcon_update() for rcon_server_frame in self.rcon_server_frames])
            logger.info("Finishing update")

    def add_new_server_frame(self, rcon_host=None, rcon_port=None, rcon_pass=None, rcon_name=None):
        """
        CAlling this method with rcon creds registers a SingleServerFrame with this app which will then be
        included in the update cycle

        :param rcon_host:
        :param rcon_port:
        :param rcon_pass:
        :return:
        """
        single_frame = SingleServerFrame(master=self.tabbed_server, loop=self.loop, rcon_host=rcon_host,
                                         rcon_port=rcon_port, rcon_pass=rcon_pass)
        self.tabbed_server.add(single_frame, text=rcon_name)
        self.rcon_server_frames.append(single_frame)

    def close(self):
        """
        This destory all the perpetually running tasks.

        :return:
        """
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.destroy()