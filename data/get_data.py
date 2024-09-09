import os
import sys
from dotenv import load_dotenv
from src.logger import logging
from src.exception import CustomException

import yfinance as yf
from pymongo import MongoClient
from newsapi import NewsApiClient


# Load env variables
load_dotenv()

# Getting the API key
NEWS_API_KEY=os.getenv('NEWS_API_KEY')
MONGODB_CONNECTION_STRING=os.getenv('MONGODB_CONNECTION_STRING')

# Set up mongodb connection
client = MongoClient(MONGODB_CONNECTION_STRING)
logging.info("Mongodb connection established")
db = client['storage']
collection1 = db['articles']
collection2 = db['stocks']
logging.info("Database brought to local variable")

# Setup news api client

newsapi = NewsApiClient(api_key=NEWS_API_KEY)
logging.info("News API connected")


# Get the Stocks

def fetch_stocks(symbols):
    stock_data = {}
    try:
        logging.info("Fetching stocks started.....")
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='2d')

            # Convert the DataFrame to a list of dictionaries
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
            
            stock_data[symbol] = data_list
        logging.info("Fetching stock completed!")

        return stock_data
    except Exception as e:
        print("An error occurred while fetching stock prices: ")
        raise CustomException(e,sys)


# Store the stocks

def store_stocks(stock_data):
    try:
        logging.info("Storing stocks initiated.....")
        for symbol, data_list in stock_data.items():
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
                
                # Insert the stock data, or update if it already exists
                result = collection2.update_one(
                    {'symbol': symbol, 'date': data_point['date']},  # Filter
                    {'$set': stock_doc},  # Update
                    upsert=True  # Insert if not exists
                )
        logging.info("Stock storing completed!")

    
    except Exception as e:
        print("An error occurred while storing stock data:")
        raise CustomException(e,sys)


def fetch_articles(stock_name):
    try:
        logging.info("Fetching articles started.....")
        article = newsapi.get_everything(q=f'{stock_name}',
                                         from_param='2024-09-02',
                                         to='2024-09-02',
                                         language='en',
                                         sort_by='relevancy',
                                         page_size=1,
                                         page=1)
        
        # Check the returned articles
        if article['status'] == 'ok' and article['totalResults'] > 0:
            logging.info("Fetching articles completed!")
            return article['articles']
        else:
            logging.info(f"No articles found. Status: {article['status']}")
            return None
        
    except Exception as e:
        print(f"An error occured while fetching articles:")
        raise CustomException(e,sys)

def store_articles(articles):
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

            result = collection1.update_one(
                {'url': article_doc['url']},
                {'$set': article_doc},
                upsert=True
            )
        logging.info("Article storing completed!")

    except Exception as e:
        print(f"An error occurred while storing articles:")
        raise CustomException(e,sys)


if __name__ == "__main__":

    # Making the dataset
    
    articles = fetch_articles("India")
    if articles:
        store_articles(articles)
    else:
        print('No articles fetched')


    stocks = fetch_stocks(['MSFT'])
    if stocks:
        store_stocks(stocks)
    else:
        print("No stocks fetched")