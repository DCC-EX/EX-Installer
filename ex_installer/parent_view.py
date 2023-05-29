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
        self.main_frame = ctk.CTkFrame(self, width=790, height=380)
        self.next_back_frame = ctk.CTkFrame(self, width=790, height=40,
                                            fg_color="#00353D", border_width=0)
        self.status_frame = ctk.CTkFrame(self, width=790, height=100)

        # Configure weights
        self.title_frame.grid_columnconfigure(0, weight=1)
        self.title_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.next_back_frame.grid_columnconfigure(0, weight=1)
        self.next_back_frame.grid_rowconfigure(0, weight=1)
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_frame.grid_rowconfigure(0, weight=1)

        # Layout view
        self.title_frame.grid(column=0, row=0, padx=5, pady=2, sticky="nsew")
        self.main_frame.grid(column=0, row=1, padx=5, pady=(2, 0), sticky="nsew")
        self.next_back_frame.grid(column=0, row=2, padx=5, pady=(0, 2), sticky="nsew")
        self.status_frame.grid(column=0, row=3, padx=5, pady=2, sticky="nsew")
