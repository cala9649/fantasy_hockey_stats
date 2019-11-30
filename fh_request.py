import configparser
import json
import requests

config = configparser.RawConfigParser()
config.read('cookies.cfg')
cookies = {"SWID": config.get('cookies', 'SWID'), "espn_s2": config.get('cookies', 'espn_s2')}

pro_team_schedule_url = "https://fantasy.espn.com/apis/v3/games/fhl/seasons/2020?view=proTeamSchedules_wl"
matchup_scores_url = "https://fantasy.espn.com/apis/v3/games/fhl/seasons/2020/segments/0/leagues/{}" \
                     "?view=mMatchupScore".format(config.get('league', 'number'))
url_header = "https://fantasy.espn.com/apis/v3/games/fhl/seasons/2020/segments/0/leagues/{}".format(
    config.get('league', 'number'))
matchup_url_template = url_header + "?scoringPeriodId={}&view=mBoxscore&view=mMatchupScore&view=mRoster&" \
                                    "view=mSettings&view=mStatus&view=mTeam&view=modular&view=mNav"
league_base_info_url = url_header + "?view=mMatchupScore&view=mTeam&view=mSettings"


def get_matchup_scores():
    return requests.get(matchup_scores_url, cookies=cookies).json()


def get_pro_schedule():
    return requests.get(pro_team_schedule_url).json()


# def request_matchup_stats(save_to_file=False):
#     for day in self.day_numbers:
#         get_daily_stats(day, save_to_file)
#

def get_daily_stats(day, save_to_file=False):
    # raw_json = json.loads(r.text)
    # if save_to_file:
    #     with open('raw_json/day_{}.json'.format(str(day)), 'w') as f:
    #             json.dump(r.json(), f)
    return requests.get(matchup_url_template.format(str(day)), cookies=cookies).json()


def get_league_info():
    return requests.get(league_base_info_url, cookies=cookies).json()
