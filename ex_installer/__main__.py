"""
Main application controller

© 2023, Peter Cole.
© 2023, Harald Barth.
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
import logging
from datetime import datetime
import os
import argparse
import sys

# Import local modules
from ex_installer.ex_installer import EXInstaller
from ex_installer.file_manager import FileManager as fm


def main(debug, fake):
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

    # Do OS specific stuff for scaling and SSL
    if sys.platform == "darwin":
        pass  # high DPI scaling works automatically it is said
    elif sys.platform.startswith("win"):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # should turn on DPI scaling on Windows
    else:
        import customtkinter
        dpi = app.winfo_fpixels('1i')
        scaling = dpi/96  # 96 looks good
        if scaling < 1:
            scaling = 1  # we do not scale smaller because of dpi
        winheight = app.winfo_screenheight()
        winwidth = app.winfo_screenwidth()
        # check if window would fit into onto screen
        if winwidth > 200 and winwidth < scaling * 880:
            scaling = winwidth / 880
        if winheight > 150 and winheight < scaling * 660:
            scaling = winheight / 660
        # as scaling smaller does not work, just issue a warning and do not scale at all
        if scaling < 1:
            print("Warning: Not everything fits on screen")
        # check if we need to bother to scale
        if scaling > 1.1:
            customtkinter.set_widget_scaling(scaling)
            customtkinter.set_window_scaling(scaling)
    # switch to first view _after_ the scaling because of a bug in Linux that would unhide all hidden buttons
    app.switch_view("welcome")
    if fake is True:
        app.enable_fake_device()
    app.mainloop()
    _log.debug("EX-Installer closed")


if __name__ == "__main__":
    # Setup command line parser with debug argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-D", "--debug", action="store_true", help="Set debug log level")
    parser.add_argument("-F", "--fake", action="store_true", help="Enable fake Arduino device for demo purposes")

    # Read arguments
    args = parser.parse_args()

    # If debug supplied, pass that to our app
    if args.debug:
        debug = True
    else:
        debug = False

    # If fake supplied, pass it also
    if args.fake:
        fake = True
    else:
        fake = False

    # Start the app
    main(debug, fake)
