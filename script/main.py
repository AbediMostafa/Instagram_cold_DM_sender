import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import subprocess
import sys
from script.models.Process import Process


def run_background_script():
    # Define the path to the background script
    background_script = "C:\\Users\\Administrator\\Desktop\\project\\script\\t.py"

    # Run the background script in the background
    process = subprocess.Popen(
        [sys.executable, background_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    Process.create(pid=process.pid)


if __name__ == "__main__":
    run_background_script()
    print("Background script started!")
