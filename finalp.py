import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


#TWELVE DATA API
def get_stock_data(symbol, start_date, end_date, interval):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "start_date": start_date,
        "end_date": end_date,
        "apikey": "aa9952037501498aa349d042e328f8a7"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

#Compare stock price and volume
def compare_stock_price(data):
    start_date = data['values'][0]['datetime']
    end_date = data['values'][-1]['datetime']
    start_price = data['values'][0]['close']
    end_price = data['values'][-1]['close']
    start_price = float(start_price)
    end_price = float(end_price)
    percent_diff = round((end_price - start_price) / start_price * 100, 2)
    return start_date, end_date, start_price, end_price, percent_diff

#POLYGON API
def get_stock_data_polygon(stocksTicker, multiplier, timespan, from_date, to_date, sort, limit):
    url = "https://api.polygon.io/v2/aggs/ticker/" + stocksTicker + "/range/" + multiplier + "/" + timespan + "/" + from_date + "/" + to_date + "?apiKey=fw2THBM8iVqFAaKWfECR_H9peNm0Bp8Y"
    params = {
        "stocksTicker": stocksTicker,
        "multiplier": multiplier,
        "timespan": timespan,
        "from": from_date,
        "to": to_date,
        "sort": sort,
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

def compare_stock_price_polygon(data):
    #panda table
    df = pd.DataFrame(data['results'])
    #average trade price
    avg_trade_price = df['c'].mean()
    #average volume
    avg_volume = df['v'].mean()
    return avg_trade_price, avg_volume
#print table
def print_table(data):
    df = pd.DataFrame(data['results'])
    df = df[['t', 'c', 'v']]
    df['t'] = df['t'].apply(convert_unix_time)
    df = df.rename(columns={"ticker": "Ticker","t": "Date", "c": "Average Trade Price", "v": "Average Volume"})
    print(df)
#convert unix time to readable date
def convert_unix_time(unix_time):
    date = pd.to_datetime(unix_time, unit='ms')
    return date



def main():
    data = get_stock_data_polygon("AAPL", "1", "day", "2020-01-31", "2020-12-31", "asc", "100")
    print_table(data)



if __name__ == "__main__":
    main()


