import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.extra.process.Process import Process
from script.ProcessManager import ProcessManager

# process = Process()
#
# while True:
#     process.start()
#
process = ProcessManager()

while True:
    process.run()
    time.sleep(2)

# Your reel has been shared.
