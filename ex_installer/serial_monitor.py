"""
Module for a serial monitor interface

This allows for interaction with an Arduino device via the serial interface
"""

# Import Python modules
import customtkinter as ctk
import logging
from queue import Queue
import sys

# Import local modules
from . import images


class SerialMonitor(ctk.CTkToplevel):
    """
    Class to define a window for the serial monitor
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Define icon bitmap, must delay due to CTkToplevel bug
        if sys.platform.startswith("win"):
            self.after(250, lambda: self.iconbitmap(images.DCC_EX_ICON_ICO))
        self.title("Serial monitor")

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Open window")

        # Set up event handlers
        event_callbacks = {
            "<<Monitor>>": self.serial_monitor
        }
        for sequence, callback in event_callbacks.items():
            self.bind_class("bind_events", sequence, callback)
        new_tags = self.bindtags() + ("bind_events",)
        self.bindtags(new_tags)

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
        self.geometry("800x500")
        self.minsize(width=800, height=500)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.window_frame = ctk.CTkFrame(self)
        self.window_frame.grid_columnconfigure(0, weight=1)
        self.window_frame.grid_rowconfigure(1, weight=1)
        self.window_frame.grid(column=0, row=0, sticky="nsew")

        # Define fonts for use
        button_font = ctk.CTkFont(family="Helvetica", size=13, weight="bold")
        instruction_font = ctk.CTkFont(family="Helvetica", size=14, weight="normal")

        # Create and configure command and monitor frames
        self.command_frame = ctk.CTkFrame(self.window_frame, width=790, height=40)
        self.monitor_frame = ctk.CTkFrame(self.window_frame, width=790, height=420)
        self.device_frame = ctk.CTkFrame(self.window_frame, width=790, height=40)
        self.command_frame.grid_columnconfigure(1, weight=1)
        self.command_frame.grid_rowconfigure(0, weight=1)
        self.monitor_frame.grid_columnconfigure(0, weight=1)
        self.monitor_frame.grid_rowconfigure(0, weight=1)
        self.device_frame.grid_columnconfigure(0, weight=1)
        self.device_frame.grid_rowconfigure(0, weight=1)
        self.command_frame.grid(column=0, row=0, sticky="nsew", padx=5, pady=(5, 0))
        self.monitor_frame.grid(column=0, row=1, sticky="nsew", padx=5, pady=2)
        self.device_frame.grid(column=0, row=2, sticky="nsew", padx=5, pady=(0, 5))

        # Create command frame widgets and layout frame
        grid_options = {"padx": 5, "pady": 5}
        self.command_label = ctk.CTkLabel(self.command_frame, text="Enter command:", font=instruction_font)
        self.command = ctk.StringVar(self)
        self.command_entry = ctk.CTkEntry(self.command_frame, textvariable=self.command)
        self.command_button = ctk.CTkButton(self.command_frame, text="Send", font=button_font)
        self.command_label.grid(column=0, row=0, sticky="w", **grid_options)
        self.command_entry.grid(column=1, row=0, sticky="ew", pady=5)
        self.command_button.grid(column=2, row=0, sticky="e", **grid_options)

        # Create monitor frame widgets and layout frame
        self.output_textbox = ctk.CTkTextbox(self.monitor_frame, border_width=3, border_spacing=5,
                                             fg_color="#E5E5E5", border_color="#00A3B9")
        self.output_textbox.grid(column=0, row=0, sticky="nsew")

        # Create device frame widgets and layout
        self.device_label = ctk.CTkLabel(self.device_frame, text=None, font=instruction_font)
        self.device_label.grid(column=0, row=0, sticky="ew", padx=5, pady=5)

        # Start serial monitor process
        self.serial_monitor()

    def monitor_queue(self, queue, event):
        """
        Monitor the provided queue for status updates
        """
        while not queue.empty():
            item = queue.get()
            if item.status == "success" or item.status == "error":
                self.process_status = item.status
                self.process_topic = item.topic
                self.process_data = item.data
                self.event_generate(f"<<{event}>>")
                return
        self.after(100, self.monitor_queue, queue, event)

    def serial_monitor(self, event=None):
        """
        Function to monitor for serial output

        Requires a selected device to work:
        - Ensure device is selected
        - Ensure device is connected
        - Use the ArduinoCLI module with thread/queue to read output
        """
        if self.acli.selected_device is not None:
            port = self.acli.detected_devices[self.acli.selected_device]['port']
            text = ("Monitoring " +
                    f"{self.acli.detected_devices[self.acli.selected_device]['matching_boards'][0]['name']} " +
                    f" on {port}")
            self.device_label.configure(text=text)
            self.acli.monitor(self.acli.cli_file_path(), port, 115200, self.queue)
            self.process_phase = "monitor"
            self.monitor_queue(self.queue, "Monitor")
        else:
            pass
        if self.process_phase == "monitor":
            print(self.process_data)
            # self.output_textbox.insert("insert", self.process_data)
