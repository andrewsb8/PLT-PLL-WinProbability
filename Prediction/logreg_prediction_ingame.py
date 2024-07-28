"""
****************************************************************************************************************
This script takes the box score of a PLL lacrosse game and predicts each team's
probability of winning the game based on a trained model.

#Author: Brian Andrews
#Last Date Modified: 6/5/2021
****************************************************************************************************************
"""

import sys
from datetime import datetime
import requests
import math
import numpy as np
import pandas as pd
import pickle
import json
import openpyxl
import matplotlib.pyplot as plt
from matplotlib.offsetbox import (TextArea, DrawingArea, OffsetImage, AnnotationBbox)
from matplotlib.cbook import get_sample_data
from wordpress_xmlrpc import Client, WordPressPost, WordPressPage
from wordpress_xmlrpc.methods import posts, media
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.compat import xmlrpc_client

with open("input.json") as json_dat_2:
    ext_data = json.load(json_dat_2)

teams = ['Whipsnakes', 'Chaos']

#construct the data frame that will hold the accumulated data
column_names = ['Goals', 'Assists', '2PtGoals', 'TotalScores', '2PtShots', '2Pt%','Shots', 'ShotPercentage', 'GroundBalls', 'Turnovers', 'CausedTurnovers','FaceoffWins','FaceoffLosses', 'FaceoffPercentage', 'ManUpGoals', 'ManUpOpportunities', 'ManUpPercentage', 'Saves', 'SavePercentage']
stat_table = pd.DataFrame(columns = column_names)
for team in teams:
    team_name = str(team)
    team_name = team_name[slice(len(team_name))]
    stat_table.loc[team_name] = [0 for ok in range(len(stat_table.columns))]
stat_table.loc["Diff"] = [0 for ok in range(len(stat_table.columns))]

for i in range(len(teams)):
    for stat in column_names:
        try:
            #print(data[team][team_name][position][i][stat])
            if stat == 'TotalScores':
                stat_table.loc[teams[i]][[stat]] = stat_table.loc[teams[i], 'Goals'] + 2*stat_table.loc[teams[i], '2PtGoals']
            elif stat == '2Pt%':
                stat_table.loc[teams[i]][[stat]] = float(stat_table.loc[teams[i], '2PtGoals']/stat_table.loc[teams[i], '2PtShots'])
            elif stat == 'ShotPercentage':
                stat_table.loc[teams[i]][[stat]] = float(stat_table.loc[teams[i], 'Goals']/stat_table.loc[teams[i], 'Shots'])
            elif stat == 'FaceoffPercentage':
                stat_table.loc[teams[i]][[stat]] = float(stat_table.loc[teams[i], 'FaceoffWins']/(stat_table.loc[teams[i], 'FaceoffWins'] + stat_table.loc[teams[i], 'FaceoffLosses']))
            elif stat == 'ManUpPercentage':
                stat_table.loc[teams[i]][[stat]] = float(stat_table.loc[teams[i], 'ManUpGoals']/stat_table.loc[teams[i], 'ManUpOpportunities'])
            #elif stat == 'SavePercentage':
                #print(team_name, other_team,stat_table.loc[other_team, 'Goals'], stat_table.loc[other_team, '2PtGoals'], stat_table.loc[team_name, 'Saves'])
                #stat_table.loc[team_name][[stat]] = float(stat_table.loc[team_name, 'Saves']/(stat_table.loc[other_team, 'Goals'] + stat_table.loc[other_team, '2PtGoals'] + stat_table.loc[team_name, 'Saves']))
            else:
                stat_table.loc[teams[i]][[stat]] = ext_data[teams[i]][stat]
                if stat == 'Goals':
                    print(team_name,position,data[teams[i]][team_name][position][j]['lastName'], data[teams[i]][team_name][position][j][stat])
        except:
            #print(stat, ": Already included or calculated elsewhere")
            continue


for i in range(len(teams)):
    team_name = str(teams[i])
    team_name = team_name[slice(len(team_name))]
    other_team = str(teams[i-1])
    other_team = other_team[slice(len(other_team))]
    print(team_name, other_team,stat_table.loc[other_team, 'Goals'], stat_table.loc[other_team, '2PtGoals'], stat_table.loc[team_name, 'Saves'])
    if stat_table.loc[other_team, 'Goals'] + stat_table.loc[other_team, '2PtGoals'] + stat_table.loc[team_name, 'Saves'] > 0:
        stat_table.loc[team_name][['SavePercentage']] = float(stat_table.loc[team_name, 'Saves']/(stat_table.loc[other_team, 'Goals'] + stat_table.loc[other_team, '2PtGoals'] + stat_table.loc[team_name, 'Saves']))
    else:
        stat_table.loc[team_name][['SavePercentage']] = 0

print(stat_table)

#*******************************************************************************************************
#begin model prediction

print("Starting prediction...")

stat_table.loc['Diff'] = stat_table.iloc[0] - stat_table.iloc[1]

model_data = pd.DataFrame(columns = stat_table.columns)
model_data = model_data.append(stat_table.loc['Diff'])

model_data = model_data.drop(columns =  ['Goals', 'Assists', '2PtGoals','FaceoffWins','FaceoffLosses', 'ManUpOpportunities', 'ManUpPercentage'])

print("Scaling data...")

#apply the scaler to the test data
scale = pickle.load(open("/hdd/PLT_Probability_Engine/v0.0.2/ingame_model/logreg_scaler","rb"))
model_dat = scale.transform(model_data)

print("loading model...")

#load the model
logreg_model = pickle.load(open("/hdd/PLT_Probability_Engine/v0.0.2/ingame_model/logreg_model","rb"))
#predict outcomes
yeet = logreg_model.predict(model_data)
print(yeet)
yeet_proba = logreg_model.predict_proba(model_data)
print(yeet_proba[0])

#********************************************************************************************************
#Record the probabilites

print("recording probabilities")

with open("/hdd/PLT_Probability_Engine/v0.0.2/ingame_model/probabilities_v_time.json") as json_again:
    probs = json.load(json_again)

print("loaded probs v time")

leng = len(probs['Time'])
probs['Time'].append(len(probs['Time']))
for i in range(len(teams)):
    team_name = str(teams[i])
    team_name = team_name[slice(len(team_name))]
    probs[team_name].append(yeet_proba[0][i-1])
    current_prob_key = team_name + '_current'
    probs[current_prob_key] = yeet_proba[0][i-1]

with open("/hdd/PLT_Probability_Engine/v0.0.2/ingame_model/probabilities_v_time.json", "w") as json_out_again:
    json.dump(probs, json_out_again)

#print(probs)

#******************************************************************************************************
#Update box score file

print("writing excel and json files\n")

#print(stat_table)
writer = pd.ExcelWriter("/hdd/PLT_Probability_Engine/v0.0.2/ingame_model/test_game_1_box_" + str(leng) + ".xlsx", engine='openpyxl')
stat_table.iloc[:2].to_excel(writer)
writer.save()
writer.close()

stat_json = stat_table.iloc[:2].to_json()
with open("/hdd/PLT_Probability_Engine/v0.0.2/ingame_model/game_1_box_" + str(leng) + ".json","w") as json_out:
    json.dump(stat_json, json_out)

#**********************************************************************************************************
#plot the probabilities

for j in range(len(teams)-1):
    team_name = str(teams[j])
    team_name = team_name[slice(len(team_name))]

fig, ax = plt.subplots()
plt.title("Win Probability vs Time")

#plot data
plt.plot(probs['Time'], [0.5 for a in range(len(probs['Time']))], '--', color = "0.5")
plt.plot(probs['Time'], [0.25 for a in range(len(probs['Time']))], '--', color = "0.5")
plt.plot(probs['Time'], [0.75 for a in range(len(probs['Time']))], '--', color = "0.5")
plt.plot(probs['Time'], probs[team_name])
plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=False,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelbottom=False) # labels along the bottom edge are off
plt.ylim(0,1)
#plt.yticks(np.arange(0,1.01,0.25))
plt.yticks(np.arange(0,1.01,0.1))
fig.canvas.draw()

#change y axis labels
labels = [item.get_text() for item in ax.get_yticklabels()]
labels[0] = '100 %'
labels[1] = '90 %'
labels[2] = '80 %'
labels[3] = '70 %'
labels[4] = '60 %'
labels[5] = '50 %'
labels[6] = '60 %'
labels[7] = '70 %'
labels[8] = '80 %'
labels[9] = '90 %'
labels[10] = '100 %'

ax.set_yticklabels(labels)

#add team names
ax.text(probs['Time'][-1]+3.5, 1.03, str(teams[0]))
ax.text(probs['Time'][-1]+3.5, -0.05, str(teams[1]))

#add team images
arr_img = plt.imread("../../logos/" + teams[0] + ".png")

xy = [0.3, 0.55]

imagebox = OffsetImage(arr_img, zoom=0.2)
imagebox.image.axes = ax

ab = AnnotationBbox(imagebox, xy,
                    xybox=(probs['Time'][-1]+8, .9),
                    xycoords='data',
                    frameon = False
                    )

ax.add_artist(ab)

arr_img = plt.imread("../../logos/" + teams[1] + ".png")

xy = [0.3, 0.55]

imagebox = OffsetImage(arr_img, zoom=0.2)
imagebox.image.axes = ax

ab = AnnotationBbox(imagebox, xy,
                    xybox=(probs['Time'][-1]+8, .12),
                    xycoords='data',
                    frameon = False
                    )

ax.add_artist(ab)

#**********************************************************************************
#Add company logos

#PLL
arr_img = plt.imread("../../logos/PLL.png")

xy = [0.3, 0.55]

imagebox = OffsetImage(arr_img, zoom=0.1)
imagebox.image.axes = ax

ab = AnnotationBbox(imagebox, xy,
                    xybox=(probs['Time'][0]-10, 1.10),
                    xycoords='data',
                    frameon = False
                    )

ax.add_artist(ab)

#PLT
arr_img = plt.imread("../../logos/PLT.png")

xy = [0.3, 0.55]

imagebox = OffsetImage(arr_img, zoom=0.25)
imagebox.image.axes = ax

ab = AnnotationBbox(imagebox, xy,
                    xybox=(probs['Time'][0]-3, 1.10),
                    xycoords='data',
                    frameon = False
                    )

ax.add_artist(ab)

#LPG
arr_img = plt.imread("../../logos/LPG.png")

xy = [0.3, 0.55]

imagebox = OffsetImage(arr_img, zoom=0.08)
imagebox.image.axes = ax

ab = AnnotationBbox(imagebox, xy,
                    xybox=(probs['Time'][0]+4, 1.10),
                    xycoords='data',
                    frameon = False
                    )

ax.add_artist(ab)

#***********************************************************************************
#Add my name!
ax.text(probs['Time'][0]-12, -0.08, "Created by: Brian Andrews")
ax.text(probs['Time'][0]-12, -0.12, "Twitter: @swerdnanairb")

#extend graph so that the images aren't cut off
plt.subplots_adjust(right = 0.8)

plt.savefig("prob_plot.png")

