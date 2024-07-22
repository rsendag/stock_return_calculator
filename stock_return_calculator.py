from re import I
from string import printable
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_user_input():
    choice = input("Do you want to (1) input N companies or (2) hold the top N companies in the S&P 500? Enter 1 or 2: ").strip()
    if choice == '1':
        stocks = input("Enter stock names (separated by space): ").split()
        num_stocks = len(stocks)
    elif choice == '2':
        stocks = None  # Will be determined dynamically
        num_stocks = input("Enter number of companies: ")
    else:
        raise ValueError("Invalid choice. Please enter 1 or 2.")
    initial_amount = float(input("Enter the initial dollar amount: "))
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")
    monthly_amount = float(input("Enter the additional monthly amount: "))
    rebalance_duration = int(input("Enter the rebalancing duration (1 to 4 in years): "))
    return choice, stocks, num_stocks, initial_amount, start_date, end_date, monthly_amount, rebalance_duration


def get_top_n_sp500_companies(date_str, num_stocks, df):

    # Extract year and month from the input date string
    year, month, _ = date_str.split('-')
    year = int(year)
    month = int(month)

    # Filter the DataFrame for the given year and month
    filtered_df = df[(df['year'] == year) & (df['month'] == month)]

    # Check if there are any matching rows
    if filtered_df.empty:
        return []
 
    #print(filtered_df)

    # Extract the top N stocks by column names as strings
    stock_columns = [str(i) for i in range(1, int(num_stocks) + 1)]
    top_n_stocks = filtered_df.iloc[0][stock_columns].tolist()

    return top_n_stocks

import os

def concatenate_csv_files(file_list):
    # Initialize an empty list to store DataFrames
    df_list = []

    # Iterate through the list of files
    for file in file_list:
        # Read each file into a DataFrame
        df = pd.read_csv(file)
        # Append the DataFrame to the list
        df_list.append(df)
    
    # Concatenate all DataFrames in the list
    concatenated_df = pd.concat(df_list, ignore_index=True)
    
    return concatenated_df


def get_csv_files_from_directory(directory_path):
    # List all files in the directory
    files = os.listdir(directory_path)
    # Filter to include only CSV files
    csv_files = [os.path.join(directory_path, f) for f in files if f.endswith('.csv')]
    return csv_files




def fetch_stock_data(stocks, start_date, end_date):
    stock_data = {}
    for stock in stocks:
        ticker = yf.Ticker(stock)
        stock_data[stock] = ticker.history(start=start_date, end=end_date, auto_adjust=False, back_adjust=True)
        stock_data[stock].index = stock_data[stock].index.tz_localize(None)  # Remove timezone information
    return stock_data

def calculate_returns(choice, stocks, num_stocks, initial_amount, start_date, end_date, monthly_amount, stock_data, df, rebalance_duration):
    start_date = pd.to_datetime(start_date).tz_localize(None)
    end_date = pd.to_datetime(end_date).tz_localize(None)
    current_date = start_date

    initial_investment_not_done = 1 # no initial investment done yet
    initial_investment_per_stock = initial_amount / int(num_stocks)
    monthly_investment_per_stock = monthly_amount / int(num_stocks)
    total_shares = {stock: 0 for stock in stocks} if stocks else {}
    initial_investment_done = {stock: 0 for stock in stocks} if stocks else {} #0 for false, 1 for partial, 2 for true
    buy_monthly = {stock: 0 for stock in stocks} if stocks else {} #0 for false, 1 for partial, 2 for true


    yearly_values = {start_date.year: initial_amount}

    initial_buyable_stocks = num_stocks

    #csv_file = "top_sp500_companies-2010-01-01-2011-12-31.csv"

    # Read the CSV file into a DataFrame
    #df = pd.read_csv(csv_file)

    #for rebalancing, wait until next year's Dec 1st
    rebalance_date = start_date.replace(year=start_date.year+rebalance_duration, month=12, day=1)

    while current_date < end_date:
        initial_buyable_stocks = num_stocks
        monthly_buyable_stocks = num_stocks
        initial_investment_per_stock = initial_amount / int(num_stocks)
        monthly_investment_per_stock = monthly_amount / int(num_stocks)
        print(f"Processing date: {current_date}")  # Debug print

        if choice == '2':  # Dynamically determine top N companies
           
            initial_amount_after_sale = 0
            num_sales = 0

            # Convert Timestamp to string in the desired format
            date_str = current_date.strftime("%Y-%m-%d")
            
            top_n_stocks = get_top_n_sp500_companies(date_str, num_stocks, df)
            #print(f"Top {num_stocks} are {top_n_stocks}")
            # Check if current holdings are still in the top 5, sell those that are not
            for stock in list(total_shares.keys()):
                if stock not in top_n_stocks:
                    sell_price = stock_data[stock].asof(current_date)["Close"]
                    total_sale = total_shares[stock] * sell_price
                    initial_amount_after_sale += total_sale
                    num_sales = num_sales + 1
                    total_shares.pop(stock)
                    initial_investment_done.pop(stock)
                    print(f"Selling {stock} at {sell_price} on {current_date} for a total of {total_sale}")

            if num_sales > 0:
                initial_investment_per_stock = (initial_amount_after_sale / num_sales) + monthly_investment_per_stock

            # Add new top n stocks to holdings
            for stock in top_n_stocks:
                if stock not in total_shares:
                    total_shares[stock] = 0
                    initial_investment_done[stock] = 0
                    stock_data[stock] = yf.Ticker(stock).history(start=start_date, end=end_date, auto_adjust=False, back_adjust=True)
                    stock_data[stock].index = stock_data[stock].index.tz_localize(None)
        
        #portfolio rebalancing: sell all and buy equal amounts

        rebalance = current_date == rebalance_date
        
        if rebalance == 1 and rebalance_date < end_date:
            print(f"======Rebalancing====={rebalance_date}")
            initial_amount_after_sale = 0
            num_sales = 0
            for stock in total_shares:
                if(total_shares[stock]>0):
                    sell_price = stock_data[stock].asof(current_date)["Close"]
                    total_sale = total_shares[stock] * sell_price
                    initial_amount_after_sale += total_sale
                    num_sales = num_sales + 1
                    print(f"Selling {stock} at {sell_price} on {current_date} for a total of {total_sale}")
                total_shares[stock] = 0
                initial_investment_done[stock] = 0

            if num_sales > 0:
                initial_investment_per_stock = (initial_amount_after_sale / int(num_stocks)) + monthly_investment_per_stock
                print(f"sales: {num_sales} - initial investment per stock = {initial_investment_per_stock}")

            if num_sales == 0:
                #no stocks has been bought yet although it is already rebalancing date
                initial_investment_per_stock = initial_amount / int(num_stocks)
                print(f"sales: {num_sales} - initial investment per stock = {initial_investment_per_stock}")


            #for rebalancing, wait until next year's Dec 1st
            rebalance_date = rebalance_date.replace(year=rebalance_date.year+rebalance_duration, month=12, day=1)

        next_available_date = {stock: current_date for stock in total_shares}
        for stock in total_shares:
            buy_monthly[stock] = 2
            stock_history = stock_data[stock]
            
            stock_history.index = stock_history.index.tz_localize(None)  # Ensure index is timezone-naive
            #print(stock_history)

            future_dates = stock_history.index[stock_history.index > current_date]
            if current_date not in stock_history.index:
                # If current date is not in the index, find the next available date
                
                if not future_dates.empty:
                    next_available_date[stock] = future_dates[0]
                else:
                    #put a large next avail day number to skip
                    next_available_date[stock] = end_date
            else:
                next_available_date[stock] = current_date

            

            if next_available_date[stock] > current_date + timedelta(days=32):
                print(f"{stock}'s next avail date is too far")
                initial_buyable_stocks -= 1
                if initial_buyable_stocks == 0:
                    initial_investment_done[stock] = 2
                    buy_monthly[stock] = 0
                    continue

                monthly_buyable_stocks -= 1
                
                #assume stock is bought (when rebalancing, stock will be bought if available)
                initial_investment_done[stock] = 2 # true (assumed, in reality no shares to be bought)
                initial_investment_per_stock += initial_investment_per_stock / initial_buyable_stocks
                monthly_investment_per_stock += monthly_investment_per_stock / monthly_buyable_stocks
                buy_monthly[stock] = 0
            else:
                buy_monthly[stock] = 2
                if initial_investment_not_done == 1:
                    initial_investment_done[stock] = 0
                    initial_investment_not_done = 0
            
            

            #if pd.isna(price):
             #   continue
            

            if initial_investment_done[stock] == 0:
                 initial_investment_done[stock] = 1 # partial -- buying will occur later
                 print(f"initial buying of {stock} should occur")

            
            if buy_monthly[stock] == 2:
                 buy_monthly[stock] = 1 # partial - buying will occur later

                
        for stock in total_shares: #this loop is for buying
            if next_available_date[stock] >= end_date:
                continue
            stock_history = stock_data[stock] 

            price = stock_history.loc[next_available_date[stock]]["Close"]
            if initial_investment_done[stock] == 1:
                shares_bought = initial_investment_per_stock / price
                print(f"New buy: {shares_bought} shares of {stock} for a total cost of {initial_investment_per_stock}")
                initial_investment_done[stock] = 2 #invested
            else:
                if buy_monthly[stock] == 1: 
                    shares_bought = monthly_investment_per_stock / price
                    print(f"monthly per stock: {monthly_investment_per_stock}")
                    buy_monthly[stock] = 2 #invested
                else:
                    shares_bought = 0

            total_shares[stock] += shares_bought

            print(f"Date: {next_available_date[stock]}, Stock: {stock}, Price: {price}, Shares Bought: {shares_bought}, Total Shares: {total_shares[stock]}")  # Debug print

        # Calculate portfolio value at the end of each month
        portfolio_value = sum(total_shares[stock] * ((stock_data[stock].loc[next_available_date[stock]]["Close"]) if total_shares[stock]>0 else 0) for stock in total_shares if next_available_date[stock] in stock_data[stock].index)
        #portfolio_value = sum(total_shares[stock] * stock_data[stock].loc[next_available_date[stock]]["Close"] for stock in total_shares if next_available_date[stock] in stock_data[stock].index)

        print(f"Portfolio Value at {current_date}: {portfolio_value}")  # Debug print

        if current_date.month == 12:  # Year-end calculation
            yearly_values[current_date.year] = portfolio_value

        # Move to the next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1, day=1)

        # Ensure current_date is timezone-naive
        current_date = current_date.tz_localize(None)
        
#    final_amount = sum(total_shares[stock] * stock_data[stock].iloc[-1]["Close"] for stock in total_shares)

    final_amount = sum(total_shares[stock] * stock_data[stock].asof(end_date)["Close"] for stock in total_shares)
    total_years = (end_date.year - start_date.year) + (end_date.month - start_date.month) / 12
    total_monthly_payments = (total_years*12*monthly_amount)-monthly_amount
    print(f"final amount: {final_amount}")
    print(f"Total monthly payments: {total_monthly_payments}")
    final_amount_wo_payments = final_amount - total_monthly_payments
    average_annual_gain = ((final_amount_wo_payments / initial_amount) ** (1 / total_years) - 1) * 100
    average_annual_gain_wrong = ((final_amount / initial_amount) ** (1 / total_years) - 1) * 100
    print(f"final amount - total monthly payments: {final_amount_wo_payments}")
    print(f"average gain wrong: {average_annual_gain_wrong}")
    print(f"average gain: {average_annual_gain}")
    return average_annual_gain, final_amount, yearly_values

def display_results(average_annual_gain, final_amount, yearly_values):
    print(f"Average Annual Percent Gain: {average_annual_gain:.2f}%")
    print(f"Final Dollar Amount: ${final_amount:.2f}")
    print("Dollar Amount at the End of Each Year:")
    for year, value in yearly_values.items():
        print(f"{year}: ${value:.2f}")

def main():
    choice, stocks, num_stocks, initial_amount, start_date, end_date, monthly_amount, rebalance_duration = get_user_input()
            
    # get all csv files from path and concatenate
    directory_path = "./"
    csv_files = get_csv_files_from_directory(directory_path)
    df = concatenate_csv_files(csv_files)

    if choice == '1':
        stock_data = fetch_stock_data(stocks, start_date, end_date)
    else:


    
        #csv_file = "top_sp500_companies-2010-01-01-2011-12-31.csv"

        # Read the CSV file into a DataFrame
        #df = pd.read_csv(csv_file)

        stocks = get_top_n_sp500_companies(start_date, num_stocks, df)
        #print(f"Top {num_stocks} are {stocks}")
        stock_data = fetch_stock_data(stocks, start_date, end_date)
        #print(stock_data)
    average_annual_gain, final_amount, yearly_values = calculate_returns(choice, stocks, num_stocks, initial_amount, start_date, end_date, monthly_amount, stock_data, df, rebalance_duration)
    display_results(average_annual_gain, final_amount, yearly_values)

if __name__ == "__main__":
    main()

