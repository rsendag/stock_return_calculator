import yfinance as yf



from datetime import datetime, timedelta
import pandas as pd
#can get the market cap only 
def get_market_cap_date(stk, date):
    # Parse the string into a datetime object
    date_obj = datetime.strptime(date, "%Y-%m-%d")

    # Extract year, month, and day
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day


    ticker = yf.Ticker(stk)

    # Subtract one day using timedelta
    new_date_obj = date_obj - timedelta(days=100)

    # Convert the datetime object back to a string
    from_date = new_date_obj.strftime("%Y-%m-%d")
    """
    shares=ticker.get_shares_full(start=from_date, end=date)
    print(shares)

    # Creating DataFrame
    df = pd.DataFrame(shares)

    # Get the last row's last column
    total_shares = df.iloc[-1, -1]

    print(f"total shares: {total_shares}")
    print(len(shares))
    """
    #get dates where we have quarterly (every 3 months) num of shares info
    #all_dates = ticker.quarterly_income_stmt.columns
    #print(ticker.quarterly_income_stmt)
    
    #print(ticker.info)
    total_shares = ticker.info.get('sharesOutstanding')

    #income_stmt = ticker.get_income_stmt(freq='quarterly')
    #df = pd.DataFrame(income_stmt)

    #total_shares = df.iloc[18,0]

    #months 03/31, 06/30, 09/30, 12/31, days could be 30/31
    """
    print("====================")
    print(income_stmt)
    print("====================")

    print(f"total shares = {total_shares}")
    """
    #hist = ticker.history(period="10y", interval="1mo")
    #print(hist)

    stock_price = ticker.history(start=from_date, end=date)
    #print(stock_price)
    price = stock_price['Close']
    #print(price)
    df = pd.DataFrame(price)

    # Get the last row's last column
    price = df.iloc[-1, -1]
    #print(f"{stk} price: {price}")

    market_cap = price * total_shares

    print(f"market cap of {stk} on {date}: {market_cap}")

ticker_symbol=input("ticker: ")
date=input("date (e.g., 2020-01-01): ")
get_market_cap_date(ticker_symbol, date)
"""
#!/usr/bin/env python
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import certifi
import json
from datetime import datetime, timedelta

# Given date as a string
date_str = date

# Parse the string into a datetime object
date_obj = datetime.strptime(date_str, "%Y-%m-%d")

# Subtract one day using timedelta
new_date_obj = date_obj - timedelta(days=7)

# Convert the datetime object back to a string
new_date = new_date_obj.strftime("%Y-%m-%d")

def get_jsonparsed_data(url):
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

url = (f"https://financialmodelingprep.com/api/v3/historical-market-capitalization/{ticker_symbol}?limit=100&from={new_date}&to={date}&apikey=tPLXri3K92yErJSEAx4CazsjkGKilNPs")
response = get_jsonparsed_data(url)
print(response)
print(f"length: {len(response)}")
print(response[0]['marketCap'])
"""