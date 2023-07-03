"""
Module for the EX-IOExpander page view
"""

# Import Python modules
import customtkinter as ctk
import logging

# Import local modules
from .common_widgets import WindowLayout
from .product_details import product_details as pd
from .file_manager import FileManager as fm


class EXIOExpander(WindowLayout):
    """
    Class for the EX-IOExpander view
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Initialise view
        """
        super().__init__(parent, *args, **kwargs)

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start view")

        # Get the local directory to work in
        self.product = "ex_ioexpander"
        self.product_name = pd[self.product]["product_name"]
        local_repo_dir = pd[self.product]["repo_name"].split("/")[1]
        self.ex_commandstation_dir = fm.get_install_dir(local_repo_dir)

        # Set up title
        self.set_title_logo(pd[self.product]["product_logo"])
        self.set_title_text("Install EX-IOExpander")

        # Set up next/back buttons
        self.next_back.set_back_text("Select Version")
        self.next_back.set_back_command(lambda view="select_version_config",
                                        product="ex_ioexpander": parent.switch_view(view, product))
        self.next_back.set_next_text("Configuration")
        self.next_back.set_next_command(None)
        self.next_back.hide_monitor_button()

        # Set up and grid container frames
        self.config_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.config_frame.grid(column=0, row=0, sticky="nsew")

        # Setup the screen
        self.setup_config_frame()

    def set_product_version(self, version, major=None, minor=None, patch=None):
        """
        Function to be called by the switch_frame function to set the chosen version

        This allows configuration options to be set based on the chosen version

        Eg.
        if self.product_major_version >=4 and self.product_minor_version >= 2:
            function_enables_track_manager()
        else:
            function_disables_track_manager()
        """
        self.product_version_name = version
        if major is not None:
            self.product_major_version = major
            if minor is not None:
                self.product_minor_version = minor
                if patch is not None:
                    self.product_patch_version = patch

    def setup_config_frame(self):
        """
        Setup the container frame for configuration options
        """
        grid_options = {"padx": 5, "pady": 5}

        self.i2c_address = ctk.StringVar(self, value=65)
        self.i2c_address_frame = ctk.CTkFrame(self.config_frame, border_width=0, fg_color="#E5E5E5")
        self.i2c_address_label = ctk.CTkLabel(self.i2c_address_frame, text="Select WiFi channel:")
        self.i2c_address_minus = ctk.CTkButton(self.i2c_address_frame, text="-", width=30,
                                               command=self.decrement_address)
        self.i2c_address_plus = ctk.CTkButton(self.i2c_address_frame, text="+", width=30,
                                              command=self.increment_address)
        self.i2c_address_entry = ctk.CTkEntry(self.i2c_address_frame, textvariable=self.i2c_address,
                                              width=30, fg_color="white", justify="center")
        self.i2c_address_frame.grid(column=0, row=0, **grid_options)

    def decrement_address(self):
        """
        Function to decrement the I2C address
        """
        value = int(self.i2c_address.get())
        if value > 8:
            value -= 1
            self.i2c_address.set(value)

    def increment_address(self):
        """
        Function to increment the I2C address
        """
        value = int(self.i2c_address.get())
        if value < 77:
            value += 1
            self.i2c_address.set(value)
