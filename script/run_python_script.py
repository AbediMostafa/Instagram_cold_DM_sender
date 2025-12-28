# insert_usernames_only.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from script.models.Account import Account
from script.models.Lead import Lead

import datetime
from peewee import *

SQL_FILE = r"C:\Users\M\Desktop\Mostafa\programming\projects\ebrahim_cold_dm\instagram_dm_sender_2025-09-17.sql"  # Update path if needed

def get_usernames_from_sql(file_path):
    """Generator: yields only usernames from the COPY block."""
    with open(file_path, 'r', encoding='utf-8') as f:
        in_copy_block = False
        print("Reading SQL file and searching for leads data...")

        for line in f:
            line = line.strip()

            if line.startswith('COPY public.leads'):
                in_copy_block = True
                print("Found leads data — extracting usernames...")
                continue

            if in_copy_block and line == '\\.':
                print("Finished reading leads data.")
                break

            if not in_copy_block or not line:
                continue

            fields = line.split('\t')

            if len(fields) > 2:
                username = fields[2]
                if username != '\\N' and username:  # Skip null usernames
                    yield username.strip()


def insert_usernames(limit=None):
    total = 0
    created = 0
    skipped = 0

    for username in get_usernames_from_sql(SQL_FILE):
        total += 1

        if limit and total > limit:
            break

        try:
            # Check if username already exists
            if Lead.select().where(Lead.username == username).exists():
                skipped += 1
            else:
                Lead.create(
                    username=username,
                    instagram_id=None,
                    times=0,
                    last_state='free',
                    account=None,
                    category=None,
                    last_command_send_date=None
                )
                created += 1

            if total % 1000 == 0:
                print(f"Processed {total} lines → {created} new leads added, {skipped} duplicates skipped")

        except Exception as e:
            print(f"Error inserting '{username}': {e}")
            skipped += 1

    print("\n=== DONE ===")
    print(f"Total usernames processed: {total}")
    print(f"Successfully added: {created}")
    print(f"Skipped (already exist or error): {skipped}")


if __name__ == "__main__":
    print("=== TEST: Inserting first 10 usernames only ===")
    insert_usernames(limit=10)

    print("\nCheck your database: Are the 10 new leads with correct usernames added?")
    answer = input("\nLooks good? Import ALL usernames now? (yes/no): ")

    if answer.strip().lower() in ['yes', 'y']:
        print("\nStarting full import of all ~300k usernames...")
        insert_usernames(limit=None)
        print("Full import completed!")
    else:
        print("Stopped. You can run the script again later.")