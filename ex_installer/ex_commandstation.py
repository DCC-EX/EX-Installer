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

        self.set_title_logo(pd["ex_commandstation"]["product_logo"])
        self.set_title_text("Install EX-CommandStation")

        self.next_back.set_back_text("Select Product")
        self.next_back.set_back_command(lambda view="select_product": parent.switch_view(view))

        self.next_back.set_next_text("Compile and upload")
        self.next_back.set_next_command(lambda product="ex_commandstation": parent.compile_upload(product))

        self.ex_commandstation_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.ex_commandstation_frame.grid(column=0, row=0, sticky="nsew")
