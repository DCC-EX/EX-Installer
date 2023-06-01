"""
Module for the EX-CommandStation page view
"""

# Import Python modules
import customtkinter as ctk

# Import local modules
from .common_widgets import WindowLayout
from .product_details import product_details as pd


class EXCommandStation(WindowLayout):
    """
    Class for the EX-CommandStation view
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set up title
        self.set_title_logo(pd["ex_commandstation"]["product_logo"])
        self.set_title_text("Install EX-CommandStation")

        # Set up next/back buttons
        self.next_back.set_back_text("Select Product")
        self.next_back.set_back_command(lambda view="select_product": parent.switch_view(view))
        self.next_back.set_next_text("Compile and upload")
        self.next_back.set_next_command(lambda product="ex_commandstation": parent.compile_upload(product))

        # Set up, configure, and grid container frame
        self.ex_commandstation_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.ex_commandstation_frame.grid_columnconfigure(0, weight=1)
        self.ex_commandstation_frame.grid_rowconfigure(0, weight=1)
        self.ex_commandstation_frame.grid(column=0, row=0, sticky="nsew")

        # Set up instruction label
        self.instruction_label = ctk.CTkLabel(self.ex_commandstation_frame, text="Instructions")

        # Set up select version frame and radio buttons
        self.version_frame = ctk.CTkFrame(self.ex_commandstation_frame,
                                          border_width=2,
                                          fg_color="#E5E5E5")

        # Set up display widgets
        self.display_switch = ctk.CTkSwitch(self.ex_commandstation_frame, onvalue="on", offvalue="off")
        self.display_combo = ctk.CTkComboBox(self.ex_commandstation_frame, values=["Select display type"])

        # Set up WiFi widgets
        self.wifi_switch = ctk.CTkSwitch(self.ex_commandstation_frame, onvalue="on", offvalue="off")
        self.wifi_frame = ctk.CTkFrame(self.ex_commandstation_frame,
                                       border_width=2,
                                       fg_color="#E5E5E5")

        # Layout frame
        self.instruction_label.grid(column=0, row=0, columnspan=3)
        self.version_frame.grid(column=0, row=1)
        self.display_switch.grid(column=0, row=2)
        self.display_combo.grid(column=1, row=2)
        self.wifi_switch.grid(column=0, row=3)
        self.wifi_frame.grid(column=1, row=3)
