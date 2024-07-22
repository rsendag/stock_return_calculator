# sp500_data_extractor.py

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from re import I
from string import printable


def get_top_n_sp500_companies(start_date, end_date, num):
    # Define the date range
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get the list of SP500 tickers
    sp500_tickers = get_sp500_tickers()
    
    # Initialize an empty DataFrame to store the results
    results = []
    
    # Loop through each month in the date range
    current_date = start_date
    while current_date <= end_date:
        monthly_data = []
        for ticker in sp500_tickers:
            try:
                # Get market cap for the current month
                market_cap = get_market_cap(ticker, current_date)
                monthly_data.append({'stock': ticker, 'year': current_date.year, 'month': current_date.month, 'market_cap': market_cap})
            except Exception as e:
                print(f"Error getting data for {ticker} on {current_date}: {e}")
        
        # Sort by market cap and get top N companies
        monthly_data = sorted(monthly_data, key=lambda x: x['market_cap'], reverse=True)[:num]

        # Transform the data to the desired format
        formatted_data = {'year': current_date.year, 'month': current_date.month}
        for idx, company in enumerate(monthly_data, start=1):
            formatted_data[str(idx)] = company['stock']
        
        results.append(formatted_data)
        """
        print(monthly_data)
        print(formatted_data)
        print(results)
        """

        
        # Move to the next month
        current_date += timedelta(days=32)
        current_date = current_date.replace(day=1)
    
    return results


import requests
from bs4 import BeautifulSoup

def get_sp500_tickers():
    # Fetch the S&P 500 companies from Wikipedia
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})

    sp500_companies = []
    for row in table.find('tbody').find_all('tr')[1:]:
        columns = row.find_all('td')
        symbol = columns[0].text.strip()
        symbol = symbol.replace('.', '-')
        name = columns[1].text.strip()
        sp500_companies.append((symbol))
    
    return sp500_companies


def get_market_cap(ticker, date):
    # Function to get market cap for a given ticker and date
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo", start=date, end=date + timedelta(days=32), auto_adjust=False, back_adjust=True)
    #print(f"==========={ticker}============")
    #print(hist)

    if hist.index.empty:
        print(f"{date} not in {ticker} history -- market_cap = 0")
        return 0.0

    if 'Close' in hist.columns and not hist.empty:
        price = hist['Close']
        
        df = pd.DataFrame(price)
        
        price = df.iloc[-1, -1]
        market_cap = price * stock.info['sharesOutstanding']
        if ticker == 'AVGO': #data has problem
            market_cap = 0.0
        if ticker == 'GOOG': #also has googl
            market_cap = 0.0
        print(f"========={ticker} market cap={market_cap}")
        return market_cap
    print(f"========={ticker} market cap={market_cap}")
    return 0.0

def main(start_date, end_date, num):
    data = get_top_n_sp500_companies(start_date, end_date, num)
    df = pd.DataFrame(data)  # Convert the list of dictionaries to a DataFrame
    fname=f"top_sp500_companies-{start_date}-{end_date}.csv"

    df.to_csv(fname, index=False)  # Save the DataFrame to a CSV file

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python sp500_data_extractor.py <start_date> <end_date> <num>")
        sys.exit(1)
    start_date, end_date, num = sys.argv[1], sys.argv[2], int(sys.argv[3])
    main(start_date, end_date, num)

