"""
Module for the EX-CommandStation page view
"""

# Import Python modules
import customtkinter as ctk
import os
from pprint import pprint

# Import local modules
from .common_widgets import WindowLayout
from .product_details import product_details as pd
from .file_manager import FileManager as fm


class EXCommandStation(WindowLayout):
    """
    Class for the EX-CommandStation view
    """

    # Dummy variables for layout design
    dummy_version_list = [
        "v4.2.53-Devel",
        "v4.2.45-Devel",
        "v4.2.25-Devel",
        "v4.1.6-Prod",
        "v4.1.5-Prod",
        "v4.0.0-Prod"
    ]

    latest_prod = "v4.1.6-Prod"

    latest_devel = "v4.2.53-Devel"

    motorshield_list = {
        "STANDARD": "#define STANDARD\n",
        "EX8874": "#define EX8874\n",
        "POLOLU": "#define POLOLU\n"
    }

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
        '#define WIFI_CHANNEL 1\n'
        '#define SCROLLMODE 1\n'
    ]

    def __init__(self, parent, *args, **kwargs):
        """
        Initialise view
        """
        super().__init__(parent, *args, **kwargs)

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
                                                    text=f"Latest Production ({self.latest_prod}) - Recommended!",
                                                    font=ctk.CTkFont(weight="bold"), value=0)
        self.latest_devel_radio = ctk.CTkRadioButton(self.version_radio_frame, variable=self.select_version,
                                                     text=f"Latest Development ({self.latest_devel})", value=1)
        self.select_version_radio = ctk.CTkRadioButton(self.version_radio_frame, variable=self.select_version,
                                                       text="Select a specific version", value=2)
        self.select_version_combo = ctk.CTkComboBox(self.version_radio_frame, values=self.dummy_version_list, width=150)

        # Layout radio frame
        self.latest_prod_radio.grid(column=0, row=0, columnspan=2, sticky="w", **grid_options)
        self.latest_devel_radio.grid(column=0, row=1, columnspan=2, sticky="w", **grid_options)
        self.select_version_radio.grid(column=0, row=2, sticky="w", **grid_options)
        self.select_version_combo.grid(column=1, row=2, sticky="e", **grid_options)

        # Set up configuration options
        self.config_radio_frame = ctk.CTkFrame(self.version_frame)
        self.config_option = ctk.IntVar(value=0)
        self.configure_radio = ctk.CTkRadioButton(self.config_radio_frame, variable=self.config_option,
                                                  text="Configure options on the next screen", value=0)
        self.use_config_radio = ctk.CTkRadioButton(self.config_radio_frame, variable=self.config_option,
                                                   text="Use my existing configuration files", value=1)
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
        self.motor_driver_label = ctk.CTkLabel(self.config_frame, text="Select your motor shield/driver")
        self.motor_driver_combo = ctk.CTkComboBox(self.config_frame, values=list(self.motorshield_list),
                                                  width=300)

        # Set up display widgets
        self.display_switch = ctk.CTkSwitch(self.config_frame, text="I have a display",
                                            onvalue="on", offvalue="off", command=self.set_display)
        self.display_combo = ctk.CTkComboBox(self.config_frame, values=list(self.supported_displays),
                                             width=300)

        # Set up WiFi widgets
        self.wifi_type = ctk.IntVar(self, value=-1)
        self.wifi_ssid = ctk.StringVar(self, value=None)
        self.wifi_pwd = ctk.StringVar(self, value=None)
        self.wifi_frame = ctk.CTkFrame(self.config_frame, border_width=0)
        self.wifi_switch = ctk.CTkSwitch(self.config_frame, text="I have WiFi",
                                         onvalue="on", offvalue="off", command=self.set_wifi)
        self.wifi_options_frame = ctk.CTkFrame(self.wifi_frame,
                                               border_width=2,
                                               fg_color="#E5E5E5")
        self.wifi_ap_radio = ctk.CTkRadioButton(self.wifi_options_frame,
                                                text="Use my EX-CommandStation as an access point",
                                                variable=self.wifi_type,
                                                value=0)
        self.wifi_st_radio = ctk.CTkRadioButton(self.wifi_options_frame,
                                                text="Connect my EX-CommandStation to my existing wireless network",
                                                variable=self.wifi_type,
                                                value=1)
        self.wifi_ssid_label = ctk.CTkLabel(self.wifi_options_frame, text="WiFi SSID:")
        self.wifi_ssid_entry = ctk.CTkEntry(self.wifi_options_frame, textvariable=self.wifi_ssid,
                                            width=200, fg_color="white")
        self.wifi_pwd_label = ctk.CTkLabel(self.wifi_options_frame, text="WiFi Password:")
        self.wifi_pwd_entry = ctk.CTkEntry(self.wifi_options_frame, textvariable=self.wifi_pwd,
                                           width=200, fg_color="white")

        # Layout WiFi frame
        self.wifi_frame.grid_columnconfigure((0, 1), weight=1)
        self.wifi_frame.grid_rowconfigure(0, weight=1)
        self.wifi_options_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.wifi_options_frame.grid_rowconfigure((0, 1, 2), weight=1)
        self.wifi_options_frame.grid(column=1, row=0)
        self.wifi_ap_radio.grid(column=0, row=0, columnspan=4, sticky="w", **grid_options)
        self.wifi_st_radio.grid(column=0, row=1, columnspan=4, sticky="w", **grid_options)
        self.wifi_ssid_label.grid(column=0, row=2, **grid_options)
        self.wifi_ssid_entry.grid(column=1, row=2, **grid_options)
        self.wifi_pwd_label.grid(column=2, row=2, **grid_options)
        self.wifi_pwd_entry.grid(column=3, row=2, **grid_options)

        # Layout frame
        self.hardware_label.grid(column=0, row=2, columnspan=2, **grid_options)
        self.motor_driver_label.grid(column=0, row=3, **grid_options)
        self.motor_driver_combo.grid(column=1, row=3, sticky="w", **grid_options)
        self.display_switch.grid(column=0, row=4, **grid_options)
        self.display_combo.grid(column=1, row=4, sticky="w", **grid_options)
        self.wifi_switch.grid(column=0, row=5)
        self.wifi_frame.grid(column=1, row=5, sticky="e", **grid_options)

    def start(self):
        """
        Function to run on first start
        """
        self.config_frame.grid_remove()
        self.next_back.set_next_command(self.display_config_screen)
        self.set_display()
        self.set_wifi()
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
            self.wifi_frame.grid()
        else:
            self.wifi_frame.grid_remove()

    def browse_configdir(self):
        """
        Opens a directory browser dialogue to select the folder containing config files
        """
        directory = ctk.filedialog.askdirectory()
        if directory:
            self.config_path.set(directory)

    def display_config_screen(self):
        self.version_frame.grid_remove()
        self.config_frame.grid()
        self.next_back.set_next_text("Compile and upload")
        self.next_back.set_next_command(lambda product=self.product: self.master.compile_upload(product))

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
        pprint(event)
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
        elif self.process_phase == "clone_repo":
            if self.process_status == "success":
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
        """
        pass
