import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Debug prints
print(f"PID: {os.getpid()}")
print(f"SERVER_IP from env: {os.getenv('SERVER_IP')}")

from script.models.Process import Process

print(f"SERVER_IP from Process: {Process.get_server_ip()}")

# Now run
from script.ProcessManager import ProcessManager

process = ProcessManager()

while True:
    process.run()