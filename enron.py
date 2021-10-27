"""
This file looks at {number_of_records} rows in a the enron csv and seperates out the contents data into 
email content, time, sender, receipient ets. 

It look at the text of the email and performs sentiment analysis and then graphs the number of emails containting
positive, netagite, and neutral sentiment 


"""
from os import X_OK
import pandas as pd
import numpy as np
from textblob import TextBlob
import re
import networkx as nx
import matplotlib.pyplot as plt

###
file_location = "enron/enron_emails.csv" #update to ur file ocation
number_of_records = 500
###

pd.options.mode.chained_assignment = None
chunk = pd.read_csv(file_location, chunksize=number_of_records)
data = next(chunk)

# data.info()



def get_text(Series, row_num_slicer):
    """returns a Series with text sliced from a list split from each message. Row_num_slicer
    tells function where to slice split text to find only the body of the message."""
    result = pd.Series(index=Series.index ,dtype= "float64")
    for row, message in enumerate(Series):
        message_words = message.split('\n')
        del message_words[:row_num_slicer]
        result.iloc[row] = message_words
    return result

def get_row(Series, row_num):
    """returns a single row split out from each message. Row_num is the index of the specific
    row that you want the function to return."""
    result = pd.Series(index=Series.index ,dtype= "float64")
    for row, message in enumerate(Series):
        message_words = message.split('\n')
        message_words = message_words[row_num]
        result.iloc[row] = message_words
    return result

def get_address(df, Series, num_cols=1):
    """returns a specified email address from each row in a Series"""
    address = re.compile('[\w\.-]+@[\w\.-]+\.\w+')
    addresses = []
    result1 = pd.Series(index=df.index,dtype= "float64")
    result2 = pd.Series(index=df.index,dtype= "float64")
    result3 = pd.Series(index=df.index,dtype= "float64")
    for i in range(len(df)):
        for message in Series:
            correspondents = re.findall(address, message)
            addresses.append(correspondents)
            result1[i] = addresses[i][0]
        if num_cols >= 2:
            if len(addresses[i]) >= 3:
                result2[i] = addresses[i][1]
                if num_cols == 3:
                    if len(addresses[i]) >= 4:
                        result3[i] = addresses[i][2]
    return result1, result2, result3

def standard_format(df, Series, string, slicer):
    """Drops rows containing messages without some specified value in the expected locations. 
    Returns original dataframe without these values. Don't forget to reindex after doing this!!!"""
    rows = []
    for row, message in enumerate(Series):
        message_words = message.split('\n')
        if string not in message_words[slicer]:
            rows.append(row)
    df = df.drop(df.index[rows])
    return df


x = len(data.index)
headers = ['Message-ID: ', 'Date: ', 'From: ', 'To: ', 'Subject: ']
for i, v in enumerate(headers):
    data = standard_format(data, data.message, v, i)
data = data.reset_index()
# print("Got rid of {} useless emails! That's {}% of the total number of messages in this dataset.".format(x - len(data.index), np.round(((x - len(data.index)) / x) * 100, decimals=2)))


data['text'] = get_text(data.message, 15)
data['date'] = get_row(data.message, 1)
data['senders'] = get_row(data.message, 2)
data['recipients'] = get_row(data.message, 3)
data['subject'] = get_row(data.message, 4)

data.date = data.date.str.replace('Date: ', '')
data.date = pd.to_datetime(data.date)

data.subject = data.subject.str.replace('Subject: ', '')

data['recipient1'], data['recipient2'], data['recipient3'] = get_address(data, data.recipients, num_cols=3)
data['sender'], x, y = get_address(data, data.senders)

del data['recipients']
del data['senders']
del data['file']
del data['message']

data = data[['date', 'sender', 'recipient1', 'recipient2', 'recipient3', 'subject', 'text']]


  

positive = negative = neutral = 0

for text in data["text"]:

    the_text = TextBlob(str(text))  # Natural Language Processing

    if the_text.sentiment.polarity > 0:
        positive += 1

    elif the_text.sentiment.polarity < 0:
        negative += 1

    else:
        neutral += 1



print(
    f"-----\nTotal Positive = {positive} \nTotal Negative = {negative} \nTotal Neutral = {neutral}")



######## Graphs ########
plt.style.use('fivethirtyeight')
# plt.title(f"'{keyword}' Sentiment for {max_tweets} Tweets")
plt.bar(["positive", "negative", "neutral"], [positive, negative, neutral])
plt.show()
