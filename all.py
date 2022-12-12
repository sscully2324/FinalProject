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
    url = "https://eodhistoricaldata.com/api/sentiments?s=" + stocks + "&order=a&from=" + froms + "&to=" + to + "&api_token=639769d9641b45.33949278"
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
        return 1
    elif score < 0:
        return -1
    else:
        return 0
'''--------------------------------------------------------------------------------------------------------------'''
#SQL SETUP
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/' + db_name)
    cur = conn.cursor()
    return cur, conn
def create_stock_table(cur, conn, data):
    cur.execute("CREATE TABLE IF NOT EXISTS stock (id INTEGER PRIMARY KEY, date TEXT, open REAL, high REAL, low REAL, close REAL, volume REAL)")
    conn.commit()
    for i in range(len(data['results'])):
        date = datetime.fromtimestamp(data['results'][i]['t']//1000)
        date = date.strftime('%Y-%m-%d')
        cur.execute("INSERT INTO stock (date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?)", (date, data['results'][i]['o'], data['results'][i]['h'], data['results'][i]['l'], data['results'][i]['c'], data['results'][i]['v']))
        conn.commit()
def create_current_stock_table(cur, conn, data):
    cur.execute("CREATE TABLE IF NOT EXISTS current_stock (id INTEGER PRIMARY KEY, current TEXT, current_open REAL, current_high REAL, current_low REAL, current_close REAL, current_volume REAL)")
    conn.commit()
    for i in range(len(data['values'])):
        cur.execute("INSERT INTO current_stock (current, current_open, current_high, current_low, current_close, current_volume) VALUES (?, ?, ?, ?, ?, ?)", (data['values'][i]['datetime'], data['values'][i]['open'], data['values'][i]['high'], data['values'][i]['low'], data['values'][i]['close'], data['values'][i]['volume']))
        conn.commit()
def insertData_news(cur, conn, data):
    cur.execute("CREATE TABLE IF NOT EXISTS news_stock(count_id INTEGER, date TEXT, score REAL, classification INTEGER)")
    conn.commit()
    count_id = cur.execute('SELECT COUNT(count_id) FROM news_stock').fetchone()[0] + 1
    start = count_id - 1
    sean_end = start + 25
    data_list = list(data.items())
    for date, score in data_list[start:sean_end]:
        classification = classify_score(score)
        cur.execute("INSERT OR IGNORE INTO news_stock VALUES (?, ?, ?, ?)", (count_id, date, score, classification))
        conn.commit()
def combine_tables(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS combine(date TEXT, score REAL, classification INTEGER, open REAL, high REAL, low REAL, close REAL, volume REAL)") 
    cur.execute("INSERT INTO combine SELECT n.date, n.score, n.classification, s.open, s.high, s.low, s.close, s.volume FROM (SELECT date, score, classification FROM news_stock GROUP BY date) AS n LEFT JOIN stock AS s ON n.date = s.date")
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

#calculates how many negative/positive sentiments and returns them in a dictionary with their corresponding count
def eod_calculation(cur, conn):
    cur.execute("SELECT classification FROM news_stock")
    classifications = cur.fetchall()
    results= {}
    for i in range(len(classifications)):
        if classifications[i][0] in results:
            results[classifications[i][0]]+=1
        else:
            results[classifications[i][0]]=0
    return results

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
    plt.title("Average Apple Stock Value over December 12th (Today)",**csfont)
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
    plt.title("Average Apple Stock Value over the Past Month",**csfont)
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.show()

#eod visualization
def eod_viz(cur,conn):
    plt.figure()
    cur.execute("SELECT score FROM news_stock")
    scores = cur.fetchall()
    for i in range(len(scores)):
        scores[i]= scores[i][0]
    cur.execute("SELECT date from news_stock")
    newsdates = cur.fetchall()
    for i in range(len(newsdates)):
        newsdates[i]= newsdates[i][0]
    plt.scatter(newsdates, scores, color = "green")
    plt.xlabel("Date")
    plt.ylabel("Sentiment Score")
    plt.title("Sentiment Scores for Apple for the Past Month")
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.xlim(0, 30)
    plt.locator_params(axis='x', nbins=30)
    plt.show()

#extra visualization bar graph of positive vs negative sentiments over the last month  ????

'''--------------------------------------------------------------------------------------------------------------'''
#MAIN
def main():
    cur, conn = setUpDatabase('stocks_final.db')
    stocks = "AAPL"
    data = setUp_news('aapl', '2022-08-31', '2022-12-09')
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
    data = get_stock_data_polygon(stocks, "1", "day", "2022-08-31", "2022-12-09", "desc", "25", "VwQcpLk2CC29SRIq8vuStvD6xOIKBDOh")
    create_stock_table(cur, conn, data)
    data = get_current_stock_data(stocks, "1min", "25", "4823639c64944e2191f8ca72b37189c8")
    create_current_stock_table(cur, conn, data)
    combine_tables(cur, conn)
    twelvedata_viz(cur, conn)
    polygon_viz(cur,conn)
    eod_viz(cur,conn)

if __name__ == '__main__':
    main()
