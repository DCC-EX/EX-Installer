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

        # Set up title
        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Welcome to EX-Installer")

        # Set up next/back buttons
        self.next_back.hide_back()
        self.next_back.set_next_text("Manage Arduino CLI")
        self.next_back.set_next_command(lambda view="manage_arduino_cli": parent.switch_view(view))

        # Create and configure welcome container
        self.welcome_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.welcome_frame.grid(column=0, row=0, sticky="nsew")
        self.welcome_frame.grid_columnconfigure(0, weight=1)
        self.welcome_frame.grid_rowconfigure(0, weight=1)

        # Create welcome label
        self.welcome_label = ctk.CTkLabel(self.welcome_frame, wraplength=780,
                                          text=("The DCC-EX team have provided EX-Installer to make it as easy as " +
                                                "possible to get up and running with our various products.\n\n"),
                                          font=self.instruction_font)

        # Layout frame
        self.welcome_label.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")
