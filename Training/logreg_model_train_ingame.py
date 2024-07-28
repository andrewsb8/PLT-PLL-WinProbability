import sys
import math
import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LogisticRegression

"""
Data is taken from PLL_Data.xlsx sheet Weekly Aggregates. Each game is taken and the stats
lines are subtracted. A logistic regression model is then trained based on the differences between
the two teams aggregated stats leading into the week in question. Win or lose will be defined
for the team with the lowest index in the current_game dataframe. Win = 1, Lose = -1.

Author: Brian Andrews
Last Date Modified: 5/21/2021
"""

#import the data to train the model
#Windows Path - backup location and also can be used for debugging/test environment
#raw_dat = pd.read_excel("C:\\Users\\BrianAndrews\\OneDrive\\Bracket_Prediction\\PLL\\PLL_Data.xlsx", sheet_name='Weekly Aggregates')
#Linux Path - "Production"
raw_dat = pd.read_excel("PLL_Data.xlsx", sheet_name='Weekly Aggregates')
raw_dat = raw_dat.iloc[:,1:] #remove the first column which only had the indexes from the data aggregation data frames
#print(raw_dat)

#create new dataframe with same columns as raw_dat
train_dat = pd.DataFrame(columns=raw_dat.columns)
train_dat = train_dat.drop(columns = ['Year','Week','Game ID','Team ID','Point Differential','Streak','Upsets','GAA','PP %'])

#number of entries
num_entries = raw_dat.shape[0]
#pull each game (2 rows each) and subtract the two stat lines to create the training data set
for i in range(0, num_entries, 2):
    current_game = raw_dat.loc[i:(i+1), :] #take two rows (1 game) at a time
    current_game = current_game.drop(columns = ['Year','Week','Game ID','Team ID','Point Differential','Streak','Upsets','GAA','PP %'])
    current_game.loc['Diff'] = current_game.iloc[0] - current_game.iloc[1]
    train_dat = train_dat.append(current_game.loc['Diff'], ignore_index = True)

#print(train_dat)

#separate the data into X and Y
X = train_dat.drop(columns = ['Win'])
Y = train_dat.loc[:,'Win']

#scale the data with a scaler
scale = RobustScaler()
scale.fit(X)
pickle.dump(scale, open("logreg_scaler","wb"))
x_train = scale.transform(X)

#now create the model to be trained and fit it to the data
#need to use a random_state to ensure same results
logreg = LogisticRegression(penalty = 'elasticnet', solver = 'saga', max_iter = 10000, fit_intercept = False, l1_ratio = 0)
logreg_model = logreg.fit(X, Y)

print(logreg_model.coef_,logreg_model.intercept_)

#MODEL IS TRAINED: output serialized version of the model
pickle.dump(logreg_model, open("logreg_model","wb"))
