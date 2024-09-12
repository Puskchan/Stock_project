from src.logger import logging
from src.exception import CustomException
from src.settings import stocks_dict
from src.utils import mongo_db_connect, mongo_service

import pandas as pd

logging.info("Dataset creation starting....")

mongo_service('start')

db = mongo_db_connect('storage')
collection1 = db['articles']
collection2 = db['stocks']


logging.info("Pushing data to CSV file..........")
stock_details = collection2.find()
df = pd.DataFrame(stock_details).drop(['_id'], axis=1)
df.to_csv('stocks.csv', index=False)
logging.info("Pushing data to CSV file completed")


mongo_service('stop')