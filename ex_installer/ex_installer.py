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
from .github_api import GitHubAPI
from .welcome import Welcome

# Set theme and appearance, and deactive screen scaling
ctk.set_default_color_theme(theme.DCC_EX_THEME)
ctk.set_appearance_mode("system")
ctk.deactivate_automatic_dpi_awareness()


class EXInstaller(ctk.CTk):
    """
    EX-Installer root window
    """
    # Create Arduino CLI and GitHub instances for the entire application
    acli = ArduinoCLI()
    gapi = GitHubAPI()

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

        self.welcome = Welcome(self)
        self.welcome.pack()
