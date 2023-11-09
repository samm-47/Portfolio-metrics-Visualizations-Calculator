# Portfolio-metrics-Visualizations-Calculator

This Python script, stock.py, is a simple stock portfolio analyzer that retrieves historical stock data for companies in the Dow Jones Industrial Average (DJIA). The script allows users to input their stock preferences, including the stock symbol and the quantity of stocks they wish to add to their portfolio.

**Installments**

Before using this script, ensure that you have the necessary Python libraries installed. You can install them using the following:

pip install requests beautifulsoup4 pandas


**Run the script:**

python stock.py

Follow the prompts to add stocks to your portfolio. You will be asked to enter the stock symbol and quantity for each stock.

The script will retrieve historical stock data using the Alpha Vantage API and save the data to CSV files for each stock.

Finally, the script calculates and prints the Mean Daily Return, Standard Deviation of Daily Returns, and Cumulative Returns for the entire portfolio.

Important Notes
The script retrieves information for the first four stocks listed in the DJIA. You can modify the script to collect data for more or fewer stocks.

Ensure that you have an active internet connection, as the script relies on web scraping and API calls to retrieve stock data.

To avoid rate limiting, the script introduces a delay between API calls. You can adjust the delay as needed.
