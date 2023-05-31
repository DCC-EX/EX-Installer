"""
Module to define widgets used across the application

Every view should include this module and base the layout on WindowLayout
"""

# Import Python modules
import customtkinter as ctk
from PIL import Image

# Import local modules
from . import images


class WindowLayout(ctk.CTkFrame):
    """
    Class to define the window layout

    All views must inherit from this
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Get parent Arduino CLI instance
        self.acli = parent.acli

        # Define top level frames
        self.title_frame = ctk.CTkFrame(self, width=790, height=80)
        self.main_frame = ctk.CTkFrame(self, width=790, height=400)
        self.status_frame = ctk.CTkFrame(self, width=790, height=100)

        # Configure column/row weights for nice resizing
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure((1, 2), weight=1)

        # Layout view
        self.title_frame.grid(column=0, row=0, padx=5, pady=2, sticky="nsew")
        self.main_frame.grid(column=0, row=1, padx=5, pady=2, sticky="nsew")
        self.status_frame.grid(column=0, row=2, padx=5, pady=2, sticky="nsew")

        # Setup frame weights
        self.title_frame.grid_columnconfigure(0, weight=1)
        self.title_frame.grid_columnconfigure(1, weight=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_frame.grid_rowconfigure(0, weight=1)

        # Define common fonts
        self.title_font = ctk.CTkFont(family="Helvetica", size=30, weight="normal")
        self.heading_font = ctk.CTkFont(family="Helvetica", size=24, weight="bold")
        self.button_font = ctk.CTkFont(family="Helvetica", size=14, weight="bold")

        # Setup title frame
        self.title_logo_label = ctk.CTkLabel(self.title_frame, text=None)
        self.title_logo_label.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.title_label = ctk.CTkLabel(self.title_frame, text=None, font=self.title_font)
        self.title_label.grid(column=1, row=0, padx=5, pady=5, sticky="w")

        # Setup next/back frame
        self.next_back = NextBack(self.main_frame, height=40,
                                  fg_color="#00353D", border_width=0)
        self.next_back.grid(column=0, row=1, sticky="sew")

    def set_title_logo(self, logo):
        """
        Function to update the title logo

        Call and pass a logo as defined in the images module
        """
        self.title_logo = Image.open(logo)
        self.title_image = ctk.CTkImage(light_image=self.title_logo, size=(200, 40))
        self.title_logo_label.configure(image=self.title_image)

    def set_title_text(self, text):
        """
        Function to update the title text
        """
        self.title_label.configure(text=text)


class NextBack(ctk.CTkFrame):
    """
    Class for defining and managing the next and back buttons
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Create the next/back button frame with buttons
        """
        super().__init__(parent, *args, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        button_font = ctk.CTkFont(family="Helvetica", size=14, weight="bold")
        button_options = {"width": 220, "height": 30, "font": button_font}

        self.back_arrow = Image.open(images.BACK_ARROW)
        self.back_arrow_image = ctk.CTkImage(light_image=self.back_arrow, size=(15, 15))
        self.back_button = ctk.CTkButton(self, image=self.back_arrow_image,
                                         text="Back", compound="left",
                                         anchor="w",
                                         **button_options)

        self.next_arrow = Image.open(images.NEXT_ARROW)
        self.next_arrow_image = ctk.CTkImage(light_image=self.next_arrow, size=(15, 15))
        self.next_button = ctk.CTkButton(self, image=self.next_arrow_image,
                                         text="Next", compound="right",
                                         anchor="e",
                                         **button_options)

        self.back_button.grid(column=0, row=0, padx=3, pady=3, sticky="w")
        self.next_button.grid(column=1, row=0, padx=3, pady=3, sticky="e")

    def set_back_text(self, text):
        """Update back button text"""
        self.back_button.configure(text=text)

    def disable_back(self):
        """Disable back button"""
        self.back_button.configure(state="disabled")

    def enable_back(self):
        """Enable back button"""
        self.back_button.configure(state="normal")

    def hide_back(self):
        """Hide back button"""
        self.back_button.grid_remove()

    def show_back(self):
        """Show back button"""
        self.back_button.grid()

    def set_back_command(self, command):
        self.back_button.configure(command=command)

    def set_next_text(self, text):
        """Update next button text"""
        self.next_button.configure(text=text)

    def disable_next(self):
        """Disable next button"""
        self.next_button.configure(state="disabled")

    def enable_next(self):
        """Enable next button"""
        self.next_button.configure(state="normal")

    def hide_next(self):
        """Hide next button"""
        self.next_button.grid_remove()

    def show_next(self):
        """Show next button"""
        self.next_button.grid()

    def set_next_command(self, command):
        self.next_button.configure(command=command)
