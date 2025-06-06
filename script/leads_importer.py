import pandas as pd
import sys
import os

import requests

#
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from script.models.Lead import Lead
#
# csvs = pd.read_csv('../csv/csv/au_nz/below/below_20k_instagram_7.csv')
# print(len(csvs))

# for csv in csvs.values.tolist():
#     if not Lead.select().where(Lead.username == csv[0]).exists():
#         Lead.create(username=csv[0])

data = {"email": "mostafaaabedi", "password": "l7rXT5tKJ684rnqr6CcP"}
resp = requests.post('http://159.100.13.222/login', data=data)

print(resp.text)
