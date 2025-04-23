import yfinance as yf
from datetime import datetime
import pandas as pd

def get_stock_data():
    try:
        ticker = "^STI"
        start_date = "2016-12-30"
        end_date = datetime.today().strftime('%Y-%m-%d')
        data = yf.download(ticker, start=start_date, end=end_date, interval="1d")
        data.reset_index(inplace=True)
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
        data = data[['Date', 'Close']]

        # Converting Date to Year and Month
        data['Year'] = data['Date'].dt.year
        data['Month'] = data['Date'].dt.month

        # Filtering only 2017 to today
        data = data[data['Year'] >= 2017]

        # Grouping by Year and Month, and then taking the average of each month
        monthly_avg = data.groupby(['Year', 'Month'])['Close'].mean().reset_index()
        monthly_avg.rename(columns={'Close': 'Average_Close'}, inplace=True)

        # Sorting by Year and Month Descending
        monthly_avg = monthly_avg.sort_values(by=['Year', 'Month'], ascending=[False, False])
        
        return monthly_avg

    except Exception as e:
        print(f"An error occurred while fetching stock data: {e}")
        return pd.DataFrame()