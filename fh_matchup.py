import json
import requests
import configparser

config = configparser.RawConfigParser()
config.read('cookies.cfg')
cookies = {"SWID": config.get('cookies', 'SWID'), "espn_s2": config.get('cookies', 'espn_s2')}
url_header = "https://fantasy.espn.com/apis/v3/games/fhl/seasons/2020/segments/0/leagues/{}".format(
    config.get('league', 'number'))
matchup_url_template = url_header + "?scoringPeriodId={}&view=mBoxscore&view=mMatchupScore&view=mRoster&" \
                                    "view=mSettings&view=mStatus&view=mTeam&view=modular&view=mNav"

class Matchup:
    def __init__(self, matchupPeriodId, schedule, settings):
        self.id = matchupPeriodId
        self.matchups = self.build_matchup_info(schedule)
        self.day_numbers = self.get_date_range(matchupPeriodId)
        self.day_data = {}
        self.name = settings['name']

    def build_matchup_info(self, schedule):
        ret_matchups = []
        for i in range(0, len(schedule)):
            if schedule[i]["matchupPeriodId"] == self.id:
                ret_matchups.append({"home": schedule[i]["home"]["teamId"], "away": schedule[i]["away"]["teamId"]})
        return ret_matchups

    def get_date_range(self, matchupNumber):
        firstDayOfWeek = 7 * (matchupNumber - 1) - 1
        scoringPeriodRange = []
        for i in range(firstDayOfWeek, firstDayOfWeek+7):
            if i >= 0:
                scoringPeriodRange.append(i)
        return scoringPeriodRange

    def request_matchup_stats(self, save_to_file=False):
        for day in self.day_numbers:
            self.request_daily_stats(day, save_to_file)

    def request_daily_stats(self, day, save_to_file):
        r = requests.get(matchup_url_template.format(str(day)), cookies=cookies)
        raw_json = json.loads(r.text)
        if save_to_file:
            with open('raw_json/day_{}.json'.format(str(day)), 'w') as f:
                json.dump(r.json(), f)
        self.day_data[day] = raw_json

    def load_matchup_stats(self):
        for day in self.day_numbers:
            self.load_daily_stats(day)

    def load_daily_stats(self, day):
        with open('raw_json/day_{}.json'.format(str(day)), 'r') as f:
            self.day_data[day] = json.load(f)