"""
Module for the EX-CommandStation page view

© 2023, Peter Cole. All rights reserved.
© 2023, M Steve Todd. All rights reserved.

This file is part of EX-Installer.

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

It is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CommandStation.  If not, see <https://www.gnu.org/licenses/>.
"""

# Import Python modules
import customtkinter as ctk
import logging
import re

# Import local modules
from .common_widgets import WindowLayout, CreateToolTip
from .product_details import product_details as pd
from .file_manager import FileManager as fm


class EXCommandStation(WindowLayout):
    """
    Class for the EX-CommandStation view
    """

    hardware_text = ("Select the appropriate options on this page to suit the hardware devices you are using with " +
                     "your EX-CommandStation device.\n\n")

    # List of supported displays and config lines for config.h
    supported_displays = {
        "LCD 16 columns x 2 rows": "#define LCD_DRIVER 0x27,16,2",
        "LCD 20 columns x 4 rows": "#define LCD_DRIVER 0x27,20,4",
        "OLED 128 x 32": "#define OLED_DRIVER 128,32",
        "OLED 128 x 64": "#define OLED_DRIVER 128,64"
    }

    # List of default config options to include in config.h
    default_config_options = [
        '#define IP_PORT 2560\n',
        '#define WIFI_HOSTNAME "dccex"\n',
        '#define SCROLLMODE 1\n'
    ]
    # List of default myAutomation options to include in myAutomation.h (none for now)
    default_myAutomation_options = []

    # List of TrakManager modes for selection to myAutomation.h
    trackmanager_modes = {
        "MAIN": "MAIN",
        "PROG": "PROG",
        "DC": "DC",
        "DCX": "DCX",
        "OFF": "OFF",
    }

    def __init__(self, parent, *args, **kwargs):
        """
        Initialise view
        """
        super().__init__(parent, *args, **kwargs)

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start view")

        # Get the local directory to work in
        self.product = "ex_commandstation"
        self.product_name = pd[self.product]["product_name"]
        local_repo_dir = pd[self.product]["repo_name"].split("/")[1]
        self.ex_commandstation_dir = fm.get_install_dir(local_repo_dir)

        # Set up title
        self.set_title_logo(pd[self.product]["product_logo"])
        self.set_title_text("Install EX-CommandStation")

        # Set up next/back buttons
        self.next_back.set_back_text("Select Version")
        self.next_back.set_back_command(lambda view="select_version_config",
                                        product="ex_commandstation": parent.switch_view(view, product))
        self.next_back.set_next_text("Configuration")
        self.next_back.set_next_command(None)
        self.next_back.hide_monitor_button()

        # Set up and grid container frames
        self.config_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.config_frame.grid(column=0, row=0, sticky="nsew")

        # Set up frame contents
        self.setup_config_frame()
        self.display_config_screen()
        self.next_back.hide_log_button()

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
        # if self.product_major_version >= 4 and self.product_minor_version >= 2:
        #     self.track_modes_switch.grid()
        # else:
        #     self.track_modes_switch.deselect()  # make sure it's off
        #     self.track_modes_switch.grid_remove()
        self.set_track_modes()

    def setup_config_frame(self):
        """
        Setup the container frame for configuration options
        """
        grid_options = {"padx": 5, "pady": 5}

        # Text for tooltips
        motor_tip = ("You need to select the appropriate motor driver used by your CommandStation. If you are " +
                     "unsure which to choose, click this tip to be redirected to our website for further help.")
        display_tip = ("Click this box to be redirected to our website for help selecting the correct display type. " +
                       "If you have no display attached to your CommandStation, leave this disabled.")
        wifi_tip = ("If you have added WiFi capability to your CommandStation, you will need to select the correct " +
                    "options to configure it as an access point (it will run as its own WiFi network you can connect " +
                    "to) or to connect it to your existing WiFi network. Click this tip to be redirected to our " +
                    "website for further information.")
        ethernet_tip = ("If you have added Ethernet capability to your CommandStation, enable this option (this " +
                        "will disable WiFi). Click this tip to be redirected to our website for further information.")
        advanced_tip = ("If you need to specify additional options not available on this screen, enable this option " +
                        "to edit the config files directly on the following screen. It is recommended not to touch " +
                        "these unless you're comfortable you know what you're doing.")
        track_tip = ("To make use of the new TrackManager feature, you will need to enable this option and set the " +
                     "appropriate mode for each motor driver output. Click this tip to be redirected to our website " +
                     "for further information.")
        power_tip = ("To enable track power to be on during startup, enable this option. Note that it will also join " +
                     "the programming and main tracks.")

        # Set up hardware instruction label
        self.hardware_label = ctk.CTkLabel(self.config_frame, text=self.hardware_text,
                                           wraplength=780, font=self.instruction_font)

        # Setup tabview for config options
        self.config_tabview = ctk.CTkTabview(self.config_frame, border_width=2,
                                             segmented_button_fg_color="#00A3B9",
                                             segmented_button_unselected_color="#00A3B9",
                                             segmented_button_selected_color="#00353D",
                                             segmented_button_selected_hover_color="#017E8F",
                                             text_color="white")
        tab_list = [
            "General",
            "Display Options",
            "WiFi Options",
            "TrackManager Config"
        ]
        for tab in tab_list:
            self.config_tabview.add(tab)
            self.config_tabview.tab(tab).grid_columnconfigure(0, weight=1)
            self.config_tabview.tab(tab).grid_rowconfigure(0, weight=1)

        # Tab frames
        tab_frame_options = {"column": 0, "row": 0, "sticky": "nsew"}
        self.general_tab_frame = ctk.CTkFrame(self.config_tabview.tab("General"), border_width=0)
        self.general_tab_frame.grid(**tab_frame_options)
        self.display_tab_frame = ctk.CTkFrame(self.config_tabview.tab("Display Options"), border_width=0)
        self.display_tab_frame.grid(**tab_frame_options)
        self.wifi_tab_frame = ctk.CTkFrame(self.config_tabview.tab("WiFi Options"), border_width=0)
        self.wifi_tab_frame.grid(**tab_frame_options)
        self.track_tab_frame = ctk.CTkFrame(self.config_tabview.tab("TrackManager Config"), border_width=0)
        self.track_tab_frame.grid(**tab_frame_options)

        # Set up motor driver widgets
        self.motor_driver_label = ctk.CTkLabel(self.general_tab_frame, text="Select your motor driver",
                                               font=self.instruction_font)
        self.motor_driver_combo = ctk.CTkComboBox(self.general_tab_frame, values=["Select motor driver"],
                                                  width=300, command=self.check_motor_driver)
        CreateToolTip(self.motor_driver_combo, motor_tip,
                      "https://dcc-ex.com/reference/hardware/motor-boards.html")

        # Set up display widgets
        self.display_enabled = ctk.StringVar(self, value="off")
        self.display_switch = ctk.CTkSwitch(self.general_tab_frame, text="I have a display", width=150,
                                            onvalue="on", offvalue="off", variable=self.display_enabled,
                                            command=self.set_display, font=self.instruction_font)
        CreateToolTip(self.display_switch, display_tip,
                      "https://dcc-ex.com/reference/hardware/i2c-displays.html")
        self.display_combo = ctk.CTkComboBox(self.display_tab_frame, values=list(self.supported_displays),
                                             width=300)

        # Set up WiFi widgets
        self.wifi_type = ctk.IntVar(self, value=0)
        self.wifi_channel = ctk.StringVar(self, value=1)
        self.wifi_enabled = ctk.StringVar(self, value="off")
        self.wifi_frame = ctk.CTkFrame(self.wifi_tab_frame, border_width=0)
        self.wifi_switch = ctk.CTkSwitch(self.general_tab_frame, text="I have WiFi", width=150,
                                         onvalue="on", offvalue="off", variable=self.wifi_enabled,
                                         command=self.set_wifi, font=self.instruction_font)
        CreateToolTip(self.wifi_switch, wifi_tip,
                      "https://dcc-ex.com/ex-commandstation/advanced-setup/supported-wifi/index.html")
        self.wifi_options_frame = ctk.CTkFrame(self.wifi_frame,
                                               border_width=2,
                                               fg_color="#E5E5E5")
        self.wifi_ap_radio = ctk.CTkRadioButton(self.wifi_options_frame,
                                                text="Use my EX-CommandStation as an access point",
                                                variable=self.wifi_type,
                                                command=self.set_wifi_widgets,
                                                value=0)
        self.wifi_st_radio = ctk.CTkRadioButton(self.wifi_options_frame,
                                                text="Connect my EX-CommandStation to my existing wireless network",
                                                variable=self.wifi_type,
                                                command=self.set_wifi_widgets,
                                                value=1)
        self.wifi_ssid_label = ctk.CTkLabel(self.wifi_options_frame, text="WiFi SSID:")
        self.wifi_ssid_entry = ctk.CTkEntry(self.wifi_options_frame,  # textvariable=self.wifi_ssid,
                                            placeholder_text="Enter your WiFi SSID/name",
                                            width=200, fg_color="white")
        self.wifi_pwd_label = ctk.CTkLabel(self.wifi_options_frame, text="WiFi Password:")
        self.wifi_pwd_entry = ctk.CTkEntry(self.wifi_options_frame,  # textvariable=self.wifi_pwd,
                                           placeholder_text="Enter your WiFi password",
                                           width=200, fg_color="white")
        self.wifi_channel_frame = ctk.CTkFrame(self.wifi_options_frame, border_width=0, fg_color="#E5E5E5")
        self.wifi_channel_label = ctk.CTkLabel(self.wifi_channel_frame, text="Select WiFi channel:")
        self.wifi_channel_minus = ctk.CTkButton(self.wifi_channel_frame, text="-", width=30,
                                                command=self.decrement_channel)
        self.wifi_channel_plus = ctk.CTkButton(self.wifi_channel_frame, text="+", width=30,
                                               command=self.increment_channel)
        self.wifi_channel_entry = ctk.CTkEntry(self.wifi_channel_frame, textvariable=self.wifi_channel,
                                               width=30, fg_color="white", state="disabled", justify="center")

        # Ethernet switch
        self.ethernet_enabled = ctk.StringVar(self, value="off")
        self.ethernet_switch = ctk.CTkSwitch(self.general_tab_frame, text="I have ethernet", width=150,
                                             onvalue="on", offvalue="off", variable=self.ethernet_enabled,
                                             command=self.set_ethernet, font=self.instruction_font)
        CreateToolTip(self.ethernet_switch, ethernet_tip,
                      "https://dcc-ex.com/reference/hardware/ethernet-boards.html")

        # Track Manager Options
        self.track_modes_enabled = ctk.StringVar(self, value="off")
        self.track_modes_switch = ctk.CTkSwitch(self.general_tab_frame, text="Set track modes", width=150,
                                                onvalue="on", offvalue="off", variable=self.track_modes_enabled,
                                                command=self.set_track_modes, font=self.instruction_font)
        CreateToolTip(self.track_modes_switch, track_tip,
                      "https://dcc-ex.com/under-development/track-manager.html")
        self.track_modes_frame = ctk.CTkFrame(self.track_tab_frame, border_width=2, fg_color="#E5E5E5")
        self.track_a_label = ctk.CTkLabel(self.track_modes_frame, text="Track A:")
        self.track_a_combo = ctk.CTkComboBox(self.track_modes_frame, values=list(self.trackmanager_modes),
                                             width=100)
        self.track_b_label = ctk.CTkLabel(self.track_modes_frame, text="Track B:")
        self.track_b_combo = ctk.CTkComboBox(self.track_modes_frame, values=list(self.trackmanager_modes),
                                             width=100)
        self.track_b_combo.set("MAIN")  # default to MAIN and PROG
        self.track_b_combo.set("PROG")

        # Set track power on startup
        self.power_on_switch = ctk.CTkSwitch(self.general_tab_frame, text="Power on", width=150,
                                             onvalue="on", offvalue="off", font=self.instruction_font)
        CreateToolTip(self.power_on_switch, power_tip)

        # Advanced configuration option
        self.advanced_config_enabled = ctk.StringVar(self, value="off")
        self.advanced_config_switch = ctk.CTkSwitch(self.general_tab_frame, text="Advanced Config", width=150,
                                                    onvalue="on", offvalue="off", variable=self.advanced_config_enabled,
                                                    command=self.set_advanced_config, font=self.instruction_font)
        CreateToolTip(self.advanced_config_switch, advanced_tip)

        # Layout wifi_frame
        self.wifi_frame.grid_columnconfigure((0, 1), weight=1)
        self.wifi_frame.grid_rowconfigure(0, weight=1)
        self.wifi_options_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.wifi_options_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.wifi_channel_frame.grid_columnconfigure(0, weight=1)
        self.wifi_channel_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.wifi_options_frame.grid(column=1, row=0)
        self.wifi_ap_radio.grid(column=0, row=0, columnspan=4, sticky="w", **grid_options)
        self.wifi_st_radio.grid(column=0, row=1, columnspan=4, sticky="w", **grid_options)
        self.wifi_ssid_label.grid(column=0, row=2, **grid_options)
        self.wifi_ssid_entry.grid(column=1, row=2, **grid_options)
        self.wifi_pwd_label.grid(column=2, row=2, **grid_options)
        self.wifi_pwd_entry.grid(column=3, row=2, **grid_options)
        self.wifi_channel_frame.grid(column=0, row=2, **grid_options)
        self.wifi_channel_label.grid(column=0, row=0, **grid_options)
        self.wifi_channel_minus.grid(column=1, row=0, sticky="e")
        self.wifi_channel_entry.grid(column=2, row=0)
        self.wifi_channel_plus.grid(column=3, row=0, sticky="w", padx=(0, 5))

        # layout track_frame
        self.track_a_label.grid(column=0, row=0, stick="e", **grid_options)
        self.track_a_combo.grid(column=1, row=0, sticky="w", **grid_options)
        self.track_b_label.grid(column=0, row=1, stick="e", **grid_options)
        self.track_b_combo.grid(column=1, row=1, sticky="w", **grid_options)

        # Layout general config_frame
        self.config_frame.grid_columnconfigure(0, weight=1)
        self.config_frame.grid_rowconfigure(1, weight=1)
        self.hardware_label.grid(column=0, row=0, **grid_options)
        self.config_tabview.grid(column=0, row=1, sticky="nsew", **grid_options)
        self.motor_driver_label.grid(column=0, row=0, stick="e", **grid_options)
        self.motor_driver_combo.grid(column=1, row=0, sticky="w", **grid_options)
        self.display_switch.grid(column=0, row=2, **grid_options)
        self.wifi_switch.grid(column=0, row=3, **grid_options)
        self.ethernet_switch.grid(column=0, row=4, **grid_options)
        self.track_modes_switch.grid(column=0, row=5, **grid_options)
        self.power_on_switch.grid(column=0, row=6, **grid_options)
        
        # self.display_combo.grid(column=1, row=4, sticky="w", **grid_options)
        # self.wifi_frame.grid(column=1, row=5, sticky="w", **grid_options)
        # self.track_modes_frame.grid(column=1, row=7, sticky="w", **grid_options)
        self.advanced_config_switch.grid(column=1, row=7, columnspan=2, sticky="e", **grid_options)

    def set_display(self):
        """
        Sets display options on or off
        """
        if self.display_switch.get() == "on":
            self.display_combo.grid()
            self.log.debug("Display enabled")
        else:
            self.display_combo.grid_remove()
            self.log.debug("Display disabled")

    def set_track_modes(self):
        """
        Sets track mode options on or off
        """
        if self.track_modes_switch.get() == "on":
            self.track_modes_frame.grid()
            self.log.debug("Track modes frame shown")
        else:
            self.track_modes_frame.grid_remove()
            self.log.debug("Track modes frame hidden")

    def set_advanced_config(self):
        """
        Sets advanced config on or off, locally and globally
        """
        if self.advanced_config_switch.get() == "on":
            self.master.advanced_config = True
            self.next_back.set_next_text("Advanced Config")
            self.log.debug("Manual Edit enabled")
        else:
            self.master.advanced_config = False
            self.next_back.set_next_text("Compile and load")
            self.log.debug("Manual Edit disabled")

    def set_wifi(self):
        """
        Sets WiFi options on or off
        """
        if self.wifi_switch.get() == "on":
            if self.ethernet_switch.get() == "on":
                self.ethernet_switch.deselect()
            self.wifi_frame.grid()
            self.set_wifi_widgets()
            self.log.debug("WiFi enabled")
        else:
            self.wifi_frame.grid_remove()
            self.log.debug("WiFi disabled")

    def set_wifi_widgets(self):
        """
        Function to display correct widgets for WiFi config
        """
        if self.wifi_type.get() == 0:
            self.wifi_ssid_label.grid_remove()
            self.wifi_ssid_entry.grid_remove()
            self.wifi_channel_frame.grid()
            if self.wifi_pwd_entry.get() == "":
                self.wifi_pwd_entry.configure(placeholder_text="Custom WiFi password")
            self.log.debug("WiFi AP mode selected")
        elif self.wifi_type.get() == 1:
            self.wifi_ssid_label.grid()
            self.wifi_ssid_entry.grid()
            self.wifi_channel_frame.grid_remove()
            if self.wifi_pwd_entry.get() == "":
                self.wifi_pwd_entry.configure(placeholder_text="Enter your WiFi password")
            self.log.debug("WiFi ST mode selected")

    def set_ethernet(self):
        """
        Function to enable Ethernet support
        """
        if self.ethernet_switch.get() == "on":
            if self.wifi_switch.get() == "on":
                self.wifi_switch.deselect()
                self.set_wifi()
            self.log.debug("Ethernet enabled")
        else:
            self.log.debug("Ethernet disabled")

    def decrement_channel(self):
        """
        Function to decrement the WiFi channel
        """
        value = int(self.wifi_channel.get())
        if value > 1:
            value -= 1
            self.wifi_channel.set(value)

    def increment_channel(self):
        """
        Function to increment the WiFi channel
        """
        value = int(self.wifi_channel.get())
        if value < 11:
            value += 1
            self.wifi_channel.set(value)

    def display_config_screen(self):
        """
        Displays the configuration options frame
        """
        self.config_frame.grid()
        self.set_display()
        self.set_wifi()
        self.set_track_modes()
        self.set_advanced_config()
        self.get_motor_drivers()
        self.check_motor_driver(self.motor_driver_combo.get())
        self.next_back.set_next_text("Compile and load")
        self.next_back.set_next_command(self.create_config_files)
        self.next_back.set_back_text("Select version")
        self.next_back.set_back_command(lambda view="select_version_config",
                                        product=self.product: self.master.switch_view(view, product))

    def get_motor_drivers(self):
        """
        Function to read the defined motor driver definition from MotorDrivers.h
        """
        self.motordriver_list = []
        match = r'^.+?\s(.+?)\sF\(".+?"\).*$'
        definition_file = fm.get_filepath(self.ex_commandstation_dir, "MotorDrivers.h")
        def_list = fm.get_list_from_file(definition_file, match)
        if def_list:
            self.motordriver_list += def_list
            self.log.debug("Found motor driver list %s", def_list)
        else:
            self.log.error("Could not get list of motor drivers")
        self.motor_driver_combo.configure(values=self.motordriver_list)

    def check_motor_driver(self, value):
        """
        Function ensure a motor driver has been selected
        """
        if value == "Select motor driver":
            self.next_back.disable_next()
        else:
            self.next_back.enable_next()

    def check_invalid_wifi_password(self):
        """
        Checks for an invalid WiFi password

        If in access point mode:
        - Must be between 8 and 64 characters

        In either mode, must not contain \ or "  # noqa: W605

        Returns tuple of (True|False, message)
        """
        error_list = []
        invalid = False
        if self.wifi_type.get() == 0:
            if len(self.wifi_pwd_entry.get()) < 8 or len(self.wifi_pwd_entry.get()) > 64:
                error_list.append("WiFi Password must be between 8 and 64 characters")
                invalid = True
        invalid_list = [r'\\', r'"']
        for character in invalid_list:
            if re.search(character, self.wifi_pwd_entry.get()):
                display = character.replace("\\\\", chr(92))
                error_list.append(f"WiFi password cannot contain {display}")
                invalid = True
        if len(error_list) > 0:
            message = ", ".join(error_list)
        else:
            message = None
        return (invalid, message)

    def generate_config(self):
        """
        Function to validate options and return any errors

        Validates all parameters have been set and generates config.h defines

        Returns a tuple of (True|False, error_list|config_list)
        """
        param_errors = []
        config_list = []
        if self.motor_driver_combo.get() == "Select motor driver":
            param_errors.append("Motor driver not set")
        else:
            line = "#define MOTOR_SHIELD_TYPE " + self.motor_driver_combo.get() + "\n"
            config_list.append(line)
        if self.display_switch.get() == "on":
            if not self.display_combo.get():
                param_errors.append("Display type not selected")
            else:
                line = self.supported_displays[self.display_combo.get()] + "\n"
                config_list.append(line)
        if self.wifi_switch.get() == "on":
            if self.wifi_type.get() == 0:
                config_list.append('#define WIFI_SSID "Your network name"\n')
                if self.wifi_pwd_entry.get() == "":
                    config_list.append('#define WIFI_PASSWORD "Your network passwd"\n')
                else:
                    invalid, issue = self.check_invalid_wifi_password()
                    if invalid:
                        param_errors.append(issue)
                    else:
                        line = '#define WIFI_PASSWORD "' + self.wifi_pwd_entry.get() + '"\n'
                        config_list.append(line)
            elif self.wifi_type.get() == 1:
                if self.wifi_ssid_entry.get() == "":
                    param_errors.append("WiFi SSID/name not set")
                else:
                    line = '#define WIFI_SSID "' + self.wifi_ssid_entry.get() + '"\n'
                    config_list.append(line)
                if self.wifi_pwd_entry.get() == "":
                    param_errors.append("WiFi password not set")
                else:
                    invalid, issue = self.check_invalid_wifi_password()
                    if invalid:
                        param_errors.append(issue)
                    else:
                        line = '#define WIFI_PASSWORD "' + self.wifi_pwd_entry.get() + '"\n'
                        config_list.append(line)
            if self.ethernet_switch.get() == "on":
                param_errors.append("Can not have both Ethernet and WiFi enabled")
            else:
                config_list.append("#define ENABLE_WIFI true\n")
            if int(self.wifi_channel.get()) < 1 or int(self.wifi_channel.get()) > 11:
                param_errors.append("WiFi channel must be from 1 to 11")
            else:
                line = "#define WIFI_CHANNEL " + self.wifi_channel.get() + "\n"
                config_list.append(line)
        if self.ethernet_switch.get() == "on":
            if self.wifi_switch.get() == "on":
                param_errors.append("Can not have both Ethernet and WiFi enabled")
            else:
                config_list.append("#define ENABLE_ETHERNET true\n")
        if len(param_errors) > 0:
            self.log.error("Missing parameters: %s", param_errors)
            return (False, param_errors)
        else:
            self.log.debug("Configuration options: %s", config_list)
            return (True, config_list)

    def generate_myAutomation(self):
        """
        Function to validate options and return any errors

        Validates all parameters have been set and generates myAutomation.h defines

        Returns a tuple of (True|False, error_list|config_list)
        """
        param_errors = []
        config_list = []

        # Enable join on startup if enabled
        if self.power_on_switch.get() == "on":
            config_list.append("AUTOSTART\n")
            config_list.append("JOIN\n")
            config_list.append("DONE\n\n")

        # write out trackmanager config, including roster entries if DCx
        if self.track_modes_enabled.get() == "on":
            if (self.track_a_combo.get().startswith("DC")):
                line = "AUTOSTART SETLOCO(1) SET_TRACK(A," + self.track_a_combo.get() + ") DONE\n"
                line += "ROSTER(1,\"DC TRACK A\",\"/* /\")\n"
            else:
                line = "AUTOSTART SET_TRACK(A," + self.track_a_combo.get() + ") DONE\n"
            config_list.append(line)
            if (self.track_b_combo.get().startswith("DC")):
                line = "AUTOSTART SETLOCO(2) SET_TRACK(B," + self.track_b_combo.get() + ") DONE\n"
                line += "ROSTER(2,\"DC TRACK B\",\"/* /\")\n"
            else:
                line = "AUTOSTART SET_TRACK(B," + self.track_b_combo.get() + ") DONE\n"
            config_list.append(line)

        if len(param_errors) > 0:
            self.log.error("Missing parameters: %s", param_errors)
            return (False, param_errors)
        else:
            self.log.debug("myAutomation options: %s", config_list)
            return (True, config_list)

    def create_config_files(self):
        """
        Function to create config.h and myAutomation.h files and progress to upload
        - Checks for file creation failures
        """
        (config, list) = self.generate_config()
        generate_myautomation = False
        if config:
            file_contents = [("// config.h - Generated by EX-Installer " +
                              f"v{self.app_version} for {self.product_name} " +
                              f"{self.product_version_name}\n\n")]
            file_contents += self.default_config_options
            file_contents += list
            config_file_path = fm.get_filepath(self.ex_commandstation_dir, "config.h")
            write_config = fm.write_config_file(config_file_path, file_contents)
            if write_config != config_file_path:
                self.process_error(f"Could not write config.h: {write_config}")
                self.log.error("Could not write config file: %s", write_config)
            else:
                generate_myautomation = True
        else:
            message = ", ".join(list)
            self.process_error(message)
            self.log.error(message)

        if generate_myautomation:
            (config, list) = self.generate_myAutomation()
            if config:
                file_contents = [("// myAutomation.h - Generated by EX-Installer " +
                                  f"v{self.app_version} for {self.product_name} " +
                                  f"{self.product_version_name}\n\n")]
                file_contents += self.default_myAutomation_options
                file_contents += list
                config_file_path = fm.get_filepath(self.ex_commandstation_dir, "myAutomation.h")
                write_config = fm.write_config_file(config_file_path, file_contents)
                if write_config == config_file_path:
                    if self.advanced_config_enabled.get() == "on":
                        self.master.switch_view("advanced_config", self.product)
                    else:
                        self.master.switch_view("compile_upload", self.product)
                else:
                    self.process_error(f"Could not write myAutomation.h: {write_config}")
                    self.log.error("Could not write myAutomation file: %s", write_config)
            else:
                message = ", ".join(list)
                self.process_error(message)
                self.log.error(message)
