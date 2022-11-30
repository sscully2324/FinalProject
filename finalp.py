import requests
import pandas as pd
import seaborn as sns
from twelvedata import TDClient
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import os
from datetime import datetime


#GNEWS SETUP
def get_news_data_gnews(stocksTicker, from_date, to_date, sort, limit, apikey):
    url = "https://gnews.io/api/v4/search?q=" + stocksTicker + "&from=" + from_date + "&to=" + to_date + "&sortby=" + sort + "&max=" + limit + "&token=" + apikey + "&lang=en" 
    params = {
        "stocksTicker": stocksTicker,
        "from": from_date,
        "to": to_date,
        "sort": sort,
        "limit": limit,
        "apikey": apikey
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data
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


#GNEWS SQL
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/' + db_name)
    cur = conn.cursor()
    return cur, conn
def create_table_news(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS news (title TEXT, description TEXT, publishedAt TEXT)")
    conn.commit()
def insert_data_news(cur, conn, data):
    for i in range(len(data['articles'])):
        cur.execute("INSERT INTO news (title, description, publishedAt) VALUES (?, ?, ?)", (data['articles'][i]['title'], data['articles'][i]['description'], data['articles'][i]['publishedAt']))
        conn.commit()
def print_db_table_news(cur, conn):
    cur.execute("SELECT * FROM news")
    rows = cur.fetchall()
    df = pd.DataFrame(rows)
    df.columns = ['Title', 'Description', 'Published At']
    print(df)
    print("---------------------------------------------------------")
    print("---------------------------------------------------------")
    print("Total Articles: " + str(len(rows)))
    print("---------------------------------------------------------")


#POLYGON SQL
def create_table_poly(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS stock (date TEXT, open REAL, high REAL, low REAL, close REAL, volume REAL)")
    conn.commit()
def insert_data_poly(cur, conn, data):
    for i in range(len(data['results'])):
        date = datetime.fromtimestamp(data['results'][i]['t']//1000)
        open = data['results'][i]['o']
        high = data['results'][i]['h']
        low = data['results'][i]['l']
        close = data['results'][i]['c']
        volume = data['results'][i]['v']
        cur.execute("INSERT INTO stock VALUES (?, ?, ?, ?, ?, ?)", (date, open, high, low, close, volume))
        conn.commit()
def print_db_table_poly(cur, conn):
    cur.execute("SELECT * FROM stock")
    rows = cur.fetchall()
    df = pd.DataFrame(rows)
    df.columns = [x[0] for x in cur.description]
    print(df)


#TWELVEDATA SQL
def create_table(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS realtime (date TEXT, open REAL, high REAL, low REAL, close REAL, volume REAL)")
    conn.commit()
def insert_data(cur, conn, data):
    for i in range(len(data['values'])):
        date = data['values'][i]['datetime']
        open = data['values'][i]['open']
        high = data['values'][i]['high']
        low = data['values'][i]['low']
        close = data['values'][i]['close']
        volume = data['values'][i]['volume']
        cur.execute("INSERT INTO realtime VALUES (?, ?, ?, ?, ?, ?)", (date, open, high, low, close, volume))
        conn.commit()
def print_db_table(cur, conn):
    cur.execute("SELECT * FROM realtime")
    rows = cur.fetchall()
    df = pd.DataFrame(rows)
    df.columns = [x[0] for x in cur.description]
    print("---------------------------------------------------------")
    print("---------------------------------------------------------")
    print(df)


'''--------------------------------------------------------------------------------------------------------------'''


def main():
    tickers = ["AAPL", "MSFT"]
    if len(tickers) > 1:
        for ticker in tickers:
            data = get_news_data_gnews(ticker, "2021-05-10", "2022-05-10", "date", "25", "e0cb64f718bf6b042c7faa469cc4a7cd") #add your gnews api here 
            cur, conn = setUpDatabase(ticker + ".db")
            create_table_news(cur, conn)
            insert_data_news(cur, conn, data)
            print(ticker)
            print_db_table_news(cur, conn)
            data = get_stock_data_polygon(ticker, "1", "day", "2021-05-10", "2022-05-10", "asc", "100", "fw2THBM8iVqFAaKWfECR_H9peNm0Bp8Y") #add your polygon api key here
            cur, conn = setUpDatabase(ticker + ".db")
            create_table_poly(cur, conn)
            insert_data_poly(cur, conn, data)
            print(ticker)
            print_db_table_poly(cur, conn)
            data = get_current_stock_data(ticker, "1min", "25", "aa9952037501498aa349d042e328f8a7") #add your twelvedata api key here
            cur, conn = setUpDatabase(ticker + ".db")
            create_table(cur, conn)
            insert_data(cur, conn, data)
            print(ticker)
            print_db_table(cur, conn)
            conn.close()
            td = TDClient(apikey="aa9952037501498aa349d042e328f8a7") #add your twelvedata api key here
            ts = td.time_series(
                symbol=ticker,
                outputsize=100,
                interval="1min",
            )
            ts.as_plotly_figure()
            ts.with_ema().as_plotly_figure().show()
    else:
        print("No Tickers")

if __name__ == "__main__":
    main()