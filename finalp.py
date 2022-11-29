import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

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

def print_poly_table(data):
    df = pd.DataFrame(data['results'])
    df['t'] = pd.to_datetime(df['t'], unit='ms')
    df.rename(columns={'t': 'date'}, inplace=True)
    df = df.set_index('date')
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
    df.rename(columns={'t': 'date'}, inplace=True)
    df = df.set_index('date')
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
    tickers = ["AAPL", "MSFT", "AMZN", "GOOG", "FB", "TSLA", "NFLX", "NVDA", "PYPL", "ADBE"]
    for ticker in tickers:
        data = get_stock_data_polygon(ticker, "1", "day", "2020-01-05", "2021-05-01", "asc", "100")
        print(ticker)
        print_poly_table(data)
        print("---------------------------------------------------------")
        plot_poly_data(data)

if __name__ == "__main__":
    main()