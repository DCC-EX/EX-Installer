"""
Module for the Select Device page view
"""

# Import Python modules
import customtkinter as ctk

# Import local modules
from .common_widgets import WindowLayout
from . import images


class SelectDevice(WindowLayout):
    # Define text to use in labels
    instruction_text = ("Select your chosen device from the options below.\n\n" +
                        "If the device detected matches multiple devices, select the correct one from the pulldown " +
                        "list provided.\n\n" +
                        "If you have a generic or clone device, it likely appears as “Unknown”. In this instance, " +
                        "you will need to select the appropriate device from the pulldown list provided.")

    """
    Class for the Welcome view
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set up title
        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Select your device")

        # Set up next/back buttons
        self.next_back.set_back_text("Manage Arduino CLI")
        self.next_back.set_back_command(lambda view="manage_arduino_cli": parent.switch_view(view))
        self.next_back.set_next_text("Select product to install")
        self.next_back.set_next_command(lambda view="select_product": parent.switch_view(view))

        # Set up and configure container frame
        self.select_device_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.select_device_frame.grid(column=0, row=0, sticky="nsew")
        self.select_device_frame.grid_columnconfigure(0, weight=1)
        self.select_device_frame.grid_rowconfigure(0, weight=1)

        # Create instruction label
        self.instruction_label = ctk.CTkLabel(self.select_device_frame,
                                              text=self.instruction_text,
                                              wraplength=780)

        # Create list device button
        self.list_device_button = ctk.CTkButton(self.select_device_frame, text="List Devices")

        # Create device list container frame
        self.device_list_frame = ctk.CTkFrame(self.select_device_frame)
