"""
Module for the Select Product page view
"""

# Import Python modules
import customtkinter as ctk
from PIL import Image

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

        self.next_back.set_back_text("Select Device")
        self.next_back.set_back_command(lambda view="select_device": parent.switch_view(view))

        self.next_back.hide_next()

        self.select_product_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.select_product_frame.grid(column=0, row=0, sticky="nsew")

        self.select_product_frame.grid_columnconfigure((0, 1), weight=1)
        self.select_product_frame.grid_rowconfigure(0, weight=1)

        self.ex_commandstation_logo = Image.open(images.EX_COMMANDSTATION_LOGO)
        self.ex_ioexpander_logo = Image.open(images.EX_IOEXPANDER_LOGO)
        self.ex_turntable_logo = Image.open(images.EX_TURNTABLE_LOGO)
        self.ex_dccinspector_logo = Image.open(images.EX_DCCINSPECTOR_LOGO)
        self.ex_fastclock_logo = Image.open(images.EX_FASTCLOCK_LOGO)

        image_size = [200, 40]
        self.ex_commandstation_image = ctk.CTkImage(light_image=self.ex_commandstation_logo, size=(400, 80))
        self.ex_ioexpander_image = ctk.CTkImage(light_image=self.ex_ioexpander_logo, size=image_size)
        self.ex_turntable_image = ctk.CTkImage(light_image=self.ex_turntable_logo, size=image_size)
        self.ex_dccinspector_image = ctk.CTkImage(light_image=self.ex_dccinspector_logo, size=image_size)
        self.ex_fastclock_image = ctk.CTkImage(light_image=self.ex_fastclock_logo, size=image_size)

        button_options = {"fg_color": "white", "border_color": "#00A3B9", "border_width": 2, "compound": "top"}
        self.ex_commandstation_button = ctk.CTkButton(self.select_product_frame,
                                                      text="Install EX-CommandStation",
                                                      image=self.ex_commandstation_image, **button_options,
                                                      command=lambda product="ex_commandstation":
                                                      parent.switch_view(product))
        self.ex_ioexpander_button = ctk.CTkButton(self.select_product_frame,
                                                  text="Install EX-IOExpander (coming soon)",
                                                  image=self.ex_ioexpander_image, **button_options,
                                                  state="disabled")
        self.ex_turntable_button = ctk.CTkButton(self.select_product_frame,
                                                 text="Install EX-Turntable (coming soon)",
                                                 image=self.ex_turntable_image, **button_options,
                                                 state="disabled")
        self.ex_dccinspector_button = ctk.CTkButton(self.select_product_frame,
                                                    text="Install EX-DCCInspector (coming soon)",
                                                    image=self.ex_dccinspector_image, **button_options,
                                                    state="disabled")
        self.ex_fastclock_button = ctk.CTkButton(self.select_product_frame,
                                                 text="Install EX-FastClock (coming soon)",
                                                 image=self.ex_fastclock_image, **button_options,
                                                 state="disabled")

        grid_options = {"sticky": "ew", "padx": 10, "pady": 10}
        self.ex_commandstation_button.grid(column=0, row=0, columnspan=2, **grid_options)
        self.ex_ioexpander_button.grid(column=0, row=1, **grid_options)
        self.ex_turntable_button.grid(column=1, row=1, **grid_options)
        self.ex_dccinspector_button.grid(column=0, row=2, **grid_options)
        self.ex_fastclock_button.grid(column=1, row=2, **grid_options)
