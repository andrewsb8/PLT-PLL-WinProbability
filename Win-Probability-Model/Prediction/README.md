The files in this directory are as follows:

Inputs -

- logreg model: pickle object of logistic regression model
- logreg scaler: pickle object of model scaler to apply to input data
- input.json: an example json file containing box score statistics for both teams in a game

Scripts -

- logreg_prediction_ingame.py: python script which takes the above as inputs and gives a output probability

Outputs -

- probabilities_vs_time.json: output json file with current win probabilities for each time as well as win probabilities vs "time" which are arrays appended to with each execution of logreg_prediction_ingame.py.
- prob_plot.png: exmaple output of the plot which is output as a result of input.json.
