import requests
from bs4 import BeautifulSoup
import json, time
from datetime import datetime
import pandas as pd

# Replace with your actual API key
rapidapi_key = '185d2edc76mshc4518fd5b454ab9p1430a0jsn8514a6fe1582'

# Define the URL of the Wikipedia page
url = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"

rapidapi_host = 'alpha-vantage.p.rapidapi.com'

def get_data():
    # Send an HTTP GET request to the URL
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the table containing the DJIA stock information (you may need to inspect the page to find the table)
        table = soup.find("table", {"class": "wikitable"})

        if table:
            # Initialize a list to store data
            stock_data = []

            # Initialize a counter to limit the iteration to four times
            counter = 0

            # Iterate through the rows of the table
            for row in table.find_all("tr"):
                columns = row.find_all("td")

                if len(columns) >= 3:
                    # Extract relevant information (such as stock symbol, company name, and industry)
                    company_name = columns[1].text.strip()
                    symbol = columns[0].text.strip()
                    industry = columns[2].text.strip()

                    # Prompt the user to specify the number of stocks for this company
                    while True:
                        # Prompt the user to specify the number of stocks for this company
                        user_input = input(f"What would you like to add to your portfolio (symbol, quantity)? ")
                        input_parts = user_input.split(",")
                        if len(input_parts) != 2:
                            print("Invalid input. Please enter both a stock symbol and a quantity separated by a comma.")
                            continue
                        stock_symbol, num_stocks = input_parts
                        num_stocks = int(num_stocks)
                        break
                    
                    historical_data = get_historical_data(stock_symbol, rapidapi_key)

                    # Append the extracted data and the number of stocks to the list
                    stock_data.append({
                        "Symbol": stock_symbol.strip(),
                        "Company Name": company_name,
                        "Industry": industry,
                        "Number of Stocks": num_stocks
                    })

                    counter += 1

                    if counter == 4:
                        break  # Exit the loop after collecting data for four stocks

            # Return the scraped data as a list
            return stock_data

        else:
            return 'Table not found on the page.'
    else:
        return f"Failed to retrieve the webpage. Status code: {response.status_code}"
    
def filter_date_range(historical_data, start_date, end_date):
    filtered_data = {}
    for date, data in historical_data.items():
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        if start_date <= date_obj <= end_date:
            filtered_data[date] = data
    return filtered_data

start_date = datetime(2020, 1, 1)
end_date = datetime(2023, 1 , 1)

def get_historical_data(symbol, api_key):
    # Define the Alpha Vantage API endpoint for monthly historical data on RapidAPI
    rapidapi_url = f"https://alpha-vantage.p.rapidapi.com/query?function=TIME_SERIES_MONTHLY_ADJUSTED" \
                   f"&symbol={symbol}"

    headers = {
        'X-RapidAPI-Host': rapidapi_host,
        'X-RapidAPI-Key': api_key
    }

    # Send an HTTP GET request to Alpha Vantage on RapidAPI to retrieve historical data
    response = requests.get(rapidapi_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'Monthly Adjusted Time Series' in data:
            monthly_data = data['Monthly Adjusted Time Series']
            filtered_data = filter_date_range(monthly_data, start_date, end_date)
            return filtered_data

    return None
if __name__ == '__main__':
    stock_data = get_data()
    # Initialize a list to store DataFrames for each stock
    all_stock_dfs = []
    # Iterate through each stock in the user input
    for stock in stock_data:
        print(f"Stock: {stock['Symbol']}, Quantity: {stock['Number of Stocks']}")
        historical_data = get_historical_data(stock['Symbol'], rapidapi_key)

        if historical_data is not None:
            # Filter the historical data based on the specified date range
            filtered_data = filter_date_range(historical_data, start_date, end_date)

            if not filtered_data:
                print(f"No historical data found for {stock['Symbol']}")
                continue

            # Create a DataFrame from the filtered historical data
            df_stock = pd.DataFrame.from_dict(filtered_data, orient='index')
            df_stock['Symbol'] = stock['Symbol']
            df_stock['Quantity'] = stock['Number of Stocks']

            # Reset index
            df_stock = df_stock.reset_index()
            
            all_stock_dfs.append(df_stock)

            # Save the DataFrame to a CSV file for each stock
            csv_filename = f'historical_stock_data_{stock["Symbol"]}.csv'
            df_stock.to_csv(csv_filename, index=False)
            print(f"Historical data for {stock['Symbol']} saved to '{csv_filename}'")

            # Introduce a delay to avoid rate limiting
            time.sleep(25)  # Adjust the delay as needed
        else:
            print(f"Failed to retrieve historical data for {stock['Symbol']}")
    print("All historical data saved.")
    all_stock_data = pd.concat(all_stock_dfs)

    # Calculate daily return for each stock
all_stock_data['5. adjusted close'] = pd.to_numeric(all_stock_data['5. adjusted close'], errors='coerce')
all_stock_data = all_stock_data.dropna(subset=['5. adjusted close'])

# Calculate daily return for each stock
all_stock_data['Daily Return'] = all_stock_data['5. adjusted close'].pct_change()

# Calculate daily return for the entire portfolio
all_stock_data['Portfolio Daily Return'] = (all_stock_data['Daily Return'] * all_stock_data['Quantity']).sum() / all_stock_data['Quantity'].sum()

# Calculate Mean Daily Return for the portfolio
mean_daily_return = all_stock_data['Portfolio Daily Return'].mean()

print(f"Mean Daily Return for the portfolio: {mean_daily_return:.4f}")
std_dev_daily_returns = all_stock_data['Portfolio Daily Return'].std()

# Calculate Cumulative Returns of the portfolio
cumulative_returns = (1 + all_stock_data['Portfolio Daily Return']).cumprod() - 1

# Print the calculated metrics
print(f"Standard Deviation of Daily Returns for the portfolio: {std_dev_daily_returns:.4f}")
print(f"Cumulative Returns of the portfolio: {cumulative_returns.iloc[-1]:.4f}")