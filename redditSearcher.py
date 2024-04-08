import csv
import praw
from datetime import datetime

# initialize Reddit instance
reddit = praw.Reddit(client_id='',
                     client_secret='',
                     user_agent='')

# specify the subreddit and thread ID
subreddit = reddit.subreddit("FantasyPL")
    
# RMT thread ##################################################################################################################################################

file = open('rmtdates_22-23.csv', 'a+', newline='', encoding="utf-8")
writer = csv.writer(file)

threads = subreddit.search("Rate My Team, Quick Questions & General Advice Daily Thread", sort='new', limit=300)

for thread in threads:
    if thread.title == 'Rate My Team, Quick Questions & General Advice Daily Thread' and thread.author == 'FPLModerator':
        writer.writerow((thread.id,datetime.utcfromtimestamp(thread.created_utc).strftime('%Y-%m-%d %H:%M:%S'))) 
        print(thread.title)
        print(thread.id)
        print(datetime.utcfromtimestamp(thread.created_utc).strftime('%Y-%m-%d %H:%M:%S'))
        print(thread.author)
        print("*************************")

file.close()

# rant thread ##################################################################################################################################################

file = open('22-23_rants.csv', 'a+', newline='', encoding="utf-8")
writer = csv.writer(file)

threads = subreddit.search("(2022/2023) RANT & DISCUSSION THREAD author:FPLModerator", sort='new', limit=50)

### rant threads
for thread in threads:
    if thread.title.endswith('(2022/2023) RANT & DISCUSSION THREAD') and thread.author == 'FPLModerator':
        print(thread.title)
        gw = thread.title.replace("(2022/2023) RANT & DISCUSSION THREAD",'')
        gw = thread.title.replace("GAME WEEK",'')
        writer.writerow((gw,thread.id)) 

file.close()