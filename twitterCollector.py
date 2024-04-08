import time
import requests
import os
import json
import csv


bearer_token = ""

search_url = "https://api.twitter.com/2/tweets/search/all"


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main():
    
    # season = "2021-22"
    season = "2022-23"

    gw_list_file = open('fpldata/' + season + '/gwdates.csv', 'r')
    gw_list = csv.reader(gw_list_file)

    for gwinfo in gw_list:

        gw = str(gwinfo[0])
        start_day = gwinfo[1]
        end_day = gwinfo[2]

        print(gw)
        print(season)

        player_list_file = open('fpldata/' + season + '/player_idlist.csv', 'r', encoding="utf-8")
        player_list = csv.reader(player_list_file)
        
        for row in player_list:
            first_name = row[0]
            second_name = row[1]
            id = row[2]
            simplified_fname = row[3]
            simplified_sname = row[4]
            alt_name = row[5]

            if simplified_fname != '' and alt_name != '':
                n = 80
            elif simplified_fname != '' or alt_name != '':
                n = 100
            else:
                n = 100

            # 1.	First name & surname
            query_params = {'query': '(' + first_name + ' ' + second_name + ' OR ' + first_name.lower() + ' ' + second_name.lower() + ') lang:en -is:retweet', 'start_time': start_day, 'end_time': end_day, 'tweet.fields': 'text,created_at', 'max_results': n}
            perform_search(query_params,id,gw,season)

            # 2.	Surname & ‘#FPL’
            query_params = {'query': '(' + second_name + ' OR ' + second_name.lower() + ') #FPL lang:en -is:retweet', 'start_time': start_day, 'end_time': end_day, 'tweet.fields': 'text,created_at', 'max_results': n}
            perform_search(query_params,id,gw,season)

            if simplified_fname != '':
                # 3.	Simplified first name & simplified surname
                query_params = {'query': '(' + simplified_fname + ' ' + simplified_sname + ' OR ' + simplified_fname.lower() + ' ' + simplified_sname.lower() + ') lang:en -is:retweet', 'start_time': start_day, 'end_time': end_day, 'tweet.fields': 'text,created_at', 'max_results': n}
                perform_search(query_params,id,gw,season)
            else:
                query_params = {'query': '(' + first_name + ' ' + simplified_sname + ' OR ' + first_name.lower() + ' ' + simplified_sname.lower() + ') lang:en -is:retweet', 'start_time': start_day, 'end_time': end_day, 'tweet.fields': 'text,created_at', 'max_results': n}
                perform_search(query_params,id,gw,season)

            # 4.	Simplified surname & ‘#FPL’
            query_params = {'query': '(' + simplified_sname + ' OR ' + simplified_sname.lower() + ') #FPL lang:en -is:retweet', 'start_time': start_day, 'end_time': end_day, 'tweet.fields': 'text,created_at', 'max_results': n}
            perform_search(query_params,id,gw,season)


            if alt_name != '':
                # 5.	Alternative name & ‘#FPL’
                query_params = {'query': alt_name + ' #FPL lang:en -is:retweet', 'start_time': start_day, 'end_time': end_day, 'tweet.fields': 'text,created_at', 'max_results': n}
                perform_search(query_params,id,gw,season)

            print("Done! id: " + str(id))
            time.sleep(8)

        player_list_file.close()

    player_list_file.close()
    gw_list_file.close()


def perform_search(params, id, gw, season):
    json_response = connect_to_endpoint(search_url, params)
    response = json.dumps(json_response, indent=4, sort_keys=True)

    data = json.loads(response)

    if not os.path.exists('twitterdata/' + season + '/gw' + gw):
        os.makedirs('twitterdata/' + season + '/gw' + gw)

    file = open('twitterdata/' + season + '/gw' + gw + '/' + str(id) + '.csv', 'a+', newline='', encoding="utf-8")
    writer = csv.writer(file)

    if 'data' in data:
        for tweet in data['data']:
            t = tweet['text'].replace('\n', ' ')
            d = tweet['created_at']
            writer.writerow((t,d))

    file.close()
    time.sleep(1)


if __name__ == "__main__":
    main()