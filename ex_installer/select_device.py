"""
Module for the Select Device page view
"""

# Import Python modules
import customtkinter as ctk
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
                        "Select your chosen device from the options below.\n\n" +
                        "If the device detected matches multiple devices, select the correct one from the pulldown " +
                        "list provided.\n\n" +
                        "If you have a generic or clone device, it likely appears as “Unknown”. In this instance, " +
                        "you will need to select the appropriate device from the pulldown list provided.")

    # temp_device_list = [
    #     {"port": "COM4",
    #      "matching_boards": [{
    #          "name": "Arduino Mega 2560",
    #          "fqbn": "arduino:avr:mega"
    #          }]
    #      },
    #     {"port": "COM5",
    #      "matching_boards": [{
    #          "name": "Unknown",
    #          "fqbn": "unknown"
    #          }]
    #      },
    #     {"port": "COM6",
    #      "matching_boards": [
    #          {"name": "Arduino Nano",
    #           "fqbn": "arduino:avr:nano"},
    #          {"name": "Arduino Uno",
    #           "fqbn": "arduino:avr:uno"}
    #       ]}
    #     ]

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
                                              wraplength=780)

        # Create list device button
        self.list_device_button = ctk.CTkButton(self.select_device_frame, width=200, height=50,
                                                text="List Devices", font=self.action_button_font,
                                                command=lambda event="list_devices": self.list_devices(event))

        # Create device list container frame
        self.device_list_frame = ctk.CTkFrame(self.select_device_frame,
                                              border_width=2,
                                              fg_color="#E5E5E5")
        self.device_list_frame.grid_columnconfigure((0, 1), weight=1)

        # Create detected device label and grid
        grid_options = {"padx": 5, "pady": 5}
        self.device_list_label = ctk.CTkLabel(self.device_list_frame,
                                              text="Select one from these detected devices")
        self.device_list_label.grid(column=0, row=0, columnspan=2, sticky="ew", **grid_options)

        # Create device list radio buttons, pulldown lists, and grid in frame
        # supported_boards = ["Select the correct device"]
        # for board in self.acli.supported_devices:
        #     supported_boards.append(board)
        # for index, device in enumerate(self.temp_device_list):
        #     value = index
        #     self.device_list_frame.grid_rowconfigure(index, weight=1)
        #     if len(self.temp_device_list[index]["matching_boards"]) > 1:
        #         matched_boards = ["Select the correct device"]
        #         for matched_board in self.temp_device_list[index]["matching_boards"]:
        #             matched_boards.append(matched_board["name"])
        #         multi_combo = ctk.CTkComboBox(self.device_list_frame, values=matched_boards, width=300)
        #         multi_combo.grid(column=1, row=index+1, sticky="e", **grid_options)
        #         text = "Multiple matches detected"
        #     elif self.temp_device_list[index]["matching_boards"][0]["name"] == "Unknown":
        #         unknown_combo = ctk.CTkComboBox(self.device_list_frame, values=supported_boards, width=300)
        #         unknown_combo.grid(column=1, row=index+1, sticky="e", **grid_options)
        #         text = "Unknown or clone detected"
        #     else:
        #         text = self.temp_device_list[index]["matching_boards"][0]["name"]
        #     radio_button = ctk.CTkRadioButton(self.device_list_frame, text=text, value=value)
        #     radio_button.grid(column=0, row=index+1, sticky="w", **grid_options)

        # Layout window
        self.instruction_label.grid(column=0, row=0)
        self.list_device_button.grid(column=0, row=1)
        self.device_list_frame.grid(column=0, row=2, ipadx=5, ipady=5)

    def list_devices(self, event):
        """
        Use the Arduino CLI to list attached devices
        """
        pprint(event)
        if event == "list_devices":
            self.acli.detected_devices = []
            self.disable_input_states(self)
            self.process_start("refresh_list", "Scanning for attached devices", "List_Devices")
            self.acli.list_boards(self.acli.cli_file_path(), self.queue)
        elif self.process_phase == "refresh_list":
            if self.process_status == "success":
                if isinstance(self.process_data, list) and len(self.process_data) > 0:
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
                #     row = 6
                #     for index, item in enumerate(self.acli.detected_devices):
                #         value = index
                #         text = (f"{self.acli.detected_devices[index]['matching_boards'][0]['name']} "
                #                 f"on {self.acli.detected_devices[index]['port']}")
                #         radio_button = ctk.CTkRadioButton(self.device_select_frame, text=text,
                #                                           variable=self.selected_device,
                #                                           value=value, command=self._select_device)
                #         if self.acli.detected_devices[index]['matching_boards'][0]['name'] == "Unknown":
                #             unknown_combo = ctk.CTkComboBox(self.device_select_frame,
                #                                             values=self.supported_device_list, width=300,
                #                                             command=lambda x: self._update_unknown(value,
                #                                                                                    unknown_combo.get()))
                #             unknown_combo.grid(column=1, row=row, sticky="e")
                #         radio_button.grid(column=0, row=row, sticky="w")
                #         row += 1
                #     self.device_select_frame.grid()
                # else:
                #     self.selected_device_label.configure(text="No available devices have been found")

                self.process_stop()
                self.restore_input_states()
            elif self.process_status == "error":
                self.process_error("Error scanning for devices")
                self.restore_input_states()
