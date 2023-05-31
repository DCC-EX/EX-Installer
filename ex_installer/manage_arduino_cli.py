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
        """
        Set up the Manage Arduino CLI view
        """
        super().__init__(parent, *args, **kwargs)

        # Set title and logo
        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Manage the Arduino CLI")

        # Set up next and back buttons
        self.next_back.show_back()
        self.next_back.set_back_text("Welcome")
        self.next_back.set_back_command(lambda view="welcome": parent.switch_view(view))

        self.next_back.set_next_text("Select your device")
        self.next_back.set_next_command(lambda view="select_device": parent.switch_view(view))

        # Create, grid, and configure container frame
        self.select_product_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.select_product_frame.grid(column=0, row=0, sticky="nsew")
        self.select_product_frame.grid_columnconfigure(0, weight=1)
        self.select_product_frame.grid_rowconfigure(0, weight=1)

        # Create install label and manage CLI button
        self.instruction_label = ctk.CTkLabel(self.select_product_frame,
                                              text="The Arduino CLI is currently not installed on your system.\n\n"
                                              + "In order to be able to upload software to your device, this "
                                              + "will need to be installed.\n\n"
                                              + "Click the <Install Arduino CLI> button below to install it")
        self.manage_cli_button = ctk.CTkButton(self.select_product_frame, width=200, height=30,
                                               text="Install Arduino CLI", font=self.button_font)

        # Create frame and widgets for additional platform support
        self.extra_platforms_frame = ctk.CTkFrame(self.select_product_frame)
        for index, platform in enumerate(self.acli.extra_platforms):
            switch = ctk.CTkSwitch(self.extra_platforms_frame, text=platform)
            switch.grid(column=0, row=index+1, sticky="w")

        self.extra_platforms_frame.grid(column=1, row=1)

        # Layout frame
        self.instruction_label.grid(column=0, row=0, columnspan=2)
        self.manage_cli_button.grid(column=0, row=1)
