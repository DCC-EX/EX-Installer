"""
Module for the Select Device page view
"""

# Import Python modules
import customtkinter as ctk
import logging
import sys
import subprocess
from pprint import pprint

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

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start view")

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
        self.next_back.hide_monitor_button()

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

        self.get_port_descriptions()

    def set_state(self):
        self.next_back.hide_log_button()
        if len(self.acli.detected_devices) == 0:
            self.list_device_button.configure(text="Scan for Devices")
            self.no_device_label.grid()
            self.device_list_frame.grid_remove()
            self.log.debug("No devices detected")
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
            self.log.debug("List devices button clicked")
            self.acli.detected_devices.clear()
            self.acli.selected_device = None
            for widget in self.device_list_frame.winfo_children():
                widget.destroy()
            self.disable_input_states(self)
            self.process_start("refresh_list", "Scanning for attached devices", "List_Devices")
            self.acli.list_boards(self.acli.cli_file_path(), self.queue)
        elif self.process_phase == "refresh_list":
            if self.process_status == "success":
                if isinstance(self.process_data, list) and len(self.process_data) > 0:
                    supported_boards = []
                    for board in self.acli.supported_devices:
                        supported_boards.append(board)
                    grid_options = {"padx": 5, "pady": 5}
                    for board in self.process_data:
                        matching_board_list = []
                        port = board["port"]["address"]
                        self.log.debug("Device on %s found: %s", port, board)
                        if "matching_boards" in board:
                            for match in board["matching_boards"]:
                                name = match["name"]
                                fqbn = match["fqbn"]
                                matching_board_list.append({"name": name, "fqbn": fqbn})
                            self.log.debug("Matches: %s", matching_board_list)
                        else:
                            matching_board_list.append({"name": "Unknown", "fqbn": "unknown"})
                            self.log.debug("Device unknown")
                        self.acli.detected_devices.append({"port": port, "matching_boards": matching_board_list})
                        self.log.debug("Found device list")
                        self.log.debug(self.acli.detected_devices)
                    for index, item in enumerate(self.acli.detected_devices):
                        text = None
                        row = index + 1
                        self.device_list_frame.grid_rowconfigure(row, weight=1)
                        self.log.debug("Process %s at index %s", item, index)
                        if len(self.acli.detected_devices[index]["matching_boards"]) > 1:
                            matched_boards = []
                            for matched_board in self.acli.detected_devices[index]["matching_boards"]:
                                matched_boards.append(matched_board["name"])
                            multi_combo = ctk.CTkComboBox(self.device_list_frame,
                                                          values="Select the correct device", width=300,
                                                          command=lambda name, i=index: self.update_board(name, i))
                            multi_combo.grid(column=1, row=row, sticky="e", **grid_options)
                            multi_combo.configure(values=matched_boards)
                            text = "Multiple matches detected"
                            text += " on " + self.acli.detected_devices[index]["port"]
                            self.log.debug("Multiple matched devices on %s", self.acli.detected_devices[index]["port"])
                            self.log.debug(self.acli.detected_devices[index]["matching_boards"])
                        elif self.acli.detected_devices[index]["matching_boards"][0]["name"] == "Unknown":
                            unknown_combo = ctk.CTkComboBox(self.device_list_frame,
                                                            values=["Select the correct device"], width=300,
                                                            command=lambda name, i=index: self.update_board(name, i))
                            unknown_combo.grid(column=1, row=row, sticky="e", **grid_options)
                            unknown_combo.configure(values=supported_boards)
                            text = "Unknown or clone detected"
                            text += " on " + self.acli.detected_devices[index]["port"]
                            self.log.debug("Unknown or clone device on %s", self.acli.detected_devices[index]["port"])
                        else:
                            text = self.acli.detected_devices[index]["matching_boards"][0]["name"]
                            text += " on " + self.acli.detected_devices[index]["port"]
                            self.log.debug("%s on %s", self.acli.detected_devices[index]["matching_boards"][0]["name"],
                                           self.acli.detected_devices[index]["port"])
                        radio_button = ctk.CTkRadioButton(self.device_list_frame, text=text,
                                                          variable=self.selected_device, value=index,
                                                          command=self.select_device)
                        radio_button.grid(column=0, row=row, sticky="w", **grid_options)
                self.set_state()
                self.process_stop()
                self.restore_input_states()
            elif self.process_status == "error":
                self.process_error("Error scanning for devices")
                self.restore_input_states()

    def update_board(self, name, index):
        if name != "Select the correct device":
            self.acli.detected_devices[index]["matching_boards"][0]["name"] = name
            self.acli.detected_devices[index]["matching_boards"][0]["fqbn"] = self.acli.supported_devices[name]
            self.selected_device.set(index)
            self.select_device()

    def select_device(self):
        self.acli.selected_device = None
        device = self.selected_device.get()
        if (
            self.acli.detected_devices[device]["matching_boards"][0]["name"] != "Unknown" and
            self.acli.detected_devices[device]["matching_boards"][0]["name"] != "Select the correct device"
        ):
            self.acli.selected_device = device
            self.next_back.enable_next()
            self.log.debug("Selected %s on port %s",
                           self.acli.detected_devices[self.acli.selected_device]["matching_boards"][0]["name"],
                           self.acli.detected_devices[self.acli.selected_device]["port"])
            self.next_back.show_monitor_button()
        else:
            self.next_back.disable_next()
            self.next_back.hide_monitor_button()

    def get_port_descriptions(self):
        """
        Function to obtain USB/serial port descriptions

        For Windows this uses WMI, for Linux it uses lsusb, and macOS uses system_profiler
        """
        if sys.platform.startswith("win"):
            command = "wmic path Win32_SerialPort get DeviceID, Name /format:list"
            output = subprocess.check_output(command, shell=True).decode("utf-8")
            ports = []
            port_info = {}
            for line in output.split("\n"):
                line = line.strip()
                if line.startswith('DeviceID='):
                    port_info['device_id'] = line.replace('DeviceID=', '')
                elif line.startswith('Name='):
                    port_info['name'] = line.replace('Name=', '')
                    ports.append(port_info)
                    port_info = {}
            pprint(ports)
        elif sys.platform.startswith("dar"):
            pass
        else:
            pass
