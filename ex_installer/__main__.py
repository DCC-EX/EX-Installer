"""
Main application controller
"""

# Import Python modules
import logging
from datetime import datetime
import os
import argparse
import sys

# Import local modules
from ex_installer.ex_installer import EXInstaller
from ex_installer.file_manager import FileManager as fm


def main(debug):
    """
    Main function to start the application
    """

    # Set up logger
    log_name = datetime.now().strftime("ex-installer-%Y%m%d-%H%M%S.log")
    log_dir = fm.get_install_dir("logs")
    log_file = os.path.join(log_dir, log_name)
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception as error:
            logging.error(f"Could not create logging directory {str(error)}")
    _log = logging.getLogger(__name__)
    if debug:
        logging.basicConfig(filename=log_file,
                            datefmt="%Y-%m-%d %H:%M:%S",
                            format="%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(funcName)s: - %(message)s",
                            level=logging.DEBUG)
    else:
        logging.basicConfig(filename=log_file,
                            datefmt="%Y-%m-%d %H:%M:%S",
                            format="%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
                            level=logging.WARNING)

    # Start the app
    _log.debug("EX-Installer launched")
    app = EXInstaller()
    if sys.platform == "darwin":
        pass  # high DPI scaling works automatically it is said
    elif sys.platform.startswith("win"):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # should turn on DPI scaling on Windows
    else:
        import customtkinter
        dpi = app.winfo_fpixels('1i')
        customtkinter.set_widget_scaling(dpi/72)
        customtkinter.set_window_scaling(dpi/72)
    app.mainloop()
    _log.debug("EX-Installer closed")


if __name__ == "__main__":
    # Setup command line parser with debug argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-D", "--debug", action="store_true", help="Set debug log level")

    # Read arguments
    args = parser.parse_args()

    # If debug supplied, pass that to our app
    if args.debug:
        debug = True
    else:
        debug = False

    # Start the app
    main(debug)
