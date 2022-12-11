import requests
import pandas as pd
import seaborn as sns
from twelvedata import TDClient
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import os
from datetime import datetime
import plotly.express as px

#POLYGON SETUP
def get_stock_data_polygon(stocksTicker, multiplier, timespan, from_date, to_date, sort, limit, apikey):
    url = "https://api.polygon.io/v2/aggs/ticker/" + stocksTicker + "/range/" + multiplier + "/" + timespan + "/" + from_date + "/" + to_date + "?adjusted=true&sort=" + sort + "&limit=" + limit + "&apiKey=" + apikey
    params = {
        "stocksTicker": stocksTicker,
        "multiplier": multiplier,
        "timespan": timespan,
        "from": from_date,
        "to": to_date,
        "sort": sort,
        "limit": limit,
        "apikey": apikey
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

#TWELVEDATA SETUP
def get_current_stock_data(symbol,interval, outputsize, apikey):
    url="https://api.twelvedata.com/time_series" + "?symbol=" + symbol + "&interval=" + interval + "&apikey=" + apikey + "&outputsize=" + outputsize
    params = {
        "symbol":symbol,
        "interval":interval,
        "outputsize":outputsize,
        "apikey":apikey
    }
    response=requests.get(url,params=params)
    data=response.json()
    print(data)
    return data


'''--------------------------------------------------------------------------------------------------------------'''

#SQL SETUP
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/' + db_name)
    cur = conn.cursor()
    return cur, conn

def create_news_table(cur, conn, data, stock):
    #make gnews table with date as primary key
    cur.execute("CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY, stock TEXT, title TEXT, description TEXT, publishedAt TEXT, source TEXT, FOREIGN KEY (stock) REFERENCES stock (stock))")
    conn.commit()
    #insert data into gnews table
    for i in range(len(data['articles'])):
        cur.execute("INSERT INTO news (stock, title, description, publishedAt, source) VALUES (?, ?, ?, ?, ?)", (stock, data['articles'][i]['title'], data['articles'][i]['description'], data['articles'][i]['publishedAt'], data['articles'][i]['source']['name']))
        conn.commit()

def create_stock_table(cur, conn, data, stock):
    #make stock table with first column referencing primary key in gnews table
    cur.execute("CREATE TABLE IF NOT EXISTS stock (id INTEGER PRIMARY KEY, stock TEXT, date TEXT, open REAL, high REAL, low REAL, close REAL, volume REAL, FOREIGN KEY (id) REFERENCES gnews (id))")
    conn.commit()
    #insert data into stock table
    for i in range(len(data['results'])):
        date = datetime.fromtimestamp(data['results'][i]['t']//1000)
        cur.execute("INSERT INTO stock (stock, date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)", (stock, date, data['results'][i]['o'], data['results'][i]['h'], data['results'][i]['l'], data['results'][i]['c'], data['results'][i]['v']))
        conn.commit()
def create_current_stock_table(cur, conn, data, stock):
    #make stock table with first column referencing primary key in gnews table
    cur.execute("CREATE TABLE IF NOT EXISTS current_stock (id INTEGER PRIMARY KEY, stock TEXT, current TEXT, current_open REAL, current_high REAL, current_low REAL, current_close REAL, current_volume REAL, FOREIGN KEY (id) REFERENCES gnews (id))")
    conn.commit()
    #insert data into stock table
    for i in range(len(data['values'])):
        cur.execute("INSERT INTO current_stock (stock, current, current_open, current_high, current_low, current_close, current_volume) VALUES (?, ?, ?, ?, ?, ?, ?)", (stock, data['values'][i]['datetime'], data['values'][i]['open'], data['values'][i]['high'], data['values'][i]['low'], data['values'][i]['close'], data['values'][i]['volume']))
        conn.commit()

#join three tables news, stock, and current_stock and create a new table called final
def join_tables(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS final AS SELECT news.id, news.stock, news.title, news.description, news.publishedAt, news.source, stock.date, stock.open, stock.high, stock.low, stock.close, stock.volume, current_stock.current, current_stock.current_open, current_stock.current_high, current_stock.current_low, current_stock.current_close, current_stock.current_volume FROM news JOIN stock ON news.stock = stock.stock JOIN current_stock ON news.stock = current_stock.stock") 
    conn.commit()



'''--------------------------------------------------------------------------------------------------------------'''

def main():

    stocks = "AAPL"
    curr, conn = setUpDatabase("stock.db")
    create_news_table(curr, conn, data, stocks)
    data = get_stock_data_polygon(stocks, "1", "day", "2021-05-10", "2022-05-10", "asc", "25", "fw2THBM8iVqFAaKWfECR_H9peNm0Bp8Y")
    create_stock_table(curr, conn, data, stocks)
    data = get_current_stock_data(stocks, "1min", "25", "aa9952037501498aa349d042e328f8a7")
    create_current_stock_table(curr, conn, data, stocks)
    join_tables(curr, conn)


    







if __name__ == "__main__":
    main()