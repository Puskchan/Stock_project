import os
import sys
from dotenv import load_dotenv
from src.logger import logging
from src.exception import CustomException
from src.settings import stocks_dict
from src.utils import mongo_db_connect, mongo_service

import yfinance as yf
from newsapi import NewsApiClient

# Start MongoDB service
mongo_service('start')

# Load the News API key from environment variables
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# Connect to the MongoDB database and define collections for articles and stocks
db = mongo_db_connect('storage')
collection1 = db['articles']
collection2 = db['stocks']

# Initialize the News API client
newsapi = NewsApiClient(api_key=NEWS_API_KEY)
logging.info("News API connected")

# Function to fetch historical stock data
def fetch_stocks(symbol: str, period: str = '1y') -> list:
    """
    Fetch historical stock data for a given symbol over a specified period.

    Args:
        symbol (str): The stock symbol to fetch data for.
        period (str): The period for which to fetch historical data (default is '1y').

    Returns:
        list: A list containing the stock symbol and its historical data.
    """
    stock_data = [symbol]
    try:
        logging.info("Fetching stocks started.....")
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

        # Convert the DataFrame to a list of dictionaries for easier processing
        data_list = []
        for index, row in hist.iterrows():
            data_list.append({
                'date': index.to_pydatetime(),
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': row['Volume']
            })
            
        stock_data.append(data_list)
        logging.info("Fetching stock completed!")

        return stock_data
    except Exception as e:
        print("An error occurred while fetching stock prices: ")
        raise CustomException(e, sys)

# Function to store stock data in the database
def store_stocks(stock_data: list) -> None:
    """
    Store stock data in the database.

    Args:
        stock_data (list): A list containing the stock symbol and its historical data.
    """
    try:
        logging.info("Storing stocks initiated.....")
        symbol, data_list = stock_data[0], stock_data[1]
        for data_point in data_list:
            stock_doc = {
                'symbol': symbol,
                'date': data_point['date'],
                'open': data_point['open'],
                'high': data_point['high'],
                'low': data_point['low'],
                'close': data_point['close'],
                'volume': data_point['volume']
            }
            
            # Insert or update the stock data in the database
            result = collection2.update_one(
                {'symbol': symbol, 'date': data_point['date']},  # Filter for existing records
                {'$set': stock_doc},  # Update the record
                upsert=True  # Insert if the record does not exist
            )
        logging.info("Stock storing completed!")

    except Exception as e:
        print("An error occurred while storing stock data:")
        raise CustomException(e, sys)

# Function to fetch articles related to a specific stock
def fetch_articles(stock_name: str, from_date: str, to_date: str, no_of_articles: int) -> list:
    """
    Fetch articles related to a specific stock within a date range.

    Args:
        stock_name (str): The name of the stock to fetch articles for.
        from_date (str): The start date for fetching articles.
        to_date (str): The end date for fetching articles.
        no_of_articles (int): The number of articles to fetch.

    Returns:
        list: A list of articles related to the stock.
    """
    try:
        logging.info("Fetching articles started.....")
        article = newsapi.get_everything(q=f'{stock_name}',
                                         from_param=from_date,
                                         to=to_date,
                                         language='en',
                                         sort_by='relevancy',
                                         page_size=no_of_articles,
                                         page=1)
        
        # Check if articles were successfully fetched
        if article['status'] == 'ok' and article['totalResults'] > 0:
            logging.info("Fetching articles completed!")
            return article['articles']
        else:
            logging.info(f"No articles found for {stock_name}. Status: {article['status']}")
            return None
        
    except Exception as e:
        print(f"An error occurred while fetching articles:")
        raise CustomException(e, sys)

# Function to store articles in the database
def store_articles(articles: list) -> None:
    """
    Store articles in the database.

    Args:
        articles (list): A list of articles to store.
    """
    try:
        logging.info("Storing articles initiated.....")
        for article in articles:
            article_doc = {
                'title': article.get('title'),
                'author': article.get('author'),
                'description': article.get('description'),
                'url': article.get('url'),
                'urlToImage': article.get('urlToImage'),
                'publishedAt': article.get('publishedAt'),
                'content': article.get('content'),
                'source': article.get('source'),
            }

            # Insert or update the article in the database
            result = collection1.update_one(
                {'url': article_doc['url']},  # Filter for existing articles
                {'$set': article_doc},  # Update the article
                upsert=True  # Insert if the article does not exist
            )
        logging.info("Article storing completed!")

    except Exception as e:
        print("An error occurred while storing articles:")
        raise CustomException(e, sys)

# Main execution block
if __name__ == "__main__":

    # Downloading the raw data to the database for each company
    for company_name, company_stock in stocks_dict.items():
        
        # Uncomment to fetch and store articles
        # articles = fetch_articles(company_name, from_date='2024-08-11', to_date='2024-08-11', no_of_articles=10)
        # if articles:
        #     store_articles(articles)
        # else:
        #     logging.info("No articles fetched")

        # Fetch and store stock data
        stocks = fetch_stocks(company_stock, period='5y')
        if stocks:
            store_stocks(stocks)
        else:
            logging.info("No stocks fetched")

    # Stop the MongoDB service
    mongo_service('stop')