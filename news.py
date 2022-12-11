import sys
import os
import sqlite3
import pandas as pd
import requests
import json
import datetime


def setUp (stocks, froms, to):
    url = "https://eodhistoricaldata.com/api/sentiments?s=" + stocks + "&order=a&from=" + froms + "&to=" + to + "&api_token=6396252345fe97.14332763"
    params = {
        "s": stocks,
        "from": froms,
        "to": to,
    }

    response = requests.get(url, params=params)
    data = response.json()
    return data

def analyze_sentiment(sentiment_scores, end_date):
  # Create a dictionary to hold the daily sentiment scores
  daily_scores = {}
  count = 0
  # If the sentiment_scores list contains fewer than 5 elements, set end_date to None manually
  if len(sentiment_scores) <= 100:
      end_date = None
  # Loop through the sentiment scores
  for entry in sentiment_scores:
    # Extract the date and normalized score for the entry
    date = entry['date']
    score = entry['normalized']
    # If the day is not already in the dictionary, add it and initialize the score to 0
    if date not in daily_scores:
      daily_scores[date] = []
    # Add the score for the current entry to the list of scores for the day
    daily_scores[date].append(score)
    count += 1
    end_date = date
    # If there are fewer than 5 scores remaining, set end_date to None and break out of the loop
    if count  >= 100:
        end_date = None
        break
  # Loop through the daily scores and calculate the average for each day
  for date, scores in daily_scores.items():
    # Calculate the average score for the day
    average_score = sum(scores) / len(scores)
    daily_scores[date] = average_score
  # Return the dictionary of daily average sentiment scores and the end_date
  return daily_scores, end_date



def setUpDatabase(db_name):
  path = os.path.dirname(os.path.abspath(__file__))
  conn = sqlite3.connect(path + '/' + db_name)
  cur = conn.cursor()
  cur.execute("CREATE TABLE IF NOT EXISTS stocks (count_id INTEGER, date TEXT, score REAL)")
  conn.commit()
  return cur, conn

def insertData(cur, conn, data):

  count_id = cur.execute('SELECT COUNT(count_id) FROM stocks').fetchone()[0] + 1
  start = count_id - 1
  sean_end = start + 25
  data_list = list(data.items())
  for date, score in data_list[start:sean_end]:
    cur.execute("INSERT OR IGNORE INTO stocks VALUES (?, ?, ?)", (count_id, date, score))
    conn.commit()



def main():
    stocks = 'aapl'
    data = setUp(stocks, '2021-12-09', '2022-12-09')
    aapl_data = data['AAPL.US']
    end_date = '2021-12-09'
    while True :
        # Call analyze_sentiment() and store the returned date in the variable "end_date"
        daily_scores, end_date  = analyze_sentiment(aapl_data, end_date)
        # Print the daily scores at index one where the date is the key and the score is the value
        for date, score in daily_scores.items():
            print(date, score)
        # If end_date is None, then all sentiment scores have been processed, so break out of the loop
        if end_date is None:
            break

    cur, conn = setUpDatabase('stocksss.db')
    insertData(cur, conn, daily_scores)
    
 

if __name__ == '__main__':
    main()
