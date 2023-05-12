import sys
import math
import pandas as pd
import openpyxl

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 10000)

"""
This script produces a data set for weekly averages, aggregates, and percentages for specific
stats which can be found in the definitions of the dataframes below. A set of data for each team
is printed to an excel sheet for each week. Those stats are each teams leading into the week labeled.
The model(s?) will be trained with these weekly aggregated stats. These sheets are manually placed
into the Weekly Aggregates sheet of PLL_Data.xlsx from test.xlsx in case anything goes wrong with
the script.

Author: Brian Andrews
Last Date Modified: 5/17/2021
"""

#create a nested list with the following column format:
#[av goals, av 2 pt shot, 2 pt %, av shots, shot %, av gb, av TO, av CT, FO %, Av PP, PP %, Av Saves, Save %, Point Differential, Streak, Upsets, GAA]

#rows for nested list will be the following:
#Whipsnakes 1
#Chaos 2
#Redwoods 3
#Archers 4
#Atlas 5
#Chrome 6
#Waterdogs 7
#Cannons 8

number_of_teams = 8
number_of_stats = 17

#*************************************************************************************************************************
#making three data frames to keep the weekly results imported data, the stat totals, and the information
#i want to put into the excel sheet for training a model preformatted.

def reset_dataframe():
    nested = [[0 for i in range(number_of_stats)] for i in range(number_of_teams)]
    main_datfram = pd.DataFrame(nested, index = [1,2,3,4,5,6,7,8], #index = ['Whipsnakes','Chaos','Redwoods','Archers','Atlas','Chrome','Waterdogs','Cannons'],
                                columns = ['av goals', 'av 2 pt shot', '2 pt %', 'av shots', 'shot %', 'av gb', 'av TO', 'av CT', 'FO %', 'av PP', 'PP %', 'av Saves', 'Save %', 'Point Differential', 'Streak', 'Upsets', 'GAA'])

    nested2 = [[0 for i in range(number_of_stats)] for i in range(number_of_teams)]
    side_datfram = pd.DataFrame(nested2, index = [1,2,3,4,5,6,7,8], #index = ['Whipsnakes','Chaos','Redwoods','Archers','Atlas','Chrome','Waterdogs','Cannons'],
                                columns = ['number_of_games', 'total goals', 'total 2 pt shot', 'total 2 pt goals', 'total shots', 'total goals (no 2 pt)', 'total gb', 'total TO', 'total CT', 'total FO','total FO won', 'total PP','total attempted PP', 'total Saves', 'total shots on goal', 'total GA'])

    #delete the lists because they are no longer needed
    del(nested,nested2)

    return main_datfram, side_datfram



#read the weekly results data
weekly_data = pd.read_excel("PLL_Data.xlsx", sheet_name='Weekly Results')

#output dataframe
training_data = pd.DataFrame()

#initiate an output excel file
writer = pd.ExcelWriter("test.xlsx", engine='openpyxl')

#***********************************************************************************************************************
#Start the calculations
#get number of games in the database
num_games = weekly_data["Game ID"].max()

#going to do one game at a time, need to take data a pair of rows at a time.
for b in range(num_games-1):
    temp_df = weekly_data.loc[b*2:(b*2)+1]
    if b == 0:
        #initialize data frames for totals and averages, get earliest year, and total number of games to parse
        main_datfram, side_datfram = reset_dataframe()
        year_check = weekly_data.loc[0,"Year"]
    else:
        #need to reset the dataframes for a new year
        if temp_df.loc[b*2,"Year"] != year_check:
            year_check = temp_df.loc[b*2,"Year"]
            print("Dataframes were reset. New year is " + str(temp_df.loc[b*2,"Year"]))
            print(side_datfram.loc[:, "number_of_games"])
            main_datfram, side_datfram = reset_dataframe()
            print(side_datfram.loc[:, "number_of_games"])


    #print(temp_df)

    """
    If a team has played at least one game, want to pull together the average stats and output that to the new db table for the training set.
    This will all be written to a dataframe and the whole dataframe will be written to the database table for verification.
    This happens before stat collection for the next game because the training set uses data leading up to the current game
    to train the model.
    """
    if side_datfram.loc[int(temp_df.loc[b*2,"Team ID"]), 'number_of_games'] > 0 and  side_datfram.loc[int(temp_df.loc[(b*2)+1,"Team ID"]), 'number_of_games'] > 0:
        transfer_df = temp_df[['Year', 'Week', 'Game ID', 'Team ID']].copy()
        transfer_df = pd.merge(transfer_df, main_datfram, left_on='Team ID', right_index = True)
        transfer_df['Win'] = temp_df['Win']
        training_data = training_data.append(transfer_df)
        del(transfer_df)

    #loop through the two teams for the current game to add to the total and average data frames. There will ALWAYS only be two teams playing.
    for c in range(b*2, (b*2)+2):
        team_id = int(temp_df.loc[c,'Team ID'])

        #Add a game to this team's number_of_games column of the side dataframe with aggregated data
        side_datfram.loc[team_id, 'number_of_games'] += 1

        #Goals (including 2 pt goals as 2 points)
        #add the stat for this row's team ID to the correct row of the side_datfram
        side_datfram.loc[team_id, 'total goals'] += temp_df.loc[c,'Goals']
        #now take the average and add it to the main_datfram
        main_datfram.loc[team_id, 'av goals'] = side_datfram.loc[team_id, 'total goals']/side_datfram.loc[team_id, 'number_of_games']

        #2 pt shots
        side_datfram.loc[team_id, 'total 2 pt shot'] += temp_df.loc[c,'2 Pt Shots']
        main_datfram.loc[team_id, 'av 2 pt shot'] = side_datfram.loc[team_id, 'total 2 pt shot']/side_datfram.loc[team_id, 'number_of_games']

        #2 pt % (total 2 pt goals)
        side_datfram.loc[team_id, 'total 2 pt goals'] += temp_df.loc[c,'2 Pt Shots']*(temp_df.loc[c,'2 Pt %']/100)
        if side_datfram.loc[team_id, 'total 2 pt shot'] != 0:
            main_datfram.loc[team_id, '2 pt %'] = side_datfram.loc[team_id, 'total 2 pt goals']/side_datfram.loc[team_id, 'total 2 pt shot']

        #Shots
        side_datfram.loc[team_id, 'total shots'] += temp_df.loc[c,'Shots']
        main_datfram.loc[team_id, 'av shots'] = side_datfram.loc[team_id, 'total shots']/side_datfram.loc[team_id, 'number_of_games']

        #shot % (Some shooting percentages in the PLL database may be incorrect. Some seem to divide # of goals by shots
        #and others seem to just divide the score by the number of shots.. May be something that needs to be corrected.
        side_datfram.loc[team_id, 'total goals (no 2 pt)'] += temp_df.loc[c,'Shots']*(temp_df.loc[c,'Shots %']/100)
        main_datfram.loc[team_id, 'shot %'] = side_datfram.loc[team_id, 'total goals (no 2 pt)']/side_datfram.loc[team_id, 'total shots']

        #gbs
        side_datfram.loc[team_id, 'total gb'] += temp_df.loc[c,'GB']
        main_datfram.loc[team_id, 'av gb'] = side_datfram.loc[team_id, 'total gb']/side_datfram.loc[team_id, 'number_of_games']

        #TOs
        side_datfram.loc[team_id, 'total TO'] += temp_df.loc[c,'TO']
        main_datfram.loc[team_id, 'av TO'] = side_datfram.loc[team_id, 'total TO']/side_datfram.loc[team_id, 'number_of_games']

        #CTOs
        side_datfram.loc[team_id, 'total CT'] += temp_df.loc[c,'CT']
        main_datfram.loc[team_id, 'av CT'] = side_datfram.loc[team_id, 'total CT']/side_datfram.loc[team_id, 'number_of_games']

        #av PowerPlay
        side_datfram.loc[team_id, 'total PP'] += temp_df.loc[c,'Power Play']
        main_datfram.loc[team_id, 'av PP'] = side_datfram.loc[team_id, 'total PP']/side_datfram.loc[team_id, 'number_of_games']

        #PP % : this quantity is reported in successful attempts and a percentage success rate which warrants division of the num
        if temp_df.loc[c,'PP %'] == 0:
            side_datfram.loc[team_id, 'total attempted PP'] += 0
        if temp_df.loc[c,'PP %'] > 0:
            side_datfram.loc[team_id, 'total attempted PP'] += temp_df.loc[c,'Power Play']/(temp_df.loc[c,'PP %']/100)
        if side_datfram.loc[team_id, 'total attempted PP'] > 0:
            main_datfram.loc[team_id, 'PP %'] = side_datfram.loc[team_id, 'total PP']/side_datfram.loc[team_id, 'total attempted PP']

        #Saves
        side_datfram.loc[team_id, 'total Saves'] += temp_df.loc[c,'Saves']
        main_datfram.loc[team_id, 'av Saves'] = side_datfram.loc[team_id, 'total Saves']/side_datfram.loc[team_id, 'number_of_games']

        #Save % : Divide saves by the save percentage to get total shots on goal and then divide saves by total shots on goal!
        side_datfram.loc[team_id, 'total shots on goal'] += temp_df.loc[c,'Saves']/(temp_df.loc[c,'Save %']/100)
        main_datfram.loc[team_id, 'Save %'] = side_datfram.loc[team_id, 'total Saves']/side_datfram.loc[team_id, 'total shots on goal']

        #now calculate quantities that depend on the other teams score in the game
        #could do this with a loop OR
        team_info = temp_df.loc[(temp_df['Game ID'] == temp_df.loc[c, 'Game ID']) & (temp_df['Team ID'] != team_id)]
        index = int(team_info.head(1).index.tolist()[0])

        #FO %
        total_FO = (4 + temp_df.loc[c, 'Goals'] + temp_df.loc[index, 'Goals'])
        side_datfram.loc[team_id, 'total FO'] += total_FO
        side_datfram.loc[team_id, 'total FO won'] += total_FO*(temp_df.loc[c,'FO %']/100)
        main_datfram.loc[team_id, 'FO %'] = side_datfram.loc[team_id, 'total FO won']/side_datfram.loc[team_id, 'total FO']
        #print(side_datfram.loc[team_id, 'total FO'], side_datfram.loc[team_id, 'total FO won'], main_datfram.loc[team_id, 'FO %'])

        #GAA
        side_datfram.loc[team_id, 'total GA'] += temp_df.loc[index, 'Goals']
        main_datfram.loc[team_id, 'GAA'] = side_datfram.loc[team_id, 'total GA']/side_datfram.loc[team_id, 'number_of_games']

        #Point Differential
        main_datfram.loc[team_id, 'Point Differential'] += temp_df.loc[c, 'Goals'] - temp_df.loc[index, 'Goals']

        #Streak
        if temp_df.loc[c, 'Win'] == 1:
            if main_datfram.loc[team_id, 'Streak'] >= 0:
                main_datfram.loc[team_id, 'Streak'] += 1
            if main_datfram.loc[team_id, 'Streak'] < 0:
                main_datfram.loc[team_id, 'Streak'] = 1
        if temp_df.loc[c, 'Win'] == 0:
            if main_datfram.loc[team_id, 'Streak'] > 0:
                main_datfram.loc[team_id, 'Streak'] = -1
            if main_datfram.loc[team_id, 'Streak'] <= 0:
                main_datfram.loc[team_id, 'Streak'] -= 1


#write training data to an excel sheet
print(training_data)
training_data.to_excel(writer, sheet_name='yeet')
writer.save()
writer.close()
