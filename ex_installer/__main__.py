"""
Main application controller
"""

# Import Python modules
import logging
from datetime import datetime
import os

# Import local modules
from ex_installer.ex_installer import EXInstaller
from .file_manager import FileManager as fm


def main():
    log_name = datetime.now().strftime("%Y%m%d-%H%M%S.log")
    log_dir = fm.get_install_dir("logs")
    log_file = os.path.join(log_dir, log_name)
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception as error:
            logging.error(f"Could not create logging directory {str(error)}")
    _log = logging.getLogger(__name__)
    logging.basicConfig(filename=log_file, level=logging.INFO)
    _log.info("EX-Installer launched")
    app = EXInstaller()
    app.mainloop()
    _log.info("EX-Installer closed")


if __name__ == "__main__":
    main()
