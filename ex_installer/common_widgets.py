"""
Module to define widgets used across the application

Every view should include this module and base the layout on WindowLayout
"""

# Import Python modules
import customtkinter as ctk
from PIL import Image
from queue import Queue

# Import local modules
from . import images


class WindowLayout(ctk.CTkFrame):
    """
    Class to define the window layout

    All views must inherit from this
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Get parent Arduino CLI and Git client instances
        self.acli = parent.acli
        self.git = parent.git

        # Variables for process and queue monitoring
        self.process_phase = None
        self.process_status = None
        self.process_topic = None
        self.process_data = None

        # Set up queue for process monitoring
        self.queue = Queue()

        # Variable for storing widget states while processes run
        self.widget_states = []

        # Define fonts
        self.instruction_font = ctk.CTkFont(family="Helvetica",
                                            size=14,
                                            weight="normal")
        self.bold_instruction_font = ctk.CTkFont(family="Helvetica",
                                                 size=14,
                                                 weight="bold")
        self.title_font = ctk.CTkFont(family="Helvetica",
                                      size=30,
                                      weight="normal")
        self.heading_font = ctk.CTkFont(family="Helvetica",
                                        size=24,
                                        weight="bold")
        self.button_font = ctk.CTkFont(family="Helvetica",
                                       size=13,
                                       weight="bold")
        self.action_button_font = ctk.CTkFont(family="Helvetica",
                                              size=16,
                                              weight="bold")

        # Define top level frames
        self.title_frame = ctk.CTkFrame(self, width=790, height=80)
        self.main_frame = ctk.CTkFrame(self, width=790, height=450)
        self.status_frame = ctk.CTkFrame(self, width=790, height=50)

        # Configure column/row weights for nice resizing
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1, minsize=450)
        self.grid_rowconfigure(2, weight=1)

        # Layout view
        self.title_frame.grid(column=0, row=0, padx=5, pady=2, sticky="nsew")
        self.main_frame.grid(column=0, row=1, padx=5, pady=2, sticky="nsew")
        self.status_frame.grid(column=0, row=2, padx=5, pady=2, sticky="nsew")

        # Setup frame weights
        self.title_frame.grid_columnconfigure(0, weight=1)
        self.title_frame.grid_columnconfigure(1, weight=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_frame.grid_rowconfigure((0, 1), weight=1)

        # Setup title frame
        self.title_logo_label = ctk.CTkLabel(self.title_frame, text=None)
        self.title_logo_label.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.title_label = ctk.CTkLabel(self.title_frame, text=None, font=self.title_font)
        self.title_label.grid(column=1, row=0, padx=5, pady=5, sticky="w")

        # Setup next/back frame
        self.next_back = NextBack(self.main_frame, height=40,
                                  fg_color="#00353D", border_width=0)
        self.next_back.grid(column=0, row=1, sticky="sew")

        # Setup status frame and widgets
        self.status_label = ctk.CTkLabel(self.status_frame, text="Idle",
                                         font=self.instruction_font, wraplength=780)
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, width=780, height=20,
                                               mode="indeterminate", orientation="horizontal")

        # Layout status frame
        self.status_label.grid(column=0, row=0, padx=5, pady=5)
        self.progress_bar.grid(column=0, row=1, padx=5, pady=5)
        self.process_stop()

    def set_title_logo(self, logo):
        """
        Function to update the title logo

        Call and pass a logo as defined in the images module
        """
        self.title_logo = Image.open(logo)
        self.title_image = ctk.CTkImage(light_image=self.title_logo, size=(200, 40))
        self.title_logo_label.configure(image=self.title_image)

    def set_title_text(self, text):
        """
        Function to update the title text
        """
        self.title_label.configure(text=text)

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

    def process_start(self, next_phase, activity, event):
        """
        Starts a background process that requires monitoring and a progress bar
        """
        self.process_phase = next_phase
        self.status_label.configure(text=activity, text_color="#00353D")
        self.monitor_queue(self.queue, event)
        self.progress_bar.start()

    def process_stop(self):
        """
        Stops the progress bar and resets status text
        """
        self.progress_bar.stop()
        self.status_label.configure(text="Idle")
        self.process_phase = None

    def process_error(self, message):
        """
        Stops the progress bar, sets status text, and makes font red
        """
        self.progress_bar.stop()
        self.status_label.configure(text=message, text_color="red")
        self.process_phase = None

    def disable_input_states(self, widget):
        """
        Stores current state of all child input widgets then sets to disabled
        """
        children = widget.winfo_children()
        for child in children:
            if isinstance(child, (ctk.CTkButton, ctk.CTkComboBox, ctk.CTkCheckBox, ctk.CTkEntry,
                                  ctk.CTkRadioButton, ctk.CTkSwitch, ctk.CTkTextbox)):
                widget_state = {
                    "widget": child,
                    "state": child.cget("state")
                }
                self.widget_states.append(widget_state)
                child.configure(state="disabled")
            self.disable_input_states(child)

    def restore_input_states(self):
        """
        Restores the state of all widgets
        """
        for widget in self.widget_states:
            widget["widget"].configure(state=widget["state"])

    @staticmethod
    def get_exception(error):
        """
        Get an exception into text to add to the queue
        """
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(error).__name__, error.args)
        return message


class NextBack(ctk.CTkFrame):
    """
    Class for defining and managing the next and back buttons
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Create the next/back button frame with buttons
        """
        super().__init__(parent, *args, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        button_font = ctk.CTkFont(family="Helvetica", size=14, weight="bold")
        button_options = {"width": 220, "height": 30, "font": button_font}

        self.back_arrow = Image.open(images.BACK_ARROW)
        self.back_arrow_image = ctk.CTkImage(light_image=self.back_arrow, size=(15, 15))
        self.back_button = ctk.CTkButton(self, image=self.back_arrow_image,
                                         text="Back", compound="left",
                                         anchor="w",
                                         **button_options)

        self.next_arrow = Image.open(images.NEXT_ARROW)
        self.next_arrow_image = ctk.CTkImage(light_image=self.next_arrow, size=(15, 15))
        self.next_button = ctk.CTkButton(self, image=self.next_arrow_image,
                                         text="Next", compound="right",
                                         anchor="e",
                                         **button_options)

        self.back_button.grid(column=0, row=0, padx=3, pady=3, sticky="w")
        self.next_button.grid(column=1, row=0, padx=3, pady=3, sticky="e")

    def set_back_text(self, text):
        """Update back button text"""
        self.back_button.configure(text=text)

    def disable_back(self):
        """Disable back button"""
        self.back_button.configure(state="disabled")

    def enable_back(self):
        """Enable back button"""
        self.back_button.configure(state="normal")

    def hide_back(self):
        """Hide back button"""
        self.back_button.grid_remove()

    def show_back(self):
        """Show back button"""
        self.back_button.grid()

    def set_back_command(self, command):
        self.back_button.configure(command=command)

    def set_next_text(self, text):
        """Update next button text"""
        self.next_button.configure(text=text)

    def disable_next(self):
        """Disable next button"""
        self.next_button.configure(state="disabled")

    def enable_next(self):
        """Enable next button"""
        self.next_button.configure(state="normal")

    def hide_next(self):
        """Hide next button"""
        self.next_button.grid_remove()

    def show_next(self):
        """Show next button"""
        self.next_button.grid()

    def set_next_command(self, command):
        self.next_button.configure(command=command)
