"""
Module for the Advanced Configuration page view
  Product info is used to build dynamic list of config files
  An edit box is shown for each config file. Changes are written to those files
  prior to advancing to Compile Upload. This view can be accessed:
  1) If user chooses "Use Existing Config Files"
  2) If user chooses "Advanced Config" on the product configuration page
  3) by backing up from Compile_Upload (only if reached from this view)
"""

# Import Python modules
import customtkinter as ctk
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

        self.product = None

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start view AdvancedConfig")

        # Set up title
        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Advanced Configuration")

        # Hide log button to start
        self.next_back.hide_log_button()
        self.next_back.hide_monitor_button()

        # Set up and configure the edit frame, which will contain the editboxes
        self.edit_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.edit_frame.grid(column=0, row=0, sticky="nsew")

        self.edit_list = []  # remember list of files to edit

    def set_product(self, product):
        """
        Function to set/reset the product, called from ex_installer when switching views
          used to trigger screen refresh
        """
        self.log.debug("in set_product(%s)", product)
        self.product = product
        self.reload_view()  # paint/repaint the screen stuff

    def save_config_files(self):
        self.log.debug("in save_config_files()")
        for file_name in self.edit_list:
            self.log.debug("saving " + file_name)
            config_file_path = fm.get_filepath(self.product_dir, file_name)
            write_config = fm.write_config_file(config_file_path, self.edit_textbox[file_name].get("1.0", "end"))
            if write_config != config_file_path:
                self.process_error(f"Could not write config.h: {write_config}")
                self.log.error("Could not write config file: %s", write_config)
                return
        self.master.switch_view("compile_upload", self.product)

    def reload_view(self):
        """
        Build/Refresh items for this view, including the dynamic list of edit boxes

        If two config files, display side by side which is quite practical

        If more than two config files, use CTkTabview for a nicer editing experience
        """
        self.log.debug("in reload_view()")

        self.product_name = pd[self.product]["product_name"]

        # empty the edit frame
        for widget in self.edit_frame.winfo_children():
            widget.destroy()

        # add instruction label
        self.instruction_label = ctk.CTkLabel(self.edit_frame,
                                              text="Review and Edit Configuration Files (if needed) for " +
                                              self.product_name,
                                              font=self.instruction_font)
        self.instruction_label.grid(column=0, row=0, columnspan=2, padx=5, pady=5)

        # get list of files to edit
        local_repo_dir = pd[self.product]["repo_name"].split("/")[1]
        self.product_dir = fm.get_install_dir(local_repo_dir)
        self.edit_list = fm.get_config_files(self.product_dir, pd[self.product]["minimum_config_files"])
        self.edit_list += fm.get_config_files(self.product_dir, pd[self.product]["other_config_files"])

        self.edit_label = {}
        self.edit_textbox = {}
        edit_column = 0
        if (len(self.edit_list)) < 3:
            self.edit_frame.grid_rowconfigure((0, 1), weight=0)
            self.edit_frame.grid_rowconfigure(2, weight=1)
            for file_name in self.edit_list:
                self.edit_frame.grid_columnconfigure(edit_column, weight=1)
                self.log.debug("adding edit box for " + file_name)
                self.edit_label[file_name] = ctk.CTkLabel(self.edit_frame, text=file_name,
                                                          font=self.instruction_font)
                self.edit_label[file_name].grid(column=edit_column, row=1, padx=5, pady=5, sticky="nsew")
                self.edit_textbox[file_name] = ctk.CTkTextbox(self.edit_frame, border_width=2, wrap="none",
                                                              fg_color="#E5E5E5", activate_scrollbars=True)
                self.edit_textbox[file_name].grid(column=edit_column, row=2, padx=4, pady=5, sticky="nsew")
                file_path = fm.get_filepath(self.product_dir, file_name)
                text = fm.read_config_file(file_path)
                self.edit_textbox[file_name].insert("0.0", text)
                edit_column += 1
        else:
            self.edit_frame.grid_columnconfigure(0, weight=1)
            self.edit_frame.grid_rowconfigure(1, weight=1)
            self.config_tabview = ctk.CTkTabview(self.edit_frame, border_width=2,
                                                 segmented_button_fg_color="#00A3B9",
                                                 segmented_button_unselected_color="#00A3B9",
                                                 segmented_button_selected_color="#00353D",
                                                 segmented_button_selected_hover_color="#017E8F",
                                                 text_color="white")
            self.config_tabview.grid(column=0, row=1, padx=5, pady=5, sticky="nsew")
            for file_name in self.edit_list:
                self.config_tabview.add(file_name)
                self.config_tabview.tab(file_name).grid_columnconfigure(0, weight=1)
                self.config_tabview.tab(file_name).grid_rowconfigure(0, weight=1)
                self.edit_textbox[file_name] = ctk.CTkTextbox(self.config_tabview.tab(file_name), border_width=2,
                                                              wrap="none", fg_color="#E5E5E5", activate_scrollbars=True)
                self.edit_textbox[file_name].grid(column=0, row=0, padx=5, pady=5, sticky="nsew")
                file_path = fm.get_filepath(self.product_dir, file_name)
                text = fm.read_config_file(file_path)
                self.edit_textbox[file_name].insert("0.0", text)

        # Set next/back buttons
        if self.master.use_existing:  # return from whence you arrived
            self.next_back.set_back_text("Select Version")
            self.next_back.set_back_command(lambda view="select_version_config",
                                            product=self.product: self.master.switch_view(view, product))
        else:
            self.next_back.set_back_text(f"Configure {pd[self.product]['product_name']}")
            self.next_back.set_back_command(lambda view=self.product: self.master.switch_view(view))
        self.next_back.set_next_text("Compile and Upload")
        self.next_back.set_next_command(lambda: self.save_config_files())
