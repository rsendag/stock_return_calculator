# run as --> streamlit run stock_return_calc_app
import streamlit as st
from stock_return_calculator import *
import matplotlib.pyplot as plt

# Set page configuration to use the full width of the browser window
st.set_page_config(layout="wide")

def get_user_input_st():
    # Title and introductory text
    st.title("SP500 Stocks Return Calculator")
    st.write("This calculator's option 2 can only be used for current companies in SP500. Limit your date selection between 1990-01-01 and 2024-07-01.\nYou can make a portfolio of stocks you pick in option1 or the top 1-20 SP500 (in market-cap) in option 2.\nIf selected option2, when top5 changes over the years, portfolio is updated accordingly following the top 5.\nInital amount invested is shared equally among stocks picked.\nRebalancing equally distributes the total amount at that time.")

    choice = st.text_input("Do you want to (1) input N companies or (2) hold the top N companies in the S&P 500? Enter 1 or 2: ").strip()
    if choice:
        if choice == '1':
            stocks = st.text_input("Enter stock names (separated by space): ").split()
            num_stocks = len(stocks)
        elif choice == '2':
            stocks = None  # Will be determined dynamically
            num_stocks = st.text_input("Enter number of companies (between 1-20): ")
        else:
            raise ValueError("Invalid choice. Please enter 1 or 2.")

    initial_amount = float(st.number_input("Enter the initial dollar amount: "))
    start_date = st.text_input("Enter the start date (YYYY-MM-DD): Must be after 1990-01-01: ")
    end_date = st.text_input("Enter the end date (YYYY-MM-DD): Must be before 2024-07-01: ")
    monthly_amount = float(st.number_input("Enter the additional monthly amount: "))
    rebalance_duration = int(st.number_input("Enter the rebalancing duration (1 to 4 in years): For no rebalancing enter 100"))

    #st.write("Your input is: ", "choice: ", choice)
    return choice, stocks, num_stocks, initial_amount, start_date, end_date, monthly_amount, rebalance_duration

def display_results_st(average_annual_gain, final_amount, yearly_values):
    print(f"Average Annual Percent Gain: {average_annual_gain:.2f}%")
    print(f"Final Dollar Amount: ${final_amount:.2f}")
    print("Dollar Amount at the End of Each Year:")
    for year, value in yearly_values.items():
        print(f"{year}: ${value:.2f}")

    st.write(f"Average Annual Percent Gain: {average_annual_gain:.2f}%")
    st.write(f"Final Dollar Amount: ${final_amount:.2f}")
    #st.write("Dollar Amount at the End of Each Year:")
    #for year, value in yearly_values.items():
    #    print(f"{year}: ${value:.2f}")

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(list(yearly_values.items()), columns=['Year', 'Value'])

    # Format the values with a dollar sign
    df['Value'] = df['Value'].apply(lambda x: f"${x:,.2f}")

    #Create a two-column layout with specified width ratios
    col1, col2 = st.columns([1, 3])


    # Display the DataFrame in the first column without the index
    with col1:
        st.table(df)



    # Create a graph
    fig, ax = plt.subplots()
    ax.plot(list(yearly_values.keys()), list(yearly_values.values()), marker='o')
    ax.set_title('Portfolio Return')
    ax.set_xlabel('Year')
    ax.set_ylabel('Value ($)')
    ax.yaxis.set_major_formatter('${x:,.0f}')
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}'))

    ax.set_xticks(list(yearly_values.keys()))  # Ensure all years are shown
    ax.set_xticklabels(list(yearly_values.keys()), rotation=90, ha='center')
    
    # Display the graph in the second column
    with col2:
        st.pyplot(fig)

def main():
    choice, stocks, num_stocks, initial_amount, start_date, end_date, monthly_amount, rebalance_duration = get_user_input_st()
            
    # get all csv files from path and concatenate
    directory_path = "./"
    csv_files = get_csv_files_from_directory(directory_path)
    df = concatenate_csv_files(csv_files)
    if st.button("Calculate Return"):
        if choice == '1':
            stock_data = fetch_stock_data(stocks, start_date, end_date)
        else:
            stocks = get_top_n_sp500_companies(start_date, num_stocks, df)
            #print(f"Top {num_stocks} are {stocks}")
            stock_data = fetch_stock_data(stocks, start_date, end_date)
            #print(stock_data)
        average_annual_gain, final_amount, yearly_values = calculate_returns(choice, stocks, num_stocks, initial_amount, start_date, end_date, monthly_amount, stock_data, df, rebalance_duration)
        display_results_st(average_annual_gain, final_amount, yearly_values)

if __name__ == "__main__":
    main()
