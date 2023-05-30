"""
Module for the Select Device page view
"""

# Import Python modules
import customtkinter as ctk

# Import local modules
from .common_widgets import WindowLayout
from . import images


class SelectDevice(WindowLayout):
    """
    Class for the Welcome view
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Select your device")

        self.next_back.set_back_text("Manage Arduino CLI")
        self.next_back.set_back_command(lambda view="manage_arduino_cli": parent.switch_view(view))

        self.next_back.set_next_text("Select product to install")
        self.next_back.set_next_command(lambda view="select_product": parent.switch_view(view))

        self.select_device_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.select_device_frame.grid(column=0, row=0, sticky="nsew")
