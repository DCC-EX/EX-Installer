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

        self.next_back.hide_next()

        self.compile_upload_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.compile_upload_frame.grid(column=0, row=0, sticky="nsew")

    def set_product(self, product):
        self.product = product
        self.set_title_text(f"Upload {pd[self.product]['product_name']}")
        self.set_title_logo(pd[product]["product_logo"])
        self.next_back.set_back_text(f"Configure {pd[self.product]['product_name']}")
        self.next_back.set_back_command(lambda view=product: self.master.switch_view(view))
