"""
Module for managing the Arduino CLI page view
"""

# Import Python modules
import customtkinter as ctk
import logging

# Import local modules
from .common_widgets import WindowLayout
from . import images


class ManageArduinoCLI(WindowLayout):
    # Define text to use in labels
    intro_text = ("We use the Arduino Command Line Interface (CLI) to upload the DCC-EX products to your Arduino. " +
                  "The CLI eliminates the need to install the more daunting Arduino IDE. EX-Installer is able to " +
                  "manage the installation and updating of the Arduino CLI for you at the click of a button.")
    installed_text = "The Arduino CLI is installed"
    not_installed_text = "The Arduino CLI is not installed"
    install_instruction_text = ("To install the Arduino CLI, simply click the install button.\n\n" +
                                "If you are using an Espressif or STMicroelectronics device (as opposed to the more " +
                                "common Uno or Mega based Arduinos), you will need to enable support for these " +
                                "by selecting the appropriate additional platform option.\n\n"
                                "Note that enabling additional platforms is likely to add several minutes to the " +
                                "installation process. Maybe grab a cup of tea or a coffee!")
    refresh_instruction_text = ("While the Arduino CLI is installed, it is recommended to refresh it periodically " +
                                "(eg. weekly) to ensure support for the various devices is kept up to date. To refresh " +
                                "the CLI, simply click the refresh button.\n\n"
                                "Note that enabling any of the additional platforms is likely to add " +
                                "several minutes to the refresh process. Maybe grab a cup of tea or a coffee!")

    """
    Class for the Manage Arduino CLI view
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Set up the Manage Arduino CLI view
        """
        super().__init__(parent, *args, **kwargs)

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start view")

        # Set up event handlers
        event_callbacks = {
            "<<Check_Arduino_CLI>>": self.check_arduino_cli,
            "<<Manage_CLI>>": self.manage_cli
        }
        for sequence, callback in event_callbacks.items():
            self.bind_class("bind_events", sequence, callback)
        new_tags = self.bindtags() + ("bind_events",)
        self.bindtags(new_tags)

        # Set up dictionary to store packages to install/refresh
        self.package_dict = {
            "Arduino AVR": "arduino:avr"
        }

        # Set title and logo
        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Manage the Arduino CLI")

        # Set up next and back buttons
        self.next_back.show_back()
        self.next_back.set_back_text("Welcome")
        self.next_back.set_back_command(lambda view="welcome": parent.switch_view(view))
        self.next_back.set_next_text("Select your device")
        self.next_back.set_next_command(lambda view="select_device": parent.switch_view(view))
        self.next_back.hide_monitor_button()

        # Create, grid, and configure container frame
        self.manage_cli_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.manage_cli_frame.grid(column=0, row=0, sticky="nsew", ipadx=5, ipady=5)
        self.manage_cli_frame.grid_columnconfigure((0, 1), weight=1)
        self.manage_cli_frame.grid_rowconfigure((0, 2), weight=4)
        self.manage_cli_frame.grid_rowconfigure(1, weight=1)

        # Create state and instruction labels and manage CLI button
        label_options = {"wraplength": 700}
        self.intro_label = ctk.CTkLabel(self.manage_cli_frame,
                                        text=self.intro_text,
                                        font=self.instruction_font,
                                        **label_options)
        self.cli_state_label = ctk.CTkLabel(self.manage_cli_frame,
                                            font=self.instruction_font,
                                            **label_options)
        self.instruction_label = ctk.CTkLabel(self.manage_cli_frame,
                                              font=self.instruction_font,
                                              wraplength=390)
        self.manage_cli_button = ctk.CTkButton(self.manage_cli_frame, width=200, height=50,
                                               text=None, font=self.action_button_font)

        # Create frame and widgets for additional platform support
        grid_options = {"padx": 5, "pady": 5}
        self.extra_platforms_frame = ctk.CTkFrame(self.manage_cli_frame,
                                                  border_width=2,
                                                  fg_color="#E5E5E5")
        self.extra_platforms_frame.grid_columnconfigure(0, weight=1)
        self.extra_platforms_label = ctk.CTkLabel(self.extra_platforms_frame,
                                                  text="Enable extra platforms")
        self.extra_platforms_label.grid(column=0, row=0, sticky="ew", **grid_options)
        switch_options = {"onvalue": "on", "offvalue": "off"}
        for index, platform in enumerate(self.acli.extra_platforms):
            self.extra_platforms_frame.grid_rowconfigure(index+1, weight=1)
            switch_var = ctk.StringVar(value="off")
            switch = ctk.CTkSwitch(self.extra_platforms_frame, variable=switch_var, text=platform, **switch_options)
            switch.configure(command=lambda object=switch: self.update_package_list(object))
            switch.grid(column=0, row=index+1, sticky="w", **grid_options)

        # Layout frame
        self.intro_label.grid(column=0, row=0, columnspan=2)
        self.cli_state_label.grid(column=0, row=1)
        self.manage_cli_button.grid(column=1, row=1)
        self.instruction_label.grid(column=0, row=2)
        self.extra_platforms_frame.grid(column=1, row=2, ipadx=5, ipady=5)

        self.set_state()

    def set_state(self):
        self.next_back.hide_log_button()
        if self.acli.is_installed(self.acli.cli_file_path()):
            self.cli_state_label.configure(text=self.installed_text,
                                           text_color="#00353D",
                                           font=self.instruction_font)
            self.instruction_label.configure(text=self.refresh_instruction_text)
            self.manage_cli_button.configure(text="Refresh Arduino CLI",
                                             command=lambda event="refresh_cli": self.manage_cli(event))
            self.next_back.enable_next()
            self.check_arduino_cli("get_cli_info")
        else:
            self.cli_state_label.configure(text=self.not_installed_text,
                                           text_color="#FF5C00",
                                           font=self.bold_instruction_font)
            self.instruction_label.configure(text=self.install_instruction_text)
            self.manage_cli_button.configure(text="Install Arduino CLI",
                                             command=lambda event="install_cli": self.manage_cli(event))
            self.next_back.disable_next()

    def update_package_list(self, switch):
        """
        Maintain the list of packages to install/refresh when switches updated
        """
        if switch.cget("variable").get() == "on":
            if not switch.cget("text") in self.package_dict:
                self.package_dict[switch.cget("text")] = self.acli.extra_platforms[switch.cget("text")]["platform_id"]
                self.log.debug("Enable package %s", self.acli.extra_platforms[switch.cget("text")]["platform_id"])
        elif switch.cget("variable").get() == "off":
            if switch.cget("text") in self.package_dict:
                del self.package_dict[switch.cget("text")]
                self.log.debug("Disable package %s", switch.cget("text"))

    def check_arduino_cli(self, event):
        """
        Function to check if the Arduino CLI is installed and if so, what version it is

        On completion, will move to the Manage Arduino CLI screen
        """
        if event == "get_cli_info":
            self.process_start("check_arduino_cli", "Checking Arduino CLI version", "Check_Arduino_CLI")
            self.disable_input_states(self)
            self.acli.get_version(self.acli.cli_file_path(), self.queue)
        elif self.process_phase == "check_arduino_cli":
            if self.process_status == "success":
                if "VersionString" in self.process_data:
                    text = self.cli_state_label.cget("text") + f" (version {self.process_data['VersionString']})"
                    self.cli_state_label.configure(text=text)
                self.process_start("get_platforms", "Obtaining list of installed platforms", "Check_Arduino_CLI")
                self.acli.get_platforms(self.acli.cli_file_path(), self.queue)
            elif self.process_status == "error":
                self.process_error("Failed to check if the Arduino CLI is installed")
                self.restore_input_states()
            else:
                self.process_error("An unknown error occurred")
        elif self.process_phase == "get_platforms":
            if self.process_status == "success":
                if type(self.process_data) is list:
                    for child in self.extra_platforms_frame.winfo_children():
                        if isinstance(child, ctk.CTkSwitch):
                            for platform in self.process_data:
                                if self.acli.extra_platforms[child.cget("text")]["platform_id"] == platform["id"]:
                                    child.cget("variable").set("on")
                                    self.update_package_list(child)
                self.restore_input_states()
                self.process_stop()
            elif self.process_status == "error":
                self.process_error("Failed to get list of installed platforms")
                self.restore_input_states()

    def manage_cli(self, event):
        """
        Manage the Arduino CLI
        """
        if event == "install_cli":
            self.disable_input_states(self)
            self.process_start("download_cli", "Downloading the Arduino CLI", "Manage_CLI")
            self.acli.download_cli(self.queue)
        elif self.process_phase == "download_cli":
            if self.process_status == "success":
                download_file = self.process_data
                self.process_start("extract_cli", "Installing the Arduino CLI", "Manage_CLI")
                self.acli.install_cli(download_file, self.acli.cli_file_path(), self.queue)
            elif self.process_status == "error":
                self.process_error("Error downloading the Arduino CLI")
        elif event == "refresh_cli" or self.process_phase == "extract_cli":
            if event == "refresh_cli":
                self.disable_input_states(self)
            if self.process_status == "success" or event == "refresh_cli":
                self.process_start("config_cli", "Configuring the Arduino CLI", "Manage_CLI")
                for widget in self.extra_platforms_frame.winfo_children():
                    if isinstance(widget, ctk.CTkSwitch):
                        if not widget.cget("text") in self.package_dict and widget.cget("variable").get() == "on":
                            self.package_dict[widget.cget("text")] = (
                                self.acli.extra_platforms[widget.cget("text")["platform_id"]]
                                )
                self.acli.initialise_config(self.acli.cli_file_path(), self.queue)
            elif self.process_status == "error":
                self.process_error("Error installing the Arduino CLI")
        elif self.process_phase == "config_cli":
            if self.process_status == "success":
                self.process_start("update_index", "Updating core index", "Manage_CLI")
                self.acli.update_index(self.acli.cli_file_path(), self.queue)
            elif self.process_status == "error":
                self.process_error("Error configuring the Arduino CLI")
        elif self.process_phase == "update_index" or self.process_phase == "install_packages":
            if self.process_status == "success":
                if self.package_dict:
                    package = next(iter(self.package_dict))
                    self.process_start("install_packages", f"Installing package {package}", "Manage_CLI")
                    self.acli.install_package(self.acli.cli_file_path(), self.package_dict[package], self.queue)
                    del self.package_dict[package]
                else:
                    self.process_start("upgrade_platforms", "Upgrading Arduino platforms", "Manage_CLI")
                    self.acli.upgrade_platforms(self.acli.cli_file_path(), self.queue)
            elif self.process_status == "error":
                self.process_error("Error updating core index")
        elif self.process_phase == "upgrade_platforms":
            if self.process_status == "success":
                self.process_start("refresh_list", "Refreshing Arduino CLI board list", "Manage_CLI")
                self.acli.list_boards(self.acli.cli_file_path(), self.queue)
            elif self.process_status == "error":
                self.process_error("Error upgrading platforms")
        elif self.process_phase == "refresh_list":
            if self.process_status == "success":
                self.process_stop()
                self.restore_input_states()
                self.set_state()
            elif self.process_status == "error":
                self.process_error("Error refreshing board list")
