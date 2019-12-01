import configparser
from datetime import datetime
import json
from os import path
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


def cache_helper(url, filename, authenticated=False, verbose=False):
    if path.exists(filename):
        with open(filename, 'r') as f:
            if verbose:
                print("Successfully opened {} from cache".format(filename))
            return json.loads(f.read())
    else:
        if authenticated:
            res = requests.get(url, cookies=cookies)
        else:
            res = requests.get(url)
        if res.status_code == 200:
            raw_json = res.json()
            with open(filename, 'w') as f:
                json.dump(raw_json, f)
            if verbose:
                print("Successfully saved {} to cache".format(filename))
            return raw_json
        else:
            print("Error {} -- could not access {}".format(res.status_code, url))


def get_matchup_scores(try_cache=True):
    if try_cache:
        day = datetime.now()
        filename = "raw_json/matchup_scores_from_day_{}".format(day.strftime("%d%m%y"))
        return cache_helper(matchup_scores_url, filename, authenticated=True)
    else:
        return requests.get(matchup_scores_url, cookies=cookies).json()


def get_pro_schedule(try_cache=True):
    if try_cache:
        day = datetime.now()
        filename = "raw_json/schedule_from_day_{}".format(day.strftime("%d%m%y"))
        return cache_helper(pro_team_schedule_url, filename)
    else:
        return requests.get(pro_team_schedule_url).json()


def get_daily_stats(day, try_cache=True):
    url = matchup_url_template.format(str(day))
    if try_cache:
        filename = "raw_json/day_{}.json".format(str(day))
        return cache_helper(url, filename, authenticated=True)
    else:
        return requests.get(url, cookies=cookies).json()


def get_league_info(try_cache=True):
    if try_cache:
        day = datetime.now()
        filename = "raw_json/league_info_day_{}".format(day.strftime("%d%m%y"))
        return cache_helper(league_base_info_url, filename, authenticated=True)
    else:
        return requests.get(league_base_info_url, cookies=cookies).json()
