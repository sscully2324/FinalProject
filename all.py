import requests
import pandas as pd
import seaborn as sns
from twelvedata import TDClient
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime
import sys
import os
import json

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
    return data

#EODHISTORICALDATA SETUP
def setUp_news (stocks, froms, to):
    url = "https://eodhistoricaldata.com/api/sentiments?s=" + stocks + "&order=a&from=" + froms + "&to=" + to + "&api_token=63966d0c94f400.49802964"
    params = {
        "s": stocks,
        "from": froms,
        "to": to,
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data
    '''--------------------------------------------------------------------------------------------------------------'''
#SENTIMENT ANALYSIS
def analyze_sentiment(sentiment_scores, end_date):
  daily_scores = {}
  count = 0
  if len(sentiment_scores) <= 100:
      end_date = None
  for entry in sentiment_scores:
    date = entry['date']
    score = entry['normalized']
    if date not in daily_scores:
      daily_scores[date] = []
    daily_scores[date].append(score)
    count += 1
    end_date = date
    if count  >= 100:
        end_date = None
        break
  for date, scores in daily_scores.items():
    average_score = sum(scores) / len(scores)
    daily_scores[date] = average_score
  return daily_scores, end_date

def classify_score(score):
    if score > 0.5:
        return "Positive"
    elif score < 0.5:
        return "Negative"
    else:
        return "Neutral"
'''--------------------------------------------------------------------------------------------------------------'''
#SQL SETUP
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/' + db_name)
    cur = conn.cursor()
    return cur, conn
def create_stock_table(cur, conn, data, stock):
    cur.execute("CREATE TABLE IF NOT EXISTS stock (id INTEGER PRIMARY KEY, stock TEXT, date TEXT, open REAL, high REAL, low REAL, close REAL, volume REAL, FOREIGN KEY (id) REFERENCES gnews (id))")
    conn.commit()
    for i in range(len(data['results'])):
        date = datetime.fromtimestamp(data['results'][i]['t']//1000)
        cur.execute("INSERT INTO stock (stock, date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)", (stock, date, data['results'][i]['o'], data['results'][i]['h'], data['results'][i]['l'], data['results'][i]['c'], data['results'][i]['v']))
        conn.commit()
def create_current_stock_table(cur, conn, data, stock):
    cur.execute("CREATE TABLE IF NOT EXISTS current_stock (id INTEGER PRIMARY KEY, stock TEXT, current TEXT, current_open REAL, current_high REAL, current_low REAL, current_close REAL, current_volume REAL, FOREIGN KEY (id) REFERENCES gnews (id))")
    conn.commit()
    for i in range(len(data['values'])):
        cur.execute("INSERT INTO current_stock (stock, current, current_open, current_high, current_low, current_close, current_volume) VALUES (?, ?, ?, ?, ?, ?, ?)", (stock, data['values'][i]['datetime'], data['values'][i]['open'], data['values'][i]['high'], data['values'][i]['low'], data['values'][i]['close'], data['values'][i]['volume']))
        conn.commit()
def insertData_news(cur, conn, data):
    cur.execute("CREATE TABLE IF NOT EXISTS news_stock(count_id INTEGER, date TEXT, score REAL, classification TEXT)")
    conn.commit()
    count_id = cur.execute('SELECT COUNT(count_id) FROM news_stock').fetchone()[0] + 1
    start = count_id - 1
    sean_end = start + 25
    data_list = list(data.items())
    for date, score in data_list[start:sean_end]:
        classification = classify_score(score)
        cur.execute("INSERT OR IGNORE INTO news_stock VALUES (?, ?, ?, ?)", (count_id, date, score, classification))
        conn.commit()
'''_____________________________________________________________________________________________________________________________________________________________________________________________________'''
#average calculation for current stock table 
def avg_current_stock(cur,conn):
    averages=[]
    cur.execute("SELECT current_high FROM current_stock")
    high = cur.fetchall()
    cur.execute("SELECT current_low FROM current_stock")
    low = cur.fetchall()
    for i in range(len(high)):
        h= high[i][0]
        l= low[i][0]
        avg = h+l/2
        averages.append(avg)
    #returns list of averages 
    return averages
#average calculation for historical stock table 
def avg_historical_stock(cur,conn):
    averages=[]
    cur.execute("SELECT high FROM stock")
    high = cur.fetchall()
    cur.execute("SELECT low FROM stock")
    low = cur.fetchall()
    for i in range(len(high)):
        h= high[i][0]
        l= low[i][0]
        avg = h+l/2
        averages.append(avg)
    #returns list of averages 
    return averages
'''_____________________________________________________________________________________________________________________________________________________________________________________________________'''
#Visualizations start 
def twelvedata_viz(cur,conn):
    plt.figure()
    y_axis = avg_current_stock(cur,conn)
    cur.execute("SELECT current FROM current_stock")
    x_axis = cur.fetchall()
    csfont = {'fontname':'Comic Sans MS'}
    for i in range(len(x_axis)):
        x_axis[i] = x_axis[i][0]
    fig = plt.figure(figsize = (10,5))
    plt.scatter(x_axis, y_axis, color = "purple")
    plt.xlabel("Date")
    plt.ylabel("Average Apple Stock Value")
    plt.title("Average Apple Stock Value over Current Time",**csfont)
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.show()

def polygon_viz(cur,conn):
    plt.figure()
    cur.execute("SELECT date FROM stock")
    x_axis = cur.fetchall()
    y_axis = avg_historical_stock(cur,conn)
    csfont = {'fontname':'Comic Sans MS'}
    for i in range(len(x_axis)):
        x_axis[i]= x_axis[i][0]
    fig = plt.figure(figsize = (10,5))
    plt.scatter(x_axis, y_axis, color = "orange")
    plt.xlabel("Date")
    plt.ylabel("Average Apple Stock Value")
    plt.title("Average Apple Stock Value over Historical Time Frame",**csfont)
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.show()





def eod_viz(cur,conn):
    pass
'''--------------------------------------------------------------------------------------------------------------'''
#MAIN
def main():
    cur, conn = setUpDatabase('stocks.db')
    stocks = "AAPL"
    data = setUp_news('aapl', '2021-12-09', '2022-12-09')
    aapl_data = data['AAPL.US']
    end_date = '2021-12-09'
    while True :
        daily_scores, end_date  = analyze_sentiment(aapl_data, end_date)
        for date, score in daily_scores.items():
            classification = classify_score(score)
            #print(date, score, classification)
        if end_date is None:
            break
    insertData_news(cur, conn, daily_scores)
    data = get_stock_data_polygon(stocks, "1", "day", "2021-05-10", "2022-05-10", "asc", "25", "fw2THBM8iVqFAaKWfECR_H9peNm0Bp8Y")
    create_stock_table(cur, conn, data, stocks)
    data = get_current_stock_data(stocks, "1min", "25", "aa9952037501498aa349d042e328f8a7")
    create_current_stock_table(cur, conn, data, stocks)
    twelvedata_viz(cur, conn)
    polygon_viz(cur,conn)
    
if __name__ == '__main__':
    main()