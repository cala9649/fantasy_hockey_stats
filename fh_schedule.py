import fh_request

playerPositions = {"forward": 3, "defense": 4, "goalie": 5, "util": 6, "bench": 7,
                   3: "forward", 4: "defense", 5: "goalie", 6: "util", 7: "bench"}


def find_weekly_averages(current_matchup_num):
    schedule = fh_request.get_matchup_scores()['schedule']
    team_weekly_scores = {'avg': {}}
    for team_num in range(1, 9):    # teams are numbered starting at 1 for some reason
        team_weekly_scores[team_num] = {}
    for game_num in range(1, current_matchup_num*4):    # games are numbered starting at 1 for some reason
        for team in ['home', 'away']:
            team_weekly_scores[schedule[game_num][team]['teamId']][game_num] = schedule[game_num][team]['totalPoints']
    for team_num in range(1, 9):    # teams are numbered starting at 1 for some reason
        total_pts = 0
        for game_num in team_weekly_scores[team_num]:
            total_pts += team_weekly_scores[team_num][game_num]
        team_weekly_scores['avg'][team_num] = total_pts / current_matchup_num
    return team_weekly_scores


def predict_score(team, num_games):
    predicted_total = 0
    for pos in team.roster:
        for player in team.roster[pos]:
            if pos != playerPositions['bench']:
                predicted_total += num_games[player] * team.averages[player]
    return round(predicted_total, 1)


def find_num_future_games(team, matchup_days):
    sched_json = fh_request.get_pro_schedule()
    num_games = {}
    for player in team.raw_player_data:
        pro_team_id = team.raw_player_data[player]['proTeamId']
        pro_team = {}
        num_games[player] = 0
        for search_team in sched_json['settings']['proTeams']:
            if search_team['id'] == pro_team_id:
                pro_team = search_team
                break
        for game in pro_team['proGamesByScoringPeriod']:
            if int(game) in matchup_days:
                num_games[player] += 1
    return num_games

