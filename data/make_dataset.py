import os
from dotenv import load_dotenv
from src.logger import logging

import pandas as pd
from pymongo import MongoClient

# logging.info("Dataset creation starting....")

# Load env variables
load_dotenv()

# Database connection
MONGODB_CONNECTION_STRING=os.getenv('MONGODB_CONNECTION_STRING')

# Set up mongodb connection
client = MongoClient(MONGODB_CONNECTION_STRING)
# logging.info("Mongodb connection established")
db = client['storage']
collection1 = db['articles']
collection2 = db['stocks']
# logging.info("Database brought to local variable")

item_details = collection2.find({'symbol':'SBIN.NS'})


print(pd.DataFrame(item_details))