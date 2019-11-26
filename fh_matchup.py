class Matchup:
    def __init__(self, matchupPeriodId, schedule, settings):
        self.id = matchupPeriodId
        self.matchups = self.build_matchup_info(schedule)
        self.days = self.get_date_range(matchupPeriodId)
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
