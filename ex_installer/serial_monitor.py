"""
Module for a serial monitor interface

This allows for interaction with an Arduino device via the serial interface
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

# Import local modules
from . import images


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
        button_font = ctk.CTkFont(family="Helvetica", size=13, weight="bold")
        instruction_font = ctk.CTkFont(family="Helvetica", size=14, weight="normal")

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
        self.command_label = ctk.CTkLabel(self.command_frame, text="Enter command:", font=instruction_font)
        self.command = ctk.StringVar(self)
        self.command_entry = ctk.CTkComboBox(self.command_frame, variable=self.command, values=self.command_history,
                                             command=self.send_command)
        self.command_entry.bind("<Return>", self.send_command)
        self.command_button = ctk.CTkButton(self.command_frame, text="Send", font=button_font, width=80,
                                            command=self.send_command)
        self.close_button = ctk.CTkButton(self.command_frame, text="Close", font=button_font, width=80,
                                          command=self.close_monitor)
        self.command_label.grid(column=0, row=0, sticky="w", **grid_options)
        self.command_entry.grid(column=1, row=0, sticky="ew", **grid_options)
        self.command_button.grid(column=2, row=0, sticky="e", pady=5)
        self.close_button.grid(column=3, row=0, sticky="e", **grid_options)

        # Create monitor frame widgets and layout frame
        self.output_textbox = ctk.CTkTextbox(self.monitor_frame, border_width=3, border_spacing=5,
                                             fg_color="#E5E5E5", border_color="#00A3B9")
        self.output_textbox.grid(column=0, row=0, sticky="nsew")

        # Create device frame widgets and layout
        self.device_label = ctk.CTkLabel(self.device_frame, text=None, font=instruction_font)
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
        Function to start the Arduino CLI in monitor mode

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
                self.output_textbox.insert("insert", f"Failed to open serial connection: {e}")
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
                    output = self.serial_port.readline().decode().strip()
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
        self.output_textbox.insert("insert", output + "\n")
        self.output_textbox.see("end")
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
        self.output_textbox.insert("insert", command_text + "\n")
        self.output_textbox.see("end")

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
