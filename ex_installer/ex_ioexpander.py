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

    instruction_text = ("Select the appropriate options on this page to suit the hardware devices you are using with " +
                        "your EX-IOExpander device.\n\n")

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

        Default config parameters from myConfig.example.h:
        - #define I2C_ADDRESS 0x65
        - // #define DIAG
        - #define DIAG_CONFIG_DELAY 5
        - // #define TEST_MODE ANALOGUE_TEST
        - // #define TEST_MODE INPUT_TEST
        - // #define TEST_MODE OUTPUT_TEST
        - // #define TEST_MODE PULLUP_TEST
        - // #define DISABLE_I2C_PULLUPS
        """
        grid_options = {"padx": 5, "pady": 5}
        self.config_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.config_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.instruction_label = ctk.CTkLabel(self.config_frame, text=self.instruction_text,
                                              wraplength=780)

        # Create I2C widgets
        self.i2c_address = ctk.StringVar(self, value=65)
        self.i2c_address_frame = ctk.CTkFrame(self.config_frame, border_width=0, fg_color="#E5E5E5")
        self.i2c_address_label = ctk.CTkLabel(self.i2c_address_frame, text="Set I2C address:")
        self.i2c_address_minus = ctk.CTkButton(self.i2c_address_frame, text="-", width=30,
                                               command=self.decrement_address)
        self.i2c_entry_frame = ctk.CTkFrame(self.i2c_address_frame, border_width=2, border_color="#00A3B9")
        self.i2c_0x_label = ctk.CTkLabel(self.i2c_entry_frame, text="0x", font=self.instruction_font,
                                         anchor="e", width=20, padx=0, pady=0)
        self.i2c_address_entry = ctk.CTkEntry(self.i2c_entry_frame, textvariable=self.i2c_address,
                                              width=28, fg_color="white", border_width=0,
                                              font=self.instruction_font)
        self.i2c_address_plus = ctk.CTkButton(self.i2c_address_frame, text="+", width=30,
                                              command=self.increment_address)
        self.disable_pullups_switch = ctk.CTkSwitch(self.config_frame, onvalue="on", offvalue="off")

        # Layout I2C address frame
        self.i2c_address_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.i2c_address_frame.grid_rowconfigure(0, weight=1)
        self.i2c_entry_frame.grid_columnconfigure((0, 1), weight=1)
        self.i2c_entry_frame.grid_rowconfigure(0, weight=1)
        self.i2c_address_label.grid(column=0, row=0, **grid_options)
        self.i2c_address_minus.grid(column=1, row=0, padx=(5, 0))
        self.i2c_0x_label.grid(column=0, row=0, sticky="e")
        self.i2c_address_entry.grid(column=1, row=0)
        self.i2c_entry_frame.grid(column=2, row=0)
        self.i2c_address_plus.grid(column=3, row=0, sticky="w", padx=(0, 5))

        # Create diagnostic setting widgets
        self.enable_diag_switch = ctk.CTkSwitch(self.config_frame, text="Enable diagnostic output",
                                                onvalue="on", offvalue="off")
        self.diag_delay_label = ctk.CTkLabel(self.config_frame, text="Set diagnostic display frequence in seconds:",
                                             font=self.instruction_font)
        self.diag_delay_entry = ctk.CTkEntry(self.config_frame)

        # Create test widgets
        self.test_frame = ctk.CTkFrame(self.config_frame)
        self.analogue_switch = ctk.CTkSwitch(self.test_frame, text="Enable analogue input pin testing",
                                             onvalue="on", offvalue="off")
        self.input_switch = ctk.CTkSwitch(self.test_frame, text="Enable digital input pin testing (no pullups)",
                                          onvalue="on", offvalue="off")
        self.output_switch = ctk.CTkSwitch(self.test_frame, text="Enable digital output pin testing",
                                           onvalue="on", offvalue="off")
        self.pullup_switch = ctk.CTkSwitch(self.test_frame, text="Enable digital input pin testing (with pullups)",
                                           onvalue="on", offvalue="off")

        # Layout test frame widgets
        self.test_frame.grid_columnconfigure((0, 1), weight=1)
        self.test_frame.grid_rowconfigure((0, 1), weight=1)
        self.input_switch.grid(column=0, row=0, **grid_options)
        self.analogue_switch.grid(column=1, row=0, **grid_options)
        self.pullup_switch.grid(column=0, row=1, **grid_options)
        self.output_switch.grid(column=1, row=1, **grid_options)

        # Layout config frame
        self.instruction_label.grid(column=0, row=0, columnspan=3, **grid_options)
        self.i2c_address_frame.grid(column=0, row=1, columnspan=3, **grid_options)
        self.enable_diag_switch.grid(column=0, row=2, **grid_options)
        self.diag_delay_label.grid(column=1, row=2, **grid_options)
        self.diag_delay_entry.grid(column=2, row=2, **grid_options)
        self.test_frame.grid(column=0, row=3, columnspan=3, **grid_options)

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
