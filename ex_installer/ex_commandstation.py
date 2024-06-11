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
                     "your EX-CommandStation device.\n\n" +
                     "If you are enabling WiFi or configuring TrackManager, enable the appropriate option and " +
                     "navigate to the appropriate tab to configure the relevant options.")

    # List of supported displays and config lines for config.h
    supported_displays = {
        "LCD 16 columns x 2 rows": "#define LCD_DRIVER 0x27,16,2\n",
        "LCD 20 columns x 4 rows": "#define LCD_DRIVER 0x27,20,4\n",
        "OLED 128 x 32": "#define OLED_DRIVER 128,32\n",
        "OLED 128 x 64": "#define OLED_DRIVER 128,64\n",
        "OLED 132 x 64": "#define OLED_DRIVER 132,64\n"
    }

    # List of default config options to include in config.h
    default_config_options = [
        '#define IP_PORT 2560\n',
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

        # Variables for version dependent options
        self.trackmanager_available = False
        self.current_override_available = False
        self.disable_prog_available = False

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
            self.product_major_version = int(major)
            if minor is not None:
                self.product_minor_version = int(minor)
                if patch is not None:
                    self.product_patch_version = int(patch)
        if (
            self.product_major_version >= 5 or
            (self.product_major_version == 4 and self.product_minor_version >= 2)
        ):
            self.track_modes_switch.configure(state="normal")
            self.trackmanager_available = True
        else:
            self.track_modes_switch.deselect()  # make sure it's off
            self.track_modes_switch.configure(state="disabled")
            self.trackmanager_available = False
        if (
            self.product_major_version >= 5 or
            (self.product_major_version >= 4 and self.product_minor_version >= 2 and self.product_patch_version >= 61)
        ):
            self.override_current_limit.configure(state="normal")
            self.current_override_available = True
        else:
            self.override_current_limit.deselect()
            self.override_current_limit.configure(state="disabled")
            self.current_override_available = False
        if self.product_major_version >= 5:
            self.disable_prog_switch.configure(state="normal")
            self.disable_prog_available = True
        else:
            self.disable_prog_switch.configure(state="disabled")
            self.disable_prog_available = False
        self.set_track_modes()
        self.current_override()
        self.check_selected_device()
        self.get_motor_drivers()

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
                     "for further information. If this option is disabled, the version you have selected does not " +
                     "include TrackManager features.")
        power_tip = ("To enable track power to be on during startup, enable this option. Note that it will also join " +
                     "the programming and main tracks.")
        current_tip = ("It is possible to define a custom current limit for the motor driver by enabling this option " +
                       "and specifying a new limit in mA. If this option is disabled, the version you have selected " +
                       "does not have this feature available.")
        disable_eeprom_tip = ("On memory restricted devices such as Uno and Nano, disabling EEPROM support frees up " +
                              "valuable memory to enable using features such as limited EXRAIL scripts. This will " +
                              "be disabled for boards such as ESP32 and Nucleo that have no EEPROM on board.")
        disable_prog_tip = ("On memory restricted devices such as Uno and Nano, disabling programming support frees " +
                            "up valuable memory to enable using features such as limited EXRAIL scripts.")

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
        self.wifi_tab_frame = ctk.CTkFrame(self.config_tabview.tab("WiFi Options"), border_width=0)
        self.wifi_tab_frame.grid(**tab_frame_options)
        self.track_tab_frame = ctk.CTkFrame(self.config_tabview.tab("TrackManager Config"), border_width=0)
        self.track_tab_frame.grid(**tab_frame_options)

        # Create options frames
        self.switch_frame = ctk.CTkFrame(self.general_tab_frame, border_width=0)
        self.options_frame = ctk.CTkFrame(self.general_tab_frame, border_width=0)

        # Set up motor driver widgets
        self.motor_driver_label = ctk.CTkLabel(self.options_frame, text="Select your motor driver:",
                                               font=self.instruction_font)
        self.motor_driver_combo = ctk.CTkComboBox(self.options_frame, values=["Select motor driver"],
                                                  width=300, command=self.check_motor_driver)
        CreateToolTip(self.motor_driver_combo, motor_tip,
                      "https://dcc-ex.com/reference/hardware/motor-boards.html")

        # Set up display widgets
        self.display_frame = ctk.CTkFrame(self.options_frame, border_width=2)
        self.display_type_label = ctk.CTkLabel(self.display_frame, text="Select display type (if in use):",
                                               font=self.instruction_font)
        self.display_enabled = ctk.StringVar(self, value="off")
        self.display_type = ctk.StringVar(self)
        self.display_switch = ctk.CTkSwitch(self.switch_frame, text="I have a display", width=200,
                                            onvalue="on", offvalue="off", variable=self.display_enabled,
                                            command=self.set_display, font=self.instruction_font)
        CreateToolTip(self.display_switch, display_tip,
                      "https://dcc-ex.com/reference/hardware/i2c-displays.html")
        self.display_radio_frame = ctk.CTkFrame(self.display_frame, fg_color="#D9D9D9", border_width=0)
        row = 0
        for display in self.supported_displays.keys():
            display_radio = ctk.CTkRadioButton(self.display_radio_frame, text=display, variable=self.display_type,
                                               font=self.instruction_font, value=self.supported_displays[display],
                                               width=200)
            display_radio.grid(column=0, row=row, sticky="w", **grid_options)
            if row == 0:
                display_radio.select()
            row += 1

        # Layout display frame
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_rowconfigure(1, weight=1)
        self.display_type_label.grid(column=0, row=0, columnspan=2, sticky="w", padx=5, pady=(5, 1))
        self.display_radio_frame.grid(column=0, row=1, sticky="w", padx=5, pady=(1, 5))

        # Set up current limit widgets
        self.override_current_limit = ctk.CTkSwitch(self.switch_frame, text="Override current limit",
                                                    onvalue="on", offvalue="off",
                                                    width=200, command=self.current_override,
                                                    font=self.instruction_font)
        CreateToolTip(self.override_current_limit, current_tip)
        self.current_limit = ctk.StringVar(self, value="")
        self.current_limit_label = ctk.CTkLabel(self.options_frame, text="Specify current limit in mA:",
                                                font=self.instruction_font)
        self.current_limit_entry = ctk.CTkEntry(self.options_frame, textvariable=self.current_limit,
                                                width=50, fg_color="white")

        # Set up WiFi widgets
        self.wifi_type = ctk.IntVar(self, value=0)
        self.wifi_channel = ctk.StringVar(self, value=1)
        self.wifi_enabled = ctk.StringVar(self, value="off")
        self.wifi_switch = ctk.CTkSwitch(self.switch_frame, text="I have WiFi", width=200,
                                         onvalue="on", offvalue="off", variable=self.wifi_enabled,
                                         command=self.set_wifi, font=self.instruction_font)
        CreateToolTip(self.wifi_switch, wifi_tip,
                      "https://dcc-ex.com/ex-commandstation/advanced-setup/supported-wifi/index.html")
        self.wifi_options_frame = ctk.CTkFrame(self.wifi_tab_frame, border_width=0)
        self.wifi_ap_radio = ctk.CTkRadioButton(self.wifi_options_frame, width=400,
                                                text="Use my EX-CommandStation as an access point",
                                                variable=self.wifi_type,
                                                command=self.set_wifi_widgets,
                                                value=0)
        self.wifi_st_radio = ctk.CTkRadioButton(self.wifi_options_frame, width=400,
                                                text="Connect my EX-CommandStation to my existing wireless network",
                                                variable=self.wifi_type,
                                                command=self.set_wifi_widgets,
                                                value=1)
        self.wifi_ssid_label = ctk.CTkLabel(self.wifi_options_frame, text="WiFi SSID:",
                                            font=self.instruction_font)
        self.wifi_ssid_entry = ctk.CTkEntry(self.wifi_options_frame,
                                            placeholder_text="Enter your WiFi SSID/name",
                                            width=200, fg_color="white", font=self.instruction_font)
        self.wifi_pwd_label = ctk.CTkLabel(self.wifi_options_frame, text="WiFi Password:",
                                           font=self.instruction_font)
        self.wifi_hostname = ctk.StringVar(self, value="dccex")
        self.wifi_pwd_entry = ctk.CTkEntry(self.wifi_options_frame,
                                           placeholder_text="Enter your WiFi password",
                                           width=200, fg_color="white", font=self.instruction_font)
        self.wifi_hostname_label = ctk.CTkLabel(self.wifi_options_frame, text="WiFi hostname:",
                                                font=self.instruction_font)
        self.wifi_hostname_entry = ctk.CTkEntry(self.wifi_options_frame, textvariable=self.wifi_hostname,
                                                width=200, fg_color="white",
                                                font=self.instruction_font)
        self.wifi_channel_frame = ctk.CTkFrame(self.wifi_options_frame, border_width=0, fg_color="#E5E5E5")
        self.wifi_channel_label = ctk.CTkLabel(self.wifi_channel_frame, text="Select WiFi channel:")
        self.wifi_channel_minus = ctk.CTkButton(self.wifi_channel_frame, text="-", width=30,
                                                command=self.decrement_channel)
        self.wifi_channel_plus = ctk.CTkButton(self.wifi_channel_frame, text="+", width=30,
                                               command=self.increment_channel)
        self.wifi_channel_entry = ctk.CTkEntry(self.wifi_channel_frame, textvariable=self.wifi_channel,
                                               width=30, fg_color="white", state="disabled", justify="center",
                                               font=self.instruction_font)

        # Ethernet switch
        self.ethernet_enabled = ctk.StringVar(self, value="off")
        self.ethernet_switch = ctk.CTkSwitch(self.switch_frame, text="I have ethernet", width=200,
                                             onvalue="on", offvalue="off", variable=self.ethernet_enabled,
                                             command=self.set_ethernet, font=self.instruction_font)
        CreateToolTip(self.ethernet_switch, ethernet_tip,
                      "https://dcc-ex.com/reference/hardware/ethernet-boards.html")

        # Track Manager Options
        self.track_modes_enabled = ctk.StringVar(self, value="off")
        self.track_modes_switch = ctk.CTkSwitch(self.switch_frame, text="Configure TrackManager", width=200,
                                                onvalue="on", offvalue="off", variable=self.track_modes_enabled,
                                                command=self.set_track_modes, font=self.instruction_font)
        CreateToolTip(self.track_modes_switch, track_tip,
                      "https://dcc-ex.com/under-development/track-manager.html")
        self.track_modes_frame = ctk.CTkFrame(self.track_tab_frame, border_width=0)
        self.track_a_label = ctk.CTkLabel(self.track_modes_frame, text="Track A:", font=self.instruction_font)
        self.track_a_combo = ctk.CTkComboBox(self.track_modes_frame, values=list(self.trackmanager_modes),
                                             width=100, font=self.instruction_font, command=self.set_a_mode)
        self.track_a_id = ctk.StringVar(self, value="1")
        self.track_a_id_label = ctk.CTkLabel(self.track_modes_frame, text="Track A loco/cab ID:",
                                             font=self.instruction_font)
        self.track_a_entry = ctk.CTkEntry(self.track_modes_frame, textvariable=self.track_a_id,
                                          font=self.instruction_font, width=60, fg_color="white")
        self.track_b_label = ctk.CTkLabel(self.track_modes_frame, text="Track B:")
        self.track_b_combo = ctk.CTkComboBox(self.track_modes_frame, values=list(self.trackmanager_modes),
                                             width=100, font=self.instruction_font, command=self.set_b_mode)
        self.track_b_id = ctk.StringVar(self, value="2")
        self.track_b_id_label = ctk.CTkLabel(self.track_modes_frame, text="Track B loco/cab ID:",
                                             font=self.instruction_font)
        self.track_b_entry = ctk.CTkEntry(self.track_modes_frame, textvariable=self.track_b_id,
                                          font=self.instruction_font, width=60, fg_color="white")
        self.track_b_combo.set("MAIN")  # default to MAIN and PROG
        self.track_b_combo.set("PROG")

        # Set track power on startup
        self.power_on_switch = ctk.CTkSwitch(self.switch_frame, text="Start with power on", width=200,
                                             onvalue="on", offvalue="off", font=self.instruction_font)
        CreateToolTip(self.power_on_switch, power_tip)

        # Blank myAutomation option
        self.blank_myautomation_switch = ctk.CTkSwitch(self.switch_frame, text="Create myAutomation.h", width=200,
                                                       onvalue="on", offvalue="off", font=self.instruction_font)

        # Advanced configuration option
        self.advanced_config_enabled = ctk.StringVar(self, value="off")
        self.advanced_config_switch = ctk.CTkSwitch(self.switch_frame, text="Advanced Config", width=200,
                                                    onvalue="on", offvalue="off", variable=self.advanced_config_enabled,
                                                    command=self.set_advanced_config, font=self.instruction_font)
        CreateToolTip(self.advanced_config_switch, advanced_tip)

        # Device hardware option widgets
        self.hardware_options_frame = ctk.CTkFrame(self.options_frame, border_width=2)
        self.device_options_label = ctk.CTkLabel(self.hardware_options_frame, text="Device hardware options:",
                                                 font=self.instruction_font)
        self.disable_eeprom_switch = ctk.CTkSwitch(self.hardware_options_frame, text="Disable EEPROM support",
                                                   width=200, onvalue="on", offvalue="off", font=self.instruction_font)
        CreateToolTip(self.disable_eeprom_switch, disable_eeprom_tip)
        self.disable_prog_switch = ctk.CTkSwitch(self.hardware_options_frame, text="Disable programming support",
                                                 width=200, onvalue="on", offvalue="off", font=self.instruction_font)
        CreateToolTip(self.disable_prog_switch, disable_prog_tip)
        low_mem = ("Note that you have selected a device that has limited memory available. We recommend disabling " +
                   "EEPROM and programming support in order to support limited EXRAIL functionality.")
        self.low_mem_label = ctk.CTkLabel(self.hardware_options_frame, text=low_mem, font=self.instruction_font,
                                          text_color="orange", width=300, wraplength=295)

        # Layout hardware options frame
        self.hardware_options_frame.grid_columnconfigure(0, weight=1)
        self.hardware_options_frame.grid_rowconfigure((1, 2), weight=1)
        self.device_options_label.grid(column=0, row=0, sticky="w", **grid_options)
        self.disable_eeprom_switch.grid(column=0, row=1, sticky="w", **grid_options)
        self.disable_prog_switch.grid(column=0, row=2, sticky="w", **grid_options)
        self.low_mem_label.grid(column=0, row=3, sticky="w", **grid_options)

        # Layout wifi_frame
        self.wifi_tab_frame.grid_columnconfigure((0, 1), weight=1)
        self.wifi_tab_frame.grid_rowconfigure(0, weight=1)
        self.wifi_options_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.wifi_options_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.wifi_channel_frame.grid_columnconfigure(0, weight=1)
        self.wifi_channel_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.wifi_options_frame.grid(column=1, row=0)
        self.wifi_ap_radio.grid(column=0, row=0, columnspan=4, **grid_options)
        self.wifi_st_radio.grid(column=0, row=1, columnspan=4, **grid_options)
        self.wifi_ssid_label.grid(column=0, row=2, sticky="e", **grid_options)
        self.wifi_ssid_entry.grid(column=1, row=2, sticky="w", **grid_options)
        self.wifi_pwd_label.grid(column=2, row=2, sticky="e", **grid_options)
        self.wifi_pwd_entry.grid(column=3, row=2, sticky="w", **grid_options)
        self.wifi_hostname_label.grid(column=0, row=3, sticky="e", **grid_options)
        self.wifi_hostname_entry.grid(column=1, row=3, sticky="w", **grid_options)
        self.wifi_channel_frame.grid(column=0, row=2, columnspan=2, **grid_options)
        self.wifi_channel_label.grid(column=0, row=0, **grid_options)
        self.wifi_channel_minus.grid(column=1, row=0, sticky="e")
        self.wifi_channel_entry.grid(column=2, row=0)
        self.wifi_channel_plus.grid(column=3, row=0, sticky="w", padx=(0, 5))

        # Layout switch frame
        self.display_switch.grid(column=0, row=0, **grid_options)
        self.wifi_switch.grid(column=0, row=1, **grid_options)
        self.ethernet_switch.grid(column=0, row=2, **grid_options)
        self.track_modes_switch.grid(column=0, row=3, **grid_options)
        self.power_on_switch.grid(column=0, row=4, **grid_options)
        self.override_current_limit.grid(column=0, row=5, **grid_options)
        self.blank_myautomation_switch.grid(column=0, row=6, **grid_options)
        self.advanced_config_switch.grid(column=0, row=7, **grid_options)

        # Layout options frame
        self.options_frame.grid_columnconfigure((0, 1), weight=1)
        self.options_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.motor_driver_label.grid(column=0, row=0, sticky="e", **grid_options)
        self.motor_driver_combo.grid(column=1, row=0, sticky="w", **grid_options)
        self.display_frame.grid(column=0, row=2, sticky="w", **grid_options)
        self.current_limit_label.grid(column=0, row=3, sticky="e", **grid_options)
        self.current_limit_entry.grid(column=1, row=3, sticky="w", **grid_options)
        self.hardware_options_frame.grid(column=1, row=2, stick="w", **grid_options)

        # Layout track_frame
        self.track_tab_frame.grid_columnconfigure(0, weight=1)
        self.track_tab_frame.grid_rowconfigure(0, weight=1)
        self.track_modes_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.track_modes_frame.grid_rowconfigure((0, 1), weight=1)
        self.track_a_label.grid(column=0, row=0, sticky="e", **grid_options)
        self.track_a_combo.grid(column=1, row=0, sticky="w", **grid_options)
        self.track_a_id_label.grid(column=2, row=0, sticky="e", **grid_options)
        self.track_a_entry.grid(column=3, row=0, sticky="w", **grid_options)
        self.track_b_label.grid(column=0, row=1, sticky="e", **grid_options)
        self.track_b_combo.grid(column=1, row=1, sticky="w", **grid_options)
        self.track_b_id_label.grid(column=2, row=1, sticky="e", **grid_options)
        self.track_b_entry.grid(column=3, row=1, sticky="w", **grid_options)

        # Layout general tab
        self.general_tab_frame.grid_columnconfigure(0, weight=1)
        self.general_tab_frame.grid_columnconfigure(1, weight=2)
        self.general_tab_frame.grid_rowconfigure(0, weight=1)
        self.switch_frame.grid(column=0, row=0, **grid_options)
        self.options_frame.grid(column=1, row=0, **grid_options)

        # Layout WiFi tab
        self.wifi_options_frame.grid(column=0, row=0, sticky="nsew")

        # Layout TrackManager tab
        self.track_modes_frame.grid(column=0, row=0, sticky="nsew")

        # Layout config_frame
        self.config_frame.grid_columnconfigure(0, weight=1)
        self.config_frame.grid_rowconfigure(1, weight=1)
        self.hardware_label.grid(column=0, row=0, **grid_options)
        self.config_tabview.grid(column=0, row=1, sticky="nsew", **grid_options)

    def check_selected_device(self):
        """
        Sets recommended device options based on selected device

        Disables EEPROM option for boards without it also
        """
        device = self.acli.selected_device
        device_fqbn = self.acli.detected_devices[device]["matching_boards"][0]["fqbn"]
        # EEPROM disabled on ESP32 and Nucleo
        if device_fqbn.startswith("esp32") or device_fqbn.startswith("STMicroelectronics:stm32"):
            self.disable_eeprom_switch.select()
            self.disable_eeprom_switch.configure(state="disabled")
        else:
            self.disable_eeprom_switch.deselect()
            self.disable_eeprom_switch.configure(state="normal")
        # Track Manager not supported on Uno/Nano, EEPROM default off and WiFi disabled
        if device_fqbn.startswith("arduino:avr:nano") or device_fqbn == "arduino:avr:uno":
            self.track_modes_switch.deselect()
            self.track_modes_switch.configure(state="disabled")
            self.disable_eeprom_switch.select()
            self.wifi_switch.deselect()
            self.wifi_switch.configure(state="disabled")
            self.low_mem_label.grid()
        else:
            if self.trackmanager_available:
                self.track_modes_switch.configure(state="normal")
            self.disable_eeprom_switch.deselect()
            self.disable_prog_switch.deselect()
            self.low_mem_label.grid_remove()
            self.wifi_switch.deselect()
            self.wifi_switch.configure(state="enabled")
        # Enable WiFi by default for ESP32 and disable control
        if device_fqbn.startswith("esp32") and not (device_fqbn.startswith("arduino:avr:nano") or
                                                    device_fqbn == "arduino:avr:uno"):
            if self.wifi_switch.get() == "off":
                self.wifi_switch.toggle()
            self.wifi_switch.configure(state="disabled")
        elif not (device_fqbn.startswith("arduino:avr:nano") or device_fqbn == "arduino:avr:uno"):
            if self.wifi_switch.get() == "on":
                self.wifi_switch.toggle()
            self.wifi_switch.configure(state="enabled")

    def set_display(self):
        """
        Sets display options on or off
        """
        if self.display_switch.get() == "on":
            for widget in self.display_radio_frame.winfo_children():
                widget.configure(state="normal")
            self.log.debug("Display enabled")
        else:
            for widget in self.display_radio_frame.winfo_children():
                widget.configure(state="disabled")
            self.log.debug("Display disabled")

    def set_track_modes(self):
        """
        Sets track mode options on or off
        """
        if self.track_modes_switch.get() == "on":
            self.config_tabview._segmented_button._buttons_dict["TrackManager Config"].configure(state="normal")
            self.log.debug("Track modes frame shown")
        else:
            self.config_tabview._segmented_button._buttons_dict["TrackManager Config"].configure(state="disabled")
            self.log.debug("Track modes frame hidden")
        self.set_a_mode()
        self.set_b_mode()

    def set_a_mode(self, event=None):
        """
        If setting track A to DC or DCX, allow setting loco/cab ID
        """
        if self.track_a_combo.get() == "DC" or self.track_a_combo.get() == "DCX":
            self.track_a_id_label.grid()
            self.track_a_entry.grid()
        else:
            self.track_a_id_label.grid_remove()
            self.track_a_entry.grid_remove()

    def set_b_mode(self, event=None):
        """
        If setting track B to DC or DCX, allow setting loco/cab ID
        """
        if self.track_b_combo.get() == "DC" or self.track_b_combo.get() == "DCX":
            self.track_b_id_label.grid()
            self.track_b_entry.grid()
        else:
            self.track_b_id_label.grid_remove()
            self.track_b_entry.grid_remove()

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
            self.config_tabview._segmented_button._buttons_dict["WiFi Options"].configure(state="normal")
            self.set_wifi_widgets()
            self.log.debug("WiFi enabled")
        else:
            self.config_tabview._segmented_button._buttons_dict["WiFi Options"].configure(state="disabled")
            self.log.debug("WiFi disabled")

    def set_wifi_widgets(self):
        """
        Function to display correct widgets for WiFi config
        """
        if self.wifi_type.get() == 0:
            self.wifi_ssid_label.grid_remove()
            self.wifi_ssid_entry.grid_remove()
            self.wifi_hostname_label.grid_remove()
            self.wifi_hostname_entry.grid_remove()
            self.wifi_channel_frame.grid()
            if self.wifi_pwd_entry.get() == "":
                self.wifi_pwd_entry.configure(placeholder_text="Custom WiFi password")
            self.log.debug("WiFi AP mode selected")
        elif self.wifi_type.get() == 1:
            self.wifi_ssid_label.grid()
            self.wifi_ssid_entry.grid()
            self.wifi_hostname_label.grid()
            self.wifi_hostname_entry.grid()
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
            if self.acli.dccex_device is not None:
                driver_list = self.restrict_dccex_motor_drivers(def_list)
            else:
                driver_list = self.remove_all_dccex_motor_drivers(def_list)
            self.motordriver_list += driver_list
            self.log.debug("Found motor driver list %s", driver_list)
        else:
            self.log.error("Could not get list of motor drivers")
        self.motor_driver_combo.configure(values=self.motordriver_list)

    def remove_all_dccex_motor_drivers(self, driver_list):
        """
        Method to remove all DCC-EX specific motor driver definitions from the provided list

        This provides an appropriate driver list for generic Arduino devices
        """
        restricted_list = []
        for device in self.acli.dccex_devices:
            restricted_list = [driver for driver in driver_list if not driver.startswith(self.acli.dccex_devices[device] + "_")]
        return restricted_list

    def restrict_dccex_motor_drivers(self, driver_list):
        """
        Method to remove generic motor driver definitions from the provided list

        Utilises the class attribute dccex_device to limit the available selections
        """
        restricted_list = [driver for driver in driver_list if driver.startswith(self.acli.dccex_device + "_")]
        return restricted_list

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

    def current_override(self):
        """
        Function to enable overriding current limit
        """
        if self.override_current_limit.get() == "on":
            self.current_limit_label.grid()
            self.current_limit_entry.grid()
        else:
            self.current_limit_label.grid_remove()
            self.current_limit_entry.grid_remove()

    def delete_config_files(self):
        """
        Function to delete config files from product directory
          needed on subsequent passes thru the logic
        """
        file_list = []
        local_repo_dir = pd[self.product]["repo_name"].split("/")[1]
        product_dir = fm.get_install_dir(local_repo_dir)
        min_list = fm.get_config_files(product_dir, pd[self.product]["minimum_config_files"])
        if min_list:
            file_list += min_list
        other_list = None
        if "other_config_files" in pd[self.product]:
            other_list = fm.get_config_files(product_dir, pd[self.product]["other_config_files"])
        if other_list:
            file_list += other_list
        self.log.debug("Deleting files: %s", file_list)
        error_list = fm.delete_config_files(product_dir, file_list)
        if error_list:
            file_list = ", ".join(error_list)
            self.process_error(f"Failed to delete one or more files: {file_list}")
            self.log.error("Failed to delete: %s", file_list)

    def generate_config(self):
        """
        Function to validate options and return any errors

        Validates all parameters have been set and generates config.h defines

        Returns a tuple of (True|False, error_list|config_list)
        """
        self.delete_config_files()
        param_errors = []
        config_list = []
        if self.motor_driver_combo.get() == "Select motor driver":
            param_errors.append("Motor driver not set")
        else:
            line = "#define MOTOR_SHIELD_TYPE " + self.motor_driver_combo.get() + "\n"
            config_list.append(line)
        if self.display_switch.get() == "on":
            config_list.append(self.display_type.get())
        if self.wifi_switch.get() == "on":
            line = '#define WIFI_HOSTNAME "' + self.wifi_hostname.get() + '"\n'
            config_list.append(line)
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
        if self.override_current_limit.get() == "on":
            try:
                int(self.current_limit.get())
            except Exception:
                param_errors.append("Current limit must be a number in mA")
            else:
                config_list.append(f"#define MAX_CURRENT {self.current_limit.get()}\n")
        if self.disable_eeprom_switch.get() == "on":
            config_list.append("#define DISABLE_EEPROM\n")
        if self.disable_prog_switch.get() == "on":
            config_list.append("#define DISABLE_PROG\n")
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
        roster_lines = []

        # Single AUTOSTART if either option enabled
        if self.power_on_switch.get() == "on" or self.track_modes_enabled.get() == "on":
            config_list.append("AUTOSTART\n")

        # Enable join on startup if enabled
        if self.power_on_switch.get() == "on":
            config_list.append("POWERON\n")

        # write out trackmanager config, including roster entries if DCx
        if self.track_modes_enabled.get() == "on":
            try:
                int(self.track_a_id.get())
            except Exception:
                param_errors.append("Track A loco/cab ID must be from 1 to 10293")
            else:
                if int(self.track_a_id.get()) < 1 or int(self.track_a_id.get()) > 10293:
                    param_errors.append("Track A loco/cab ID must be from 1 to 10293")
            try:
                int(self.track_b_id.get())
            except Exception:
                param_errors.append("Track B loco/cab ID must be from 1 to 10293")
            else:
                if int(self.track_b_id.get()) < 1 or int(self.track_b_id.get()) > 10293:
                    param_errors.append("Track B loco/cab ID must be from 1 to 10293")
            if (self.track_a_combo.get().startswith("DC")):
                line = (f"SETLOCO({self.track_a_id.get()}) SET_TRACK(A," + self.track_a_combo.get() + ")\n")
                roster_lines.append(f"ROSTER({self.track_a_id.get()},\"DC TRACK A\",\"/* /\")\n")
            else:
                line = "SET_TRACK(A," + self.track_a_combo.get() + ")\n"
            config_list.append(line)
            if (self.track_b_combo.get().startswith("DC")):
                line = (f"SETLOCO({self.track_b_id.get()}) SET_TRACK(B," + self.track_b_combo.get() + ")\n")
                roster_lines.append(f"ROSTER({self.track_b_id.get()},\"DC TRACK B\",\"/* /\")\n")
            else:
                line = "SET_TRACK(B," + self.track_b_combo.get() + ")\n"
            config_list.append(line)
        # Single AUTOSTART if either option enabled
        if self.power_on_switch.get() == "on" or self.track_modes_enabled.get() == "on":
            config_list.append("DONE\n\n")
        if self.track_modes_enabled.get() == "on" and len(roster_lines) > 0:
            config_list += roster_lines

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
                if len(list) > 0 or self.blank_myautomation_switch.get() == "on":
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
                    self.log.debug("No myAutomation.h parameters, not writing file")
                    if self.advanced_config_enabled.get() == "on":
                        self.master.switch_view("advanced_config", self.product)
                    else:
                        self.master.switch_view("compile_upload", self.product)
            else:
                message = ", ".join(list)
                self.process_error(message)
                self.log.error(message)
