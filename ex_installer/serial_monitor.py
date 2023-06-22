"""
Module for a serial monitor interface

This allows for interaction with an Arduino device via the serial interface
"""

# Import Python modules
import customtkinter as ctk
import logging

# Import local modules
# from .common_widgets import WindowLayout


class SerialMonitor(ctk.CTkToplevel):
    """
    Class to define a window for the serial monitor
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set up logger
        self.log = logging.getLogger(__name__)
        self.log.debug("Open window")

        self.geometry("400x300")

        self.label = ctk.CTkLabel(self, text="Serial monitor")
        self.label.grid(column=0, row=0, sticky="nsew")
