import yfinance as yf
from datetime import datetime
import pandas as pd
from prophet import Prophet

def get_stock_data():
    try:
        ticker = "^STI"
        start_date = "1994-12-01"
        end_date = datetime.today().strftime('%Y-%m-%d')
        data = yf.download(ticker, start=start_date, end=end_date, interval="1d")
        data.reset_index(inplace=True)
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
        data = data[['Date', 'Close']]

        # Forecast future prices
        forecast_df = forecast_sti_with_fallback(data)
        full_data = pd.concat([data, forecast_df], ignore_index=True)

        # Converting Date to Year and Month
        full_data['Year'] = full_data['Date'].dt.year
        full_data['Month'] = full_data['Date'].dt.month

        # Filtering out before 1995
        full_data = full_data[full_data['Year'] >= 1995]

        # Grouping by Year and Month, and then taking the average of each month
        monthly_avg = full_data.groupby(['Year', 'Month'])['Close'].mean().reset_index()
        monthly_avg.rename(columns={'Close': 'Average_Close'}, inplace=True)

        # Sorting by Year and Month Descending
        monthly_avg = monthly_avg.sort_values(by=['Year', 'Month'], ascending=[False, False])
        
        return monthly_avg

    except Exception as e:
        print(f"An error occurred while fetching stock data: {e}")
        return pd.DataFrame()

def forecast_sti_with_fallback(df):
    df_temp = df.rename(columns={'Date': 'ds', 'Close': 'y'}).copy()
    df_temp['ds'] = pd.to_datetime(df_temp['ds'])

    # Target forecast: December of today's year + 10
    today = datetime.today()
    target_date = datetime(today.year + 10, 12, 31)

    last_date = df_temp['ds'].max()
    total_days = (target_date - last_date).days

    try:
        m = Prophet(yearly_seasonality=True, changepoint_prior_scale=0.5)
        m.add_seasonality(name='monthly', period=12, fourier_order=5)
        m.fit(df_temp[['ds', 'y']])

        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), end=target_date, freq='B')
        future = pd.DataFrame({'ds': forecast_dates})
        forecast = m.predict(future)[['ds', 'yhat']].tail(total_days)
        forecast.rename(columns={'ds': 'Date', 'yhat': 'Close'}, inplace=True)

    except Exception as e:
        print(f"Prophet failed, using fallback. Error: {e}")
        last_price = df_temp['y'].iloc[-1]
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(days=1), periods=total_days, freq='D')
        forecast = pd.DataFrame({'Date': forecast_dates, 'Close': last_price})

    return forecast[['Date', 'Close']]