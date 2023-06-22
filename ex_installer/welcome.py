"""
Module for the Welcome page view
"""

# Import Python modules
import customtkinter as ctk
import logging

# Import local modules
from .common_widgets import WindowLayout, FormattedTextbox
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

        self.welcome_textbox = FormattedTextbox(self.welcome_frame, wrap="word", width=700, height=360,
                                                activate_scrollbars=False, font=self.instruction_font)
        self.version_label = ctk.CTkLabel(self.welcome_frame, text=(f"Version {self.app_version}"),
                                          font=self.instruction_font)

        # Debug switch
        self.debug_switch = ctk.CTkSwitch(self.welcome_frame, text="Enable debug logging",
                                          onvalue="on", offvalue="off", command=self.set_debug)

        # Layout frame
        grid_options = {"padx": 5, "pady": 5}

        self.welcome_textbox.grid(column=0, row=0, **grid_options)
        self.version_label.grid(column=0, row=20, sticky="s", **grid_options)
        self.debug_switch.grid(column=0, row=20, sticky="se", **grid_options)

        self.set_text()

    def set_text(self):
        self.welcome_textbox.insert(
            "insert",
            "EX-Installer simplifies the process of setting up the various software products " +
            "created by the DCC-EX team.\n\n" +
            "As our products provide for a large number of different configurations and allow a number of optional " +
            "features, we need to ask you some questions about what hardware you have and what options you want " +
            "to enable.\n\n" +
            "Steps:\n\n"
        )
        bullet_list = [
            "We first need to install the Arduino Command Line Interface (CLI).\n",
            "You then need to select the type of Arduino you wish to install on.\n",
            "Next you will select which of our products you wish to install.\n",
            "From here you can choose some of the options for the software and apply additional configuration.\n",
            "Finally, you will load the software on to your Arduino.\n\n"
        ]
        for item in bullet_list:
            self.welcome_textbox.insert_bullet("insert", item)

        self.welcome_textbox.insert(
            "insert",
            "The following pages you lead you through this process.\n\n" +
            "To continue, click the 'Manage Arduino CLI' button below and follow the instructions on each page.\n\n" +
            "(The button on the lower right on each page will move you to the next step. The button on the lower " +
            "left of each page will allow you to go back and change your selections.)\n\n"
        )
        self.welcome_textbox.configure(state="disabled")

    def set_debug(self):
        """
        Function to enable or disable debug logging
        """
        if self.debug_switch.get() == "on":
            self.log.parent.setLevel(logging.DEBUG)
        elif self.debug_switch.get() == "off":
            self.log.parent.setLevel(logging.WARNING)
