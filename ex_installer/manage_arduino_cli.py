"""
Module for managing the Arduino CLI page view
"""

# Import Python modules
import customtkinter as ctk

# Import local modules
from .common_widgets import WindowLayout
from . import images


class ManageArduinoCLI(WindowLayout):
    # Define text to use in labels
    version = "1.2.3"
    intro_text = ("The Arduino CLI is utilised to compile and upload any DCC-EX products " +
                  "to your Arduino device. EX-Installer is able to manage the installation " +
                  "and management of the Arduino CLI for you at the click of a button.")
    installed_text = f"The Arduino CLI version {version} is currently installed"
    not_installed_text = "The Arduino CLI is currently not installed"
    install_instruction_text = ("To install the Arduino CLI, simply click the install button to start.\n\n" +
                                "If you are using an Espressif or STMicroelectronics device, you will need to " +
                                "enable support for these by selecting the appropriate additional platform option.\n\n"
                                "Note that enabling additional platforms is likely to add several minutes to the " +
                                "installation process. Maybe grab a cup of tea or a coffee!")
    refresh_instruction_text = ("While the Arduino CLI is installed, it is recommended to refresh it regularly " +
                                "to ensure support for the various devices is kept up to date. To refresh the CLI, " +
                                "siimply click the refresh button.\n\n"
                                "Note that enabling any of the additional platforms is likely to add " +
                                "several minutes to the refresh process. Maybe grab a cup of tea or a coffee!")

    """
    Class for the Manage Arduino CLI view
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Set up the Manage Arduino CLI view
        """
        super().__init__(parent, *args, **kwargs)

        # Set title and logo
        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Manage the Arduino CLI")

        # Set up next and back buttons
        self.next_back.show_back()
        self.next_back.set_back_text("Welcome")
        self.next_back.set_back_command(lambda view="welcome": parent.switch_view(view))

        self.next_back.set_next_text("Select your device")
        self.next_back.set_next_command(lambda view="select_device": parent.switch_view(view))

        # Create, grid, and configure container frame
        self.select_product_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.select_product_frame.grid(column=0, row=0, sticky="nsew", ipadx=5, ipady=5)
        self.select_product_frame.grid_columnconfigure((0, 1), weight=1)
        self.select_product_frame.grid_rowconfigure((0, 1, 2), weight=1)

        # Create state and instruction labels and manage CLI button
        label_options = {"wraplength": 780}
        self.intro_label = ctk.CTkLabel(self.select_product_frame,
                                        text=self.intro_text,
                                        **label_options)
        self.cli_state_label = ctk.CTkLabel(self.select_product_frame,
                                            **label_options)
        self.instruction_label = ctk.CTkLabel(self.select_product_frame,
                                              wraplength=390)
        self.manage_cli_button = ctk.CTkButton(self.select_product_frame, width=200, height=30,
                                               text=None, font=self.button_font)

        # Create frame and widgets for additional platform support
        grid_options = {"padx": 5, "pady": 5}
        self.extra_platforms_frame = ctk.CTkFrame(self.select_product_frame,
                                                  border_width=2,
                                                  fg_color="#E5E5E5")
        self.extra_platforms_frame.grid_columnconfigure(0, weight=1)
        self.extra_platforms_label = ctk.CTkLabel(self.extra_platforms_frame,
                                                  text="Enable extra platforms")
        self.extra_platforms_label.grid(column=0, row=0, sticky="ew", **grid_options)
        switch_options = {"onvalue": "on", "offvalue": "off"}
        for index, platform in enumerate(self.acli.extra_platforms):
            self.extra_platforms_frame.grid_rowconfigure(index+1, weight=1)
            switch = ctk.CTkSwitch(self.extra_platforms_frame, text=platform, **switch_options)
            switch.grid(column=0, row=index+1, sticky="w", **grid_options)

        # Layout frame
        self.intro_label.grid(column=0, row=0, columnspan=2)
        self.cli_state_label.grid(column=0, row=1)
        self.manage_cli_button.grid(column=1, row=1)
        self.instruction_label.grid(column=0, row=2)
        self.extra_platforms_frame.grid(column=1, row=2, ipadx=5, ipady=5)

        self.set_state()

    def set_state(self):
        if self.acli.is_installed(self.acli.cli_file_path()):
            self.cli_state_label.configure(text=self.installed_text,
                                           text_color="#00353D",
                                           font=ctk.CTkFont(weight="normal"))
            self.instruction_label.configure(text=self.refresh_instruction_text)
            self.manage_cli_button.configure(text="Refresh Arduino CLI")
            # self.next_back.enable_next()
        else:
            self.cli_state_label.configure(text=self.not_installed_text,
                                           text_color="#FF5C00",
                                           font=ctk.CTkFont(weight="bold"))
            self.instruction_label.configure(text=self.install_instruction_text)
            self.manage_cli_button.configure(text="Install Arduino CLI")
            # self.next_back.disable_next()
