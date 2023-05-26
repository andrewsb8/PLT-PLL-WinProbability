# ProLacrosseTalk Win Probability Model for the Premier Lacrosse League

This repository contains the raw data used, scripts to clean and aggregate data and train a logistic regression win probability model and present the results in plot and json form. The method for generating the model is a little creative due to the lack of a large repository of historical professional lacrosse game data and no time series data on a per-game basis available. The only data available was only box scores and some scoring information.

The data used for this project is in Weekly_Results and Weekly_Aggregates of PLL_Data.xlsx.

In general, I went about creating the model in the following way:

- Take game results for each team in every single week.
- Generate weekly aggregate and average stats (e.g. Aggregates in Week 2 only consider Week 1 and aggregates in week 8 considered weeks 1 through 7.). Seasons were considered separately.
- The logistic regression model was trained against this aggregate data with the following logic. The difference between teams' aggregate stats may be good predictors of future performance. By using the difference, you could extrapolate this logic to in-game situations. For example, a team who scores six more goals on average than their opponent leading up to the matchup is more likely to win the upcoming game. Similarly, a team ahead by 6 goals within a game is the more likely team to win. The key was utilizing the **difference** between the teams' stats to determine an advantage or win probability.
- Box scores were recorded manually during games, due to lack of a live data feed, and win probabilities were calculated using the trained model periodically and then uploaded to the ProLacrosseTalk website as a plot.

Here is the box score and the final win probability plots generated with this method:

![alt text](https://github.com/andrewsb8/PLT-PLL-WinProbability/blob/main/Win-Probability-Model/Prediction/championship_boxscore.png)

![alt text](https://github.com/andrewsb8/PLT-PLL-WinProbability/blob/main/Win-Probability-Model/Prediction/prob_plot.png)

You can see via the game flow that the Whipsnakes were narrowing their early game deficit in the second quarter and around half time. This is reflected by an actual advantage given to the Whipsnakes without an actual lead. Chaos were committing a large number of turnovers and losing their lead, and this is reflected in the Whipsnakes' win probability. The advantage quickly slipped away as the Chaos scored multiple successive goals in the third quarter and maintained the lead through the rest of the game.

Link to the [box score](https://stats.premierlacrosseleague.com/games/2021/championship-2021-9-19).

This model was originally uploaded to [Pro Lacrosse Talk](https://prolacrossetalk.com/lacrosse-betting/live-stats/) in real time (removed from prediction script for privacy) using the WordPress API. Later I made posts solely on [Twitter](https://twitter.com/swerdnanairb/status/1439655247836766210?s=20).
