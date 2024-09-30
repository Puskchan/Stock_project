import sys
from src.logger import logging
from src.exception import CustomException
from src.utils import mongo_db_connect, mongo_service

import pandas as pd

logging.info("Dataset creation starting....")

mongo_service('start')

db = mongo_db_connect('storage')
collection1 = db['articles']
collection2 = db['stocks']

def make_csv(collection,file_name):
    try:
        logging.info("Pushing data to CSV file..........")
        details = collection.find()
        df = pd.DataFrame(details).drop(['_id'], axis=1)
        df.to_csv(f'{file_name}.csv', index=False)
        logging.info("Pushing data to CSV file completed")
    except Exception as e:
        print("Making CSV file - Failed")
        raise CustomException(e,sys)


if __name__=="__main__":

    make_csv(collection=collection1, file_name="articles")
    make_csv(collection=collection2, file_name="stocks")

    mongo_service('stop')