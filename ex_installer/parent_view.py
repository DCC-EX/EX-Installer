"""
Module to define the view layout to inherit for all views
"""

import customtkinter as ctk


class ParentView(ctk.CTkFrame):
    """
    Class to define the template for all views
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Define top level frames
        self.title_frame = ctk.CTkFrame(self, width=790, height=80)
        self.main_frame = ctk.CTkFrame(self, width=790, height=400)
        self.status_frame = ctk.CTkFrame(self, width=790, height=100)

        # Configure layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1, 2), weight=1)

        self.title_frame.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")
        self.main_frame.grid(column=0, row=1, padx=5, pady=5, sticky="nsew")
        self.status_frame.grid(column=0, row=2, padx=5, pady=5, sticky="nsew")

        # Define next/back button frame
        self.next_back_frame = ctk.CTkFrame(self.main_frame, width=780, height=40, fg_color="#00353D")

        # Layout frame
        # self.main_frame.columnconfigure(0, weight=1)
        # self.main_frame.rowconfigure(0, weight=1)

        # self.next_back_frame.grid(column=0, row=100, sticky="s")
