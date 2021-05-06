
import platform
import tkinter as tk

from tkinter import ttk


###############################################################
# Class to modify a button so you know when you are hovering
# over it
###############################################################
class HoverButton(tk.Button):
    def __init__(self, master, button_colour="sky blue", **kw):
        tk.Button.__init__(self,master=master, **kw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.custom_colour = button_colour

    def on_enter(self, e):
        """
        When the mouse/VR pointer enters this button, this event is fired

        :param e: The incoming event object
        :return:
        """
        if platform.system() == "Darwin":  ### if its a Mac
            self['highlightbackground'] = self.custom_colour
        else:
            self['bg'] = self.custom_colour


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




class ScrollableFrame(ttk.LabelFrame):
    """
    I wanted a frame with scroll bars that i could add lots of content to.

    This is modified from https://blog.tecladocode.com/tkinter-scrollable-frames/

    Thank you Jose Salvatierra!

    Expands the canvas properly came from
    https://stackoverflow.com/questions/29319445/tkinter-how-to-get-frame-in-canvas-window-to-expand-to-the-size-of-the-canvas


    """
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas,relief="raised", borderwidth=10)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame.bind("<Configure>", self.OnFrameConfigure)
        self.canvas.bind('<Configure>', self.FrameWidth)

        self.canvas.pack(side="left", fill="both", expand=tk.YES)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)


    def FrameWidth(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def OnFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")