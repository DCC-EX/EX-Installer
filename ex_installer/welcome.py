"""
Module for the Welcome page view
"""

# Import Python modules
import customtkinter as ctk
from PIL import Image

# Import local modules
from .parent_view import ParentView
from . import images


class Welcome(ParentView):
    """
    Class for the Welcome view
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 2), weight=0)
        self.grid_rowconfigure((1, 3), weight=1)

        self.ex_installer_logo = Image.open(images.EX_INSTALLER_LOGO)
        self.ex_installer_image = ctk.CTkImage(light_image=self.ex_installer_logo,
                                               size=(300, 60))
        self.ex_installer_title = ctk.CTkLabel(self.title_frame, image=self.ex_installer_image, text=None)

        self.ex_installer_title.grid(column=0, row=0, sticky="w")
