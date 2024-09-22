import os
import sys
import subprocess
from dotenv import load_dotenv
from src.logger import logging
from src.exception import CustomException
from pymongo import MongoClient

# Load env variables
load_dotenv()

# Validate required environment variables
def validate_env_variables() -> None:
    """
    Validates that all required environment variables are set.

    Raises:
        EnvironmentError: If any required environment variable is missing.
    """
    required_vars = ['SUDO', 'MONGODB_CONNECTION_STRING', 'NEWS_API_KEY']
    missing_vars = [var for var in required_vars if os.getenv(var) is None]
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Call the validation function at the start of the application
validate_env_variables()

# Getting the API key
SUDO=os.getenv('SUDO')
MONGODB_CONNECTION_STRING=os.getenv('MONGODB_CONNECTION_STRING')


# Start/Stop the mongodb service
def mongo_service(option: str = 'status') -> None:
    """
    Starts, stops, or checks the status of the MongoDB service.

    Args:
        option (str): The action to perform ('start', 'stop', or 'status').

    Raises:
        ValueError: If an invalid option is provided.
        CustomException: If an error occurs while executing the command.
    """
    if option not in ['start', 'stop', 'status']:
        raise ValueError("Invalid option. Choose 'start', 'stop', or 'status'.")
    
    try:
        command = f"echo {SUDO}| sudo -S systemctl {option} mongod"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        logging.info(f"Mongo DB {option} - {'No error' if result.stderr == '' else result.stderr}")
    except Exception as e:
        logging.error(f"An error occurred while {option} the MongoDB service: {str(e)}")
        raise CustomException(e, sys)

# Set up mongodb connection
def mongo_db_connect(database: str) -> MongoClient:
    """
    Establishes a connection to the specified MongoDB database.

    Args:
        database (str): The name of the database to connect to.

    Returns:
        MongoClient: The MongoDB client connected to the specified database.

    Raises:
        CustomException: If an error occurs while connecting to the database.
    """
    try:
        client = MongoClient(MONGODB_CONNECTION_STRING)
        logging.info("Mongodb connection established")
        db = client[database]
        logging.info("Database brought to local variable")
        return db
    except Exception as e:
        logging.error(f"An error occurred while connecting to mongo database: {str(e)}")
        raise CustomException(e, sys)