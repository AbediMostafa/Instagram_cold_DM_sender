import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from script.models.Account import Account
# from script.models.Lead import Lead

import pandas as pd
import csv
import sys

count = 0

csv.field_size_limit(10 ** 7)

input_file = r"C:\Users\M\Downloads\Telegram Desktop\l\l.csv"
output_file = r"C:\Users\M\Downloads\Telegram Desktop\l\final.csv"

with open(input_file, mode="r", encoding="utf-8") as infile, open(output_file, mode="w", encoding="utf-8",
                                                                  newline="") as outfile:
    reader = csv.DictReader(infile)  # Read input as a dictionary
    writer = csv.writer(outfile)  # Write to output CSV

    for row in reader:
        count += 1
        country_code = row.get("country_code", "").strip()
        instagram = row.get("instagram", "")
        platform = row.get("platform", "")

        if country_code in ("US", "GB") and instagram and platform == 'Shopify':
            writer.writerow([instagram, country_code, platform])

print(count)
