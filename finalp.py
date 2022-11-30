import requests
import pandas as pd
import sqlite3
import seaborn as sns
from twelvedata import TDClient
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from sqlalchemy import create_engine
engine = create_engine('sqlite:///stocks.db', echo=True)

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
    df.rename(columns={'t': 'date'}, inplace=True)
    df = df.set_index('date')
    df = df[['o', 'h', 'l', 'c', 'v']]
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    print(df)
    print("---------------------------------------------------------")
    print("Stock: " + data['ticker'])
    print("---------------------------------------------------------")
    print("Average Open: " + str(round(df['Open'].mean(), 2)))
    print("Average High: " + str(round(df['High'].mean(), 2)))
    print("Average Low: " + str(round(df['Low'].mean(), 2)))
    print("Average Close: " + str(round(df['Close'].mean(), 2)))
    print("---------------------------------------------------------")
    print("Total Volume: " + str(df['Volume'].sum()))
    print("---------------------------------------------------------")

    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS " + data['ticker'] + " (date text, open real, high real, low real, close real, volume real)")
    df.to_sql(data['ticker'], con=engine, if_exists='replace')
    conn.commit()
    conn.close()

def plot_poly_data(data):
    sns.set_theme(style="darkgrid")
    df = pd.DataFrame(data['results'])
    df['t'] = pd.to_datetime(df['t'], unit='ms')
    df.rename(columns={'t': 'date'}, inplace=True)
    df = df.set_index('date')
    df = df[['o', 'h', 'l', 'c', 'v']]
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    plt.title(data['ticker'])
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
            data = get_stock_data_polygon(ticker, "1", "day", "2020-01-05", "2021-05-01", "asc", "100")
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