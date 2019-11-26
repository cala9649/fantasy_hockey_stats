import fh_matchup
import fh_league
import fh_output
import fh_statistizer
import fh_schedule


def generate_weekly_report(matchup_number):
    teams = []
    my_league = fh_league.League()
    week_matchup = fh_matchup.Matchup(matchup_number, my_league.schedule, my_league.settings)
    my_league.build_teams(week_matchup.days)
    my_league.build_scores(week_matchup.days)
    my_league.find_league_optimum_lineups()
    my_league.find_league_mvps()
    league_luckiness = fh_statistizer.calculate_luckiness(my_league.teams)
    fh_output.generate_weekly_report(matchup_number, week_matchup, my_league.teams, league_luckiness)

def make_predictions(matchup_number):
    teams = []
    my_league = fh_league.League()
    week_matchup = fh_matchup.Matchup(matchup_number, my_league.schedule, my_league.settings)
    my_league.build_teams(week_matchup.days)
    my_league.build_scores(week_matchup.days)
    for matchup in week_matchup.matchups:
        home_team = my_league.teams[matchup['home']-1]
        home_num_games = fh_schedule.find_num_future_games(home_team, week_matchup.days)
        away_team = my_league.teams[matchup['away']-1]
        away_num_games = fh_schedule.find_num_future_games(away_team, week_matchup.days)
        print("{} {} - {}".format(home_team.loc, home_team.nick, fh_schedule.predict_score(home_team, home_num_games)))
        print("   vs   ")
        print("{} {} - {}".format(away_team.loc, away_team.nick, fh_schedule.predict_score(away_team, away_num_games)))
        print("\n\n")

if __name__ == "__main__":
    matchup_number = 8
    generate_weekly_report(matchup_number)
    # make_predictions(matchup_number)
