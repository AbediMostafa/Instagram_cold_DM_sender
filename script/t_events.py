import random
import sys
import os

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.models.Setting import Setting
from script.models.Account import Account
from script.models.AccountHelper import get_next_account
import csv
import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

# Input and output file paths
input_csv = "noah - 50K.csv"  # Replace with your input CSV filename
output_csv = "instagram_usernames_only.csv"
max_retries = 3
max_threads = 500
timeout = 25  # Timeout in seconds for loading the website

def extract_instagram_username(url):
    for attempt in range(max_retries):
        try:
            # Send GET request to the website
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all <a> tags with href containing "instagram.com"
            instagram_links = soup.find_all("a", href=re.compile(r"(https?://)?(www\.)?instagram\.com/"))

            if instagram_links:
                # Extract Instagram username from the first valid link
                for link in instagram_links:
                    href = link.get('href')
                    if href:
                        # Clean up the URL to extract the username
                        username = re.sub(r"(https?://)?(www\.)?instagram\.com/", "", href).split('/')[0]
                        username = username.split('?')[0]  # Remove query parameters if any
                        return username
            return None
        except Exception as e:
            print(f"Error processing {url} (Attempt {attempt + 1}): {e}")
            sleep(1)  # Wait before retrying
    return None

def process_website(row):
    website = row.get('Website')  # Adjust the column name if needed
    if website:
        username = extract_instagram_username(website)
        print(f"Website: {website}, Instagram: {username}")
        return username
    return None

# Read the input CSV and process websites using multithreading
def scrape_instagram_usernames(input_csv, output_csv):
    usernames = []

    with open(input_csv, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

        with ThreadPoolExecutor(max_threads) as executor:
            future_to_row = {executor.submit(process_website, row): row for row in rows}
            for future in as_completed(future_to_row):
                username = future.result()
                if username:
                    usernames.append(username)

    # Write usernames to the output CSV
    with open(output_csv, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["Instagram Username"])  # Header
        for username in usernames:
            writer.writerow([username])

    print(f"Instagram usernames have been saved to {output_csv}")

# Run the scraper
scrape_instagram_usernames(input_csv, output_csv)
