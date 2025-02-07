import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.models.Lead import Lead

import pandas as pd
from peewee import *
import requests
import certifi
import logging
import httpx
from bs4 import BeautifulSoup
import re
import zlib

# Send GET request to the website
lead = Lead.get_leads(1, category='copywriting')

print(lead)
print(lead[0])
print(lead[0].username)