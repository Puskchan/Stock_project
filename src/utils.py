import os
import sys
import subprocess
from dotenv import load_dotenv
from src.logger import logging
from src.exception import CustomException
from pymongo import MongoClient

# Load env variables
load_dotenv()

# Getting the API key
SUDO=os.getenv('SUDO')
MONGODB_CONNECTION_STRING=os.getenv('MONGODB_CONNECTION_STRING')


# Start/Stop the mongodb service
def mongo_service(option='status'):
    try:
        command = f"echo {SUDO}| sudo -S systemctl {option} mongod"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        logging.info(f"Mongo DB {option} - {'No error' if result.stderr == '' else result.stderr}")
    except Exception as e:
        print(f"An error occurred while starting/stopping to mongo service: ")
        raise CustomException(e,sys)

# Set up mongodb connection
def mongo_db_connect(database):
    try:
        client = MongoClient(MONGODB_CONNECTION_STRING)
        logging.info("Mongodb connection established")
        db = client[database]
        logging.info("Database brought to local variable")
        return db
    except Exception as e:
        print(f"An error occurred while connecting to mongo database: ")
        raise CustomException(e,sys)