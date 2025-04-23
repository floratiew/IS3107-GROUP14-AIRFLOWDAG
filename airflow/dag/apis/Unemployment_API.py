import requests
import pandas as pd
from datetime import datetime
from prophet import Prophet

def get_unemployment_data():
    dataset_id = "d_b0da22a41f952764376a2b7b5b0f2533"
    url = "https://data.gov.sg/api/action/datastore_search?resource_id=" + dataset_id
    response = requests.get(url)
    
    if response.status_code == 200: #check if HTTP request to API is successful
        data = response.json()
        records = data['result']['records']
        df = pd.DataFrame(records)
        df_long = df.melt(id_vars=['_id', 'DataSeries'], 
            var_name='Quarter', 
            value_name='Unemployment Rate')
        df_long = df_long[df_long.DataSeries == 'Resident Unemployment Rate']  #only residents (SC + PR) can buy Resale flats
        df_long = df_long.drop(columns=['_id', 'DataSeries'])

        # Convert columns to appropriate data type
        df_long['Unemployment Rate'] = pd.to_numeric(df_long['Unemployment Rate'])

        def expand_quarter(row):
            year = int(row['Quarter'][:4])
            quarter = row['Quarter'][-2:]
            quarter_months = {
                '1Q': [1, 2, 3],
                '2Q': [4, 5, 6],
                '3Q': [7, 8, 9],
                '4Q': [10, 11, 12]
            }
            months = quarter_months.get(quarter, []) #change quarters into months
            return pd.DataFrame({
                'Year': [year] * 3,
                'Month': months,
                'Unemployment Rate': [row['Unemployment Rate']] * 3
            })

        df_expanded = pd.concat([expand_quarter(row) for _, row in df_long.iterrows()], ignore_index=True)
        df_expanded = df_expanded[df_expanded['Year'] >= 2017] #filter out years before 2017

        # Forecast using Prophet or fallback
        forecast_df = forecast_unemployment_with_fallback(df_expanded)

        # Append and sort final DataFrame
        df_expanded = pd.concat([df_expanded, forecast_df], ignore_index=True)
        df_expanded = df_expanded.sort_values(by=['Year', 'Month'], ascending=[False, False]) #sort descending by year then by month

        return df_expanded
    else:
        print(f"Request failed with status code {response.status_code}")
        return pd.DataFrame()

def forecast_unemployment_with_fallback(df):
    today = datetime.today()
    current_year, current_month = today.year, today.month

    df2 = df.copy()
    df2['ds'] = pd.to_datetime(df2[['Year', 'Month']].assign(day=1))

    group = df2.sort_values(by='ds')
    last_date = group['ds'].max()
    last_year, last_month = last_date.year, last_date.month

    months_gap = (current_year - last_year) * 12 + (current_month - last_month)
    if months_gap <= 0:
        return pd.DataFrame()

    if len(group) >= 12:
        model_df = group[['ds', 'Unemployment Rate']].rename(columns={'Unemployment Rate': 'y'})
        m = Prophet()
        m.fit(model_df)

        future = m.make_future_dataframe(periods=months_gap, freq='MS')
        forecast = m.predict(future)[['ds', 'yhat']].tail(months_gap)
        forecast['Unemployment Rate'] = forecast['yhat']
    else:
        last_rate = group['Unemployment Rate'].iloc[-1]
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), 
                                       periods=months_gap, freq='MS')
        forecast = pd.DataFrame({'ds': forecast_dates, 'Unemployment Rate': last_rate})

    forecast['Year'] = forecast['ds'].dt.year
    forecast['Month'] = forecast['ds'].dt.month
    forecast['Unemployment Rate'] = forecast['Unemployment Rate'].round(1)

    return forecast[['Year', 'Month', 'Unemployment Rate']]