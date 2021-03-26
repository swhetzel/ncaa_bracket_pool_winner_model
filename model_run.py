# -*- coding: utf-8 -*-
"""
This file provides an example of how the bracket model might be used.

It is currently set to run 10,000 iterations of the model and 
display the winners and losers of each run. It will also provide 
examples of brackets that lead to the participant "Stephen" winning
and will show advanced readouts with how often certain teams make
each round when he wins the bracket pool. No teams are currently set
to automatically make certain rounds in this model run. The probability
model is currently set to "scaled" which uses calculated probabilities
to determine the result of each matchup. 


"""
import bracket_model as ncaa

picks_file = "ncaa_picks.csv"
probabilities_file = "ncaa_pcts.csv"
current_points_file = "current_points.csv"
schedules_file = "ncaa_games.csv"
iterations = 10000
probability_setting = "scaled"

elite_eight = []
final_four = []
championship = []
champion = []

win_count, loss_count, win_pcts, loss_pcts = ncaa.count_outcomes(
    iterations,
    schedules_file,
    current_points_file,
    probabilities_file,
    picks_file,
    win_check="Stephen",
    examples=True,
    advanced=True,
    probability=probability_setting,
    elite_8=elite_eight,
    final_4=final_four,
    champ_game=championship,
    champ=champion,
)

ncaa.results_to_csv(win_count, loss_count, win_pcts, loss_pcts, iterations, probability_setting)


print("Win count: " + str(win_count))
print("Win pcts: " + str(win_pcts))
print("Loss count: " + str(loss_count))
print("Loss pcts: " + str(loss_pcts))
