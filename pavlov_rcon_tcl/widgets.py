
import platform
import tkinter as tk


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
        """
        When the mouse/VR pointer enters this button, this event is fired

        :param e: The incoming event object
        :return:
        """
        if platform.system() == "Darwin":  ### if its a Mac
            self['highlightbackground'] = "green"
        else:
            self['bg'] = "green"


    def on_leave(self, e):
        """
        When the mouse/VR pointer leaves the button, execute this

        :param e: The incoming event object 
        :return:
        """
        if platform.system() == "Darwin":  ### if its a Mac
            self['highlightbackground'] = "SystemButtonFace"
        else:
            self['bg'] = "SystemButtonFace"