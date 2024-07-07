"""
Module for a serial monitor interface

This allows for interaction with an Arduino device via the serial interface

© 2024, Peter Cole.
© 2023, Peter Cole.
All rights reserved.

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
from queue import Queue
from threading import Thread
import subprocess
import platform
import traceback
from CTkMessagebox import CTkMessagebox
import os
import sys
import serial
import re
from datetime import datetime

# Import local modules
from . import images
from .common_fonts import CommonFonts
from .file_manager import FileManager as fm

# Define valid monitor highlights
monitor_highlights = {
    "Version": {
        "regex": r"^\<(iDCC-EX\sV-.*)\>$",
        "matches": 1,
        "tag": "green"
    },
    "WiFi AP Details (ESP32)": {
        "regex": r"^\<\*\sWifi\sAP\sSSID\s(.+?)\sPASS\s(.+?)\s\*\>$",
        "matches": 2,
        "tag": "blue"
    },
    "WiFi AP Details (ESP8266)": {
        "regex": r"^AT\+CWSAP_CUR=\"(.+?)\",\"(.+?)\".*$",
        "matches": 2,
        "tag": "blue"
    },
    "WiFi AP IP": {
        "regex": r"<\*\sWifi\sAP\sIP\s(\d*\.\d*\.\d*\.\d*)\s\*\>",
        "matches": 1,
        "tag": "purple"
    },
    "Port (ESP32)": {
        "regex": r".*port\s(\d*)\s\*\>",
        "matches": 1,
        "tag": "purple"
    },
    "Port (ESP8266)": {
        "regex": r"^AT\+CIPSERVER=\d*,(\d*).*$",
        "matches": 1,
        "tag": "purple"
    },
    "WiFi Firmware": {
        "regex": r"^AT\sversion\:(.+?)$",
        "matches": 1,
        "tag": "green"
    },
    "WiFi ST Details": {
        "regex": r"^AT\+CWJAP_CUR=\"(.+?)\",\"(.+?)\".*$",
        "matches": 2,
        "tag": "blue"
    },
    "WiFi ST IP": {
        "regex": r"\"(\d*\.\d*\.\d*\.\d*)\"",
        "matches": 1,
        "tag": "purple"
    }
}


class SerialMonitor(ctk.CTkToplevel):
    """
    Class to define a window for the serial monitor
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Open window")
        self.report_callback_exception = self.exception_handler

        # Set up fonts
        self.common_fonts = CommonFonts(self)

        # Set up event handlers
        event_callbacks = {
            "<<Monitor>>": self.monitor
        }
        for sequence, callback in event_callbacks.items():
            self.bind_class("bind_events", sequence, callback)
        new_tags = self.bindtags() + ("bind_events",)
        self.bindtags(new_tags)

        # Make sure closing the window closes the serial port nicely
        self.protocol("WM_DELETE_WINDOW", self.close_monitor)

        # Set icon and title
        if sys.platform.startswith("win"):
            self.after(250, lambda icon=images.DCC_EX_ICON_ICO: self.iconbitmap(icon))
        self.title("Device Monitor")

        # Hide window while GUI is built initially, show after 250ms
        self.withdraw()
        self.after(250, self.deiconify)

        # Get existing Arduino CLI instance
        self.acli = self.master.winfo_toplevel().acli

        # Create queue and variables for process monitoring
        self.queue = Queue()
        self.process_phase = None
        self.process_status = None
        self.process_topic = None
        self.process_data = None

        # Set up main window geometry and parent frame
        self.geometry("800x550")
        self.minsize(width=800, height=550)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.window_frame = ctk.CTkFrame(self, fg_color="grey95")
        self.window_frame.grid_columnconfigure(0, weight=1)
        self.window_frame.grid_rowconfigure(2, weight=1)
        self.window_frame.grid(column=0, row=0, sticky="nsew")

        # Define fonts for use
        self.button_font = self.common_fonts.button_font
        self.instruction_font = self.common_fonts.instruction_font
        self.bold_instruction_font = self.common_fonts.bold_instruction_font
        self.action_button_font = self.common_fonts.action_button_font

        self.command_frame = ctk.CTkFrame(self.window_frame, width=790, height=40)
        self.monitor_frame = ctk.CTkFrame(self.window_frame, width=790, height=420)
        self.device_frame = ctk.CTkFrame(self.window_frame, width=790, height=40)
        self.command_frame.grid_columnconfigure(1, weight=1)
        self.command_frame.grid_rowconfigure(0, weight=1)
        self.monitor_frame.grid_columnconfigure(0, weight=1)
        self.monitor_frame.grid_rowconfigure(0, weight=1)
        self.device_frame.grid_columnconfigure(0, weight=1)
        self.device_frame.grid_rowconfigure(0, weight=1)
        self.command_frame.grid(column=0, row=1, sticky="nsew", padx=5, pady=2)
        self.monitor_frame.grid(column=0, row=2, sticky="nsew", padx=5, pady=2)
        self.device_frame.grid(column=0, row=3, sticky="nsew", padx=5, pady=(0, 5))

        # Create command frame widgets and layout frame
        self.command_history = []
        grid_options = {"padx": 5, "pady": 5}
        self.command_label = ctk.CTkLabel(self.command_frame, text="Enter command:", font=self.instruction_font)
        self.command = ctk.StringVar(self)
        self.command_entry = ctk.CTkComboBox(self.command_frame, variable=self.command, values=self.command_history,
                                             command=self.send_command)
        self.command_entry.bind("<Return>", self.send_command)
        self.command_button = ctk.CTkButton(self.command_frame, text="Send", font=self.button_font, width=80,
                                            command=self.send_command)
        self.save_log_button = ctk.CTkButton(self.command_frame, text="Save Log", font=self.button_font, width=80,
                                             command=self.show_save_log_popup)
        self.close_button = ctk.CTkButton(self.command_frame, text="Close", font=self.button_font, width=80,
                                          command=self.close_monitor)
        self.command_label.grid(column=0, row=0, sticky="w", **grid_options)
        self.command_entry.grid(column=1, row=0, sticky="ew", **grid_options)
        self.command_button.grid(column=2, row=0, sticky="e", pady=5)
        self.save_log_button.grid(column=3, row=0, sticky="e", padx=(5, 0), pady=5)
        self.close_button.grid(column=4, row=0, sticky="e", **grid_options)

        # Create monitor frame widgets and layout frame
        self.output_textbox = ctk.CTkTextbox(self.monitor_frame, border_width=3, border_spacing=5,
                                             fg_color="#E5E5E5", border_color="#00A3B9")
        self.output_textbox.grid(column=0, row=0, sticky="nsew")

        # Create highlighter tags
        self.output_textbox.tag_add("green", "end")
        self.output_textbox.tag_config("green",
                                       background="green",
                                       foreground="white")
        self.output_textbox.tag_add("blue", "end")
        self.output_textbox.tag_config("blue",
                                       background="blue",
                                       foreground="white")
        self.output_textbox.tag_add("purple", "end")
        self.output_textbox.tag_config("purple",
                                       background="purple3",
                                       foreground="white")
        self.output_textbox.tag_add("warning", "end")
        self.output_textbox.tag_config("warning",
                                       background="orange red",
                                       foreground="white")
        self.output_textbox.tag_add("error", "end")
        self.output_textbox.tag_config("red",
                                       background="red",
                                       foreground="white")

        # Create device frame widgets and layout
        self.device_label = ctk.CTkLabel(self.device_frame, text=None, font=self.instruction_font)
        self.device_label.grid(column=0, row=0, sticky="ew", padx=5, pady=5)

        # Start serial monitor process
        self.monitor()

    def close_monitor(self):
        """
        Close the monitor window nicely:

        - If serial port open, close it
        - If thread running, join/end it
        - Destroy this object
        """
        self.close_clicked = True
        if hasattr(self, "serial_port") and self.serial_port:
            if self.serial_port is not None:
                self.serial_port.close()
            if self.read_thread is not None:
                self.read_thread.join()
        self.destroy()

    def monitor(self, event=None):
        """
        Function to monitoring using PySerial

        Starts the process, and then creates a thread to read the output continuously
        """
        self.command_entry.configure(state="disabled")
        self.command_button.configure(state="disabled")
        self.close_clicked = False
        if self.acli.selected_device is not None:
            port = self.acli.detected_devices[self.acli.selected_device]['port']
            text = ("Monitoring " +
                    f"{self.acli.detected_devices[self.acli.selected_device]['matching_boards'][0]['name']} " +
                    f" on {port}")
            self.device_label.configure(text=text)
            try:
                self.serial_port = serial.Serial(port, 115200)
            except serial.SerialException as e:
                self.log.error(f"Failed to open serial connection: {e}")
                self.output_textbox.configure(state="normal")
                self.output_textbox.insert("insert", f"Failed to open serial connection: {e}")
                self.output_textbox.configure(state="disabled")
                return

            self.command_entry.configure(state="normal")
            self.command_button.configure(state="normal")
            self.read_thread = Thread(target=self.read_output)
            self.read_thread.daemon = True
            self.read_thread.start()

    def read_output(self):
        """
        Function to read serial output
        """
        while True:
            try:
                if self.serial_port.in_waiting > 0:
                    output = self.serial_port.readline()
                    """
                    if closing the window, the serial port was closed and it may have garbage, ignore it
                    """
                    if self.close_clicked:
                        return
                    output = output.decode().strip()
                    self.update_textbox(output)
            except OSError as e:
                if not self.close_clicked:
                    self.log.error(f"Error accessing serial port: {e}")
                break

    def update_textbox(self, output):
        """
        Function to update the textbox with output from the Arduino CLI in monitor mode
        """
        self.output_textbox.configure(state="normal")
        for highlight in monitor_highlights.keys():
            regex = monitor_highlights[highlight]["regex"]
            matches = monitor_highlights[highlight]["matches"]
            tag = monitor_highlights[highlight]["tag"]
            match = re.search(regex, output)
            if match and len(match.groups()) == matches:
                for group in match.groups():
                    temp = output.split(group)
                    self.output_textbox.insert("insert", temp[0])
                    self.output_textbox.insert("insert", group, tag)
                    output = temp[1]
        self.output_textbox.insert("insert", output + "\n")
        self.output_textbox.see("end")
        self.output_textbox.update_idletasks()
        self.output_textbox.configure(state="disabled")

    def send_command(self, event=None):
        """
        Function to send a command to the serial port
        """
        command_text = self.command_entry.get()
        if command_text != "":
            self.serial_port.write((command_text + "\n").encode())
            if command_text not in self.command_history:
                self.command_history.append(command_text)
            self.command_entry.configure(values=self.command_history)
            self.command_entry.set("")
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert("insert", command_text + "\n")
        self.output_textbox.configure(state="disabled")
        self.output_textbox.see("end")

    def show_save_log_popup(self):
        """
        Function to show the message box to select the folder to save device log
        """
        if hasattr(self, "log_popup") and self.log_popup is not None and self.log_popup.winfo_exists():
            self.log_popup.focus()
        else:
            self.log_popup = ctk.CTkToplevel(self)
            self.log_popup.focus()
            self.log_popup.lift(self)

            # Ensure pop up is within the confines of the app window to start
            main_window = self.winfo_toplevel()
            log_offset_x = main_window.winfo_x() + 75
            log_offset_y = main_window.winfo_y() + 200
            self.log_popup.geometry(f"+{log_offset_x}+{log_offset_y}")
            self.log_popup.update()

            # Set icon and title
            if sys.platform.startswith("win"):
                self.log_popup.after(250, lambda icon=images.DCC_EX_ICON_ICO: self.log_popup.iconbitmap(icon))
            self.log_popup.title("Save device log")
            self.log_popup.withdraw()
            self.log_popup.after(250, self.log_popup.deiconify)
            self.log_popup.grid_columnconfigure(0, weight=1)
            self.log_popup.grid_rowconfigure(0, weight=1)
            self.window_frame = ctk.CTkFrame(self.log_popup, fg_color="grey95")
            self.window_frame.grid_columnconfigure((0, 1, 2), weight=1)
            self.window_frame.grid_rowconfigure((0, 1), weight=1)
            self.window_frame.grid(column=0, row=0, sticky="nsew")
            self.folder_label = ctk.CTkLabel(self.window_frame, text="Select the folder to save the log:",
                                             font=self.instruction_font)
            self.status_frame = ctk.CTkFrame(self.window_frame, border_width=2)
            self.status_label = ctk.CTkLabel(self.status_frame, text="Status:",
                                             font=self.instruction_font)
            self.status_text = ctk.CTkLabel(self.status_frame, text="Enter or select destination",
                                            font=self.bold_instruction_font)
            self.log_path = ctk.StringVar(value=None)
            self.log_path_entry = ctk.CTkEntry(self.window_frame, textvariable=self.log_path,
                                               width=300)
            self.browse_button = ctk.CTkButton(self.window_frame, text="Browse",
                                               width=80, command=self.browse_log_dir)
            self.save_button = ctk.CTkButton(self.window_frame, width=200, height=50,
                                             text="Save and open log", font=self.action_button_font,
                                             command=self.save_log_file)
            self.folder_label.grid(column=0, row=0, padx=(10, 1), pady=(10, 5))
            self.log_path_entry.grid(column=1, row=0, padx=1, pady=(10, 5))
            self.browse_button.grid(column=2, row=0, padx=(1, 10), pady=(10, 5))
            self.save_button.grid(column=0, row=1, columnspan=3, padx=10, pady=5)
            self.status_frame.grid_columnconfigure((0, 1), weight=1)
            self.status_frame.grid_rowconfigure(0, weight=1)
            self.status_frame.grid(column=0, row=2, columnspan=3, sticky="nsew", padx=10, pady=(5, 10))
            self.status_label.grid(column=0, row=0, padx=5, pady=5)
            self.status_text.grid(column=1, row=0, padx=5, pady=5)

    def browse_log_dir(self):
        """
        Opens a directory browser dialogue to select the folder to save the device log to
        """
        directory = ctk.filedialog.askdirectory()
        if directory:
            self.log_path.set(directory)
            self.log.debug("Save device log to %s", directory)
            self.log_popup.focus()

    def save_log_file(self):
        """
        Function to save the device log file to the chosen location, and open it
        """
        if fm.is_valid_dir(self.log_path.get()):
            log_name = datetime.now().strftime("device-logs-%Y%m%d-%H%M%S.log")
            log_file = os.path.join(self.log_path.get(), log_name)
            file_contents = self.output_textbox.get("1.0", ctk.END)
            try:
                with open(log_file, "w", encoding="utf-8") as f:
                    f.writelines(file_contents)
                f.close()
            except Exception as error:
                message = "Unable to save device log"
                self.status_text.configure(text=message, text_color="red")
                self.log.error("Failed to save device log: %s", error)
            else:
                self.log_popup.destroy()
                self.focus()
                if platform.system() == "Darwin":
                    subprocess.call(("open", log_file))
                elif platform.system() == "Windows":
                    os.startfile(log_file)
                else:
                    subprocess.call(("xdg-open", log_file))
        else:
            if self.log_path.get() == "":
                message = "You must specify a valid folder to save to"
            else:
                message = f"{self.log_path.get()} is not a valid directory"
            self.status_text.configure(text=message, text_color="red")

    def exception_handler(self, exc_type, exc_value, exc_traceback):
        """
        Handler for uncaught exceptions
        """
        message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        log_file = None
        for handler in self.log.parent.handlers:
            if handler.__class__.__name__ == "FileHandler":
                log_file = handler.baseFilename
        self.log.critical("Uncaught exception: %s", message)
        critical = CTkMessagebox(master=self, title="Error",
                                 message="EX-Installer experienced an unknown error, " +
                                 "please send the log file to the DCC-EX team for further analysis",
                                 icon="cancel", option_1="Show log", option_2="Exit",
                                 border_width=3, cancel_button=None)
        if critical.get() == "Show log":
            if platform.system() == "Darwin":
                subprocess.call(("open", log_file))
            elif platform.system() == "Windows":
                os.startfile(log_file)
            else:
                subprocess.call(("xdg-open", log_file))
        elif critical.get() == "Exit":
            sys.exit()
