"""
Module for the Welcome page view
"""

# Import Python modules
import customtkinter as ctk

# Import local modules
from .common_widgets import WindowLayout
from . import images


class Welcome(WindowLayout):
    """
    Class for the Welcome view
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Welcome to EX-Installer")

        self.next_back.hide_back()

        self.next_back.set_next_text("Manage Arduino CLI")
        self.next_back.set_next_command(lambda view="manage_arduino_cli": parent.switch_view(view))

        self.welcome_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.welcome_frame.grid(column=0, row=0, sticky="nsew")
