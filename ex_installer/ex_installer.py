"""
This is the root window of the EX-Installer application.

© 2023, Peter Cole. All rights reserved.
© 2023, Harald Barth. All rights reserved.

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
import sys
import logging
import traceback
from CTkMessagebox import CTkMessagebox
import subprocess
import os
import platform
from tkinter import Menu
import webbrowser

# Import local modules
from . import images
from . import theme
from .arduino_cli import ArduinoCLI
from .git_client import GitClient
from .welcome import Welcome
from .manage_arduino_cli import ManageArduinoCLI
from .select_device import SelectDevice
from .select_product import SelectProduct
from .select_version_config import SelectVersionConfig
from .ex_commandstation import EXCommandStation
from .ex_ioexpander import EXIOExpander
from .ex_turntable import EXTurntable
from .advanced_config import AdvancedConfig
from .compile_upload import CompileUpload
from ex_installer.version import ex_installer_version

# Set theme and appearance, and deactive screen scaling
ctk.set_default_color_theme(theme.DCC_EX_THEME)
ctk.set_appearance_mode("light")
ctk.deactivate_automatic_dpi_awareness()


class EXInstaller(ctk.CTk):
    """
    EX-Installer root window
    """
    # Create Arduino CLI and GitHub instances for the entire application
    acli = ArduinoCLI()
    git = GitClient()

    # Set application version
    app_version = ex_installer_version

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start view")
        self.report_callback_exception = self.exception_handler

        # Hide window while GUI is built initially, show after 250ms
        self.withdraw()
        self.after(250, self.deiconify)

        # Dictionary to retain views once created for switching between them while retaining options
        self.frames = {}

        # Set window geometry, title, and icon
        self.title("EX-Installer")

        if sys.platform.startswith("win"):
            self.iconbitmap(images.DCC_EX_ICON_ICO)
            self.iconbitmap(default=images.DCC_EX_ICON_ICO)

        self.geometry("800x600")
        self.minsize(width=800, height=600)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.views = {
            "welcome": Welcome,
            "manage_arduino_cli": ManageArduinoCLI,
            "select_device": SelectDevice,
            "select_product": SelectProduct,
            "select_version_config": SelectVersionConfig,
            "ex_commandstation": EXCommandStation,
            "ex_ioexpander": EXIOExpander,
            "ex_turntable": EXTurntable,
            "advanced_config": AdvancedConfig,
            "compile_upload": CompileUpload
        }
        self.view = None
        self.use_existing = False  # needed for backing up to select_version_config
        self.advanced_config = False  # needed for backing up

        # Create basic menu for Info -> About
        self.menubar = Menu(self)
        self.info_menu = Menu(self.menubar, tearoff=0)
        self.info_menu.add_command(label="About", command=self.about)
        self.info_menu.add_command(label="DCC-EX Website", command=self.website)
        self.info_menu.add_command(label="EX-Installer Instructions", command=self.instructions)
        self.menubar.add_cascade(label="Info", menu=self.info_menu)
        self.configure(menu=self.menubar)

    def exception_handler(self, exc_type, exc_value, exc_traceback):
        """
        Handler for uncaught exceptions
        """
        message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        log_file = None
        for handler in self.log.parent.handlers:
            if handler.__class__.__name__ == "FileHandler":
                log_file = handler.baseFilename
        self.log.critical("Uncaught exception: %s", message)
        critical = CTkMessagebox(master=self, title="Error",
                                 message="EX-Installer experienced an unknown error, " +
                                 "please send the log file to the DCC-EX team for further analysis",
                                 icon="cancel", option_1="Show log", option_2="Exit",
                                 border_width=3, cancel_button=None)
        if critical.get() == "Show log":
            if platform.system() == "Darwin":
                subprocess.call(("open", log_file))
            elif platform.system() == "Windows":
                os.startfile(log_file)
            else:
                subprocess.call(("xdg-open", log_file))
        elif critical.get() == "Exit":
            sys.exit()

    def switch_view(self, view_class, product=None, version=None):
        """
        Function to switch views

        These views require a product parameter to be supplied:
        - compile_upload
        - select_version_config
        - advanced_config

        These views should get version info if available:
        - ex_commandstation

        Version should ideally contain semantic numbering, but any name will work
        If semantic numbering is used, the product configuration screens can determine
        options based on those numbers

        For semantic numbering to work, it must match GitHub tag format:
        vX.Y.Z-Prod|Devel

        Version info will be available in:
        self.product_version_name
        self.product_major_version
        self.product_minor_version
        self.product_patch_version

        All default to None if not defined
        """
        calling_product = None
        if view_class:
            if version:
                version_details = GitClient.extract_version_details(version)
            if self.view:
                if hasattr(self.view, "product"):
                    calling_product = self.view.product
                    self.log.debug("Calling product %s", calling_product)
                self.log.debug("Switch from existing view %s", self.view._name)
            if view_class in self.frames:
                self.log.debug("view_class=%s", view_class)
                self.view = self.frames[view_class]
                if (
                    view_class == "compile_upload" or view_class == "advanced_config" or
                    (view_class == "select_version_config" and product != calling_product)
                ):
                    self.view.destroy()
                    self.view = self.views[view_class](self)
                    self.frames[view_class] = self.view
                    self.view.set_product(product)
                    if hasattr(self.view, "set_product_version"):
                        self.view.set_product_version(version, *version_details)
                    self.view.grid(column=0, row=0, sticky="nsew")
                    self.log.debug("Changing product for %s", view_class)
                    return
                elif view_class == "select_version_config":
                    self.view.set_product(product)
                if version and hasattr(self.view, "set_product_version"):
                    self.view.set_product_version(version, *version_details)
                self.view.tkraise()
                self.log.debug("Raising view %s", view_class)
            else:
                self.view = self.views[view_class](self)
                self.frames[view_class] = self.view
                if (
                    view_class == "compile_upload" or view_class == "advanced_config" or
                    view_class == "select_version_config"
                ):
                    self.view.set_product(product)
                if hasattr(self.view, "set_product_version"):
                    self.view.set_product_version(version, *version_details)
                self.view.grid(column=0, row=0, sticky="nsew")
                self.log.debug("Launching new instance of %s", view_class)

    def about(self):
        """
        Message box popup for the Info -> About menu item
        """
        about_list = [f"EX-Installer version {self.app_version}"]
        if self.acli.selected_device is not None:
            index = self.acli.selected_device
            board = self.acli.detected_devices[index]["matching_boards"][0]["name"]
            port = self.acli.detected_devices[index]["port"]
            about_list.append(f"Current selected device: {board} on port {port}")
        about_message = "\n\n".join(about_list)
        about_box = CTkMessagebox(master=self, title="About EX-Installer", icon="info",
                                  message=about_message, border_width=3, cancel_button=None,
                                  option_2="OK", option_1="Show log", icon_size=(30, 30),
                                  font=ctk.CTkFont(family="Helvetica", size=14, weight="normal"))
        if about_box.get() == "Show log":
            log_file = None
            for handler in self.log.parent.handlers:
                if handler.__class__.__name__ == "FileHandler":
                    log_file = handler.baseFilename
            if platform.system() == "Darwin":
                subprocess.call(("open", log_file))
            elif platform.system() == "Windows":
                os.startfile(log_file)
            else:
                subprocess.call(("xdg-open", log_file))

    def website(self):
        """
        Link to the DCC-EX website from the Info menu
        """
        webbrowser.open_new("https://dcc-ex.com")

    def instructions(self):
        """
        Link to EX-Installer instructions from the Info menu
        """
        webbrowser.open_new("https://dcc-ex.com/ex-installer/index.html")
