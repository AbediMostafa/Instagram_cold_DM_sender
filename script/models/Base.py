from peewee import *
from script.extra.config import *
from dotenv import load_dotenv
import os

load_dotenv()

# Get the values from environment variables
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
host = os.getenv('POSTGRES_HOST')
port = int(os.getenv('POSTGRES_PORT'))
database_name = os.getenv('POSTGRES_DB')

# Set up the database connection
database = PostgresqlDatabase(
    database_name,
    user=user,
    password=password,
    host=host,
    port=port,
)

database.connect()


class BaseModel(Model):
    class Meta:
        database = database
