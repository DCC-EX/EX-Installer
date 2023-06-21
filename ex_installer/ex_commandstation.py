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

    def set_product_version(self):
        """
        Function to be called by the switch_frame function to set the chosen version

        This allows configuration options to be set based on the chosen version
        """
        pass

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
        self.wifi_channel_frame = ctk.CTkFrame(self.wifi_options_frame, border_width=2)
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

        # Layout WiFi frame
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
        self.wifi_channel_frame.grid(column=0, row=3, columnspan=4, **grid_options)
        self.wifi_channel_label.grid(column=0, row=0, **grid_options)
        self.wifi_channel_minus.grid(column=1, row=0, sticky="e")
        self.wifi_channel_entry.grid(column=2, row=0)
        self.wifi_channel_plus.grid(column=3, row=0, sticky="w", padx=(0, 5))

        # Layout frame
        self.hardware_label.grid(column=0, row=2, columnspan=2, **grid_options)
        self.motor_driver_label.grid(column=0, row=3, stick="e", **grid_options)
        self.motor_driver_combo.grid(column=1, row=3, sticky="w", **grid_options)
        self.display_switch.grid(column=0, row=4, sticky="e", **grid_options)
        self.display_combo.grid(column=1, row=4, sticky="w", **grid_options)
        self.wifi_switch.grid(column=0, row=5, sticky="e", **grid_options)
        self.wifi_frame.grid(column=1, row=5, sticky="w", **grid_options)
        self.ethernet_switch.grid(column=0, row=6, sticky="e", **grid_options)

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
            if self.wifi_pwd_entry.get() == "":
                self.wifi_pwd_entry.configure(placeholder_text="Custom WiFi password")
            self.log.debug("WiFi AP mode selected")
        elif self.wifi_type.get() == 1:
            self.wifi_ssid_label.grid()
            self.wifi_ssid_entry.grid()
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
        self.get_motor_drivers()
        self.check_motor_driver(self.motor_driver_combo.get())
        self.next_back.set_next_text("Compile and upload")
        self.next_back.set_next_command(self.create_config_file)
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

    def create_config_file(self):
        """
        Function to create config.h file and progress to upload

        - Check for config errors
        - Checks for the existence of user config files
        - Prompts to back those up if they exist
        - If they exist, delete before create to ensure no conflicts
        """
        (config, list) = self.generate_config()
        if config:
            file_contents = [("// EX-CommandStation config.h generated by EX-Installer version " +
                              f"{self.app_version}\n\n")]
            if self.product_version_name:
                file_contents.append("// Configuration generated for EX-CommandStation version " +
                                     "f{self.product_version_name}")
            file_contents += self.default_config_options
            file_contents += list
            config_file_path = fm.get_filepath(self.ex_commandstation_dir, "config.h")
            write_config = fm.write_config_file(config_file_path, file_contents)
            if write_config == config_file_path:
                # self.master.compile_upload(self.product)
                self.master.switch_view("compile_upload", self.product)
            else:
                self.process_error(f"Could not write config.h: {write_config}")
                self.log.error("Could not write config file: %s", write_config)
        else:
            message = ", ".join(list)
            self.process_error(message)
            self.log.error(message)
