"""
Module for the Select Product page view
"""

# Import Python modules
import customtkinter as ctk

# Import local modules
from .common_widgets import WindowLayout
from . import images


class SelectProduct(WindowLayout):
    """
    Class for the Select Product view
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Select the Product to install")

        self.product_selection = ctk.StringVar(value=None)
        self.product_selection.set("ex_commandstation")

        self.next_back.set_back_text("Select Device")
        self.next_back.set_back_command(lambda view="select_device": parent.switch_view(view))

        self.next_back.set_next_text("Configure and install")
        self.next_back.set_next_command(lambda view=self.product_selection.get(): parent.switch_view(view))

        self.select_product_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.select_product_frame.grid(column=0, row=0, sticky="nsew")
