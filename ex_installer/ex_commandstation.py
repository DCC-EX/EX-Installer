"""
Module for the EX-CommandStation page view
"""

# Import Python modules
import customtkinter as ctk

# Import local modules
from .common_widgets import WindowLayout
from .product_details import product_details as pd


class EXCommandStation(WindowLayout):
    """
    Class for the EX-CommandStation view
    """

    # Dummy variables for layout design
    dummy_version_list = [
        "v4.2.53-Devel",
        "v4.2.45-Devel",
        "v4.2.25-Devel",
        "v4.1.6-Prod",
        "v4.1.5-Prod",
        "v4.0.0-Prod"
    ]

    latest_prod = "v4.1.6-Prod"

    latest_devel = "v4.2.53-Devel"

    motorshield_list = {
        "STANDARD": "#define STANDARD\n",
        "EX8874": "#define EX8874\n",
        "POLOLU": "#define POLOLU\n"
    }

    # Instruction text
    version_text = ("For most users we recommended staying with the latest Production release, however you can " +
                    "install other versions if you know what you're doing, or if a version has been suggested by " +
                    "the DCC-EX team.")

    hardware_text = ("Select the appropriate options on this page to suit the hardware devices you are using with " +
                     "your EX-CommandStation device.\n\n")

    # Regular expressions to find user config files
    config_files = [
        r"(^config\.h$)",
        r"(^myHal\.cpp$)",
        r"^my.*\.[^?]*example\.h$|(^my.*\.h$)"
    ]

    # List of supported displays and config lines for config.h
    supported_displays = {
        "LCD - 16 columns x 2 rows": "#define LCD_DRIVER 0x27,16,2",
        "LCD 16 columns x 4 rows": "#define LCD_DRIVER  0x27,16,4",
        "OLED 128 x 32": "#define OLED_DRIVER 128,32",
        "OLED 128 x 64": "#define OLED_DRIVER 128,64"
    }

    # List of default config options to include in config.h
    default_config_options = [
        '#define IP_PORT 2560\n',
        '#define WIFI_HOSTNAME "dccex"\n',
        '#define WIFI_CHANNEL 1\n'
        '#define SCROLLMODE 1\n'
    ]

    def __init__(self, parent, *args, **kwargs):
        """
        Initialise view
        """
        super().__init__(parent, *args, **kwargs)

        # Set up title
        self.set_title_logo(pd["ex_commandstation"]["product_logo"])
        self.set_title_text("Install EX-CommandStation")

        # Set up next/back buttons
        self.next_back.set_back_text("Select Product")
        self.next_back.set_back_command(lambda view="select_product": parent.switch_view(view))
        self.next_back.set_next_text("Compile and upload")
        self.next_back.set_next_command(lambda product="ex_commandstation": parent.compile_upload(product))

        # Set up, configure, and grid container frame
        self.ex_commandstation_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.ex_commandstation_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.ex_commandstation_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.ex_commandstation_frame.grid(column=0, row=0, sticky="nsew")

        grid_options = {"padx": 5, "pady": 5}

        # Set up version instructions
        self.version_label = ctk.CTkLabel(self.ex_commandstation_frame, text=self.version_text,
                                          wraplength=780, font=self.instruction_font)

        # Set up select version frame and radio buttons
        self.version_frame = ctk.CTkFrame(self.ex_commandstation_frame,
                                          border_width=2,
                                          fg_color="#E5E5E5")
        self.version_frame.grid_columnconfigure((0, 1), weight=1)
        self.version_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.select_version = ctk.IntVar(value=0)
        self.latest_prod_radio = ctk.CTkRadioButton(self.version_frame, variable=self.select_version,
                                                    text=f"Latest Production ({self.latest_prod}) - Recommended!",
                                                    font=ctk.CTkFont(weight="bold"), value=0)
        self.latest_devel_radio = ctk.CTkRadioButton(self.version_frame, variable=self.select_version,
                                                     text=f"Latest Development ({self.latest_devel})", value=1)
        self.select_version_radio = ctk.CTkRadioButton(self.version_frame, variable=self.select_version,
                                                       text="Select a specific version", value=2)
        self.select_version_combo = ctk.CTkComboBox(self.version_frame, values=self.dummy_version_list, width=150)

        # Layout version frame
        self.version_frame.grid_columnconfigure((0, 1), weight=1)
        self.version_frame.grid_rowconfigure((0, 1, 2), weight=1)
        self.latest_prod_radio.grid(column=0, row=0, columnspan=2, sticky="w", **grid_options)
        self.latest_devel_radio.grid(column=0, row=1, columnspan=2, sticky="w", **grid_options)
        self.select_version_radio.grid(column=0, row=2, sticky="w", **grid_options)
        self.select_version_combo.grid(column=1, row=2, sticky="e", **grid_options)

        # Set up hardware instruction label
        self.hardware_label = ctk.CTkLabel(self.ex_commandstation_frame, text=self.hardware_text,
                                           wraplength=780, font=self.instruction_font)

        # Set up motor driver widgets
        self.motor_driver_label = ctk.CTkLabel(self.ex_commandstation_frame, text="Select your motor shield/driver")
        self.motor_driver_combo = ctk.CTkComboBox(self.ex_commandstation_frame, values=list(self.motorshield_list),
                                                  width=300)

        # Set up display widgets
        self.display_switch = ctk.CTkSwitch(self.ex_commandstation_frame, text="I have a display",
                                            onvalue="on", offvalue="off")
        self.display_combo = ctk.CTkComboBox(self.ex_commandstation_frame, values=list(self.supported_displays),
                                             width=300)

        # Set up WiFi widgets
        self.wifi_type = ctk.IntVar(self, value=-1)
        self.wifi_ssid = ctk.StringVar(self, value=None)
        self.wifi_pwd = ctk.StringVar(self, value=None)
        self.wifi_frame = ctk.CTkFrame(self.ex_commandstation_frame, border_width=0)
        self.wifi_switch = ctk.CTkSwitch(self.wifi_frame, text="I have WiFi",
                                         onvalue="on", offvalue="off")
        self.wifi_options_frame = ctk.CTkFrame(self.wifi_frame,
                                               border_width=2,
                                               fg_color="#E5E5E5")
        self.wifi_ap_radio = ctk.CTkRadioButton(self.wifi_options_frame,
                                                text="Use my EX-CommandStation as an access point",
                                                variable=self.wifi_type,
                                                value=0)
        self.wifi_st_radio = ctk.CTkRadioButton(self.wifi_options_frame,
                                                text="Connect my EX-CommandStation to my existing wireless network",
                                                variable=self.wifi_type,
                                                value=1)
        self.wifi_ssid_label = ctk.CTkLabel(self.wifi_options_frame, text="WiFi SSID:")
        self.wifi_ssid_entry = ctk.CTkEntry(self.wifi_options_frame, textvariable=self.wifi_ssid,
                                            width=200, fg_color="white")
        self.wifi_pwd_label = ctk.CTkLabel(self.wifi_options_frame, text="WiFi Password:")
        self.wifi_pwd_entry = ctk.CTkEntry(self.wifi_options_frame, textvariable=self.wifi_pwd,
                                           width=200, fg_color="white")

        # Layout WiFi frame
        self.wifi_frame.grid_columnconfigure((0, 1), weight=1)
        self.wifi_frame.grid_rowconfigure(0, weight=1)
        self.wifi_options_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.wifi_options_frame.grid_rowconfigure((0, 1, 2), weight=1)
        self.wifi_options_frame.grid(column=1, row=0)
        self.wifi_switch.grid(column=0, row=0)
        self.wifi_ap_radio.grid(column=0, row=0, columnspan=4, sticky="w", **grid_options)
        self.wifi_st_radio.grid(column=0, row=1, columnspan=4, sticky="w", **grid_options)
        self.wifi_ssid_label.grid(column=0, row=2, **grid_options)
        self.wifi_ssid_entry.grid(column=1, row=2, **grid_options)
        self.wifi_pwd_label.grid(column=2, row=2, **grid_options)
        self.wifi_pwd_entry.grid(column=3, row=2, **grid_options)

        # Layout frame
        self.version_label.grid(column=0, row=0, columnspan=2, **grid_options)
        self.version_frame.grid(column=0, row=1, columnspan=2, **grid_options)
        self.hardware_label.grid(column=0, row=2, columnspan=2, **grid_options)
        self.motor_driver_label.grid(column=0, row=3, **grid_options)
        self.motor_driver_combo.grid(column=1, row=3, sticky="w", **grid_options)
        self.display_switch.grid(column=0, row=4, **grid_options)
        self.display_combo.grid(column=1, row=4, sticky="w", **grid_options)
        self.wifi_frame.grid(column=0, row=5, columnspan=2, sticky="ew", **grid_options)
