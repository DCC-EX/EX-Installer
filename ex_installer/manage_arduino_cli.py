"""
Module for managing the Arduino CLI page view

© 2024, Peter Cole.
© 2023, Peter Cole.
All rights reserved.

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

# Import local modules
from .common_widgets import WindowLayout, CreateToolTip
from . import images
from .product_details import product_details as pd


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
                                "(eg. weekly) to ensure support for the various devices is kept up to date. To " +
                                "refresh the CLI, simply click the refresh button.\n\n"
                                "Note that enabling any of the additional platforms is likely to add " +
                                "several minutes to the refresh process. Maybe grab a cup of tea or a coffee!")

    """
    Class for the Manage Arduino CLI view.

    Managing the CLI should all be driven by events.

    There are two event callbacks:

        - <<Check_Arduino_CLI>> - used to check if the Arduino is installed and if so, which version
        - <<Manage_CLI>> - used to manage installation and updates of the Arduino CLI
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
        self.packages_to_install = self.package_dict.copy()

        # Set up list for library installs
        self.library_list = []

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

        # Tooltip
        extra_platforms_tip = ("If you are using common Arduino AVR devices (eg. Mega2560, Uno, or Nano), then you " +
                               "can disregard these options as support is already included with the Arduino CLI.")
        CreateToolTip(self.extra_platforms_label, extra_platforms_tip)

        """
        To add additional supported platforms, these must be added to the extra_platforms dictionary in the arduino_cli
        module.
        """
        for index, platform in enumerate(self.acli.extra_platforms):
            platform_tip = (f"Support for {platform} devices is not included with the Arduino CLI by default. " +
                            "In order to be able to load any of our software on to these devices, you must " +
                            "enable this option.")
            self.extra_platforms_frame.grid_rowconfigure(index+1, weight=1)
            switch_var = ctk.StringVar(value="off")
            switch = ctk.CTkSwitch(self.extra_platforms_frame, variable=switch_var, text=platform, **switch_options)
            switch.configure(command=lambda object=switch: self.update_package_list(object))
            CreateToolTip(switch, platform_tip)
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
        self.get_library_list()
        if self.acli.is_installed(self.acli.cli_file_path()):
            self.cli_state_label.configure(text=self.installed_text,
                                           text_color="#00353D",
                                           font=self.instruction_font)
            self.instruction_label.configure(text=self.refresh_instruction_text)
            self.manage_cli_button.configure(text="Refresh Arduino CLI", command=self._generate_refresh_cli)
            self._generate_check_cli()
            self.next_back.enable_next()
        else:
            self.cli_state_label.configure(text=self.not_installed_text,
                                           text_color="#FF5C00",
                                           font=self.bold_instruction_font)
            self.instruction_label.configure(text=self.install_instruction_text)
            self.manage_cli_button.configure(text="Install Arduino CLI", command=self._generate_install_cli)
            self.next_back.disable_next()

    def get_library_list(self):
        """
        Get list of library dependencies from product details
        """
        self.library_list = []
        for product in pd:
            if "arduino_libraries" in pd[product]:
                for library in pd[product]["arduino_libraries"]:
                    self.library_list.append(library)

    def update_package_list(self, switch):
        """
        Maintain the list of packages to install/refresh when switches updated
        """
        if switch.cget("variable").get() == "on":
            if not switch.cget("text") in self.package_dict:
                self.package_dict[switch.cget("text")] = self.acli.extra_platforms[switch.cget("text")]["platform_id"]
                self.log.debug("Enable package and install %s",
                               self.acli.extra_platforms[switch.cget("text")]["platform_id"])
        elif switch.cget("variable").get() == "off":
            if switch.cget("text") in self.package_dict:
                del self.package_dict[switch.cget("text")]
                self.log.debug("Disable package %s", switch.cget("text"))

    def _generate_check_cli(self):
        """
        Generates an event to start checking the state of the Arduino CLI.

        For some reason this doesn't generate the event, call check_arduino_cli method with None argument for now.
        """
        self.process_phase = "check_arduino_cli"
        self.process_status = "start"
        # This doesn't work for some reason, call with None for now
        # self.event_generate("<<Check_Arduino_CLI>>")
        self.check_arduino_cli(None)

    def check_arduino_cli(self, event):
        """
        Check the version of the Arduino CLI, and if additional platforms are installed.
        """
        self.log.debug(f"check_arduino_cli() called\nprocess_phase: {self.process_phase}\nprocess_status: " +
                       f"{self.process_status}")
        if self.process_status == "error":
            self._process_error()
        else:
            match self.process_phase:
                case "check_arduino_cli":
                    self._check_cli_version()
                case "get_platforms":
                    self._get_installed_platforms()
                case _:
                    self._process_error()

    def _check_cli_version(self):
        """
        Method to check the version of CLI that is present (if installed).

        If we need to start, call the acli.get_version() method.

        If it was successful, call _get_platforms().

        Any other status is an error.
        """
        self.log.debug(f"_check_cli_version() {self.process_status}")
        if self.process_status == "start":
            self.process_start("check_arduino_cli", "Checking Arduino CLI version", "Check_Arduino_CLI")
            self.disable_input_states(self)
            self.acli.get_version(self.acli.cli_file_path(), self.queue)
        elif self.process_status == "success":
            if "VersionString" in self.process_data:
                text = self.cli_state_label.cget("text") + f" (version {self.process_data['VersionString']})"
                self.cli_state_label.configure(text=text)
            self.process_status = "start"
            self._get_installed_platforms()
        elif self.process_status == "error":
            self.process_error("Failed to check if the Arduino CLI is installed")
            self.restore_input_states()
        else:
            self.process_error("An unknown error occurred")

    def _get_installed_platforms(self):
        """
        Method to obtain the currently installed Arduino platforms.

        If we need to start call the acli.get_platforms() method.

        If successful:

        - Set the extra_platforms_frame CTKSwitch widgets to the correct state
        - If a package is installed and an explicit version is defined, compare these
        - If a package is installed but not the explicit version, add to the list
        - If a package is installed without an explicit version but not latest, add to the list
        - If a package is not installed but should be, add to the list

        Any other status is an error.
        """
        self.log.debug(f"_get_installed_platforms() {self.process_status}")
        if self.process_status == "start":
            self.process_start("get_platforms", "Obtaining list of installed platforms", "Check_Arduino_CLI")
            self.acli.get_platforms(self.acli.cli_file_path(), self.queue)
        elif self.process_status == "success":
            if len(self.process_data) > 0 and "platforms" in self.process_data:
                if isinstance(self.process_data["platforms"], list):
                    self.process_data = self.process_data["platforms"]
            if isinstance(self.process_data, list):
                for child in self.extra_platforms_frame.winfo_children():
                    if isinstance(child, ctk.CTkSwitch):
                        # Need to compare against the platform ID and version
                        if "@" in self.acli.extra_platforms[child.cget("text")]["platform_id"]:
                            result = (self.acli.extra_platforms[child.cget("text")]["platform_id"]).split("@", 2)
                            platformid = result[0]
                            required_version = result[1]
                        else:
                            platformid = self.acli.extra_platforms[child.cget("text")]["platform_id"]
                            required_version = None
                        for platform in self.process_data:
                            if platformid == platform["id"]:
                                child.cget("variable").set("on")
                                installed = platform["installed"]
                                latest = platform["latest"]
                                # Don't update if our installed platform the right version
                                if required_version is not None and installed == required_version:
                                    break
                                # Don't update if we already have the latest
                                elif required_version is None and installed == latest:
                                    break
                                # Anything else means we must update
                                else:
                                    if required_version is not None:
                                        self.log.debug(f"Must update {platformid} from {installed} to " +
                                                       f"{required_version}")
                                    else:
                                        self.log.debug(f"Must update {platformid} from {installed} to {latest}")
                                    self.update_package_list(child)

            self.restore_input_states()
            self.process_stop()
        else:
            self.process_error("An unknown error occurred")

    def _generate_install_cli(self):
        """
        Generates an event to start installing the Arduino CLI.
        """
        self.process_phase = "install_cli"
        self.process_status = "start"
        self.event_generate("<<Manage_CLI>>")

    def _generate_refresh_cli(self):
        """
        Generates an event to start refreshing the Arduino CLI.
        """
        self.process_phase = "refresh_cli"
        self.process_status = "start"
        self.event_generate("<<Manage_CLI>>")

    def manage_cli(self, event):
        """
        Method to manage the state of the Arduino CLI.

        If not installed, it must:

        - Download the latest CLI
        - Extract the CLI
        - Initialise the CLI config with the selected platform types
        - Update the CLI core index
        - Upgrade platforms
        - Install required packages (this should match any specific version and not just upgrade)
        - Install any required libraries
        - Refresh the list of attached boards

        If already installed, it must:

        - Update the CLI core index
        - Upgrade platforms
        - Upgrade required packages (this should match any specific version and not just upgrade)
        - Install any required libraries
        - Refresh the list of attached boards
        """
        self.log.debug(f"manage_cli() called\nprocess_phase: {self.process_phase}\nprocess_status: " +
                       f"{self.process_status}")
        if self.process_status == "error":
            self._process_error()
        else:
            match self.process_phase:
                case "install_cli":
                    self.process_status = "start"
                    self.disable_input_states(self)
                    self._download_cli()
                case "refresh_cli":
                    self.process_status = "start"
                    self.disable_input_states(self)
                    self._update_core_index()
                case "download_cli":
                    self._download_cli()
                case "extract_cli":
                    self._extract_cli()
                case "init_cli":
                    self._init_cli()
                case "update_index":
                    self._update_core_index()
                case "upgrade_platforms":
                    self._upgrade_platforms()
                case "install_packages":
                    self._install_packages()
                case "install_libraries":
                    self._install_libraries()
                case "refresh_boards":
                    self._refresh_boards()
                case _:
                    self._process_error()

    def _process_error(self):
        """
        Method to deal with an error in the process.
        """
        self.process_error(self.process_topic)
        self.restore_input_states()
        self.log.error(f"Error encountered in process phase {self.process_phase}")
        self.log.error(self.process_data)

    def _download_cli(self):
        """
        Method to start downloading the Arduino CLI.

        If we need to start, call the acli.download_cli() method.

        If it was successful, call _extract_cli().

        Any other status is an error.
        """
        self.log.debug(f"_download_cli() {self.process_status}")
        if self.process_status == "start":
            self.disable_input_states(self)
            self.process_start("download_cli", "Downloading the Arduino CLI", "Manage_CLI")
            self.acli.download_cli(self.queue)
        elif self.process_status == "success":
            self.process_status = "start"
            self._extract_cli()
        else:
            self._process_error()

    def _extract_cli(self):
        """
        Method to start extracting the Arduino CLI, which relies on the downloaded file being
        available in the process_data attribute.

        If we need to start, call the acli.install_cli() method.

        If it was successful, call _init_cli().

        Any other status is an error.
        """
        self.log.debug(f"_extract_cli() {self.process_status}")
        if self.process_status == "start":
            download_file = self.process_data
            self.process_start("extract_cli", "Installing the Arduino CLI", "Manage_CLI")
            self.acli.install_cli(download_file, self.acli.cli_file_path(), self.queue)
        elif self.process_status == "success":
            self.process_status = "start"
            self._init_cli()
        else:
            self._process_error()

    def _init_cli(self):
        """
        Method to start the CLI initialisation process.

        Note that this must cycle through each widget in the "extra_platforms_frame" frame to
        be able to flag each additional platform that needs to be installed.

        If we need to start, call the acli.initialise_config() method.

        If successful, call _update_core_index().

        Any other status is an error.
        """
        self.log.debug(f"_init_cli() {self.process_status}")
        if self.process_status == "start":
            self.process_start("init_cli", "Configuring the Arduino CLI", "Manage_CLI")
            for widget in self.extra_platforms_frame.winfo_children():
                if isinstance(widget, ctk.CTkSwitch):
                    if not widget.cget("text") in self.package_dict and widget.cget("variable").get() == "on":
                        self.package_dict[widget.cget("text")] = (
                            self.acli.extra_platforms[widget.cget("text")["platform_id"]]
                            )
            self.acli.initialise_config(self.acli.cli_file_path(), self.queue)
        elif self.process_status == "success":
            self.process_status = "start"
            self._update_core_index()
        else:
            self._process_error()

    def _update_core_index(self):
        """
        Method to start the core index update process.

        If we need to start, call the acli.update_index() method.

        If successful, call _upgrade_platforms().

        Any other status is an error.
        """
        self.log.debug(f"_update_core_index() {self.process_status}")
        if self.process_status == "start":
            self.process_start("update_index", "Updating core index", "Manage_CLI")
            self.acli.update_index(self.acli.cli_file_path(), self.queue)
        elif self.process_status == "success":
            self.process_status = "start"
            self._upgrade_platforms()
        else:
            self._process_error()

    def _upgrade_platforms(self):
        """
        Method to start the upgrade platforms process.

        If we need to start, call the acli.upgrade_platforms() method.

        If successful, call _install_packages().

        Any other status is an error.
        """
        self.log.debug(f"_upgrade_platforms() {self.process_status}")
        if self.process_status == "start":
            self.process_start("upgrade_platforms", "Upgrading Arduino platforms", "Manage_CLI")
            self.acli.upgrade_platforms(self.acli.cli_file_path(), self.queue)
        elif self.process_status == "success":
            self.packages_to_install = self.package_dict.copy()
            self.process_status = "start"
            self._install_packages()
        else:
            self._process_error()

    def _install_packages(self):
        """
        Method to process installing all required packages.

        This needs to cycle through each package to install them.

        If we need to start, call _install_single_package().

        Any other status is an error.
        """
        self.log.debug(f"_install_packages() {self.process_status}")
        if self.process_status == "start" or (len(self.packages_to_install) > 0 and self.process_status == "success"):
            package = next(iter(self.packages_to_install))
            packagestr = self.packages_to_install[package]
            del self.packages_to_install[package]
            self._install_single_package(package, packagestr)
        elif self.process_status == "success":
            self.process_status = "start"
            self.libraries_to_install = self.library_list.copy()
            self._install_libraries()
        else:
            self._process_error()

    def _install_single_package(self, package, packagestr):
        """
        Method to start installing the specified package.
        """
        self.log.debug(f"_install_single_package() {self.process_status}\npackage: {package}, packagestr: {packagestr}")
        self.process_start("install_packages", f"Installing package {package}", "Manage_CLI")
        self.acli.install_package(self.acli.cli_file_path(), packagestr, self.queue)

    def _install_libraries(self):
        """
        Method to start installing the required libraries.

        This needs to cycle through each library to install them.

        If we need to start, call _install_single_library().

        Any other status is an error.
        """
        self.log.debug(f"_install_libraries() {self.process_status}")
        if self.process_status == "start" or (len(self.libraries_to_install) > 0 and self.process_status == "success"):
            library = self.libraries_to_install[0]
            del self.libraries_to_install[0]
            self._install_single_library(library)
        elif self.process_status == "success":
            self.process_status = "start"
            self._refresh_boards()
        else:
            self._process_error()

    def _install_single_library(self, library):
        """
        Method to start installing the specified library.
        """
        self.log.debug(f"_install_single_library() {self.process_status}\nlibrary: {library}")
        self.process_start("install_libraries", "Install Arduino library " + library, "Manage_CLI")
        self.acli.install_library(self.acli.cli_file_path(), library, self.queue)

    def _refresh_boards(self):
        """
        Method to start refreshing the list of attached boards.

        If we need to start, call the acli.list_boards() method.

        If successful, call _process_finished().

        Any other status is an error.
        """
        self.log.debug(f"_refresh_boards() {self.process_status}")
        if self.process_status == "start":
            self.process_start("refresh_boards", "Refreshing Arduino CLI board list", "Manage_CLI")
            self.acli.list_boards(self.acli.cli_file_path(), self.queue)
        elif self.process_status == "success":
            self._process_finished()
        else:
            self._process_error()

    def _process_finished(self):
        """
        Method to finalise the processes on successful completion.
        """
        self.log.debug("_process_finished()")
        self.process_stop()
        self.restore_input_states()
        self.set_state()
