import fh_request


class Matchup:
    def __init__(self, matchup_period_id, schedule, settings):
        self.id = matchup_period_id
        self.matchups = self.build_matchup_info(schedule)
        self.day_numbers = []
        self.set_date_range()
        self.day_data = {}
        self.name = settings['name']

    def build_matchup_info(self, schedule):
        ret_matchups = []
        for i in range(0, len(schedule)):
            if schedule[i]["matchupPeriodId"] == self.id:
                ret_matchups.append({"home": schedule[i]["home"]["teamId"], "away": schedule[i]["away"]["teamId"]})
        return ret_matchups

    def set_date_range(self):
        first_day_of_week = 7 * (self.id - 1) - 1
        for i in range(first_day_of_week, first_day_of_week+7):
            if i >= 0:
                self.day_numbers.append(i)

    def set_matchup_stats(self):
        for day in self.day_numbers:
            self.day_data[day] = fh_request.get_daily_stats(day)