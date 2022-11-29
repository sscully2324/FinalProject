import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


#function to get stock data from Twelve Data API
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

#create a function to compare the % difference in stock price between the start and end date for each company
def compare_stock_price(data):
    start_date = data['values'][0]['datetime']
    end_date = data['values'][-1]['datetime']
    start_price = data['values'][0]['close']
    end_price = data['values'][-1]['close']
    #make the start and end price into a float
    start_price = float(start_price)
    end_price = float(end_price)
    percent_diff = round((end_price - start_price) / start_price * 100, 2)
    return start_date, end_date, start_price, end_price, percent_diff

#test compare_stock_price function
data = get_stock_data("AAPL", "2020-01-01", "2020-12-31", "1day")
start_date, end_date, start_price, end_price, percent_diff = compare_stock_price(data)
print(start_date, end_date, start_price, end_price, percent_diff)

#use Polygon API to have a list of all the stocks with paramters as stocksTicker, multiplier, timespan, from, to, sort, and limit
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

#test get_all_stocks function
data = get_stock_data_polygon("AAPL", "1", "day", "2020-01-01", "2020-12-31", "asc", "10")
print(data)
