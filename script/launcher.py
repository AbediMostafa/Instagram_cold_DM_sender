import subprocess
import time
import argparse
import os

# Get the directory where launcher.py is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='Launch multiple CMD windows')
parser.add_argument('--count', type=int, default=10, help='Number of CMD windows (default: 10)')
parser.add_argument('--delay', type=float, default=0.5, help='Delay between launches in seconds (default: 0.5)')
parser.add_argument('--path', type=str, default=SCRIPT_DIR, help='Script path')
parser.add_argument('--script', type=str, default='t.py', help='Python script name (default: t.py)')

args = parser.parse_args()


print(f"Starting {args.count} CMD windows...")
print(f"Path: {args.path}")
print(f"Script: {args.script}")
print("-" * 40)

for i in range(args.count):
    subprocess.Popen(
        ['cmd', '/k', f'cd /d {args.path} && python {args.script}'],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print(f"Started {i+1}/{args.count}")
    time.sleep(args.delay)

print("-" * 40)
print(f"Done! {args.count} windows opened.")