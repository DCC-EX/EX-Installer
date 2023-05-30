"""
Module for managing the Arduino CLI page view
"""

# Import Python modules
import customtkinter as ctk

# Import local modules
from .common_widgets import WindowLayout
from . import images


class ManageArduinoCLI(WindowLayout):
    """
    Class for the Manage Arduino CLI view
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Manage the Arduino CLI")

        self.next_back.show_back()
        self.next_back.set_back_text("Welcome")
        self.next_back.set_back_command(lambda view="welcome": parent.switch_view(view))

        self.next_back.set_next_text("Select your device")
        self.next_back.set_next_command(lambda view="select_device": parent.switch_view(view))

        self.select_product_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.select_product_frame.grid(column=0, row=0, sticky="nsew")
