import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import csv
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import os
import pandas as pd
import itertools

print(torch.__version__)
print(torch.cuda.is_available())
device = torch.device('cuda')

model_name = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.model_max_length = 512
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.to(device)

def getSentiment(entries):

    length = 0
    total = 0

    for row in entries:
        sentiment = predictSentiment(row[0])
        total = total + sentiment
        length = length + 1
    
    if length == 0:
        return 0
    
    return total / length
            

def preprocess(text):
    text = re.sub(r'[^\x00-\x7f]',r'', text)

    # removes words beginning with '@' to remove Twitter handles
    text = re.sub(r'@\S+', ' ', text)
    
    # converts all text to lower case
    text = text.lower()

    # removes urls
    text = re.split('http.*', str(text))[0]
    
    # tokenize the text
    words = nltk.word_tokenize(text)
    
    # remove stop words
    stop_words = set(stopwords.words("english"))
    words = [word for word in words if word not in stop_words]

    # perform lemmatization
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]

    return " ".join(words)


def predictSentiment(text):
    text = text.encode('utf-8').decode('utf-8')
    
    text = preprocess(text)
    
    inputs = tokenizer.encode_plus(text, return_tensors="pt", padding=True, truncation=True).to(device)
    
    outputs = model(**inputs.to(device))
    scores = outputs.logits.softmax(dim=1).detach().cpu().numpy()[0]

    sentiment_score = scores[2] - scores[0]
    
    return sentiment_score


def getEntryCount(entries):
    return len(list(entries))


# season = "2021-22"
season = "2022-23"

num_gws = 0

if (season == "2021-22"):
    num_gws = 38
elif (season == "2022-23"):
    num_gws = 28


for position_dir in os.listdir(r"fpldata/" + season + "/sorted_players"):
    for name_dir in os.listdir(r"fpldata/" + season + "/sorted_players/" + position_dir):
        
        id = name_dir.split("_")[-1]
        new_df = pd.DataFrame(0, index = range(0,num_gws), columns=['rant_sentiment','rant_count','rmt_sentiment','rmt_count', 'twitter_sentiment','twitter_count'])

        gw_file = pd.read_csv(r"fpldata/" + season + "/sorted_players/" + position_dir + "/" + name_dir + "/gw.csv")
        
        print(position_dir + " " + name_dir)

        ### rant
        if os.path.exists(r"fpldata/" + season + "/sorted_players/" + position_dir + "/" + name_dir + "/rant"):
            for rant_file in os.listdir(r"fpldata/" + season + "/sorted_players/" + position_dir + "/" + name_dir + "/rant"):
                week = rant_file.replace(".csv", "")
                week = week.replace("\ufeff", "")
                week = int(float(week))
                rant_file = open(r"fpldata/" + season + "/sorted_players/" + position_dir + "/" + name_dir + "/rant/" + rant_file, 'r', encoding="utf-8")
                reader1 = csv.reader(rant_file)
                reader1, reader2 = itertools.tee(reader1)
                new_df.loc[week-1,'rant_sentiment'] = getSentiment(reader1)
                new_df.loc[week-1,'rant_count'] = getEntryCount(reader2)
                rant_file.close()

        ### rmt
        if os.path.exists(r"fpldata/" + season + "/sorted_players/" + position_dir + "/" + name_dir + "/rmt"):
            for rmt_file in os.listdir(r"fpldata/" + season + "/sorted_players/" + position_dir + "/" + name_dir + "/rmt"):
                week = rmt_file.replace(".csv", "")
                week = week.replace("\ufeff", "")
                week = int(float(week))
                rmt_file = open(r"fpldata/" + season + "/sorted_players/" + position_dir + "/" + name_dir + "/rmt/" + rmt_file, 'r', encoding="utf-8")
                reader1 = csv.reader(rmt_file)
                reader1, reader2 = itertools.tee(reader1)
                new_df.loc[week-1,'rmt_sentiment'] = getSentiment(reader1)
                new_df.loc[week-1,'rmt_count'] = getEntryCount(reader2)
                rmt_file.close()
        
        ### twitter
        for week_dir in os.listdir(r"C://Users/benhi/Documents/IP/twitterdata_local/" + season):
            week = week_dir.replace("gw", "")
            week = week.replace("\ufeff", "")
            week = int(float(week))
            if os.path.exists(r"C://Users/benhi/Documents/IP/twitterdata_local/" + season + "/" + week_dir + "/" + id + ".csv"):
                twitter_file = open(r"C://Users/benhi/Documents/IP/twitterdata_local/" + season + "/" + week_dir + "/" + id + ".csv", 'r', encoding="utf-8")
                reader1 = csv.reader(twitter_file)
                reader1, reader2 = itertools.tee(reader1)
                new_df.loc[week-1,'twitter_sentiment'] = getSentiment(reader1)
                new_df.loc[week-1,'twitter_count'] = getEntryCount(reader2)
                twitter_file.close()
        
        if (season == "2022-23"):
            new_df.drop(index=6, inplace=True)
            new_df.reset_index(drop=True, inplace=True)
        
        output_df = pd.concat([gw_file,new_df], axis=1)

        output_df.dropna(axis=0, how='any', inplace=True)
        
        output_df.to_csv(r"fpldata/" + season + "/sorted_players/" + position_dir + "/" + name_dir + "/data.csv")

