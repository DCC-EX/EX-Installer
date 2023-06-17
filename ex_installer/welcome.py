"""
Module for the Welcome page view
"""

# Import Python modules
import customtkinter as ctk
import logging

# Import local modules
from .common_widgets import WindowLayout
from . import images


class Welcome(WindowLayout):
    """
    Class for the Welcome view
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start view")

        # Set up title
        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Welcome to EX-Installer")

        # Set up next/back buttons
        self.next_back.hide_back()
        self.next_back.set_next_text("Manage Arduino CLI")
        self.next_back.set_next_command(lambda view="manage_arduino_cli": parent.switch_view(view))
        self.next_back.hide_log_button()

        # Create and configure welcome container
        self.welcome_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.welcome_frame.grid(column=0, row=0, sticky="nsew")
        self.welcome_frame.grid_columnconfigure(0, weight=1)
        self.welcome_frame.grid_rowconfigure((0, 20), weight=1)

        # Create welcome label
        self.welcome_label = ctk.CTkLabel(self.welcome_frame, wraplength=780,
                                          text=("The DCC-EX team have provided EX-Installer to make it as easy as " +
                                                "possible to get up and running with our various products.\n\n"),
                                          font=self.instruction_font)
        self.version_label = ctk.CTkLabel(self.welcome_frame, text=(f"Version {self.app_version}"),
                                          font=self.instruction_font)

        # Debug switch
        self.debug_switch = ctk.CTkSwitch(self.welcome_frame, text="Enable debug logging",
                                          onvalue="on", offvalue="off", command=self.set_debug)

        # Layout frame
        self.welcome_label.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")
        self.version_label.grid(column=0, row=20, padx=5, pady=5, sticky="s")
        self.debug_switch.grid(column=0, row=20, padx=5, pady=5, sticky="se")

    def set_debug(self):
        """
        Function to enable or disable debug logging
        """
        if self.debug_switch.get() == "on":
            self.log.parent.setLevel(logging.DEBUG)
        elif self.debug_switch.get() == "off":
            self.log.parent.setLevel(logging.WARNING)
