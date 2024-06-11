"""
Module to define widgets used across the application

Every view should include this module and base the layout on WindowLayout

© 2024, Peter Cole.
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
import sys


class CommonFonts(ctk.CTkFont):
    """
    Class to define common fonts used across all application modules/classes
    """
    default_font = "Arial"

    if sys.platform.startswith("lin"):
        default_font = "FreeSans"

    def __init__(self, root):
        super().__init__(family=self.default_font)

        # Define fonts
        self.instruction_font = ctk.CTkFont(family=self.default_font,
                                            size=14,
                                            weight="normal")

        self.bold_instruction_font = ctk.CTkFont(family=self.default_font,
                                                 size=14,
                                                 weight="bold")

        self.italic_instruction_font = ctk.CTkFont(family=self.default_font,
                                                   size=14,
                                                   weight="normal",
                                                   slant="italic")

        self.large_bold_instruction_font = ctk.CTkFont(family=self.default_font,
                                                       size=16,
                                                       weight="bold")

        self.small_italic_instruction_font = ctk.CTkFont(family=self.default_font,
                                                         size=12,
                                                         weight="normal",
                                                         slant="italic")

        self.title_font = ctk.CTkFont(family=self.default_font,
                                      size=30,
                                      weight="normal")

        self.heading_font = ctk.CTkFont(family=self.default_font,
                                        size=24,
                                        weight="bold")

        self.button_font = ctk.CTkFont(family=self.default_font,
                                       size=13,
                                       weight="bold")

        self.action_button_font = ctk.CTkFont(family=self.default_font,
                                              size=16,
                                              weight="bold")
