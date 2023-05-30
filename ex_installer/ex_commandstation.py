"""
Module for the EX-CommandStation page view
"""

# Import Python modules
import customtkinter as ctk

# Import local modules
from .common_widgets import WindowLayout
from . import images


class EXCommandStation(WindowLayout):
    """
    Class for the EX-CommandStation view
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.set_title_logo(images.EX_COMMANDSTATION_LOGO)
        self.set_title_text("Install EX-CommandStation")

        self.next_back.set_back_text("Select Product")
        self.next_back.set_back_command(lambda view="select_product": parent.switch_view(view))

        self.next_back.set_next_text("Upload")
        self.next_back.set_next_command(None)

        self.ex_commandstation_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.ex_commandstation_frame.grid(column=0, row=0, sticky="nsew")
