"""
Module for the EX-CommandStation page view
"""

# Import Python modules
import customtkinter as ctk
import logging

# Import local modules
from .common_widgets import WindowLayout
from .product_details import product_details as pd
from .file_manager import FileManager as fm
from .advanced_config import AdvancedConfig

class EXCommandStation(WindowLayout):
    """
    Class for the EX-CommandStation view
    """

    hardware_text = ("Select the appropriate options on this page to suit the hardware devices you are using with " +
                     "your EX-CommandStation device.\n\n")

    # List of supported displays and config lines for config.h
    supported_displays = {
        "LCD - 16 columns x 2 rows": "#define LCD_DRIVER 0x27,16,2",
        "LCD 16 columns x 4 rows": "#define LCD_DRIVER  0x27,16,4",
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
        "DC"  : "DC",
        "DCX" : "DCX",
        "OFF" : "OFF",
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
        if major:
            self.product_major_version = major
            if minor:
                self.product_minor_version
                if patch:
                    self.product_patch_version

    def setup_config_frame(self):
        """
        Setup the container frame for configuration options
        """
        grid_options = {"padx": 5, "pady": 5}

        # Set up hardware instruction label
        self.hardware_label = ctk.CTkLabel(self.config_frame, text=self.hardware_text,
                                           wraplength=780, font=self.instruction_font)

        # Set up motor driver widgets
        self.motor_driver_label = ctk.CTkLabel(self.config_frame, text="Select your motor driver")
        self.motor_driver_combo = ctk.CTkComboBox(self.config_frame, values=["Select motor driver"],
                                                  width=300, command=self.check_motor_driver)

        # Set up display widgets
        self.display_enabled = ctk.StringVar(self, value="off")
        self.display_switch = ctk.CTkSwitch(self.config_frame, text="I have a display", width=150,
                                            onvalue="on", offvalue="off", variable=self.display_enabled,
                                            command=self.set_display)
        self.display_combo = ctk.CTkComboBox(self.config_frame, values=list(self.supported_displays),
                                             width=300)

        # Set up WiFi widgets
        self.wifi_type = ctk.IntVar(self, value=0)
        self.wifi_channel = ctk.StringVar(self, value=1)
        self.wifi_enabled = ctk.StringVar(self, value="off")
        self.wifi_frame = ctk.CTkFrame(self.config_frame, border_width=0)
        self.wifi_switch = ctk.CTkSwitch(self.config_frame, text="I have WiFi", width=150,
                                         onvalue="on", offvalue="off", variable=self.wifi_enabled,
                                         command=self.set_wifi)
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
        self.ethernet_switch = ctk.CTkSwitch(self.config_frame, text="I have ethernet", width=150,
                                             onvalue="on", offvalue="off", variable=self.ethernet_enabled,
                                             command=self.set_ethernet)

        # Track Manager Options
        self.track_modes_enabled = ctk.StringVar(self, value="off")
        self.track_modes_switch = ctk.CTkSwitch(self.config_frame, text="Set track modes", width=150,
                                            onvalue="on", offvalue="off", variable=self.track_modes_enabled,
                                            command=self.set_track_modes)
        self.track_modes_frame = ctk.CTkFrame(self.config_frame, border_width=2, fg_color="#E5E5E5")
        self.track_a_label = ctk.CTkLabel(self.track_modes_frame, text="Track A:")
        self.track_a_combo = ctk.CTkComboBox(self.track_modes_frame, values=list(self.trackmanager_modes),
                                                  width=100)
        self.track_b_label = ctk.CTkLabel(self.track_modes_frame, text="Track B:")
        self.track_b_combo = ctk.CTkComboBox(self.track_modes_frame, values=list(self.trackmanager_modes),
                                                  width=100)      
        self.track_b_combo.set("MAIN") # default to MAIN and PROG
        self.track_b_combo.set("PROG")

        # advanced configuration option
        self.advanced_config_enabled = ctk.StringVar(self, value="off")
        self.advanced_config_switch = ctk.CTkSwitch(self.config_frame, text="Advanced Config", width=150,
                                            onvalue="on", offvalue="off", variable=self.advanced_config_enabled,
                                            command=self.set_advanced_config)
        self.advanced_config_label = ctk.CTkLabel(self.config_frame, text="Config files can be directly edited on next screen")

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

        # Layout config_frame
        self.hardware_label.grid(column=0, row=2, columnspan=2, **grid_options)
        self.motor_driver_label.grid(column=0, row=3, stick="e", **grid_options)
        self.motor_driver_combo.grid(column=1, row=3, sticky="w", **grid_options)
        self.display_switch.grid(column=0, row=4, sticky="e", **grid_options)
        self.display_combo.grid(column=1, row=4, sticky="w", **grid_options)
        self.wifi_switch.grid(column=0, row=5, sticky="e", **grid_options)
        self.wifi_frame.grid(column=1, row=5, sticky="w", **grid_options)
        self.ethernet_switch.grid(column=0, row=6, sticky="e", **grid_options)
        self.track_modes_switch.grid(column=0, row=7, sticky="e", **grid_options)
        self.track_modes_frame.grid(column=1, row=7, sticky="w", **grid_options)
        self.advanced_config_switch.grid(column=0, row=8, sticky="e", **grid_options)
        self.advanced_config_label.grid(column=1, row=8, sticky="w", **grid_options)

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
            self.advanced_config_label.grid()
            self.next_back.set_next_text("Advanced Config")
            self.log.debug("Manual Edit enabled")
        else:
            self.master.advanced_config = False
            self.advanced_config_label.grid_remove()
            self.next_back.set_next_text("Compile and Upload")
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

        # if Track Modes not enabled, return empty list
        if self.track_modes_enabled.get() == "off" :
            return (True, config_list)

        # write out trackmanager config, including roster entries if DCx
        if (self.track_a_combo.get().startswith("DC")): 
            line = "AUTOSTART SETLOCO(1) SET_TRACK(A,"+ self.track_a_combo.get() + ") DONE\n"
            line += "ROSTER(1,\"DC TRACK A\",\"/* /\")\n"
        else:
            line = "AUTOSTART SET_TRACK(A,"+ self.track_a_combo.get() + ") DONE\n"
        config_list.append(line)
        if (self.track_b_combo.get().startswith("DC")): 
            line = "AUTOSTART SETLOCO(2) SET_TRACK(B,"+ self.track_b_combo.get() + ") DONE\n"
            line += "ROSTER(2,\"DC TRACK B\",\"/* /\")\n"
        else:
            line = "AUTOSTART SET_TRACK(B,"+ self.track_b_combo.get() + ") DONE\n"
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

        - Check for config errors
        - Checks for the existence of user config files
        - Prompts to back those up if they exist
        - If they exist, delete before create to ensure no conflicts
        """
        (config, list) = self.generate_config()
        if config:
            file_contents = [("// EX-CommandStation config.h generated by EX-Installer version " +
                              f"{self.app_version}\n")]
            if self.product_version_name:
                file_contents.append("// Configuration generated for EX-CommandStation version " +
                                     self.product_version_name + "\n\n")
            file_contents += self.default_config_options
            file_contents += list
            config_file_path = fm.get_filepath(self.ex_commandstation_dir, "config.h")
            write_config = fm.write_config_file(config_file_path, file_contents)
            if write_config != config_file_path:
                self.process_error(f"Could not write config.h: {write_config}")
                self.log.error("Could not write config file: %s", write_config)
        else:
            message = ", ".join(list)
            self.process_error(message)
            self.log.error(message)

        (config, list) = self.generate_myAutomation()
        if config:
            file_contents = [("// EX-CommandStation myAutomation.h generated by EX-Installer version " +
                              f"{self.app_version}\n")]
            if self.product_version_name:
                file_contents.append("// Configuration generated for EX-CommandStation version " +
                                     self.product_version_name + "\n\n")
            file_contents += self.default_myAutomation_options
            file_contents += list
            config_file_path = fm.get_filepath(self.ex_commandstation_dir, "myAutomation.h")
            write_config = fm.write_config_file(config_file_path, file_contents)
            if write_config == config_file_path:
                if self.advanced_config_enabled.get() == "on" :
                    if "advanced_config" in self.master.frames :
                        # refresh the text boxes before REvisiting
                        self.master.frames["advanced_config"].reload_view()
                    self.master.switch_view("advanced_config", self.product)
                else :
                    self.master.switch_view("compile_upload", self.product)
            else:
                self.process_error(f"Could not write myAutomation.h: {write_config}")
                self.log.error("Could not write myAutomation file: %s", write_config)
        else:
            message = ", ".join(list)
            self.process_error(message)
            self.log.error(message)
