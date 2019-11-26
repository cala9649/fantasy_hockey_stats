import json
import requests
import configparser

config = configparser.ConfigParser()
config.read('cookies.cfg')
cookies = {"SWID": config.get('cookies', 'SWID'), "espn_s2": config.get('cookies', 'espn_s2')}

pro_team_schedule_url = "https://fantasy.espn.com/apis/v3/games/fhl/seasons/2020?view=proTeamSchedules_wl"

playerPositions = {"forward": 3, "defense": 4, "goalie": 5, "util": 6, "bench": 7, 3: "forward", 4: "defense", 5: "goalie", 6: "util", 7: "bench"}

def predict_score(team, num_games):
    predicted_total = 0
    for pos in team.roster:
        for player in team.roster[pos]:
            if pos != playerPositions['bench']:
                predicted_total += num_games[player] * team.averages[player]
    return round(predicted_total,1)

def find_num_future_games(team, matchup_days):
    r = requests.get(pro_team_schedule_url)
    sched_json = json.loads(r.text)
    num_games = {}
    for player in team.raw_player_data:
        pro_team_id = team.raw_player_data[player]['proTeamId']
        pro_team = ""
        num_games[player] = 0
        for search_team in sched_json['settings']['proTeams']:
            if search_team['id'] == pro_team_id:
                pro_team = search_team
                break
        for game in pro_team['proGamesByScoringPeriod']:
            if int(game) in matchup_days:
                num_games[player] += 1
    return num_games

