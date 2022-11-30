import requests
import pandas as pd
import seaborn as sns
from twelvedata import TDClient
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import os

#GNEWS
def get_news_data_gnews(stocksTicker, from_date, to_date, sort, limit):
    api_key = "e0cb64f718bf6b042c7faa469cc4a7cd"
    url = "https://gnews.io/api/v4/search?q=" + stocksTicker + "&from=" + from_date + "&to=" + to_date + "&sortby=" + sort + "&max=" + limit + "&token=" + api_key+ "&lang=en" 
    params = {
        "stocksTicker": stocksTicker,
        "from": from_date,
        "to": to_date,
        "sort": sort,
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data
#POLYGON
def get_stock_data_polygon(stocksTicker, multiplier, timespan, from_date, to_date, sort, limit):
    url = "https://api.polygon.io/v2/aggs/ticker/" + stocksTicker + "/range/" + multiplier + "/" + timespan + "/" + from_date + "/" + to_date + "?apiKey=kQ7_G94gpM45HRLw4XrF9a_pW1sRLNqb" #enter your api key here
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
#TWELVEDATA
def get_current_stock_data(symbol,interval):
    url="https://api.twelvedata.com/time_series"
    params = {
        "symbol":symbol,
        "interval":interval,
        "apikey":"9699f1b5bb0b4a8c9a54b2e112630369" #enter your api key here
    }
    response=requests.get(url,params=params)
    data=response.json()
    print(data)
    return data

'''--------------------------------------------------------------------------------------------------------------'''

#SQL

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

#POLYGON
def create_table_poly(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS stock (date TEXT, open REAL, high REAL, low REAL, close REAL, volume REAL)")
    conn.commit()

def insert_data_poly(cur, conn, data):
    for i in range(len(data['results'])):
        date = data['results'][i]['t']
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

#TWELVEDATA
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
    print(df)

    
'''--------------------------------------------------------------------------------------------------------------'''


#TWELVEDATA API (current stock data)
def get_current_stock_data(symbol,interval):
    url="https://api.twelvedata.com/time_series"
    params = {
        "symbol":symbol,
        "interval":interval,
        "apikey":"9699f1b5bb0b4a8c9a54b2e112630369"
    }

    response=requests.get(url,params=params)
    data=response.json()
    print(data)
    return data

#Get time series values, and calculate average for the current day. 
#Add all of these values to SQL table
def get_twelvedata_table(data):
    data['values']
    pass

def main():
    tickers = ["AAPL", "MSFT"]
    #Polygon API
    if len(tickers) > 1:
        for ticker in tickers:
            data = get_news_data_gnews(ticker, "2021-05-01", "2022-05-05", "date", "10")
            cur, conn = setUpDatabase(ticker + ".db")
            create_table_news(cur, conn)
            insert_data_news(cur, conn, data)
            print(ticker)
            print_db_table_news(cur, conn)
            data = get_stock_data_polygon(ticker, "1", "day", "2020-01-05", "2022-05-01", "asc", "100")
            cur, conn = setUpDatabase(ticker + ".db")
            create_table_poly(cur, conn)
            insert_data_poly(cur, conn, data)
            print(ticker)
            print_db_table_poly(cur, conn)
            data = get_current_stock_data(ticker, "1min")
            cur, conn = setUpDatabase(ticker + ".db")
            create_table(cur, conn)
            insert_data(cur, conn, data)
            print(ticker)
            print_poly_table(data)
            print("---------------------------------------------------------")
            plot_poly_data(data)
    elif len(tickers) == 1:
        data = get_stock_data_polygon(tickers[0], "1", "day", "2020-05-05", "2021-05-05", "asc", "100")
        print(tickers[0])
        print_poly_table(data)
        print("---------------------------------------------------------")
        plot_poly_data(data)
    else:
        print("No Tickers")
    
    #TwelveData API
    for ticker in tickers:
        td = TDClient(apikey="9699f1b5bb0b4a8c9a54b2e112630369")
        ts = td.time_series(
            symbol=ticker,
            outputsize=100,
            interval="1min",
        )
        ts.as_plotly_figure()
        ts.with_ema().as_plotly_figure().show()

if __name__ == "__main__":
    main()