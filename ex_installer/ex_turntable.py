"""
Module for the EX-Turntable page view

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
import logging

# Import local modules
from .common_widgets import WindowLayout
from .product_details import product_details as pd
from .file_manager import FileManager as fm


class EXTurntable(WindowLayout):
    """
    Class for the EX-Turntable view
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Initialise view
        """
        super().__init__(parent, *args, **kwargs)

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start view")

        # Get the local directory to work in
        self.product = "ex_turntable"
        self.product_name = pd[self.product]["product_name"]
        local_repo_dir = pd[self.product]["repo_name"].split("/")[1]
        self.ex_turntable_dir = fm.get_install_dir(local_repo_dir)

        # Set up title
        self.set_title_logo(pd[self.product]["product_logo"])
        self.set_title_text("Install EX-Turntable")

        # Set up next/back buttons
        self.next_back.set_back_text("Select Version")
        self.next_back.set_back_command(lambda view="select_version_config",
                                        product="ex_turntable": parent.switch_view(view, product))
        self.next_back.set_next_text("Compile and load")
        self.next_back.set_next_command(self.generate_config)
        self.next_back.hide_monitor_button()
        self.next_back.hide_log_button()

        # Set up and grid container frames
        self.config_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.config_frame.grid(column=0, row=0, sticky="nsew")

        # Setup the screen
        self.setup_config_frame()

    def set_product_version(self, version, major=None, minor=None, patch=None):
        """
        Function to be called by the switch_frame function to set the chosen version

        This allows configuration options to be set based on the chosen version

        Eg.
        if self.product_major_version >=4 and self.product_minor_version >= 2:
            function_enables_track_manager()
        else:
            function_disables_track_manager()
        """
        self.product_version_name = version
        if major is not None:
            self.product_major_version = major
            if minor is not None:
                self.product_minor_version = minor
                if patch is not None:
                    self.product_patch_version = patch

    def setup_config_frame(self):
        """
        Setup the container frame for configuration options

        Default config parameters from config.example.h:
        - #define I2C_ADDRESS 0x60
        - #define TURNTABLE_EX_MODE TURNTABLE
        - // #define TURNTABLE_EX_MODE TRAVERSER
        - // #define SENSOR_TESTING
        - #define HOME_SENSOR_ACTIVE_STATE LOW
        - #define LIMIT_SENSOR_ACTIVE_STATE LOW
        - #define RELAY_ACTIVE_STATE HIGH
        - #define PHASE_SWITCHING AUTO
        - #define PHASE_SWITCH_ANGLE 45
        - #define STEPPER_DRIVER ULN2003_HALF_CW (READ FROM standard_steppers.h)
        - #define DISABLE_OUTPUTS_IDLE
        - #define STEPPER_MAX_SPEED 200
        - #define STEPPER_ACCELERATION 25
        - // #define DEBUG
        - // #define SANITY_STEPS 10000
        - // #define HOME_SENSITIVITY 300
        - // #define FULL_STEP_COUNT 4096
        - // #define DEBOUNCE_DELAY 10
        """
        grid_options = {"padx": 5, "pady": 5}
        config_label_options = {"width": 500, "wraplength": 480, "font": self.instruction_font}
        self.config_frame.grid_columnconfigure((0, 1), weight=1)
        self.config_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # Instruction widgets
        instruction_text = ("To load EX-Turntable, you need to specify the " +
                            "I\u00B2C address.")
        self.instruction_label = ctk.CTkLabel(self.config_frame, text=instruction_text,
                                              **config_label_options)

        # Create I2C widgets
        self.i2c_address = ctk.StringVar(self, value=65)
        self.i2c_address_frame = ctk.CTkFrame(self.config_frame, border_width=0, fg_color="#E5E5E5")
        self.i2c_address_label = ctk.CTkLabel(self.i2c_address_frame, text="Set I\u00B2C address:")
        self.i2c_address_minus = ctk.CTkButton(self.i2c_address_frame, text="-", width=30,
                                               command=self.decrement_address)
        self.i2c_entry_frame = ctk.CTkFrame(self.i2c_address_frame, border_width=2, border_color="#00A3B9")
        self.i2c_0x_label = ctk.CTkLabel(self.i2c_entry_frame, text="0x", font=self.instruction_font,
                                         width=20, padx=0, pady=0, fg_color="#E5E5E5")
        self.i2c_address_entry = ctk.CTkEntry(self.i2c_entry_frame, textvariable=self.i2c_address,
                                              width=30, fg_color="white", border_width=0, justify="left",
                                              font=self.instruction_font)
        self.i2c_address_plus = ctk.CTkButton(self.i2c_address_frame, text="+", width=30,
                                              command=self.increment_address)

        # Validate I2C address if entered manually
        self.i2c_address_entry.bind("<FocusOut>", self.validate_i2c_address)

        # Layout I2C address frame
        self.i2c_address_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.i2c_address_frame.grid_rowconfigure(0, weight=1)
        self.i2c_entry_frame.grid_columnconfigure((0, 1), weight=1)
        self.i2c_entry_frame.grid_rowconfigure(0, weight=1)
        self.i2c_address_label.grid(column=0, row=0, **grid_options)
        self.i2c_address_minus.grid(column=1, row=0, padx=(5, 0))
        self.i2c_0x_label.grid(column=0, row=0, sticky="e")
        self.i2c_address_entry.grid(column=1, row=0, padx=0)
        self.i2c_entry_frame.grid(column=2, row=0, padx=0)
        self.i2c_address_plus.grid(column=3, row=0, sticky="w", padx=(0, 5))

        # Create mode widgets
        self.mode_frame = ctk.CTkFrame(self.config_frame)
        self.mode_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.mode_frame.grid_rowconfigure(0, weight=1)
        self.turntable_label = ctk.CTkLabel(self.mode_frame, text="Turntable", font=self.bold_instruction_font,
                                            width=100)
        self.mode_switch = ctk.CTkSwitch(self.mode_frame, text=None, onvalue="traverser", offvalue="turntable",
                                         command=self.set_mode)
        self.traverser_label = ctk.CTkLabel(self.mode_frame, text="Traverser", font=self.instruction_font,
                                            width=100)

        # Layout mode frame
        self.turntable_label.grid(column=0, row=0, sticky="e", **grid_options)
        self.mode_switch.grid(column=1, row=0, **grid_options)
        self.traverser_label.grid(column=2, row=0, sticky="w", **grid_options)

        # Layout config frame
        self.instruction_label.grid(column=0, row=0, **grid_options)
        self.i2c_address_frame.grid(column=1, row=0, sticky="w", **grid_options)
        self.mode_frame.grid(column=0, row=2, **grid_options)

    def decrement_address(self):
        """
        Function to decrement the I2C address
        """
        value = int(self.i2c_address.get())
        if value > 8:
            value -= 1
            self.i2c_address.set(value)
        self.validate_i2c_address()

    def increment_address(self):
        """
        Function to increment the I2C address
        """
        value = int(self.i2c_address.get())
        if value < 77:
            value += 1
            self.i2c_address.set(value)
        self.validate_i2c_address()

    def validate_i2c_address(self, event=None):
        """
        Function to validate the I2C address
        """
        if int(self.i2c_address.get()) < 8:
            self.process_error("I\u00B2C address must be between 0x8 and 0x77")
            self.i2c_address.set(8)
            self.i2c_address_entry.configure(text_color="red")
            self.next_back.disable_next()
        elif int(self.i2c_address.get()) > 77:
            self.process_error("I\u00B2C address must be between 0x8 and 0x77")
            self.i2c_address.set(77)
            self.i2c_address_entry.configure(text_color="red")
            self.next_back.disable_next()
        else:
            self.process_stop()
            self.i2c_address_entry.configure(text_color="#00353D")
            self.next_back.enable_next()

    def set_mode(self):
        if self.mode_switch.get() == "turntable":
            self.turntable_label.configure(font=self.bold_instruction_font)
            self.traverser_label.configure(font=self.instruction_font)
        else:
            self.turntable_label.configure(font=self.instruction_font)
            self.traverser_label.configure(font=self.bold_instruction_font)

    def generate_config(self):
        """
        Validates all configuration parameters and if valid generates myConfig.h

        Any invalid parameters will prevent continuing and flag as errors
        """
        param_errors = []
        config_list = []
        # if int(self.i2c_address.get()) < 8 or int(self.i2c_address.get()) > 77:
        #     param_errors.append("I\u00B2C address must be between 0x8 and 0x77")
        # else:
        #     line = f"#define I2C_ADDRESS 0x{self.i2c_address.get()}\n"
        #     config_list.append(line)
        # if self.enable_diag_switch.get() == "on":
        #     config_list.append("#define DIAG\n")
        # try:
        #     int(self.diag_delay.get())
        # except Exception:
        #     param_errors.append("Diagnostic display interval must be in whole seconds")
        # else:
        #     line = f"#define DIAG_CONFIG_DELAY {self.diag_delay.get()}\n"
        #     config_list.append(line)
        # if self.analogue_switch.get() == "on":
        #     config_list.append("#define TEST_MODE ANALOGUE_TEST\n")
        # elif self.input_switch.get() == "on":
        #     config_list.append("#define TEST_MODE INPUT_TEST\n")
        # elif self.output_switch.get() == "on":
        #     config_list.append("#define TEST_MODE OUTPUT_TEST\n")
        # elif self.pullup_switch.get() == "on":
        #     config_list.append("#define TEST_MODE PULLUP_TEST\n")
        # if self.disable_pullups_switch.get() == "on":
        #     config_list.append("#define DISABLE_I2C_PULLUPS\n")
        # if len(param_errors) > 0:
        #     message = ", ".join(param_errors)
        #     self.process_error(message)
        # else:
        #     self.process_stop()
        #     file_contents = [("// myConfig.h - Generated by EX-Installer " +
        #                       f"v{self.app_version} for {self.product_name} " +
        #                       f"{self.product_version_name}\n\n")]
        #     file_contents += config_list
        #     config_file_path = fm.get_filepath(self.ex_turntable_dir, "myConfig.h")
        #     write_config = fm.write_config_file(config_file_path, file_contents)
        #     if write_config != config_file_path:
        #         self.process_error(f"Could not write config.h: {write_config}")
        #         self.log.error("Could not write config file: %s", write_config)
        #     else:
        #         self.master.switch_view("compile_upload", self.product)