"""
Module for the Advanced Configuration page view
"""

# Import Python modules
import customtkinter as ctk
from PIL import Image
import logging

# Import local modules
from .common_widgets import WindowLayout
from . import images
from .product_details import product_details as pd
from .file_manager import FileManager as fm

class AdvancedConfig(WindowLayout):
    """
    Class for the Edit Config Files view
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start view AdvancedConfig")

        # Define product variable
        # self.product = None
        self.product = "ex_commandstation"

        # get the filenames to be edited
        local_repo_dir = pd[self.product]["repo_name"].split("/")[1]
        self.ex_commandstation_dir = fm.get_install_dir(local_repo_dir)
        self.config_file_path = fm.get_filepath(self.ex_commandstation_dir, "config.h")
        self.myAutomation_file_path = fm.get_filepath(self.ex_commandstation_dir, "myAutomation.h")

        # Set up title
        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Advanced Configuration")

        # Hide log button to start
        self.next_back.hide_log_button()

        # Set up and configure the edit frame, which will contain the editboxes
        self.edit_frame = ctk.CTkFrame(self.main_frame, height=360, border_width=1)
        self.edit_frame.grid(column=0, row=0, sticky="nsew")

        self.edit_frame.grid_columnconfigure((0, 1), weight=1)
        self.edit_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # add instruction label
        self.instruction_label = ctk.CTkLabel(self.edit_frame,
                                              text="Review and Edit Configuration Files (if needed)",
                                              font=self.instruction_font)
        self.instruction_label.grid(   column=0, row=0, columnspan=2, padx=5, pady=5)
        # add editors  //TODO: put these in a loop based on settings from elsewhere
        self.config_label = ctk.CTkLabel(self.edit_frame, text=self.config_file_path)
        self.config_label.grid(        column=0, row=1, sticky="w")
        self.config_textbox = ctk.CTkTextbox(self.edit_frame, border_width=2, border_spacing=5,
                                              fg_color="#E5E5E5", width=780, height=180)
        self.config_textbox.grid(      column=0, row=2, sticky="nsew")
        self.myAutomation_label = ctk.CTkLabel(self.edit_frame, text=self.myAutomation_file_path)
        self.myAutomation_label.grid(  column=0, row=3, sticky="w")
        self.myAutomation_textbox = ctk.CTkTextbox(self.edit_frame, border_width=2, border_spacing=5,
                                              fg_color="#E5E5E5", width=780, height=180)
        self.myAutomation_textbox.grid(column=0, row=4, sticky="nsew")

        # Set next/back buttons
        self.next_back.set_back_text(f"Configure {pd[self.product]['product_name']}")
        self.next_back.set_back_command(lambda view=self.product: self.master.switch_view(view))
        self.next_back.set_next_text("Compile and Upload")
        self.next_back.set_next_command(lambda : self.save_config_files()) #TODO: this is a strange "fix" or func runs too early

        self.read_config_files()

    def save_config_files(self) :
        self.log.debug("in save_config_files()")
        write_config = fm.write_config_file(self.config_file_path, self.config_textbox.get("1.0", "end"))
        if write_config != self.config_file_path:
            self.process_error(f"Could not write config.h: {write_config}")
            self.log.error("Could not write config file: %s", write_config)
            return
        write_config = fm.write_config_file(self.myAutomation_file_path, self.myAutomation_textbox.get("1.0", "end"))
        if write_config != self.myAutomation_file_path:
            self.process_error(f"Could not write myAutomation.h: {write_config}")
            self.log.error("Could not write config file: %s", write_config)
            return
        self.master.switch_view("compile_upload", self.product)

    def read_config_files(self) :
        # copy the file contents into the edit boxes
        text = fm.read_config_file(self.config_file_path)
        self.config_textbox.delete("0.0", "end")
        self.config_textbox.insert("0.0", text)
        text = fm.read_config_file(self.myAutomation_file_path)
        self.myAutomation_textbox.delete("0.0", "end")
        self.myAutomation_textbox.insert("0.0", text)

