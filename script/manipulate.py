import requests
from spintax import spin
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.models.Category import Category

c =Category.select().where(Category.title == 'Cold DM Sam').first()

print(c.title)
