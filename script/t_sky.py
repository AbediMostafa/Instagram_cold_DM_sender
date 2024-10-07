import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.models.Lead import Lead

import pandas as pd
from peewee import *


relative_path = '../csv/csv/de_fr_it_es_fi_no_se/below/below_20k_instagram_2.csv'
# relative_path = '../csv/csv/au_nz/above/above_20k_instagram_1.csv'
absolute_path = os.path.abspath(relative_path)

df = pd.read_csv(absolute_path)
usernames = df.iloc[:, 0]

for username in usernames:
    if not Lead.select().where(Lead.username == username).exists():
        Lead.create(username=username)
