# ProLacrosseTalk Win Probability Model for the Premier Lacrosse League

This repository contains the raw data used, scripts to clean and aggregate data and train a logistic regression win probability model and present the results in plot and json form. The method for generating the model is a little creative since there was not a large repository of historical professional lacrosse game data. The data that was available was only box scores and maybe scoring information.

In general, I went about creating a model this way:

- Take game results for each team in every single week.
- Generate weekly aggregate and average stats (e.g. Aggregates in Week 2 only consider Week 1 and aggregates in week 8 considered weeks 1 through 7.). Seasons were considered separately.
- The logistic regression model was trained against this aggregate data with the following logic. The difference between teams' aggregate stats may be good predictors of future performance. By using the difference, you could extrapolate this logic to in-game situations. For example, a team who scores six more goals on average than their opponent leading up to the matchup is more likely to win the upcoming game. Similarly, a team ahead by 6 goals within a game is the more likely team to win. The key was utilizing the **difference** between the teams' stats to determine an advantage or win probability.
- Box scores were recorded manually during games, due to lack of a live data feed, and win probabilities were calculated using the trained model periodically and then uploaded to the ProLacrosseTalk website as a plot.

Here is an example of one of the final win probability plots generated with this method followed by the box score:

![alt text](https://github.com/andrewsb8/PLT-PLL-WinProbability/blob/main/Win-Probability-Model/Prediction/prob_plot.png)

![alt text]()

Link to the ![https://stats.premierlacrosseleague.com/games/2021/championship-2021-9-19](game).

These figures were originally sent right to ![https://prolacrossetalk.com/lacrosse-betting/live-stats/](Pro Lacrosse Talk).
Later I made posts solely on ![https://twitter.com/swerdnanairb/status/1439655247836766210?s=20](Twitter).

The different folders contain scripts for data cleaning and model generation as well as examples of input and output. The data used for this project is in Weekly_Results of PLL_Data.xlsx.
