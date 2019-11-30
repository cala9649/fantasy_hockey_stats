import fh_request


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

    def get_date_range(self, matchup_num):
        first_day_of_week = 7 * (matchup_num - 1) - 1
        scoring_period_range = []
        for i in range(first_day_of_week, first_day_of_week+7):
            if i >= 0:
                scoring_period_range.append(i)
        return scoring_period_range

    def set_matchup_stats(self):
        for day in self.day_numbers:
            self.day_data[day] = fh_request.get_daily_stats(day)

    def load_matchup_stats(self):
        for day in self.day_numbers:
            self.load_daily_stats(day)

    def load_daily_stats(self, day):
        with open('raw_json/day_{}.json'.format(str(day)), 'r') as f:
            self.day_data[day] = json.load(f)
