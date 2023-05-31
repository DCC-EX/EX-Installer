"""
This is the root window of the EX-Installer application.
"""

# Import Python modules
import customtkinter as ctk
import sys

# Import local modules
from . import images
from . import theme
from .arduino_cli import ArduinoCLI
from .welcome import Welcome
from .manage_arduino_cli import ManageArduinoCLI
from .select_device import SelectDevice
from .select_product import SelectProduct
from .ex_commandstation import EXCommandStation
from .compile_upload import CompileUpload

# Set theme and appearance, and deactive screen scaling
ctk.set_default_color_theme(theme.DCC_EX_THEME)
ctk.set_appearance_mode("light")
ctk.deactivate_automatic_dpi_awareness()


class EXInstaller(ctk.CTk):
    """
    EX-Installer root window
    """
    # Create Arduino CLI and GitHub instances for the entire application
    acli = ArduinoCLI()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hide window while GUI is built initially, show after 250ms
        self.withdraw()
        self.after(250, self.deiconify)

        # Set window geometry, title, and icon
        self.title("EX-Installer")

        if sys.platform.startswith("win"):
            self.iconbitmap(images.DCC_EX_ICON_ICO)

        self.geometry("800x600")
        self.minsize(width=800, height=600)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.views = {
            "welcome": Welcome,
            "manage_arduino_cli": ManageArduinoCLI,
            "select_device": SelectDevice,
            "select_product": SelectProduct,
            "ex_commandstation": EXCommandStation,
        }
        self.view = None

        self.switch_view("welcome")

    def switch_view(self, view_class):
        """
        Function to switch views
        """
        if view_class:
            if self.view:
                self.view.destroy()
            self.view = self.views[view_class](self)
            self.view.grid(column=0, row=0, sticky="nsew")

    def compile_upload(self, product):
        """
        Function to switch to the compile and upload view
        """
        if product:
            if self.view:
                self.view.destroy()
            self.view = CompileUpload(self)
            self.view.set_product(product)
            self.view.grid(column=0, row=0, sticky="nsew")
