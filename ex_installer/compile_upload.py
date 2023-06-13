"""
Module for the Compile and Upload page view
"""

# Import Python modules
import customtkinter as ctk
import sys
import logging

# Import local modules
from .common_widgets import WindowLayout
from .product_details import product_details as pd
from .file_manager import FileManager as fm


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

        # Hide next button as there is no next
        self.next_back.hide_next()

        # Set up container frame
        self.compile_upload_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.compile_upload_frame.grid(column=0, row=0, sticky="nsew")

        # Set up text variables
        self.intro_text = None
        self.instruction_text = ("Please ensure your device is connected to your USB port and then " +
                                 "click the Upload button to commence installing the software.")

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
                                           text="Upload", font=self.action_button_font,
                                           command=lambda event="upload_software": self.upload_software(event))
        self.details_label = ctk.CTkLabel(self.compile_upload_frame, text="Results will be shown below:",
                                          font=self.instruction_font)
        self.details_textbox = ctk.CTkTextbox(self.compile_upload_frame, border_width=2, border_spacing=5,
                                              fg_color="#E5E5E5", width=780, height=180, state="disabled")

        # Layout frame
        grid_options = {"padx": 5, "pady": 5}
        self.compile_upload_frame.grid_columnconfigure(0, weight=1)
        self.compile_upload_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.intro_label.grid(column=0, row=0, **grid_options)
        self.congrats_label.grid(column=0, row=0, **grid_options)
        self.instruction_label.grid(column=0, row=1, **grid_options)
        self.success_label.grid(column=0, row=1, **grid_options)
        self.upload_button.grid(column=0, row=2, **grid_options)
        self.details_label.grid(column=0, row=3, **grid_options)
        self.details_textbox.grid(column=0, row=4, **grid_options)

    def set_product(self, product):
        """
        Function to set the product details of what's being uploaded
        """
        self.product = product
        self.set_title_text(f"Upload {pd[self.product]['product_name']}")
        self.set_title_logo(pd[product]["product_logo"])
        self.congrats_label.grid_remove()
        self.success_label.grid_remove()
        self.next_back.set_back_text(f"Configure {pd[self.product]['product_name']}")
        self.next_back.set_back_command(lambda view=product: self.master.switch_view(view))
        text = (f"{pd[self.product]['product_name']} is now ready to be uploaded to your " +
                f"{self.acli.detected_devices[self.acli.selected_device]['matching_boards'][0]['name']} " +
                f"attached to {self.acli.detected_devices[self.acli.selected_device]['port']}")
        self.intro_label.configure(text=text)
        local_repo_dir = pd[self.product]["repo_name"].split("/")[1]
        self.install_dir = fm.get_install_dir(local_repo_dir)

    def upload_software(self, event):
        """
        Function to start the upload process via the Arduino CLI
        """
        if event == "upload_software":
            self.disable_input_states(self)
            self.set_details("")
            self.process_start("uploading",
                               f"Compiling and uploading {pd[self.product]['product_name']} to your device",
                               "Upload_Software")
            self.acli.upload_sketch(self.acli.cli_file_path(),
                                    self.acli.detected_devices[self.acli.selected_device]["matching_boards"][0]["fqbn"],
                                    self.acli.detected_devices[self.acli.selected_device]["port"],
                                    self.install_dir,
                                    self.queue)
        elif self.process_phase == "uploading":
            if self.process_status == "success":
                self.process_stop()
                self.restore_input_states()
                self.set_details(self.process_data)
                self.upload_success()
            elif self.process_status == "error":
                self.process_error("Error uploading software")
                self.restore_input_states()
                self.set_details(self.process_data)
                self.upload_error()
            self.next_back.enable_next()
            self.next_back.show_next()
            self.next_back.set_next_text("Close EX-Installer")
            self.next_back.set_next_command(sys.exit)

    def upload_success(self):
        """
        Function to display successful outcome after upload
        """
        self.intro_label.grid_remove()
        self.instruction_label.grid_remove()
        self.congrats_label.configure(text="Congratulations!")
        self.congrats_label.grid()
        text = (f"{pd[self.product]['product_name']} has successfully been uploaded to your " +
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
        text = (f"{pd[self.product]['product_name']} was not successfully uploaded to your " +
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
