"""
Module for a serial monitor interface

This allows for interaction with an Arduino device via the serial interface
"""

# Import Python modules
import customtkinter as ctk
import logging
from queue import Queue
import sys
from threading import Thread, Lock
import subprocess
from collections import namedtuple
import platform
from pprint import pprint

# Import local modules
from . import images

QueueMessage = namedtuple("QueueMessage", ["status", "data"])


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
            "<<Monitor>>": self.monitor
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
        self.monitor()

    def monitor_queue(self, queue, event):
        """
        Monitor the provided queue for status updates
        """
        while not queue.empty():
            item = queue.get()
            if item.status == "output" or item.status == "error":
                self.process_status = item.status
                self.process_data = item.data
                self.event_generate(f"<<{event}>>")
                return
        self.after(100, self.monitor_queue, queue, event)

    def monitor(self, event=None):
        """
        Function to monitor for serial output

        Requires a selected device to work:
        - Ensure device is selected
        - Ensure device is connected
        - Use the ArduinoCLI module with thread/queue to read output
        """
        self.command_button.configure(state="disabled")
        if self.acli.selected_device is not None:
            port = self.acli.detected_devices[self.acli.selected_device]['port']
            text = ("Monitoring " +
                    f"{self.acli.detected_devices[self.acli.selected_device]['matching_boards'][0]['name']} " +
                    f" on {port}")
            self.device_label.configure(text=text)
            self.process_phase = "monitor"
            self.monitor_queue(self.queue, "Monitor")
            params = ["monitor", "-p", port, "-c", "baudrate=115200"]
            self.monitor_thread = ThreadedSerialMonitor(self.acli.cli_file_path(), params, self.queue)
            self.monitor_thread.start()
        if self.process_phase == "monitor":
            print(type(self.process_data))
            pprint(self.process_data)
            if self.process_data:
                self.output_textbox.insert("insert", self.process_data)


class ThreadedSerialMonitor(Thread):
    """
    Class to run the serial monitor process in its own thread
    """
    monitor_lock = Lock()

    def __init__(self, acli_path, params, queue):
        """
        Initialise the monitor object
        """
        super().__init__()

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Start thread")

        # Set variables
        self.params = params
        self.process_params = [acli_path]
        self.process_params += self.params
        self.queue = queue

    def run(self, *args, **kwargs):
        """
        Override for Thread.run()

        Creates a thread and executes with the provided parameters

        Results are placed in the provided queue object
        """
        self.queue.put(
            QueueMessage("info", f"Arduino CLI parameters: {self.params}")
        )
        self.log.debug("Queue info %s", self.params)
        with self.monitor_lock:
            startupinfo = None
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            try:
                self.monitor_process = subprocess.Popen(self.process_params, stdout=subprocess.PIPE,
                                                        stderr=subprocess.PIPE, startupinfo=startupinfo)
            except Exception as error:
                self.queue.put(
                    QueueMessage("error", str(error))
                )
                self.log.error("Caught exception: %s", str(error))
            else:
                while True:
                    output = self.monitor_process.stdout.readline()
                    self.queue.put(
                        QueueMessage("output", output)
                    )
