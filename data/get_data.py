import os
import sys
import subprocess
from dotenv import load_dotenv
from src.logger import logging
from src.exception import CustomException

import yfinance as yf
from pymongo import MongoClient
from newsapi import NewsApiClient


# Load env variables
load_dotenv()


# Getting the API key
SUDO=os.getenv('SUDO')
NEWS_API_KEY=os.getenv('NEWS_API_KEY')
MONGODB_CONNECTION_STRING=os.getenv('MONGODB_CONNECTION_STRING')


# Start the mongodb service
command = f"echo {SUDO}| sudo -S systemctl start mongod"
result = subprocess.run(command, shell=True, capture_output=True, text=True)

logging.info(f"Mongo DB starting - {result.stderr}")


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

def fetch_stocks(symbol, period='1y'):
    stock_data = [symbol]
    try:
        logging.info("Fetching stocks started.....")
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

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
            
        stock_data.append(data_list)
        logging.info("Fetching stock completed!")

        return stock_data
    except Exception as e:
        print("An error occurred while fetching stock prices: ")
        raise CustomException(e,sys)


# Store the stocks

def store_stocks(stock_data):
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


def fetch_articles(stock_name, from_date, to_date, no_of_articles):
    try:
        logging.info("Fetching articles started.....")
        article = newsapi.get_everything(q=f'{stock_name}',
                                         from_param=from_date,
                                         to=to_date,
                                         language='en',
                                         sort_by='relevancy',
                                         page_size=no_of_articles,
                                         page=1)
        
        # Check the returned articles
        if article['status'] == 'ok' and article['totalResults'] > 0:
            logging.info("Fetching articles completed!")
            return article['articles']
        else:
            logging.info(f"No articles found for {stock_name}. Status: {article['status']}")
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

    stocks_dict = {'Asian Paints': 'ASIANPAINT.NS', 'Britannia': 'BRITANNIA.NS', 'Cipla': 'CIPLA.NS', 
               'Eicher Motors': 'EICHERMOT.NS', 'Nestle India': 'NESTLEIND.NS', 'Grasim': 'GRASIM.NS', 
               'Hero MotoCorp': 'HEROMOTOCO.NS', 'Hindalco': 'HINDALCO.NS', 'Hindustan Unilever': 'HINDUNILVR.NS', 
               'ITC': 'ITC.NS', 'Larsen & Toubro': 'LT.NS', 'Mahindra & Mahindra': 'M&M.NS', 
               'Reliance': 'RELIANCE.NS', 'Tata Consumer Products': 'TATACONSUM.NS', 
               'Tata Motors': 'TATAMOTORS.NS', 'Tata Steel': 'TATASTEEL.NS', 'Wipro': 'WIPRO.NS', 
               'Apollo Hospitals Enterprise': 'APOLLOHOSP.NS', 'Dr Reddys Laboratories': 'DRREDDY.NS', 
               'Titan Company': 'TITAN.NS', 'State Bank of India': 'SBIN.NS', 'Shriram Finance': 'SHRIRAMFIN.NS', 
               'Bharat Petroleum Corporation': 'BPCL.NS', 'Kotak Mahindra Bank': 'KOTAKBANK.NS', 'Infosys': 'INFY.NS', 
               'Bajaj Finance': 'BAJFINANCE.NS', 'Adani Enterprises': 'ADANIENT.NS', 
               'Sun Pharmaceuticals': 'SUNPHARMA.NS', 'JSW Steel': 'JSWSTEEL.NS', 'HDFC Bank': 'HDFCBANK.NS', 
               'Tata Consultancy Services': 'TCS.NS', 'ICICI Bank': 'ICICIBANK.NS', 
               'Power Grid Corporation of India': 'POWERGRID.NS', 'Maruti Suzuki India': 'MARUTI.NS', 
               'IndusInd Bank': 'INDUSINDBK.NS', 'Axis Bank': 'AXISBANK.NS', 'HCL Technologies': 'HCLTECH.NS', 
               'Oil & Natural Gas Corporation': 'ONGC.NS', 'NTPC': 'NTPC.NS', 'Coal India': 'COALINDIA.NS', 
               'Bharti Airtel': 'BHARTIARTL.NS', 'Tech Mahindra': 'TECHM.NS', 'LTIMindtree': 'LTIM.NS', 
               'Divis Laboratories': 'DIVISLAB.NS', 'Adani Ports & Special Economic Zone': 'ADANIPORTS.NS', 
               'HDFC Life Insurance Company': 'HDFCLIFE.NS', 'SBI Life Insurance Company': 'SBILIFE.NS', 
               'UltraTech Cement': 'ULTRACEMCO.NS', 'Bajaj Auto': 'BAJAJ-AUTO.NS', 'Bajaj Finserv': 'BAJFINANCE.NS'
               }

    # Downloading the raw data to database

    for company_name, company_stock in stocks_dict.items():
        
        # articles = fetch_articles(company_name, from_date='2024-08-11', to_date='2024-08-11', no_of_articles=10)
        # if articles:
        #     store_articles(articles)
        # else:
        #     logging.info("No articles fetched")


        stocks = fetch_stocks(company_stock, period='5y')
        if stocks:
            store_stocks(stocks)
        else:
            logging.info("No stocks fetched")

    
    command = f"echo {SUDO}| sudo -S systemctl stop mongod"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    logging.info(f"Mongo DB stopping - {result.stderr}")