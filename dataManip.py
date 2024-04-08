import os
import csv
import shutil
import pandas as pd
import numpy as np


def getTeamStats(season, id):
    stats = []
    team_file = open('fpldata/' + season + '/teams.csv', 'r', encoding="utf-8")

    stats = {"strength_attack_home": '', "strength_attack_away": '', "strength_defence_home": '', "strength_defence_away": '', "last_finish": '', "strength": ''}

    position_dict = pd.read_csv(team_file)
    for index, row in position_dict.iterrows():
        if row["id"] == id:
            stats["strength_attack_home"] = row["strength_attack_home"]
            stats["strength_attack_away"] = row["strength_attack_away"]
            stats["strength_defence_home"] = row["strength_defence_home"]
            stats["strength_defence_away"] = row["strength_defence_away"]
            stats["last_finish"] = row["last_finish"]
            stats["strength"] = row["strength"]

    team_file.close()
    return stats


# sort players into their position folders ################################################################################################################      
def sort_players(season):
    for dir_name in os.listdir("fpldata/" + season + "/players/"):

        names = dir_name.split("_")
        first_name = names[0]
        second_name = names[1]
        id = str(names[2])

        position_file = open('fpldata/' + season + '/cleaned_players.csv', 'r', encoding="utf-8")

        position = ""
        position_dict = csv.DictReader(position_file)
        for row in position_dict:
            if row["first_name"] == first_name and row["second_name"] == second_name:
                position = row["element_type"]

        if len(position) > 1:
            destination = "fpldata/" + season + "/sorted_players/" + position + "/" + first_name + "_" + second_name + "_" + id
        else:
            print("Error: " + first_name + " " + second_name)
            destination = "fpldata/" + season + "/sorted_players/UNSORTED/" + first_name + "_" + second_name + "_" + id

        shutil.copytree("fpldata/" + season + "/players/" + dir_name, destination)
        position_file.close()

# Create csv ready for model ##################################################################################################################      

def createCols(window_size, previousgw_features, thisgw_features):
    features = thisgw_features.copy()
    features[0] = 'points'

    for i in range(0,window_size):
        for feature in previousgw_features:
            features.append(feature + str(i+1))
    
    return features


def createCSV(position, season, window_size, previousgw_features, thisgw_features):
    cols = createCols(window_size, previousgw_features, thisgw_features)

    output_df = pd.DataFrame(columns=cols)

    for dir_name in os.listdir("fpldata/" + season + "/sorted_players/" + position + "/"):
        data = pd.read_csv("fpldata/" + season + "/sorted_players/" + position + "/" + dir_name + "/data.csv")

        data['total_points_tally'] = data['total_points'].cumsum()
        data['goals_scored_tally'] = data['goals_scored'].cumsum()
        data['goals_conceded_tally'] = data['goals_conceded'].cumsum()
        data['assists_tally'] = data['assists'].cumsum()

        data['minutes_avg'] = data['minutes'].expanding().mean()
        data['bps_avg'] = data['bps'].expanding().mean()

        avg_mins = data['minutes'].mean()

        for index,row in data.iterrows(): 
            team_stats = getTeamStats(id=row["opponent_team"],season=season)   
            data.at[index, 'opponent_strength_attack_home'] = team_stats.get("strength_attack_home")
            data.at[index, 'opponent_strength_attack_away'] = team_stats.get("strength_attack_away")
            data.at[index, 'opponent_strength_defence_home'] = team_stats.get("strength_defence_home")
            data.at[index, 'opponent_strength_defence_away'] = team_stats.get("strength_defence_away")
            data.at[index, 'opponent_last_finish'] = team_stats.get("last_finish")
            data.at[index, 'opponent_strength'] = team_stats.get("strength")


        if avg_mins > 25:
            for i in range(window_size,len(data)):
                df = data.loc[i-window_size:i-1, previousgw_features]
                df.reset_index(drop=True, inplace=True)
                rows=[]

                for j in range(len(df)):
                    temp=df.loc[[j]]
                    temp.columns=np.arange(j*len(temp.columns),(j+1)*len(temp.columns))
                    temp.reset_index(drop=True, inplace=True)
                    rows=rows+[temp] 

                previous_df=pd.concat(rows,axis=1) 
                previous_df.reset_index(drop=True, inplace=True) 
                
                this_df = data.loc[i:i, thisgw_features]
                this_df.reset_index(drop=True, inplace=True) 
                output_df['was_home'] = output_df['was_home'].astype(int)

                concat_df = pd.merge(this_df,previous_df, left_index=True, right_index=True)
                concat_df.columns = cols
                output_df = pd.concat([output_df,concat_df])

        output_df.to_csv('datasets/' + season + '_' + position + '.csv')


def generateAllCSV(seasons, window_size, previousgw_features, thisgw_features):
    positions = ["GK","DEF","MID","FWD"]

    for position in positions:
        for season in seasons:
            createCSV(position, season, window_size, previousgw_features, thisgw_features)


previousgw_features = ['bps', 'goals_scored', 'goals_conceded', 'assists', 'yellow_cards', 'red_cards', 'minutes',
                                'saves', 'penalties_saved', 'opponent_strength_attack_home', 'opponent_strength_attack_away', 'opponent_strength_defence_home',
                         'opponent_strength_defence_away', 'opponent_last_finish', 'opponent_strength', 'creativity', 'influence', 'threat',
                           'total_points']

currentgw_features = ['total_points', 'selected', 'transfers_in', 'transfers_out' ,'value' ,'was_home',
                        'opponent_strength_attack_home', 'opponent_strength_attack_away', 'opponent_strength_defence_home',
                         'opponent_strength_defence_away', 'opponent_last_finish', 'opponent_strength', 
                         'total_points_tally', 'goals_scored_tally', 'goals_conceded_tally', 'assists_tally', 'bps_avg', 'minutes_avg',
                         'rant_sentiment','rant_count','rmt_sentiment','rmt_count', 'twitter_sentiment','twitter_count']

seasons = ["2021-22","2022-23"]

window_size = 3

# sort_players("2022-23")
# sort_players("2021-22")

generateAllCSV(seasons,window_size,previousgw_features,currentgw_features)
