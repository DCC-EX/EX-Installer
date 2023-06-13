"""
Module for the Select Device page view
"""

# Import Python modules
import customtkinter as ctk

# Import local modules
from .common_widgets import WindowLayout
from . import images


class SelectDevice(WindowLayout):
    """
    Class for the Select Device view
    """

    # Define text to use in labels
    instruction_text = ("Ensure your Arduino device is connected to your computer's USB port.\n\n" +
                        "If the device detected matches multiple devices, select the correct one from the pulldown " +
                        "list provided.\n\n" +
                        "If you have a generic or clone device, it likely appears as “Unknown”. In this instance, " +
                        "you will need to select the appropriate device from the pulldown list provided.")

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set up event handlers
        event_callbacks = {
            "<<List_Devices>>": self.list_devices
        }
        for sequence, callback in event_callbacks.items():
            self.bind_class("bind_events", sequence, callback)
        new_tags = self.bindtags() + ("bind_events",)
        self.bindtags(new_tags)

        # Start with an empty device list
        self.acli.detected_devices = []

        # Set up title
        self.set_title_logo(images.EX_INSTALLER_LOGO)
        self.set_title_text("Select your device")

        # Set up next/back buttons
        self.next_back.set_back_text("Manage Arduino CLI")
        self.next_back.set_back_command(lambda view="manage_arduino_cli": parent.switch_view(view))
        self.next_back.set_next_text("Select product to install")
        self.next_back.set_next_command(lambda view="select_product": parent.switch_view(view))

        # Set up and configure container frame
        self.select_device_frame = ctk.CTkFrame(self.main_frame, height=360)
        self.select_device_frame.grid(column=0, row=0, sticky="nsew", ipadx=5, ipady=5)
        self.select_device_frame.grid_columnconfigure(0, weight=1)
        self.select_device_frame.grid_rowconfigure((0, 1, 2), weight=1)

        # Create instruction label
        self.instruction_label = ctk.CTkLabel(self.select_device_frame,
                                              text=self.instruction_text,
                                              font=self.instruction_font,
                                              wraplength=780)

        # Create list device button
        self.list_device_button = ctk.CTkButton(self.select_device_frame, width=200, height=50,
                                                text=None, font=self.action_button_font,
                                                command=lambda event="list_devices": self.list_devices(event))

        # Create device list container frame and variable
        self.device_list_frame = ctk.CTkFrame(self.select_device_frame,
                                              border_width=2,
                                              fg_color="#E5E5E5")
        self.device_list_frame.grid_columnconfigure((0, 1), weight=1)
        self.device_list_frame.grid_rowconfigure(0, weight=1)
        self.selected_device = ctk.IntVar(self, value=-1)

        # Create detected device label and grid
        grid_options = {"padx": 5, "pady": 5}
        self.no_device_label = ctk.CTkLabel(self.select_device_frame, text="No devices found",
                                            font=self.bold_instruction_font)
        self.device_list_label = ctk.CTkLabel(self.device_list_frame, text="Select your device",
                                              font=self.instruction_font)
        self.device_list_label.grid(column=0, row=0, columnspan=2, **grid_options)

        # Layout window
        self.instruction_label.grid(column=0, row=0)
        self.no_device_label.grid(column=0, row=1)
        self.device_list_frame.grid(column=0, row=1, ipadx=5, ipady=5)
        self.list_device_button.grid(column=0, row=2)

        self.set_state()

    def set_state(self):
        if len(self.acli.detected_devices) == 0:
            self.list_device_button.configure(text="Scan for Devices")
            self.no_device_label.grid()
            self.device_list_frame.grid_remove()
        else:
            self.list_device_button.configure(text="Refresh Device List")
            self.no_device_label.grid_remove()
            self.device_list_frame.grid()
        if not self.acli.selected_device:
            self.next_back.disable_next()
        else:
            self.next_back.enable_next()

    def list_devices(self, event):
        """
        Use the Arduino CLI to list attached devices
        """
        if event == "list_devices":
            self.acli.detected_devices = []
            self.acli.selected_device = None
            self.disable_input_states(self)
            self.process_start("refresh_list", "Scanning for attached devices", "List_Devices")
            self.acli.list_boards(self.acli.cli_file_path(), self.queue)
        elif self.process_phase == "refresh_list":
            if self.process_status == "success":
                if isinstance(self.process_data, list) and len(self.process_data) > 0:
                    supported_boards = ["Select the correct device"]
                    for board in self.acli.supported_devices:
                        supported_boards.append(board)
                    grid_options = {"padx": 5, "pady": 5}
                    for board in self.process_data:
                        matching_board_list = []
                        port = board["port"]["address"]
                        if "matching_boards" in board:
                            for match in board["matching_boards"]:
                                name = match["name"]
                                fqbn = match["fqbn"]
                                matching_board_list.append({"name": name, "fqbn": fqbn})
                        else:
                            matching_board_list.append({"name": "Unknown", "fqbn": "unknown"})
                        self.acli.detected_devices.append({"port": port, "matching_boards": matching_board_list})
                    for index, item in enumerate(self.acli.detected_devices):
                        text = None
                        self.device_list_frame.grid_rowconfigure(index+1, weight=1)
                        if len(self.acli.detected_devices[index]["matching_boards"]) > 1:
                            matched_boards = ["Select the correct device"]
                            for matched_board in self.acli.detected_devices[index]["matching_boards"]:
                                matched_boards.append(matched_board["name"])
                            multi_combo = ctk.CTkComboBox(self.device_list_frame, values=matched_boards, width=300,
                                                          command=lambda x: self.update_board(index, multi_combo.get()))
                            multi_combo.grid(column=1, row=index+1, sticky="e", **grid_options)
                            text = "Multiple matches detected"
                            text += " on " + self.acli.detected_devices[index]["port"]
                        elif self.acli.detected_devices[index]["matching_boards"][0]["name"] == "Unknown":
                            unknown_combo = ctk.CTkComboBox(self.device_list_frame, values=supported_boards, width=300,
                                                            command=lambda x: self.update_board(index,
                                                                                                unknown_combo.get()))
                            unknown_combo.grid(column=1, row=index+1, sticky="e", **grid_options)
                            text = "Unknown or clone detected"
                            text += " on " + self.acli.detected_devices[index]["port"]
                        else:
                            text = self.acli.detected_devices[index]["matching_boards"][0]["name"]
                            text += " on " + self.acli.detected_devices[index]["port"]
                        radio_button = ctk.CTkRadioButton(self.device_list_frame, text=text,
                                                          variable=self.selected_device, value=index,
                                                          command=self.select_device)
                        radio_button.grid(column=0, row=index+1, sticky="w", **grid_options)
                self.set_state()
                self.process_stop()
                self.restore_input_states()
            elif self.process_status == "error":
                self.process_error("Error scanning for devices")
                self.restore_input_states()

    def update_board(self, index, name):
        if name != "Select the correct device":
            self.acli.detected_devices[index]["matching_boards"][0]["name"] = name
            self.acli.detected_devices[index]["matching_boards"][0]["fqbn"] = self.acli.supported_devices[name]
            self.selected_device.set(index)
            self.select_device()

    def select_device(self):
        self.acli.selected_device = None
        device = self.selected_device.get()
        if not self.acli.detected_devices[device]["matching_boards"][0]["name"] == "Unknown":
            self.acli.selected_device = device
            self.next_back.enable_next()
        else:
            self.next_back.disable_next()
