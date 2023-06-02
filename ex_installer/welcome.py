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

        # Set up event handlers
        event_callbacks = {
            "<<Check_Arduino_CLI>>": self.check_arduino_cli
        }
        for sequence, callback in event_callbacks.items():
            self.bind_class("bind_events", sequence, callback)
        new_tags = self.bindtags() + ("bind_events",)
        self.bindtags(new_tags)

        # Set up next/back buttons
        self.next_back.hide_back()
        self.next_back.set_next_text("Manage Arduino CLI")
        self.next_back.set_next_command(lambda event="next_button": self.check_arduino_cli(event))

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

    def check_arduino_cli(self, event):
        """
        Function to check if the Arduino CLI is installed and if so, what version it is

        On completion, will move to the Manage Arduino CLI screen
        """
        if event == "next_button":
            self.next_back.disable_next()
            self.process_start("check_arduino_cli", "Checking for Arduino CLI", "Check_Arduino_CLI")
            self.acli.get_version(self.acli.cli_file_path(), self.queue)
        elif self.process_phase == "check_arduino_cli":
            if self.process_status == "success":
                self.process_stop()
                self.master.switch_view("manage_arduino_cli")
            elif self.process_status == "error":
                self.process_error("Failed to check if the Arduino CLI is installed")
            else:
                self.process_error("An unknown error occurred")
