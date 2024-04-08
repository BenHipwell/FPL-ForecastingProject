import time
import csv
import praw


# initialize Reddit instance
reddit = praw.Reddit(client_id='',
                     client_secret='',
                     user_agent='')

# specify the subreddit and thread ID
subreddit = reddit.subreddit("FantasyPL")

id_file = open('rmtdates_22-23.csv', 'r', encoding="utf-8")
list = csv.reader(id_file)

for row in list:

    gw = row[0]
    thread_id = row[1]

    if int(gw) > 0:

        print("gw: " + str(gw))
        print("thread: " + str(thread_id))

        gw_file = open('rdata/2022-23/rmt/' + str(gw) + '.csv', 'a+', newline='', encoding="utf-8")
        writer = csv.writer(gw_file)

        # get the thread
        thread = reddit.submission(id=thread_id)
        
        thread.comments.replace_more(limit=None)

        # get all comments (including all comments of comments)
        comments = thread.comments.list()
        print(len(comments))

        for comment in comments:
            writer.writerow((comment.body.replace('\n', ' '),comment.score))

        gw_file.close()
        time.sleep(100)

id_file.close()