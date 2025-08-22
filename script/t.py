import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.extra.process.Process import Process

process = Process()

while True:
    process.start()
