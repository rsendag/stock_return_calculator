import requests
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_sp500_companies():
    # Fetch the S&P 500 companies from Wikipedia
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})

    sp500_companies = []
    for row in table.find('tbody').find_all('tr')[1:]:
        columns = row.find_all('td')
        symbol = columns[0].text.strip()
        name = columns[1].text.strip()
        sp500_companies.append((symbol, name))
    
    return sp500_companies

def get_closest_earlier_date_index(date_list, target_date):
    date_list_naive = [date.tz_localize(None) if date.tzinfo else date for date in date_list]
    
    earlier_dates = [date for date in date_list_naive if date <= target_date]
    if not earlier_dates:
        return None
    return max(earlier_dates)

def get_market_cap_on_date(symbol, target_date):
    stock = yf.Ticker(symbol)
    start_date = (pd.Timestamp(target_date) - timedelta(days=30)).strftime('%Y-%m-%d')
    #print(f"1==date_range: {start_date}-{target_date}")
    end_date = target_date

    history = stock.history(start=start_date, end=end_date)
    if history.empty:
        #print(f"${symbol}: No price data found.")
        #return None
        return 0 # market_cap = 0 if not found
  
    target_date = pd.to_datetime(target_date).tz_localize(None)
    history.index = history.index.tz_localize(None)

    #print(f"2 target_date= {target_date}")
    closest_date = get_closest_earlier_date_index(history.index,target_date)
    if closest_date is None:
        print(f"${symbol}: No earlier price data found for {target_date}.")
        return None
    
    price = history.loc[closest_date]["Close"]
    shares_outstanding = stock.info.get('sharesOutstanding')
    if not shares_outstanding:
        return None
    market_cap = price * shares_outstanding
    
 
    print(f"Using data from {closest_date.date()} for ${symbol}-- market cap = {market_cap}")
    return market_cap

def get_top_5_sp500_companies(target_date):
    sp500_companies = get_sp500_companies()

    market_caps = {}
    for symbol, name in sp500_companies:
        print(f"Processing {symbol} on {target_date}")
        market_cap = get_market_cap_on_date(symbol, target_date)
        if market_cap is not None:
            market_caps[symbol] = market_cap

    market_caps_df = pd.DataFrame.from_dict(market_caps, orient='index', columns=['MarketCap'])
    top_5_companies = market_caps_df.sort_values(by='MarketCap', ascending=False).head(5)

    company_names = []
    for symbol in top_5_companies.index:
        stock = yf.Ticker(symbol)
        company_names.append(stock.info['longName'])

    top_5_list = []
    for i, symbol in enumerate(top_5_companies.index):
        top_5_list.append({
            'rank': i+1,
            'company_name': company_names[i],
            'symbol': symbol,
            'market_cap': top_5_companies.loc[symbol]['MarketCap']
        })

    return top_5_list


# Example usage
if __name__ == "__main__":
    target_date = input("Target Date (e.g., 2020-01-01) : ")#'2022-01-01'  # Replace with your desired date in 'YYYY-MM-DD' format
    top_5 = get_top_5_sp500_companies(target_date)
    print(f"Top 5 companies in S&P 500 by market capitalization on {target_date}:")
    for company in top_5:
        print(f"{company['rank']}. {company['company_name']} ({company['symbol']}): ${company['market_cap']:,}")
