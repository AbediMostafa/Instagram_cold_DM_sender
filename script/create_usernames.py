import random

# Base words related to "mobleman", "choob", "zendegi" and their translations/related terms
keywords = [
    'mobleman', 'choob', 'zendegi',
    'wood', 'timber', 'oak', 'pine', 'maple',
    'furniture', 'sofa', 'chair', 'table', 'couch', 'desk',
    'life', 'living', 'home', 'decor', 'style', 'interior'
]

# Allowed characters: lowercase letters, digits, underscore, dot
chars = 'abcdefghijklmnopqrstuvwxyz0123456789._'

# Generate usernames
usernames = set()

while len(usernames) < 500:
    base = random.choice(keywords)
    # Add a random suffix or prefix
    if random.random() < 0.5:
        name = base + random.choice(['', '_', '.', str(random.randint(1, 9999))])
    else:
        name = random.choice(['', '_', '.', str(random.randint(1, 9999))]) + base

    # Randomly insert extra word/number
    if random.random() < 0.5:
        extra = random.choice(keywords)
        name = name + random.choice(['', '_', '.']) + extra

    # Ensure length < 30 and only allowed characters
    name = ''.join(c for c in name.lower() if c in chars)
    if 1 < len(name) < 30:
        usernames.add(name)

# Convert to list
username_list = sorted(usernames)

import pandas as pd

df = pd.DataFrame(username_list, columns=['username'])

import caas_jupyter_tools

caas_jupyter_tools.display_dataframe_to_user(name="Generated Instagram Usernames", dataframe=df)
