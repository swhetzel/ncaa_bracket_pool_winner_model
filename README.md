# ncaa_bracket_pool_winner_model
This repository contains code used to model who will win a NCAA bracket pool during the 2021 NCAA Men's basketball tournament. 

The model uses 538's team rating data and their formula to calculate head to head outcome probabilities to simulate tournament results round by round. Each instance of the model randomizes the outcomes of all Sweet 16 games and then uses those results to randomize the outcomes of subsequent rounds. These results are then used to calculate resulting point totals for members of the bracket pool based on their picks. 

Team Ratings Source: https://projects.fivethirtyeight.com/march-madness-api/2021/fivethirtyeight_ncaa_forecasts.csv
Outcome probability calculation source: https://fivethirtyeight.com/features/how-our-march-madness-predictions-work-2/

The function 'count_outcomes' in the bracket_model module runs the tournament model for however many iterations you designate and then provides dictionaries with the total 1st place and last place finishes of each bracket participant along with dictionaries with the percent of the time that each participant finished first or last. This function also contains options for focusing on a certain participant's results, providing examples of bracket results that end in their winning the pool along with outputs detailing how often certain teams make certain rounds when they win so that they can pinpoint what teams they need to win or lose moving forward in order to win the competition. 

The 'count_outcomes' function also allows you to run instances of the model where certain outcomes are guaranteed. For instance you could run the model with the stipulation that Baylor University makes the final 4 to see how that set outcome would change the spread of ultimate results. 

The function 'results to csv' in the bracket_model module writes the results of the model runs to a csv file for easy import into an excel document to be shared with participants. 

This repository relies on several CSVs to run the model properly:
    a CSV containing a complete list of picks for every participant
    a CSV containing the 538 rating data for each team
    a CSV containing the current points of each participant for rounds 1 and 2
    a CSV containing the schedule of each team should they advance to the next round - useful in determining resultant matchups in each subsequent round
