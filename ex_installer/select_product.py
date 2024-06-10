"""
Module for the Select Product page view

© 2023, Peter Cole. All rights reserved.

This file is part of EX-Installer.

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

It is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CommandStation.  If not, see <https://www.gnu.org/licenses/>.
"""

# Import Python modules
import customtkinter as ctk
from PIL import Image
import logging

# Import local modules
from .common_widgets import WindowLayout
from . import images
from .product_details import product_details as pd


class SelectProduct(WindowLayout):
    """
    Class for the Select Product view
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start view")

        # Define product variable
        self.product = None

        # Set up title
        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Select the Product to install")

        # Set next/back buttons
        self.next_back.set_back_text("Select Device")
        self.next_back.set_back_command(lambda view="select_device": parent.switch_view(view))
        self.next_back.hide_next()
        self.next_back.hide_monitor_button()

        # Set up and configure the container frame
        self.select_product_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.select_product_frame.grid(column=0, row=0, sticky="nsew")

        self.select_product_frame.grid_columnconfigure((0, 1), weight=1)
        self.select_product_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # Create instruction label
        self.instruction_label = ctk.CTkLabel(self.select_product_frame,
                                              text="Click the logo to choose the product to install",
                                              font=self.instruction_font)

        # Create product logos
        self.ex_commandstation_logo = Image.open(images.EX_COMMANDSTATION_LOGO)
        self.ex_ioexpander_logo = Image.open(images.EX_IOEXPANDER_LOGO)
        self.ex_turntable_logo = Image.open(images.EX_TURNTABLE_LOGO)
        self.ex_dccinspector_logo = Image.open(images.EX_DCCINSPECTOR_LOGO)
        self.ex_fastclock_logo = Image.open(images.EX_FASTCLOCK_LOGO)

        # Create product images
        image_size = [200, 40]
        self.ex_commandstation_image = ctk.CTkImage(light_image=self.ex_commandstation_logo, size=(300, 60))
        self.ex_ioexpander_image = ctk.CTkImage(light_image=self.ex_ioexpander_logo, size=image_size)
        self.ex_turntable_image = ctk.CTkImage(light_image=self.ex_turntable_logo, size=image_size)
        self.ex_dccinspector_image = ctk.CTkImage(light_image=self.ex_dccinspector_logo, size=image_size)
        self.ex_fastclock_image = ctk.CTkImage(light_image=self.ex_fastclock_logo, size=image_size)

        # Create product buttons
        button_options = {"fg_color": "white",
                          "border_color": "#00A3B9",
                          "border_width": 2,
                          "compound": "top",
                          "text_color": "#00353D",
                          "height": 80}
        self.ex_commandstation_button = ctk.CTkButton(self.select_product_frame,
                                                      text=None, width=500,
                                                      image=self.ex_commandstation_image, **button_options,
                                                      command=lambda product="ex_commandstation":
                                                      self.check_product_device(product))
        self.ex_ioexpander_button = ctk.CTkButton(self.select_product_frame,
                                                  text=None,
                                                  image=self.ex_ioexpander_image, **button_options,
                                                  command=lambda product="ex_ioexpander":
                                                  self.check_product_device(product))
        self.ex_turntable_button = ctk.CTkButton(self.select_product_frame,
                                                 text=None,
                                                 image=self.ex_turntable_image, **button_options,
                                                 command=lambda product="ex_turntable":
                                                 self.check_product_device(product))
        self.ex_dccinspector_button = ctk.CTkButton(self.select_product_frame,
                                                    text="(coming soon)",
                                                    image=self.ex_dccinspector_image, **button_options,
                                                    state="disabled")
        self.ex_fastclock_button = ctk.CTkButton(self.select_product_frame,
                                                 text="(coming soon)",
                                                 image=self.ex_fastclock_image, **button_options,
                                                 state="disabled")

        # Layout product buttons
        grid_options = {"sticky": "ew", "padx": 10, "pady": 10}
        self.instruction_label.grid(column=0, row=0, columnspan=2, padx=5, pady=5)
        self.ex_commandstation_button.grid(column=0, row=1, columnspan=2, padx=10, pady=10)
        self.ex_ioexpander_button.grid(column=0, row=2, **grid_options)
        self.ex_turntable_button.grid(column=1, row=2, **grid_options)

        # Disable these for the moment as it's misleading that they're "coming soon"
        # self.ex_dccinspector_button.grid(column=0, row=3, **grid_options)
        # self.ex_fastclock_button.grid(column=1, row=3, **grid_options)

        # Hide log button to start
        self.next_back.hide_log_button()

    def check_product_device(self, product):
        """
        Method to validate the selected device is compatible with the selected product.
        """
        device_fqbn = self.acli.detected_devices[self.acli.selected_device]["matching_boards"][0]["fqbn"]
        device_name = self.acli.detected_devices[self.acli.selected_device]["matching_boards"][0]["name"]
        product_name = pd[product]["product_name"]
        if device_fqbn not in pd[product]["supported_devices"]:
            self.process_error(f"Device type {device_name} is not supported for use with {product_name}\n" +
                               "Return to the Select Device screen and select a supported device")
            self.log.error("Device type %s is not supported for %s", device_name, product_name)
        else:
            self.master.switch_view("select_version_config", product)
            self.log.debug("Selected %s", product_name)
