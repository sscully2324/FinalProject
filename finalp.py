import requests
import json
import pandas as pd
import sqlite3
import seaborn as sns
from twelvedata import TDClient
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['date.converter'] = 'concise'

#POLYGON API (historical data)
def get_stock_data_polygon(stocksTicker, multiplier, timespan, from_date, to_date, sort, limit):
    url = "https://api.polygon.io/v2/aggs/ticker/" + stocksTicker + "/range/" + multiplier + "/" + timespan + "/" + from_date + "/" + to_date + "?apiKey=kQ7_G94gpM45HRLw4XrF9a_pW1sRLNqb"
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

def print_poly_table(data):
    df = pd.DataFrame(data['results'])
    df['t'] = pd.to_datetime(df['t'], unit='ms')
    df.rename(columns={'t': 'Date'}, inplace=True)
    df = df.set_index('Date')
    df = df[['o', 'h', 'l', 'c', 'v']]
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    print(df)
    print("Average Open: ", df['Open'].mean())
    print("Average High: ", df['High'].mean())
    print("Average Low: ", df['Low'].mean())
    print("Average Close: ", df['Close'].mean())

def plot_poly_data(data):
    sns.set_theme(style="darkgrid")
    df = pd.DataFrame(data['results'])
    df['t'] = pd.to_datetime(df['t'], unit='ms')
    df.rename(columns={'t': 'Date'}, inplace=True)
    df = df.set_index('Date')
    df = df[['o', 'h', 'l', 'c', 'v']]
    plt.title(data['ticker'])
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    sns.lineplot(data=df[
        ['Open', 'High', 'Low', 'Close']
    ], palette="tab10", linewidth=2.5)
    plt.text(0.5, 0.9, "Average Open: " + str(round(df['Open'].mean(), 2)), horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.85, "Average High: " + str(round(df['High'].mean(), 2)), horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.8, "Average Low: " + str(round(df['Low'].mean(), 2)), horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.75, "Average Close: " + str(round(df['Close'].mean(), 2)), horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.show()

def main():
    tickers = ["AAPL", "MSFT"]
    #Polygon API
    if len(tickers) > 1:
        for ticker in tickers:
            data = get_stock_data_polygon(ticker, "1", "day", "2020-12-01", "2021-03-12", "asc", "100")
            print(ticker)
            print_poly_table(data)
            print("---------------------------------------------------------")
            plot_poly_data(data)
    elif len(tickers) == 1:
        data = get_stock_data_polygon(tickers[0], "1", "day", "2020-12-01", "2021-03-12", "asc", "100")
        print_poly_table(data)
        plot_poly_data(data)
    else:
        print("No Tickers")
    
    #TwelveData API
    for tickerr in tickers:
        td = TDClient(apikey="9699f1b5bb0b4a8c9a54b2e112630369")
        ts = td.time_series(
            symbol=tickerr,
            outputsize=100,
            interval="1min",
        )
        ts.as_plotly_figure()
        ts.with_ema(time_period=7).as_plotly_figure().show()
    


if __name__ == "__main__":
    main()