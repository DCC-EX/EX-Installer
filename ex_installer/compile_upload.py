"""
Module for the Compile and Upload page view
"""

# Import Python modules
import customtkinter as ctk

# Import local modules
from .common_widgets import WindowLayout
from .product_details import product_details as pd


class CompileUpload(WindowLayout):
    """
    Class for the Compile and Upload view
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.product = None

        self.next_back.set_back_text("Select Product")
        self.next_back.set_back_command(lambda view="select_product": parent.switch_view(view))

        self.next_back.hide_next()

        self.compile_upload_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.compile_upload_frame.grid(column=0, row=0, sticky="nsew")

    def set_product(self, product):
        self.product = product
        self.set_title_text(f"Upload {pd[self.product]['product_name']}")
        self.set_title_logo(pd[product]["product_logo"])
