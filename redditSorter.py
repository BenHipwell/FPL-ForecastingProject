import os
import csv

season = "2022-23"

player_list_file = open('fpldata/' + season + '/player_idlist.csv', 'r', encoding="utf-8")
player_list = csv.reader(player_list_file)

player_dict = {}

for player in player_list:
    id = player[2]
    fname = player[0]
    sname = player[1]
    alt_sname = player[4]
    special_name = player[5]

    player_dict[sname] = id
    player_dict[alt_sname] = id
    if player[5] != "":
        player_dict[special_name] = id


for filename in os.listdir("rdata/" + season + "/rant/"):
    print(filename)
    rmt_gw_file = open("rdata/" + season + "/rant/" + filename, 'r', encoding="utf-8")
    comment_list = csv.reader(rmt_gw_file)

    for comment in comment_list:

        for key, value in player_dict.items():
            if key in comment[0].split(" "):

                for foldername in os.listdir("fpldata/" + season + "/players/"):
                    split_name = foldername.split("_")
                    file_id = split_name[2]

                    if file_id == value:

                        if not os.path.exists('fpldata/' + season + '/players/' + foldername + '/rant'):
                            os.makedirs('fpldata/' + season + '/players/' + foldername + '/rant')
                                                
                        file = open('fpldata/' + season + '/players/' + foldername + '/rant/' + filename, 'a+', newline='', encoding="utf-8")
                        writer = csv.writer(file)
                        writer.writerow([comment[0]])
                        file.close()
                        
player_list_file.close()