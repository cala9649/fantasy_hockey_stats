import json
import requests
import configparser

config = configparser.ConfigParser()
config.read('cookies.cfg')
cookies = {"SWID": config.get('cookies', 'SWID'), "espn_s2": config.get('cookies', 'espn_s2')}
url_header = "https://fantasy.espn.com/apis/v3/games/fhl/seasons/2020/segments/0/leagues/{}".format(config.get('league', 'number'))
league_base_info_url = url_header + "?view=mMatchupScore&view=mTeam&view=mSettings"
matchup_url_template = url_header + "?scoringPeriodId={}&view=mBoxscore&view=mMatchupScore&view=mRoster&view=mSettings&view=mStatus&view=mTeam&view=modular&view=mNav"

playerPositions = {"forward": 3, "defense": 4, "goalie": 5, "util": 6, "bench": 7, 3: "forward", 4: "defense", 5: "goalie", 6: "util", 7: "bench"}

class Team:
    def __init__(self, id, abbrev, loc, nick, ownerId, logo_url):
        self.id =       id
        self.abbrev =   abbrev
        self.loc =      loc
        self.nick =     nick
        self.ownerId =  ownerId
        self.owner =    ''
        self.dispName = ''
        self.roster =   {3: [], 4: [], 5: [], 6: [], 7: []}
        self.bench =    {}
        self.util =     {}
        self.scores =   {'total': {}}
        self.averages = {}
        self.player_num_games = {}
        self.logo = logo_url
        self.opt_roster =   {3: [], 4: [], 5: [], 6: [], 7: []}
        self.opt_bench =    {}
        self.mvp = {'player': "", 'score': 0, 'pos': ""}
        self.raw_player_data = {}

    def find_optimum_lineup(self):
        roster_allowed_per_position = {3: 9, 4: 5, 5: 2, 6: 1, 7: 5}
        tmp_roster = {3: [], 4: [], 5: [], 6: [], 7: []}
        for pos in self.roster:
            for player in self.roster[pos]:
                if pos == playerPositions['bench']:
                    bench_pos = 3 if self.bench[player] <= 3 else self.bench[player]
                    tmp_roster[bench_pos].append(player)
                elif pos == playerPositions['util']:
                    util_pos = 3 if self.util[player] <= 3 else self.util[player]
                    tmp_roster[util_pos].append(player)
                else:
                    tmp_roster[pos].append(player)
                if player not in(self.scores['total'].keys()):
                    self.scores['total'][player] = 0
        opt_scores = {3: [], 4: [], 5: [], 6: [], 7: []}
        for pos in tmp_roster:
            for player in tmp_roster[pos]:
                opt_scores[pos].append(self.scores['total'][player])
        # Set up list to compare top scores
        for pos in opt_scores:
            opt_scores[pos] = sorted(opt_scores[pos])
            opt_scores[pos].reverse()
        util_players = []
        util_scores = []
        # Fill fwds, defense, & goalies
        for pos in tmp_roster:
            for player in tmp_roster[pos]:
                if self.scores['total'][player] >= opt_scores[pos][roster_allowed_per_position[pos]-1]:
                    self.opt_roster[pos].append(player)
                elif pos in [3, 4]:
                    util_players.append(player)
                    util_scores.append(self.scores['total'][player])
                else:
                    self.opt_roster[playerPositions['bench']].append(player)
                    self.opt_bench[player] = pos
        # pick best util player
        # TODO: causes an error if the week doesn't have complete data
        max_score_index = util_scores.index(max(util_scores))
        self.opt_roster[playerPositions['util']].append(util_players[max_score_index])
        util_players.pop(max_score_index)
        util_scores.pop(max_score_index)
        # place all other players on the bench
        for player in util_players:
            self.opt_roster[playerPositions['bench']].append(player)
            if player in tmp_roster[3]:
                self.opt_bench[player] = 3
            else:
                self.opt_bench[player] = 4

    def find_mvp(self):
        for player in self.scores['total']:
            if self.scores['total'][player] > self.mvp['score']:
                self.mvp['player'] = player
                self.mvp['score'] = round(self.scores['total'][player],1)
                for pos in self.roster:
                    if player in self.roster[pos]:
                        self.mvp['pos'] = playerPositions[pos]

    def calc_total_score(self):
        score_total = 0
        for player in self.scores['total']:
            if player not in self.bench.keys():
                score_total += self.scores['total'][player]
        return round(score_total,1)

    def calc_opt_total_score(self):
        opt_score_total = 0
        for player in self.scores['total']:
            if player not in self.opt_bench.keys():
                opt_score_total += self.scores['total'][player]
        return round(opt_score_total,1)

    def __str__(self):
        return "{} {} [{}]\n{}".format(self.loc, self.nick, self.abbrev, {'id': self.id, 'ownerId': self.ownerId, 'owner': self.owner, 'dispName': self.dispName, 'roster': self.roster, 'bench': self.bench, 'util': self.util, 'scores': self.scores})

class League:
    def __init__(self):
        raw_info = self.get_league_info()
        self.schedule = raw_info['schedule']
        self.settings = raw_info['settings']
        self.teams = []
        self.raw_teams = raw_info['teams']
        self.members = raw_info['members']

    def get_league_info(self):
        # This might only return the current league info?
        r = requests.get(league_base_info_url, cookies=cookies)
        league_info = json.loads(r.text)
        return league_info

    def build_teams(self, scoringPeriodRange):
        for team in self.raw_teams:
            self.teams.append(Team(team['id'], team['abbrev'], team['location'], team['nickname'], team['owners'][0], team['logo']))
        for team in self.teams:
            for dude in self.members:
                if dude['id'] == team.owner:
                    team.dispName = dude['displayName']
                    team.owner = dude['firstName'] + " " + dude['lastName']
                    break
            for day in scoringPeriodRange:
                team.scores[day] = {}

    def build_scores(self, scoringPeriodRange):
        for day in scoringPeriodRange:
            matchup_data = get_daily_stats(day)
            for matchup_team in matchup_data['teams']:
                players = matchup_team['roster']['entries']
                full_roster = []
                team = [i for i in self.teams if i.id == matchup_team['id']][0]
                for pos in team.roster:
                    full_roster += team.roster[pos]
                for playa in players:
                    stats_list = playa['playerPoolEntry']['player']['stats']
                    playa_name = playa['playerPoolEntry']['player']['fullName']
                    team.raw_player_data[playa_name] = playa['playerPoolEntry']['player']
                    if not(playa_name in full_roster):
                        full_roster += [playa_name]
                        if playa['lineupSlotId'] == playerPositions['bench']:
                            team.bench[playa_name] = playa['playerPoolEntry']['player']['defaultPositionId']
                        elif playa['lineupSlotId'] == playerPositions['util']:
                            team.util[playa_name] = playa['playerPoolEntry']['player']['defaultPositionId']
                        team.roster[playa['lineupSlotId']] += [playa_name]
                    for stat in stats_list:
                        if stat['scoringPeriodId'] == day:
                            team.scores[day][playa_name] = stat['appliedTotal']
                            try:
                                team.scores['total'][playa_name] += stat['appliedTotal']
                            except KeyError:
                                team.scores['total'][playa_name] = stat['appliedTotal']
                            try:
                                team.player_num_games[playa_name] += 1
                            except KeyError:
                                team.player_num_games[playa_name] = 1
                        elif stat['id'] == "002020":
                            team.averages[playa_name] = stat['appliedAverage']

    def find_league_optimum_lineups(self):
        for team in self.teams:
            team.find_optimum_lineup()

    def find_league_mvps(self):
        for team in self.teams:
            team.find_mvp()

def get_daily_stats(day):
    r = requests.get(matchup_url_template.format(day), cookies=cookies)
    return json.loads(r.text)
