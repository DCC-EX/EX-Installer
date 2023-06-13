"""
Module for the EX-CommandStation page view
"""

# Import Python modules
import customtkinter as ctk
import os
import logging

# Import local modules
from .common_widgets import WindowLayout
from .product_details import product_details as pd
from .file_manager import FileManager as fm


class EXCommandStation(WindowLayout):
    """
    Class for the EX-CommandStation view
    """

    # Instruction text
    version_text = ("For most users we recommended staying with the latest Production release, however you can " +
                    "install other versions if you know what you're doing, or if a version has been suggested by " +
                    "the DCC-EX team.")

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

        # Set up event handlers
        event_callbacks = {
            "<<Setup_Local_Repo>>": self.setup_local_repo
        }
        for sequence, callback in event_callbacks.items():
            self.bind_class("bind_events", sequence, callback)
        new_tags = self.bindtags() + ("bind_events",)
        self.bindtags(new_tags)

        # Get the local directory to work in
        self.product = "ex_commandstation"
        local_repo_dir = pd[self.product]["repo_name"].split("/")[1]
        self.ex_commandstation_dir = fm.get_install_dir(local_repo_dir)

        # Set up required variables
        self.branch_name = pd[self.product]["default_branch"]
        self.repo = None
        self.version_list = None
        self.latest_prod = None
        self.latest_devel = None

        # Set up title
        self.set_title_logo(pd[self.product]["product_logo"])
        self.set_title_text("Install EX-CommandStation")

        # Set up next/back buttons
        self.next_back.set_back_text("Select Product")
        self.next_back.set_back_command(lambda view="select_product": parent.switch_view(view))
        self.next_back.set_next_text("Configuration")
        self.next_back.set_next_command(None)

        # Set up and grid container frames
        self.version_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.config_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.version_frame.grid(column=0, row=0, sticky="nsew")
        self.config_frame.grid(column=0, row=0, sticky="nsew")

        # Set up frame contents
        self.setup_version_frame()
        self.setup_config_frame()

        # print(self.acli.detected_devices[self.acli.selected_device]["matching_boards"][0]["fqbn"])

        self.start()

    def setup_version_frame(self):
        grid_options = {"padx": 5, "pady": 5}

        # Set up version instructions
        self.version_label = ctk.CTkLabel(self.version_frame, text=self.version_text,
                                          wraplength=780, font=self.instruction_font)

        # Set up select version radio frame and radio buttons
        self.version_radio_frame = ctk.CTkFrame(self.version_frame,
                                                border_width=2,
                                                fg_color="#E5E5E5")
        self.version_radio_frame.grid_columnconfigure((0, 1), weight=1)
        self.version_radio_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.select_version = ctk.IntVar(value=0)
        self.latest_prod_radio = ctk.CTkRadioButton(self.version_radio_frame, variable=self.select_version,
                                                    text="Latest Production - Recommended!",
                                                    font=ctk.CTkFont(weight="bold"), value=0,
                                                    command=self.set_version)
        self.latest_devel_radio = ctk.CTkRadioButton(self.version_radio_frame, variable=self.select_version,
                                                     text="Latest Development", value=1,
                                                     command=self.set_version)
        self.select_version_radio = ctk.CTkRadioButton(self.version_radio_frame, variable=self.select_version,
                                                       text="Select a specific version", value=2,
                                                       command=self.set_version)
        self.select_version_combo = ctk.CTkComboBox(self.version_radio_frame, values=["Select a version"], width=150,
                                                    command=self.set_select_version)

        # Layout radio frame
        self.latest_prod_radio.grid(column=0, row=0, columnspan=2, sticky="w", **grid_options)
        self.latest_devel_radio.grid(column=0, row=1, columnspan=2, sticky="w", **grid_options)
        self.select_version_radio.grid(column=0, row=2, sticky="w", **grid_options)
        self.select_version_combo.grid(column=1, row=2, sticky="e", **grid_options)

        # Set up configuration options
        self.config_radio_frame = ctk.CTkFrame(self.version_frame)
        self.config_option = ctk.IntVar(value=0)
        self.configure_radio = ctk.CTkRadioButton(self.config_radio_frame, variable=self.config_option,
                                                  text="Configure options on the next screen", value=0,
                                                  command=self.set_next_config)
        self.use_config_radio = ctk.CTkRadioButton(self.config_radio_frame, variable=self.config_option,
                                                   text="Use my existing configuration files", value=1,
                                                   command=self.set_next_config)
        self.config_path = ctk.StringVar(value=None)
        self.config_file_entry = ctk.CTkEntry(self.config_radio_frame, textvariable=self.config_path,
                                              width=300)
        self.browse_button = ctk.CTkButton(self.config_radio_frame, text="Browse",
                                           width=80, command=self.browse_configdir)

        # Configure and layout config frame
        self.config_radio_frame.grid_columnconfigure((0, 1), weight=1)
        self.config_radio_frame.grid_rowconfigure((0, 1), weight=1)
        self.configure_radio.grid(column=0, row=0, columnspan=3, sticky="w", **grid_options)
        self.use_config_radio.grid(column=0, row=1, sticky="w", **grid_options)
        self.config_file_entry.grid(column=1, row=1, **grid_options)
        self.browse_button.grid(column=2, row=1, sticky="w", **grid_options)

        # Configure and layout version frame
        self.version_frame.grid_columnconfigure(0, weight=1)
        self.version_frame.grid_rowconfigure((0, 1, 2), weight=1)
        self.version_label.grid(column=0, row=0, **grid_options)
        self.version_radio_frame.grid(column=0, row=1, **grid_options)
        self.config_radio_frame.grid(column=0, row=2, **grid_options)

    def setup_config_frame(self):
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
        self.wifi_ssid = ctk.StringVar(self, value="Enter your WiFi SSID/name")
        self.wifi_pwd = ctk.StringVar(self, value="Enter your WiFi password")
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
        self.wifi_ssid_entry = ctk.CTkEntry(self.wifi_options_frame, textvariable=self.wifi_ssid,
                                            width=200, fg_color="white")
        self.wifi_pwd_label = ctk.CTkLabel(self.wifi_options_frame, text="WiFi Password:")
        self.wifi_pwd_entry = ctk.CTkEntry(self.wifi_options_frame, textvariable=self.wifi_pwd,
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

    def start(self):
        """
        Function to run on first start
        """
        self.display_version_screen()
        self.setup_local_repo("setup_local_repo")

    def set_display(self):
        """
        Sets display options on or off
        """
        if self.display_switch.get() == "on":
            self.display_combo.grid()
        else:
            self.display_combo.grid_remove()

    def set_wifi(self):
        """
        Sets WiFi options on or off
        """
        if self.wifi_switch.get() == "on":
            if self.ethernet_switch.get() == "on":
                self.ethernet_switch.deselect()
            self.wifi_frame.grid()
            self.set_wifi_widgets()
        else:
            self.wifi_frame.grid_remove()

    def set_wifi_widgets(self):
        """
        Function to display correct widgets for WiFi config
        """
        if self.wifi_type.get() == 0:
            self.wifi_ssid_label.grid_remove()
            self.wifi_ssid_entry.grid_remove()
            self.wifi_pwd_label.grid_remove()
            self.wifi_pwd_entry.grid_remove()
        elif self.wifi_type.get() == 1:
            self.wifi_ssid_label.grid()
            self.wifi_ssid_entry.grid()
            self.wifi_pwd_label.grid()
            self.wifi_pwd_entry.grid()

    def set_ethernet(self):
        """
        Function to enable Ethernet support
        """
        if self.ethernet_switch.get() == "on":
            if self.wifi_switch.get() == "on":
                self.wifi_switch.deselect()
                self.set_wifi()

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

    def browse_configdir(self):
        """
        Opens a directory browser dialogue to select the folder containing config files
        """
        directory = ctk.filedialog.askdirectory()
        if directory:
            self.config_path.set(directory)
            self.config_option.set(1)
            self.set_next_config()

    def display_version_screen(self):
        """
        Displays the version selection frame
        """
        self.config_frame.grid_remove()
        self.version_frame.grid()
        self.set_next_config()
        self.next_back.set_back_text("Select Product")
        self.next_back.set_back_command(lambda view="select_product": self.master.switch_view(view))

    def display_config_screen(self):
        """
        Displays the configuration options frame
        """
        self.version_frame.grid_remove()
        self.config_frame.grid()
        self.set_display()
        self.set_wifi()
        self.get_motor_drivers()
        self.check_motor_driver(self.motor_driver_combo.get())
        self.next_back.set_next_text("Compile and upload")
        self.next_back.set_next_command(self.create_config_file)
        self.next_back.set_back_text("Select version")
        self.next_back.set_back_command(self.display_version_screen)

    def setup_local_repo(self, event):
        """
        Function to setup the local repository

        Process:
        - check if the product directory already exists
        - if so
            - if the product directory is already a cloned repo
            - any locally modified files that would interfere with Git commands
            - any existing configuration files
        - if not, clone repo
        - get list of versions, latest prod, and latest devel versions
        """
        if event == "setup_local_repo":
            self.disable_input_states(self)
            if os.path.exists(self.ex_commandstation_dir) and os.path.isdir(self.ex_commandstation_dir):
                if self.git.dir_is_git_repo(self.ex_commandstation_dir):
                    self.repo = self.git.get_repo(self.ex_commandstation_dir)
                    if self.repo:
                        changes = self.git.check_local_changes(self.repo)
                        if changes:
                            self.process_error(f"Local changes detected: f{changes}")
                            self.restore_input_states()
                        else:
                            self.setup_local_repo("get_latest")
                    else:
                        self.process_error(f"{self.ex_commandstation_dir} appears to be a Git repository but is not")
                        self.restore_input_states()
                else:
                    if fm.dir_is_empty(self.ex_commandstation_dir):
                        self.setup_local_repo("clone_repo")
                    else:
                        self.process_error(f"{self.ex_commandstation_dir} contains files but is not a repo")
                        self.restore_input_states()
            else:
                self.setup_local_repo("clone_repo")
        elif event == "clone_repo":
            self.process_start("clone_repo", "Clone repository", "Setup_Local_Repo")
            self.git.clone_repo(pd[self.product]["repo_url"], self.ex_commandstation_dir, self.queue)
        elif self.process_phase == "clone_repo" or event == "get_latest":
            if self.process_status == "success" or event == "get_latest":
                self.repo = self.git.get_repo(self.ex_commandstation_dir)
                branch_ref = self.git.get_branch_ref(self.repo, self.branch_name)
                try:
                    self.repo.checkout(refname=branch_ref)
                except Exception as error:
                    message = self.get_exception(error)
                    self.process_error(message)
                    self.restore_input_states()
                else:
                    self.process_start("pull_latest", "Get latest software updates", "Setup_Local_Repo")
                    self.git.pull_latest(self.repo, self.branch_name, self.queue)
            elif self.process_status == "error":
                self.process_error(self.process_data)
                self.restore_input_states()
        elif self.process_phase == "pull_latest":
            if self.process_status == "success":
                self.set_versions(self.repo)
                self.process_stop()
                self.restore_input_states()
            elif self.process_status == "error":
                self.process_error("Could not pull latest updates from GitHub")
                self.restore_input_states()

    def set_versions(self, repo):
        """
        Function to obtain versions available in the repo

        Once versions obtained, set appropriately
        """
        self.latest_prod = self.git.get_latest_prod(self.repo)
        if self.latest_prod:
            self.latest_prod_radio.configure(text=f"Latest Production ({self.latest_prod[0]}) - Recommended!")
        else:
            self.latest_prod_radio.grid_remove()
            self.select_version.set(-1)
        self.latest_devel = self.git.get_latest_devel(self.repo)
        if self.latest_devel:
            self.latest_devel_radio.configure(text=f"Latest Development ({self.latest_devel[0]})")
        else:
            self.latest_devel_radio.grid_remove()
        self.version_list = self.git.get_repo_versions(self.repo)
        if self.version_list:
            version_select = list(self.version_list.keys())
            self.select_version_combo.configure(values=version_select)
        self.set_version()

    def set_version(self):
        """
        Function to checkout the selected version according to the radio buttons
        """
        if self.select_version.get() == 0:
            self.repo.checkout(refname=self.latest_prod[1])
            self.next_back.enable_next()
        elif self.select_version.get() == 1:
            self.repo.checkout(refname=self.latest_devel[1])
            self.next_back.enable_next()
        elif self.select_version.get() == 2:
            if self.select_version_combo.get() != "Select a version":
                self.repo.checkout(refname=self.version_list[self.select_version_combo.get()]["ref"])
                self.next_back.enable_next()
            else:
                self.next_back.disable_next()

    def set_select_version(self, value):
        """
        Function to set select a specific version when setting via combobox
        """
        if self.select_version.get() != 2:
            self.select_version.set(2)
        self.set_version()

    def set_next_config(self):
        """
        Function to select what configuration to do next
        """
        if self.config_option.get() == 0:
            self.next_back.set_next_command(self.display_config_screen)
            self.next_back.set_next_text("Configuration")
            self.next_back.enable_next()
        elif self.config_option.get() == 1:
            self.next_back.set_next_command(self.copy_config_files)
            self.next_back.set_next_text("Compile and upload")
            self.validate_config_dir()

    def validate_config_dir(self):
        """
        Function to validate the selected directory for config files:

        - Is a valid directory
        - Contains at least the specified minimum config files
        """
        if self.config_path.get():
            config_files = fm.get_config_files(self.config_path.get(), pd[self.product]["minimum_config_files"])
            if config_files:
                self.next_back.enable_next()
            else:
                file_names = ", ".join(pd[self.product]["minimum_config_files"])
                self.process_error(("Selected configuration directory is missing the required files: " +
                                   f"{file_names}"))
                self.next_back.disable_next()
        else:
            self.next_back.disable_next()

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
        self.motor_driver_combo.configure(values=self.motordriver_list)

    def check_motor_driver(self, value):
        """
        Function ensure a motor driver has been selected
        """
        if value == "Select motor driver":
            self.next_back.disable_next()
        else:
            self.next_back.enable_next()

    def copy_config_files(self):
        """
        Function to either create config files or copy from specified directory
        """
        if self.config_option.get() == 0:
            print("Create config files here")
            self.master.compile_upload(self.product)
        elif self.config_option.get() == 1:
            copy_list = fm.get_config_files(self.config_path.get(), pd[self.product]["minimum_config_files"])
            if copy_list:
                extra_list = fm.get_config_files(self.config_path.get(), pd[self.product]["other_config_files"])
                if extra_list:
                    copy_list += extra_list
                file_copy = fm.copy_config_files(self.config_path.get(), self.ex_commandstation_dir, copy_list)
                if file_copy:
                    file_list = ", ".join(file_copy)
                    self.process_error(f"Failed to copy one or more files: {file_list}")
                else:
                    self.master.compile_upload(self.product)
            else:
                self.process_error("Selected configuration directory is missing the required files")

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
                config_list.append('#define WIFI_PASSWORD "Your network passwd"\n')
            elif self.wifi_type.get() == 1:
                if self.wifi_ssid.get() == "Enter your WiFi SSID/name":
                    param_errors.append("WiFi SSID/name not set")
                else:
                    line = '#define WIFI_SSID "' + self.wifi_ssid.get() + '"\n'
                    config_list.append(line)
                if self.wifi_pwd.get() == "Enter your WiFi password":
                    param_errors.append("WiFi password not set")
                else:
                    line = '#define WIFI_PASSWORD "' + self.wifi_pwd.get() + '"\n'
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
            return (False, param_errors)
        else:
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
            file_contents = ["// EX-CommandStation config.h generated by EX-Installer\n\n"]
            file_contents += self.default_config_options
            file_contents += list
            config_file_path = fm.get_filepath(self.ex_commandstation_dir, "config.h")
            write_config = fm.write_config_file(config_file_path, file_contents)
            if write_config == config_file_path:
                self.master.compile_upload(self.product)
            else:
                self.process_error(f"Could not write config.h: {write_config}")
        else:
            message = ", ".join(list)
            self.process_error(message)
