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
import webbrowser

# Import local modules
from .common_widgets import WindowLayout, CreateToolTip
from .product_details import product_details as pd
from .file_manager import FileManager as fm


class EXTurntable(WindowLayout):
    """
    Class for the EX-Turntable view
    """

    advanced_config_options = [
        "#define LED_FAST 100\n",
        "#define LED_SLOW 500\n",
        "// #define DEBUG\n",
        "// #define SANITY_STEPS 10000\n",
        "// #define HOME_SENSITIVITY 300\n",
        "// #define FULL_STEP_COUNT 4096\n",
        "// #define DEBOUNCE_DELAY 10\n"
    ]

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
        """
        grid_options = {"padx": 5, "pady": 5}
        toggle_instruction_options = {"width": 250, "font": self.instruction_font}
        self.config_frame.grid_columnconfigure(0, weight=1)
        self.config_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        toggle_options = {"text": None, "width": 30, "fg_color": "#00A3B9", "progress_color": "#00A3B9"}
        toggle_label_options = {"width": 100}
        subframe_options = {"border_width": 0, "fg_color": "#E5E5E5"}

        # Instructions
        instructions = ("EX-Turntable requires a litte more DIY knowledge when it comes to working with stepper " +
                        "drivers and motors, and the home and limit sensors. Please ensure you read the " +
                        "documentation prior to installing (Click this text to open it).")

        # Tooltip text
        i2c_tip = ("You need to specify an available, valid I\u00B2C address for EX-Turntable. Valid values are " +
                   "from 0x08 to 0x77. Click this tip to open the EX-Turntable documentation")
        stepper_tip = ("Selecting the correct stepper driver is imperative for the correct operation of your " +
                       "turntable. Click this tip to open the stepper information in the documentation.")
        mode_tip = ("EX-Turntable can operate in either turntable (continuous rotation) or traverser ( limited " +
                    "rotation) mode. Click this tip to open the traverser documentation for more information.")
        active_state_tip = ("Active low sensors set their output to 0V or ground when activated, whereas active high " +
                            "sensors set their output to 5V. When using relays, active low means the relays are " +
                            "activated when the input is set to 0V or ground, and deactivated when set to 5V. The " +
                            "inverse is true for active high relays.")
        sensor_test_tip = ("When running EX-Turntable in traverser mode, it is recommended to run in sensor testing " +
                           "mode initially to ensure the home and limit sensors are configured correctly. Failure " +
                           "to check your sensors may lead to mechanical damage should the traverser be driven " +
                           "beyond the physical design limitations. Click this tip to open the relevant documentation.")
        phase_tip = ("By default, EX-Turntable will use attached relays to invert the polarity or phase of the " +
                     "turntable bridge track at the angle specified. Click this tip to open the relevant " +
                     "documentation.")
        idle_tip = ("By default, the stepper is disabled when idle. This prevents the driver from over heating and " +
                    "consuming excess power. If your configuration requires the stepper to forcibly maintain " +
                    "position when idle, disable this option.")
        speed_tip = ("This defines the top speed of the stepper. The limit here is determined by the Arduion " +
                     "device. A sensible max speed for Nanos/Unos would be 4000.")
        accel_tip = ("This defines the rate at which the stepper speed increases to the top speed, and decreases " +
                     "until it stops.")

        # Subframes for grouping
        self.main_options_frame = ctk.CTkFrame(self.config_frame)   # I2C, operating mode
        self.stepper_frame = ctk.CTkFrame(self.config_frame)        # Stepper driver, disable idle, speed/accel
        self.phase_frame = ctk.CTkFrame(self.config_frame)          # Auto, angle, relay active
        self.sensor_frame = ctk.CTkFrame(self.config_frame)         # Testing, home/limit

        self.main_options_frame.grid_columnconfigure(0, weight=1)
        self.main_options_frame.grid_rowconfigure(0, weight=1)
        self.stepper_frame.grid_columnconfigure(0, weight=1)
        self.stepper_frame.grid_rowconfigure(0, weight=1)
        self.phase_frame.grid_columnconfigure(0, weight=1)
        self.phase_frame.grid_rowconfigure(0, weight=1)
        self.sensor_frame.grid_columnconfigure(0, weight=1)
        self.sensor_frame.grid_rowconfigure(0, weight=1)

        # Instruction widgets
        self.instruction_label = ctk.CTkLabel(self.config_frame, text=instructions, width=780, wraplength=760,
                                              font=self.instruction_font)
        self.instruction_label.bind("<Button-1>", lambda x:
                                    webbrowser.open_new("https://dcc-ex.com/ex-turntable/index.html"))

        i2c_label_text = ("To load EX-Turntable, you need to specify the I\u00B2C address.")
        self.i2c_label = ctk.CTkLabel(self.main_options_frame, text=i2c_label_text, font=self.instruction_font)
        CreateToolTip(self.i2c_label, i2c_tip, "https://dcc-ex.com/ex-turntable/configure.html#i2c-address")

        # Create I2C widgets
        self.i2c_address = ctk.StringVar(self, value=60)
        self.i2c_address_frame = ctk.CTkFrame(self.main_options_frame, border_width=0, fg_color="#E5E5E5")
        self.i2c_address_label = ctk.CTkLabel(self.i2c_address_frame, text="Set I\u00B2C address:",
                                              font=self.instruction_font)
        CreateToolTip(self.i2c_address_label, i2c_tip, "https://dcc-ex.com/ex-turntable/configure.html#i2c-address")
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

        # Create stepper selection widgets
        self.stepper_label = ctk.CTkLabel(self.config_frame, text="Select the stepper driver:",
                                          font=self.instruction_font)
        CreateToolTip(self.stepper_label, stepper_tip,
                      "https://dcc-ex.com/ex-turntable/purchasing.html#supported-stepper-drivers-and-motors")
        self.stepper_combo = ctk.CTkComboBox(self.config_frame, values=["Select stepper driver"],
                                             width=200, command=self.check_stepper)

        # Create mode widgets
        self.mode_frame = ctk.CTkFrame(self.config_frame, **subframe_options)
        self.mode_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.mode_frame.grid_rowconfigure(0, weight=1)
        self.mode_label = ctk.CTkLabel(self.mode_frame, text="Select the operating mode:",
                                       **toggle_instruction_options)
        CreateToolTip(self.mode_label, mode_tip,
                      "https://dcc-ex.com/ex-turntable/traverser.html")
        self.turntable_label = ctk.CTkLabel(self.mode_frame, text="Turntable", **toggle_label_options)
        self.mode_switch = ctk.CTkSwitch(self.mode_frame, onvalue="TRAVERSER", offvalue="TURNTABLE",
                                         command=self.set_mode, **toggle_options)
        self.traverser_label = ctk.CTkLabel(self.mode_frame, text="Traverser", **toggle_label_options)

        # Layout mode frame
        self.mode_label.grid(column=0, row=0, **grid_options)
        self.turntable_label.grid(column=1, row=0, sticky="e", padx=(5, 0), pady=5)
        self.mode_switch.grid(column=2, row=0, **grid_options)
        self.traverser_label.grid(column=3, row=0, sticky="w", padx=(0, 5), pady=5)

        # Create phase switch widgets
        self.phase_frame = ctk.CTkFrame(self.config_frame)
        self.auto_switch = ctk.CTkSwitch(self.phase_frame, text="Enable automatic phase switching",
                                         onvalue="AUTO", offvalue="MANUAL", font=self.instruction_font,
                                         command=self.set_phase_switching)
        self.auto_switch.select()
        self.phase_angle = ctk.StringVar(self, value="45")
        self.phase_angle_entry = ctk.CTkEntry(self.phase_frame, textvariable=self.phase_angle, width=40,
                                              font=self.instruction_font)

        # Layout phase frame
        self.auto_switch.grid(column=0, row=0, **grid_options)
        CreateToolTip(self.auto_switch, phase_tip,
                      "https://dcc-ex.com/ex-turntable/overview.html#important-phase-or-polarity-switching")
        self.phase_angle_entry.grid(column=1, row=0, **grid_options)

        # Create sensor widgets
        self.home_sensor_frame = ctk.CTkFrame(self.config_frame, **subframe_options)
        self.limit_sensor_frame = ctk.CTkFrame(self.config_frame, **subframe_options)
        self.home_sensor_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.home_sensor_frame.grid_rowconfigure(0, weight=1)
        self.limit_sensor_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.limit_sensor_frame.grid_rowconfigure(0, weight=1)
        self.home_label = ctk.CTkLabel(self.home_sensor_frame, text="Set the home sensor active type:",
                                       **toggle_instruction_options)
        CreateToolTip(self.home_label, active_state_tip)
        self.limit_label = ctk.CTkLabel(self.limit_sensor_frame, text="Set the limit sensor active type:",
                                        **toggle_instruction_options)
        CreateToolTip(self.limit_label, active_state_tip)
        self.home_low_label = ctk.CTkLabel(self.home_sensor_frame, text="Active Low", **toggle_label_options)
        self.home_switch = ctk.CTkSwitch(self.home_sensor_frame, onvalue="HIGH", offvalue="LOW",
                                         command=self.set_home, **toggle_options)
        self.home_high_label = ctk.CTkLabel(self.home_sensor_frame, text="Active High", **toggle_label_options)
        self.limit_low_label = ctk.CTkLabel(self.limit_sensor_frame, text="Active Low", **toggle_label_options)
        self.limit_switch = ctk.CTkSwitch(self.limit_sensor_frame, onvalue="HIGH", offvalue="LOW",
                                          command=self.set_limit, **toggle_options)
        self.limit_high_label = ctk.CTkLabel(self.limit_sensor_frame, text="Active High", **toggle_label_options)

        # Layout sensor frames
        self.home_label.grid(column=0, row=0, **grid_options)
        self.home_low_label.grid(column=1, row=0, sticky="e", padx=(5, 0), pady=5)
        self.home_switch.grid(column=2, row=0, **grid_options)
        self.home_high_label.grid(column=3, row=0, sticky="w", padx=(0, 5), pady=5)
        self.limit_label.grid(column=0, row=0, **grid_options)
        self.limit_low_label.grid(column=1, row=0, sticky="e", padx=(5, 0), pady=5)
        self.limit_switch.grid(column=2, row=0, **grid_options)
        self.limit_high_label.grid(column=3, row=0, sticky="w", padx=(0, 5), pady=5)

        # Create test and stepper disable idle widgets
        self.sensor_test_switch = ctk.CTkSwitch(self.config_frame, text="Enable sensor testing mode",
                                                onvalue="on", offvalue="off", font=self.instruction_font)
        CreateToolTip(self.sensor_test_switch, sensor_test_tip,
                      "https://dcc-ex.com/ex-turntable/traverser.html#considerations-turntable-vs-traverser")
        self.disable_idle_switch = ctk.CTkSwitch(self.config_frame, text="Disable stepper when idle",
                                                 onvalue="on", offvalue="off", font=self.instruction_font)
        self.disable_idle_switch.select()
        CreateToolTip(self.disable_idle_switch, idle_tip)

        # Create stepper tuning widgets
        self.speed_label = ctk.CTkLabel(self.config_frame, text="Set the stepper top speed",
                                        font=self.instruction_font)
        self.speed = ctk.StringVar(self, value="200")
        self.speed_entry = ctk.CTkEntry(self.config_frame, textvariable=self.speed, font=self.instruction_font)
        self.accel_label = ctk.CTkLabel(self.config_frame, text="Set acceleration/deceleration rate",
                                        font=self.instruction_font)
        self.accel = ctk.StringVar(self, value="25")
        self.accel_entry = ctk.CTkEntry(self.config_frame, textvariable=self.accel, font=self.instruction_font)

        # Create relay widgets
        self.relay_frame = ctk.CTkFrame(self.config_frame, **subframe_options)
        self.relay_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.relay_frame.grid_rowconfigure(0, weight=1)
        self.relay_label = ctk.CTkLabel(self.relay_frame, text="Set the relay active type:",
                                        **toggle_instruction_options)
        CreateToolTip(self.relay_label, active_state_tip)
        self.relay_low_label = ctk.CTkLabel(self.relay_frame, text="Active Low", **toggle_label_options)
        self.relay_switch = ctk.CTkSwitch(self.relay_frame, onvalue="HIGH", offvalue="LOW",
                                          command=self.set_relay, **toggle_options)
        self.relay_switch.select()
        self.relay_high_label = ctk.CTkLabel(self.relay_frame, text="Active High", **toggle_label_options)

        # Layout relay frame
        self.relay_label.grid(column=0, row=0, **grid_options)
        self.relay_low_label.grid(column=1, row=0, sticky="e", padx=(5, 0), pady=5)
        self.relay_switch.grid(column=2, row=0, **grid_options)
        self.relay_high_label.grid(column=3, row=0, sticky="w", padx=(0, 5), pady=5)

        # Advanced config widget
        self.advanced_config_enabled = ctk.CTkSwitch(self.config_frame, text="Advanced Config",
                                                     onvalue="on", offvalue="off",
                                                     font=self.instruction_font,
                                                     command=self.set_advanced_config)

        # Layout config frame
        self.instruction_label.grid(column=0, row=0, **grid_options)
        self.main_options_frame.grid(column=0, row=1, **grid_options)
        # self.stepper_frame.grid(column=0, row=2, **grid_options)
        # self.phase_frame.grid(column=0, row=3, **grid_options)
        # self.sensor_frame.grid(column=0, row=4, **grid_options)
        self.advanced_config_enabled.grid(column=0, row=5, sticky="e", **grid_options)

        # self.i2c_label.grid(column=0, row=0, **grid_options)
        # self.i2c_address_frame.grid(column=1, row=0, sticky="w", **grid_options)
        # self.stepper_label.grid(column=0, row=1, **grid_options)
        # self.stepper_combo.grid(column=1, row=1, **grid_options)
        # self.phase_frame.grid(column=0, row=2, columnspan=2, **grid_options)
        # self.sensor_test_switch.grid(column=0, row=3, **grid_options)
        # self.disable_idle_switch.grid(column=1, row=3, **grid_options)
        # self.mode_frame.grid(column=0, row=4, columnspan=2, **grid_options)
        # self.home_sensor_frame.grid(column=0, row=5, columnspan=2, **grid_options)
        # self.limit_sensor_frame.grid(column=0, row=6, columnspan=2, **grid_options)
        # self.relay_frame.grid(column=0, row=7, columnspan=2, **grid_options)
        # self.speed_label.grid(column=0, row=8, **grid_options)
        # self.accel_label.grid(column=1, row=8, **grid_options)
        # self.speed_entry.grid(column=0, row=9, **grid_options)
        # self.accel_entry.grid(column=1, row=9, **grid_options)
        # self.advanced_config_enabled.grid(column=0, row=10, **grid_options)

        # Set toggles
        self.get_steppers()
        self.check_stepper(self.stepper_combo.get())
        self.set_home()
        self.set_limit()
        self.set_mode()
        self.set_relay()

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
        """
        Highlight the chosen option for the mode toggle switch
        """
        if self.mode_switch.get() == "TURNTABLE":
            self.turntable_label.configure(font=self.bold_instruction_font)
            self.traverser_label.configure(font=self.small_italic_instruction_font)
            self.limit_switch.configure(state="disabled")
            self.limit_switch.configure(fg_color="#939BA2", progress_color="#939BA2")
            self.limit_high_label.configure(font=self.small_italic_instruction_font)
            self.limit_low_label.configure(font=self.small_italic_instruction_font)
        else:
            self.turntable_label.configure(font=self.small_italic_instruction_font)
            self.traverser_label.configure(font=self.bold_instruction_font)
            self.limit_switch.configure(state="normal")
            self.limit_switch.configure(fg_color="#00A3B9", progress_color="#00A3B9")
            self.set_limit()

    def set_home(self):
        """
        Highlight the chosen option for the home sensor toggle switch
        """
        if self.home_switch.get() == "LOW":
            self.home_low_label.configure(font=self.bold_instruction_font)
            self.home_high_label.configure(font=self.small_italic_instruction_font)
        else:
            self.home_low_label.configure(font=self.small_italic_instruction_font)
            self.home_high_label.configure(font=self.bold_instruction_font)

    def set_limit(self):
        """
        Highlight the chosen option for the limit sensor toggle switch
        """
        if self.limit_switch.get() == "LOW":
            self.limit_low_label.configure(font=self.bold_instruction_font)
            self.limit_high_label.configure(font=self.small_italic_instruction_font)
        else:
            self.limit_low_label.configure(font=self.small_italic_instruction_font)
            self.limit_high_label.configure(font=self.bold_instruction_font)

    def set_relay(self):
        """
        Highlight the chosen option for the relay toggle switch
        """
        if self.relay_switch.get() == "LOW":
            self.relay_low_label.configure(font=self.bold_instruction_font)
            self.relay_high_label.configure(font=self.small_italic_instruction_font)
        else:
            self.relay_low_label.configure(font=self.small_italic_instruction_font)
            self.relay_high_label.configure(font=self.bold_instruction_font)

    def set_phase_switching(self):
        """
        Function to hide/display phase switching angle
        """
        if self.auto_switch.get() == "AUTO":
            self.phase_angle_entry.grid()
        else:
            self.phase_angle_entry.grid_remove()

    def get_steppers(self):
        """
        Function to read the defined stepper definitions from standard_steppers.h
        """
        self.stepper_list = []
        match = r'^#define\s(.+?)\sAccelStepper.*$'
        definition_file = fm.get_filepath(self.ex_turntable_dir, "standard_steppers.h")
        def_list = fm.get_list_from_file(definition_file, match)
        if def_list:
            self.stepper_list += def_list
            self.log.debug("Found stepper list %s", def_list)
        else:
            self.log.error("Could not get list of steppers")
        self.stepper_combo.configure(values=self.stepper_list)

    def check_stepper(self, value):
        """
        Function ensure a motor driver has been selected
        """
        if value == "Select stepper driver":
            self.next_back.disable_next()
        else:
            self.next_back.enable_next()

    def set_advanced_config(self):
        """
        Sets next screen to be config editing rather than compile/upload
        """
        if self.advanced_config_enabled.get() == "on":
            self.next_back.set_next_text("Advanced config")
        else:
            self.next_back.set_next_text("Compile and load")

    def generate_config(self):
        """
        Validates all configuration parameters and if valid generates myConfig.h

        Any invalid parameters will prevent continuing and flag as errors
        """
        param_errors = []
        config_list = []
        if int(self.i2c_address.get()) < 8 or int(self.i2c_address.get()) > 77:
            param_errors.append("I\u00B2C address must be between 0x8 and 0x77")
        else:
            line = f"#define I2C_ADDRESS 0x{self.i2c_address.get()}\n"
            config_list.append(line)
        config_list.append(f"#define TURNTABLE_EX_MODE {self.mode_switch.get()}\n")
        if self.sensor_test_switch.get() == "on":
            config_list.append("#define SENSOR_TESTING\n")
        config_list.append(f"#define HOME_SENSOR_ACTIVE_STATE {self.home_switch.get()}\n")
        config_list.append(f"#define LIMIT_SENSOR_ACTIVE_STATE {self.limit_switch.get()}\n")
        config_list.append(f"#define RELAY_ACTIVE_STATE {self.relay_switch.get()}\n")
        config_list.append(f"#define PHASE_SWITCHING {self.auto_switch.get()}\n")
        if self.auto_switch.get() == "AUTO":
            try:
                int(self.phase_angle.get())
            except Exception:
                param_errors.append("Phase switch angle must be between 0 and 180")
            else:
                if (int(self.phase_angle.get()) < 0 or int(self.phase_angle.get()) > 180):
                    param_errors.append("Phase switch angle must be between 0 and 180")
                else:
                    line = f"#define PHASE_SWITCH_ANGLE {self.phase_angle.get()}\n"
                    config_list.append(line)
        if self.stepper_combo.get() == "Select stepper driver":
            param_errors.append("You must select a stepper driver")
        else:
            config_list.append(f"#define STEPPER_DRIVER {self.stepper_combo.get()}\n")
        if self.disable_idle_switch.get() == "on":
            config_list.append("#define DISABLE_OUTPUTS_IDLE\n")
        try:
            int(self.speed.get())
        except Exception:
            param_errors.append("You must provide a numeric speed value")
        else:
            if (int(self.speed.get()) < 10 or int(self.speed.get()) > 20000):
                param_errors.append("Speed must be between 10 and 20000")
            else:
                config_list.append(f"#define STEPPER_MAX_SPEED {self.speed.get()}\n")
        try:
            int(self.accel.get())
        except Exception:
            param_errors.append("You must provide a numeric acceleration value")
        else:
            if (int(self.accel.get()) < 1 or int(self.accel.get()) > 1000):
                param_errors.append("Acceleration must be between 1 and 1000")
            else:
                config_list.append(f"#define STEPPER_ACCELERATION {self.accel.get()}\n")
        if len(param_errors) > 0:
            message = ", ".join(param_errors)
            self.process_error(message)
        else:
            self.process_stop()
            file_contents = [("// config.h - Generated by EX-Installer " +
                              f"v{self.app_version} for {self.product_name} " +
                              f"{self.product_version_name}\n\n")]
            file_contents += config_list
            file_contents += self.advanced_config_options
            config_file_path = fm.get_filepath(self.ex_turntable_dir, "config.h")
            write_config = fm.write_config_file(config_file_path, file_contents)
            if write_config != config_file_path:
                self.process_error(f"Could not write config.h: {write_config}")
                self.log.error("Could not write config file: %s", write_config)
            else:
                if self.advanced_config_enabled.get() == "on":
                    self.master.switch_view("advanced_config", self.product)
                else:
                    self.master.switch_view("compile_upload", self.product)
