# -*- coding: utf-8 -*-
"""
This module contains functions that simulate runs of the 2021 NCAA tournament 
from the Sweet 16 onwards to calculate who is most likely to win a March 
Madness bracket pool.

The model uses 538's team rating data and their formula to calculate head to
head outcome probabilities to simulate tournament results round by round. Each
instance randomizes the outcomes of all Sweet 16 games and then uses those 
results to randomize the outcomes of subsequent rounds. These results are then
used to calculate resulting point totals for members of the bracket pool based
on their picks. It is also possible to run the model with a "coin flip" chance
for each team to win each game by setting probability='even' in the 
count_outcomes function. 

Team Ratings Source: https://projects.fivethirtyeight.com/march-madness-api/2021/fivethirtyeight_ncaa_forecasts.csv
Outcome probability calculation source: https://fivethirtyeight.com/features/how-our-march-madness-predictions-work-2/

The function 'count_outcomes' runs the tournament model for however many 
iterations you designate and then provides dictionaries with the total 1st 
place and last place finishes of each bracket participant along with 
dictionaries with the percent of the time that they finished first or last. 
This function also contains options for focusing on a certain participant's 
results, providing examples of bracket results that end in their winning the 
pool along with outputs detailing how often certain teams make certain rounds 
when they win so that they can pinpoint what teams they need to win or lose 
moving forward in order to win. 

The 'count_outcomes' function also allows you to run instances of the model 
where certain outcomes are guaranteed. for instance you could run the model 
with the stipulation that Baylor University makes the final 4 to see how that
outcome would change the spread of results. 

The function 'results to csv' will write the results to a csv file for easy 
import into an excel document to be shared with participants. 

This module relies on several CSVs to run properly:
    a CSV containing a complete list of picks for every participant
    a CSV containing the 538 rating data for each team
    a CSV containing the current points of each participant for rounds 1 and 2
    a CSV containing the schedule of each team should they advance to the next
    round - useful in determining resultant matchups in each subsequent round. 
"""

import csv
import random


def get_formatted_picks(filename):
    """Gets a formatted dictionary of each players picks"""
    picks, stage_dict, teams = {}, {}, []
    name, stage, last_stage, last_name = "", "", "", ""
    with open(filename) as picks_csv:
        reader = csv.reader(picks_csv)
        header_row = next(reader)
        for row in reader:
            # print(row)
            name = row[0]
            stage = row[1]
            team = row[2]
            if name != last_name and last_name != "":
                picks[last_name] = stage_dict
                stage_dict = {}
                teams = []
                teams.append(team)
            else:
                if stage != last_stage and last_stage != "":
                    stage_dict[last_stage] = teams
                    teams = []
                    teams.append(team)
                    if stage == "Champion":
                        stage_dict[stage] = [team]
                else:
                    teams.append(team)
            last_name = name
            last_stage = stage
        return picks


def get_pcts(filename):
    """Gets a formatted list of chances for each team in each round"""
    pct_dict = {}
    with open(filename) as pcts_csv:
        reader = csv.reader(pcts_csv)
        header_row = next(reader)
        team = ""
        pct1, pct2, pct3, pct4 = float(0), float(0), float(0), float(0)
        for row in reader:
            team = row[0]
            pct1 = float(row[1])
            pct2 = float(row[2])
            pct3 = float(row[3])
            pct4 = float(row[4])
            rating = float(row[5])
            pcts = [pct1, pct2, pct3, pct4, rating]
            pct_dict[team] = pcts
    return pct_dict


def get_teams_list(pct_dict):
    """Gets a list of all teams still in the tournament"""
    teams = []
    for team, lists in pct_dict.items():
        teams.append(team)
    return teams


def get_schedules(filename):
    """Gets a dictionary with everyone's possible games as value lists"""
    with open(filename) as schedules_csv:
        reader = csv.reader(schedules_csv)
        header_row = next(reader)
        schedules = {}
        for row in reader:
            team = row[0]
            games = []
            games.append(int(row[1]))
            games.append(int(row[2]))
            games.append(int(row[3]))
            games.append(float(row[4]))
            schedules[team] = games
    return schedules


def get_modeled_round(
    stage, current_teams, schedules, pcts, probability="scaled", final_4=[]
):
    """Gets a list of teams for a given round based on a list of teams in the previous round"""

    if stage == "elite eight":
        game1 = 1
        game2 = 8
    if stage == "final four":
        game1 = 9
        game2 = 12
    if stage == "championship":
        game1 = 13
        game2 = 14
    if stage == "champion":
        game1 = 15
        game2 = 15
    game_nums = [i for i in range(game1, game2 + 1)]
    games_dict = {}
    for i in game_nums:
        teams_in_game = []
        for team, games in schedules.items():
            if i in games and team in current_teams:
                teams_in_game.append(team)
        games_dict[i] = teams_in_game
    # print(games_dict)
    next_round = []
    for game, teams in games_dict.items():
        flag = 0
        team1_rating = pcts[teams[0]][4]
        team2_rating = pcts[teams[1]][4]
        team1_pct = int(
            10000 / (1 + 10 ** (-(team1_rating - team2_rating) * (30.464 / 400)))
        )
        team2_pct = int(
            10000 / (1 + 10 ** (-(team2_rating - team1_rating) * (30.464 / 400)))
        )

        outcome = random.randint(1, 10000)
        highest_pct = 0
        high_team = 0
        low_team = 0
        if team1_pct > team2_pct:
            highest_pct = team1_pct
            high_team = 0
            low_team = 1
        else:
            highest_pct = team2_pct
            high_team = 1
            low_team = 0
        for team in teams:
            if team in final_4:
                next_round.append(team)
                flag = 0
                break
            else:
                flag = 1
        if flag == 1:
            if outcome < highest_pct and probability == "scaled":
                next_round.append(teams[high_team])
            elif probability == "scaled":
                next_round.append(teams[low_team])
            if outcome < 5000 and probability == "even":
                next_round.append(teams[high_team])
            elif probability == "even":
                next_round.append(teams[low_team])
    return next_round


def get_current_points(filename):
    """Get the current points of a player returned as a dictionary"""
    current_points = {}
    with open(filename) as current_points_csv:
        reader = csv.reader(current_points_csv)
        header_row = next(reader)
        for row in reader:
            current_points[row[0]] = int(row[1])
    return current_points


def get_points(elite_eight, final_four, championship, champion, picks, filename):
    """Get the total points for a player based on a single iteration"""
    current_points_dict = get_current_points(filename)
    points_dict = {}
    for player, dicts in picks.items():
        points = 0
        current_points = current_points_dict[player]
        eight_count = 0
        for team in elite_eight:
            if team in dicts["Elite 8"]:
                eight_count += 1
        four_count = 0
        for team in final_four:
            if team in dicts["Final 4"]:
                four_count += 1
        championship_count = 0
        for team in championship:
            if team in dicts["Championship"]:
                championship_count += 1
        champion_count = 0
        for team in champion:
            if team in dicts["Champion"]:
                champion_count += 1
        points = (
            (40 * eight_count)
            + (80 * four_count)
            + (160 * championship_count)
            + (320 * champion_count)
            + current_points
        )
        points_dict[player] = points
    # print(points_dict)
    return points_dict


def get_winner(points_dict):
    """Gets the winner for an iteration"""
    high_score = 0
    winner = ""
    for player, score in points_dict.items():
        if score > high_score:
            winner = player
            high_score = score
        elif score == high_score:
            winner = "tie"
    # print(winner)
    return winner


def get_loser(points_dict):
    """Gets the winner for an iteration"""
    low_score = 10000
    loser = ""
    for player, score in points_dict.items():
        if score < low_score:
            loser = player
            low_score = score
        elif score == low_score:
            loser = "tie"
    # print(winner)
    return loser


def format_automatic_inclusion_lists(elite_8, final_4, champ_game, champ):
    for team in champ:
        if team not in champ_game:
            champ_game.append(team)
    for team in champ_game:
        if team not in final_4:
            final_4.append(team)
    for team in final_4:
        if team not in elite_8:
            elite_8.append(team)
    if len(champ_game) > 2 or len(final_4) > 4 or len(elite_8) > 8:
        print("Too many teams in a round. Fix error and run again.")
    else:
        return elite_8, final_4, champ_game, champ


def get_win_loss_pcts(win_count, loss_count, iterations):
    """Get the win and loss percentages by person based on the number of iterations"""
    win_pcts, loss_pcts = {}, {}
    for name, wins in win_count.items():
        win_pcts[name] = round(wins/iterations,3)
    for name, losses in loss_count.items():
        loss_pcts[name] = round(losses/iterations,3)
    return win_pcts, loss_pcts


def count_outcomes(
    iterations,
    schedules_file,
    current_points_file,
    probabilities_file,
    picks_file,
    win_check="",
    examples=False,
    advanced=False,
    probability="scaled",
    elite_8=[],
    final_4=[],
    champ_game=[],
    champ=[],
):
    """Counts the winners for a set of iterations"""

    # Bring in initial tournament and player bracket information
    pcts = get_pcts(probabilities_file)
    picks = get_formatted_picks(picks_file)
    schedules = get_schedules(schedules_file)

    # Establish the win and loss count dictionaries which will track each winner in the model
    win_count = {}
    loss_count = {}
    for name, pick_list in picks.items():
        win_count[name] = 0
    win_count["tie"] = 0
    for name, pick_list in picks.items():
        loss_count[name] = 0
    loss_count["tie"] = 0

    # Establish the dictionary counting the number of times a team is in each round per all iterations
    teams_round_counts = {}
    teams_list = []
    for team, games in schedules.items():
        teams_round_counts[team] = [0, 0, 0, 0]
        teams_list.append(team)
    elite_8, final4, champ_game, champ = format_automatic_inclusion_lists(
        elite_8, final_4, champ_game, champ
    )

    for i in range(0, iterations):
        elite_eight = get_modeled_round(
            "elite eight", teams_list, schedules, pcts, probability, elite_8
        )
        final_four = get_modeled_round(
            "final four", elite_eight, schedules, pcts, probability, final_4
        )
        championship = get_modeled_round(
            "championship", final_four, schedules, pcts, probability, champ_game
        )
        champion = get_modeled_round(
            "champion", championship, schedules, pcts, probability, champ
        )
        points_dict = get_points(
            elite_eight, final_four, championship, champion, picks, current_points_file
        )
        winner = get_winner(points_dict)
        win_count[winner] += 1
        loser = get_loser(points_dict)
        loss_count[loser] += 1

        if win_check == winner and examples == True:
            print("Winner: " + winner)
            print("Elite 8: " + str(elite_eight))
            print("Final 4: " + str(final_four))
            print("Championship: " + str(championship))
            print("Champion: " + str(champion))
            print(str(points_dict) + "\n")
        if advanced == True and win_check == winner:
            for curteam in teams_list:
                if curteam in elite_eight:
                    teams_round_counts[curteam][0] += 1
                if curteam in final_four:
                    teams_round_counts[curteam][1] += 1
                if curteam in championship:
                    teams_round_counts[curteam][2] += 1
                if curteam in champion:
                    teams_round_counts[curteam][3] += 1
    if advanced == True:
        for team, counts in teams_round_counts.items():
            temp_list = [0, 0, 0, 0]
            counter = 0
            for count in counts:
                try:
                    temp_list[counter] = round(count / win_count[win_check], 3)
                    counter += 1
                except ZeroDivisionError:
                    continue
            teams_round_counts[team] = temp_list
        print(
            "The percentage of times each team makes a certain round when "
            + win_check
            + " wins"
        )
        for team, counts in teams_round_counts.items():
            print(team + ": " + str(counts))
        print("")
        
    win_pcts, loss_pcts = get_win_loss_pcts(win_count, loss_count, iterations)
    
    return win_count, loss_count, win_pcts, loss_pcts


def results_to_csv(
    win_count,
    loss_count,
    win_pcts,
    loss_pcts,
    iterations,
    probability,
    filename="ncaa_outcomes.csv",
):
    """Creates a csv with the win and loss counts by player for a run of the model"""

    csv_lists = [
        [
            "These are the results of a model run with "
            + str(iterations)
            + " iterations using a "
            + probability
            + " probability model."
        ],
        ["player", "wins", "losses", "win pcts", "loss pcts"],
    ]

    for player, counts in win_count.items():
        csv_line = []
        csv_line.append(player)
        csv_line.append(win_count[player])
        csv_line.append(loss_count[player])
        csv_line.append(win_pcts[player])
        csv_line.append(loss_pcts[player])
        csv_lists.append(csv_line)
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for line in csv_lists:
            writer.writerow(line)
