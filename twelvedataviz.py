import requests
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

#Making First Vizualization with TwelveData API
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

#Print TwelveData Table
def print_current_table(data):
    df = pd.DataFrame(data['values'])
    df = df.set_index('datetime')
    df.columns = ['Open','High','Low','Close',"Volume"]
    #calculation from table here
    df['Average Value'] = round((df['High'].astype(float)+df['Low'].astype(float))/2,4)
    #returns dataframe 
    return df

def main():
    stocks = "AAPL"
    current = get_current_stock_data(stocks, "1min", "100", "f3cdc7c31b684fdf9de786f2f913fa51")
    tbl = print_current_table(current)
    print(tbl)

    # makes list of date values for x-axis
    xAxis=[]
    for d in current['values']:
        xAxis.append(d['datetime'])
        
    # Make VIZ 1 from TwelveData API 
    fig = px.line(tbl, x=xAxis, y="Average Value", title="Average " + current['meta']['symbol'] + " Stock Value per Current Minute").update_layout(xaxis_title="Current Time (Military)")
    fig.update_traces(line_color='purple')
    fig.update_layout(
    font_family="Courier New",
    font_color="black",
    title_font_family="Times New Roman",
    title_font_color="black",
    legend_title_font_color="green")
    fig.show()


if __name__ == "__main__":
    main()