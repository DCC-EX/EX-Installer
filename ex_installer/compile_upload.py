"""
Module for the Compile and Upload page view

© 2023, Peter Cole. All rights reserved.

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

# Import local modules
from .common_widgets import WindowLayout
from .product_details import product_details as pd
from .file_manager import FileManager as fm
from . import images


class CompileUpload(WindowLayout):
    """
    Class for the Compile and Upload view
    """

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
            "<<Upload_Software>>": self.upload_software
        }
        for sequence, callback in event_callbacks.items():
            self.bind_class("bind_events", sequence, callback)
        new_tags = self.bindtags() + ("bind_events",)
        self.bindtags(new_tags)

        # Define variables
        self.product = None
        self.install_dir = None

        # Set up container frame
        self.compile_upload_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.compile_upload_frame.grid(column=0, row=0, sticky="nsew")

        # Set up text variables
        self.intro_text = None
        self.instruction_text = ("Please ensure your device is connected to your USB port and then " +
                                 "click the Load button to commence loading the software on to your device.")

        # Create widgets
        self.intro_label = ctk.CTkLabel(self.compile_upload_frame, text=self.intro_text,
                                        font=self.instruction_font, wraplength=780)
        self.instruction_label = ctk.CTkLabel(self.compile_upload_frame, text=self.instruction_text,
                                              font=self.instruction_font, wraplength=780)
        self.congrats_label = ctk.CTkLabel(self.compile_upload_frame, text=None,
                                           font=self.heading_font)
        self.success_label = ctk.CTkLabel(self.compile_upload_frame, text=None,
                                          font=self.instruction_font)
        self.upload_button = ctk.CTkButton(self.compile_upload_frame, width=200, height=50,
                                           text="Load", font=self.action_button_font,
                                           command=lambda event="upload_software": self.upload_software(event))
        self.details_label = ctk.CTkLabel(self.compile_upload_frame, text="Results will be shown below:",
                                          font=self.instruction_font)
        self.details_textbox = ctk.CTkTextbox(self.compile_upload_frame, border_width=2, border_spacing=5,
                                              fg_color="#E5E5E5", width=780, height=180, state="disabled")
        self.backup_config_button = ctk.CTkButton(self.compile_upload_frame, width=200, height=50,
                                                  text="Backup config files", font=self.action_button_font,
                                                  command=self.show_backup_popup)

        # Layout frame
        grid_options = {"padx": 5, "pady": 5}
        self.compile_upload_frame.grid_columnconfigure((0, 1), weight=1)
        self.compile_upload_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.intro_label.grid(column=0, row=0, columnspan=2, **grid_options)
        self.congrats_label.grid(column=0, row=0, columnspan=2, **grid_options)
        self.instruction_label.grid(column=0, row=1, columnspan=2, **grid_options)
        self.success_label.grid(column=0, row=1, columnspan=2, **grid_options)
        self.upload_button.grid(column=0, row=2, columnspan=2, **grid_options)
        self.backup_config_button.grid(column=1, row=2, **grid_options)
        self.details_label.grid(column=0, row=3, columnspan=2, **grid_options)
        self.details_textbox.grid(column=0, row=4, columnspan=2, **grid_options)

        # Hide next and log buttons to start
        self.next_back.hide_log_button()
        self.next_back.hide_next()
        self.next_back.hide_monitor_button()

        # Hide backup button to start
        self.backup_config_button.grid_remove()

        # Set next button up
        self.next_back.set_next_text("Close EX-Installer")
        self.next_back.set_next_command(sys.exit)
        self.next_back.enable_next()

    def set_product(self, product):
        """
        Function to set the product details of what's being uploaded
          called from ex_installer when switching views
          also refreshes product-dependent screen items
        """
        self.product = product
        self.set_title_text(f"Load {pd[self.product]['product_name']}")
        self.set_title_logo(pd[product]["product_logo"])
        self.congrats_label.grid_remove()
        self.success_label.grid_remove()
        text = (f"{pd[self.product]['product_name']} is now ready to be loaded on to your " +
                f"{self.acli.detected_devices[self.acli.selected_device]['matching_boards'][0]['name']} " +
                f"attached to {self.acli.detected_devices[self.acli.selected_device]['port']}")
        self.intro_label.configure(text=text)
        local_repo_dir = pd[self.product]["repo_name"].split("/")[1]
        self.install_dir = fm.get_install_dir(local_repo_dir)
        if self.master.advanced_config:
            self.next_back.set_back_text("Advanced Config")
            self.next_back.set_back_command(lambda view="advanced_config",
                                            product=self.product: self.master.switch_view(view, product))
        elif self.master.use_existing:
            self.next_back.set_back_text("Select Version")
            self.next_back.set_back_command(lambda view="select_version_config",
                                            product=self.product: self.master.switch_view(view, product))
        else:
            self.next_back.set_back_text(f"Configure {pd[self.product]['product_name']}")
            self.next_back.set_back_command(lambda view=product: self.master.switch_view(view))

    def show_backup_button(self):
        self.upload_button.configure(text="Load again")
        self.upload_button.grid_configure(columnspan=1)
        self.backup_config_button.grid()

    def upload_software(self, event):
        """
        Function to start the upload process via the Arduino CLI
        """
        device = self.acli.detected_devices[self.acli.selected_device]["matching_boards"][0]["name"]
        fqbn = self.acli.detected_devices[self.acli.selected_device]["matching_boards"][0]["fqbn"]
        port = self.acli.detected_devices[self.acli.selected_device]["port"]
        if event == "upload_software":
            self.disable_input_states(self)
            self.set_details("")
            self.process_start("compiling",
                               f"Compiling {pd[self.product]['product_name']} for your {device}",
                               "Upload_Software")
            self.acli.compile_sketch(self.acli.cli_file_path(), fqbn, self.install_dir, self.queue)
        elif self.process_phase == "compiling":
            if self.process_status == "success":
                self.set_details(self.process_data)
                self.process_start("uploading",
                                   f"Loading {pd[self.product]['product_name']} on to your {device}",
                                   "Upload_Software")
                self.acli.upload_sketch(self.acli.cli_file_path(), fqbn, port, self.install_dir, self.queue)
            elif self.process_status == "error":
                self.set_details(self.process_data)
                self.process_error(self.process_topic)
                self.restore_input_states()
                self.next_back.hide_monitor_button()
                self.next_back.show_next()
                self.next_back.show_log_button()
                self.show_backup_button()
        elif self.process_phase == "uploading":
            if self.process_status == "success":
                self.process_stop()
                self.restore_input_states()
                self.set_details(self.process_data)
                self.upload_success()
                self.next_back.hide_log_button()
                self.next_back.show_monitor_button()
            elif self.process_status == "error":
                self.process_error(self.process_topic)
                self.restore_input_states()
                self.set_details(self.process_data)
                self.upload_error()
                self.next_back.hide_monitor_button()
                self.next_back.show_log_button()
            self.next_back.show_next()
            self.show_backup_button()

    def upload_success(self):
        """
        Function to display successful outcome after upload
        """
        self.intro_label.grid_remove()
        self.instruction_label.grid_remove()
        self.congrats_label.configure(text="Congratulations!")
        self.congrats_label.grid()
        text = (f"{pd[self.product]['product_name']} has successfully been loaded on to your " +
                f"{self.acli.detected_devices[self.acli.selected_device]['matching_boards'][0]['name']}")
        self.success_label.configure(text=text)
        self.success_label.grid()

    def upload_error(self):
        """
        Function to display unsuccessful outcome after upload error
        """
        self.intro_label.grid_remove()
        self.instruction_label.grid_remove()
        self.congrats_label.configure(text="Error!")
        self.congrats_label.grid()
        text = (f"{pd[self.product]['product_name']} was not successfully loaded on to your " +
                f"{self.acli.detected_devices[self.acli.selected_device]['matching_boards'][0]['name']}")
        self.success_label.configure(text=text)
        self.success_label.grid()

    def set_details(self, text):
        """
        Function to update the contents of the details textbox
        """
        self.details_textbox.configure(state="normal")
        self.details_textbox.delete("0.0", "end")
        self.details_textbox.insert("0.0", text)
        self.details_textbox.configure(state="disabled")

    def show_backup_popup(self):
        """
        Function to show the message box to select the backup folder
        """
        if hasattr(self, "backup_popup") and self.backup_popup is not None and self.backup_popup.winfo_exists():
            self.backup_popup.focus()
        else:
            self.backup_popup = ctk.CTkToplevel(self)
            self.backup_popup.focus()
            self.backup_popup.lift(self)

            # Set icon and title
            if sys.platform.startswith("win"):
                self.backup_popup.after(250, lambda icon=images.DCC_EX_ICON_ICO: self.backup_popup.iconbitmap(icon))
            self.backup_popup.title("Backup config files")
            self.backup_popup.withdraw()
            self.backup_popup.after(250, self.backup_popup.deiconify)
            self.backup_popup.grid_columnconfigure(0, weight=1)
            self.backup_popup.grid_rowconfigure(0, weight=1)
            self.window_frame = ctk.CTkFrame(self.backup_popup, fg_color="grey95")
            self.window_frame.grid_columnconfigure((0, 1, 2), weight=1)
            self.window_frame.grid_rowconfigure((0, 1), weight=1)
            self.window_frame.grid(column=0, row=0, sticky="nsew")
            self.folder_label = ctk.CTkLabel(self.window_frame, text="Select the folder to store your config files:",
                                             font=self.instruction_font)
            self.status_frame = ctk.CTkFrame(self.window_frame, border_width=2)
            self.status_label = ctk.CTkLabel(self.status_frame, text="Status:",
                                             font=self.instruction_font)
            self.status_text = ctk.CTkLabel(self.status_frame, text="Enter or select backup destination",
                                            font=self.bold_instruction_font)
            self.backup_path = ctk.StringVar(value=None)
            self.backup_path_entry = ctk.CTkEntry(self.window_frame, textvariable=self.backup_path,
                                                  width=300)
            self.browse_button = ctk.CTkButton(self.window_frame, text="Browse",
                                               width=80, command=self.browse_backup_dir)
            self.backup_button = ctk.CTkButton(self.window_frame, width=200, height=50,
                                               text="Backup files", font=self.action_button_font,
                                               command=lambda overwrite=False: self.backup_config_files(overwrite))
            self.overwrite_button = ctk.CTkButton(self.window_frame, width=200, height=50,
                                                  text="Overwrite?", font=self.action_button_font,
                                                  command=lambda overwrite=True: self.backup_config_files(overwrite))
            self.folder_label.grid(column=0, row=0, padx=(10, 1), pady=(10, 5))
            self.backup_path_entry.grid(column=1, row=0, padx=1, pady=(10, 5))
            self.browse_button.grid(column=2, row=0, padx=(1, 10), pady=(10, 5))
            self.backup_button.grid(column=0, row=1, columnspan=3, padx=10, pady=5)
            self.overwrite_button.grid(column=0, row=1, columnspan=3, padx=10, pady=5)
            self.overwrite_button.grid_remove()
            self.status_frame.grid_columnconfigure((0, 1), weight=1)
            self.status_frame.grid_rowconfigure(0, weight=1)
            self.status_frame.grid(column=0, row=2, columnspan=3, sticky="nsew", padx=10, pady=(5, 10))
            self.status_label.grid(column=0, row=0, padx=5, pady=5)
            self.status_text.grid(column=1, row=0, padx=5, pady=5)

    def browse_backup_dir(self):
        """
        Opens a directory browser dialogue to select the folder containing config files
        """
        directory = ctk.filedialog.askdirectory()
        if directory:
            self.backup_path.set(directory)
            self.log.debug("Backup config to %s", directory)
            self.backup_popup.focus()

    def backup_config_files(self, overwrite):
        """
        Function to backup config files to the specified folder
        """
        if fm.is_valid_dir(self.backup_path.get()):
            local_repo_dir = pd[self.product]["repo_name"].split("/")[1]
            install_dir = fm.get_install_dir(local_repo_dir)
            check_list = fm.get_config_files(self.backup_path.get(), pd[self.product]["minimum_config_files"])
            if hasattr(pd[self.product], "other_config_files"):
                extra_check_list = fm.get_config_files(install_dir, pd[self.product]["other_config_files"])
                if extra_check_list:
                    check_list += extra_check_list
            if check_list and not overwrite:
                error_list = ", ".join(check_list)
                message = ("Existing files found , click Overwrite to overwrite them\n" +
                           f"Files found: {error_list}")
                self.status_text.configure(text=message, text_color="orange")
                self.backup_button.grid_remove()
                self.overwrite_button.grid()
                self.log.debug(message)
            else:
                copy_list = fm.get_config_files(install_dir, pd[self.product]["minimum_config_files"])
                if copy_list:
                    if "other_config_files" in pd[self.product]:
                        extra_list = fm.get_config_files(install_dir, pd[self.product]["other_config_files"])
                        if extra_list:
                            copy_list += extra_list
                    file_copy = fm.copy_config_files(install_dir, self.backup_path.get(), copy_list)
                    if file_copy:
                        file_list = ", ".join(file_copy)
                        self.status_text.configure(text=f"Failed to copy one or more files: {file_list}",
                                                   text_color="red")
                        self.log.error("Failed to copy: %s", file_list)
                    else:
                        self.status_text.configure(text="Backup successful", text_color="green")
                        self.log.debug("Backup successful")
                else:
                    self.status_text.configure("Selected configuration directory is missing the required files",
                                               text_color="red")
                    self.log.error("Directory %s is missing required files", self.config_path.get())
                self.overwrite_button.grid_remove()
                self.backup_button.grid()
        else:
            if self.backup_path.get() == "":
                message = "You must specific a valid folder to backup to"
            else:
                message = f"{self.backup_path.get()} is not a valid directory"
            self.status_text.configure(text=message,
                                       text_color="red")
            self.overwrite_button.grid_remove()
            self.backup_button.grid()
