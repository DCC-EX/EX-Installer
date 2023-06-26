import subprocess
import platform
from threading import Thread
from pprint import pprint

port = "COM3"
cli = r"C:\Users\Peter\ex-installer\arduino-cli\arduino-cli.exe"
params = [cli, "monitor", "-p", port, "-c", "baudrate=115200"]

startupinfo = None
if platform.system() == "Windows":
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
monitor_process = subprocess.Popen(params, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   startupinfo=startupinfo)

# stdout, stderr = monitor_process.communicate()

for line in iter(monitor_process.stdout.readline, b""):
    print(line.decode("utf=8"), end="")

# monitor_thread = Thread(target=monitor_process.communicate())

# pprint(vars(monitor_thread))
