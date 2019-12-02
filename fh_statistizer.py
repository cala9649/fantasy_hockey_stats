from statistics import mean

playerPositions = {"forward": 3, "defense": 4, "goalie": 5, "util": 6, "bench": 7,
                   3: "forward", 4: "defense", 5: "goalie", 6: "util", 7: "bench"}


def calculate_luckiness(teams):
    league_luckiness = {}
    for luck_team in teams:
        skating_players = {}
        bench_players = {}
        for pos in luck_team.roster:
            for player in luck_team.roster[pos]:
                try:
                    if playerPositions[pos] == "bench":
                        bench_players[player] = {'avg': (luck_team.scores['total'][player] /
                                                         luck_team.player_num_games[player]) /
                                                 luck_team.averages[player], 'pos': playerPositions['bench']}
                    else:
                        skating_players[player] = {'avg': (luck_team.scores['total'][player] /
                                                           luck_team.player_num_games[player]) /
                                                   luck_team.averages[player], 'pos': pos}
                except (KeyError, ZeroDivisionError):
                    skating_players[player] = {'avg': 0, 'pos': pos}
        skating_stats = {}
        bench_stats = {}
        skating_stats['mean_luck'] = mean([skating_players[i]['avg'] for i in skating_players])
        skating_stats['lucky_player'] = {"name": "", "performance_percentage": 0}
        for player in skating_players:
            if skating_players[player]['avg'] > skating_stats['lucky_player']['performance_percentage']:
                skating_stats['lucky_player']['name'] = player
                skating_stats['lucky_player']['performance_percentage'] = skating_players[player]['avg']
                skating_stats['lucky_player']['pos'] = skating_players[player]['pos']
        skating_stats['unlucky_player'] = {"name": "", "performance_percentage": 10}
        for player in skating_players:
            if skating_players[player]['avg'] < skating_stats['unlucky_player']['performance_percentage']:
                skating_stats['unlucky_player']['name'] = player
                skating_stats['unlucky_player']['performance_percentage'] = skating_players[player]['avg']
                skating_stats['unlucky_player']['pos'] = skating_players[player]['pos']
        skating_stats['num_lucky'] = len([i for i in skating_players if 1.15 < skating_players[i]['avg'] <= 1.4])
        skating_stats['num_very_lucky'] = len([i for i in skating_players if 1.4 < skating_players[i]['avg'] <= 1.8])
        skating_stats['num_extremely_lucky'] = len([i for i in skating_players if skating_players[i]['avg'] > 1.8])
        skating_stats['num_unlucky'] = len([i for i in skating_players if 0.85 > skating_players[i]['avg'] >= 0.60])
        skating_stats['num_very_unlucky'] = len([i for i in skating_players if 0.60 > skating_players[i]['avg'] >= 0.4])
        skating_stats['num_extremely_unlucky'] = len([i for i in skating_players if skating_players[i]['avg'] < 0.4])
        bench_mean_luck = mean([bench_players[i]['avg'] for i in bench_players])
        bench_stats['lucky_player'] = {"name": "", "performance_percentage": 0}
        for player in bench_players:
            if bench_players[player]['avg'] > bench_stats['lucky_player']['performance_percentage']:
                bench_stats['lucky_player']['name'] = player
                bench_stats['lucky_player']['performance_percentage'] = bench_players[player]['avg']
                bench_stats['lucky_player']['pos'] = bench_players[player]['pos']
        bench_stats['unlucky_player'] = {"name": "", "performance_percentage": 10}
        for player in bench_players:
            if bench_players[player]['avg'] < bench_stats['unlucky_player']['performance_percentage']:
                bench_stats['unlucky_player']['name'] = player
                bench_stats['unlucky_player']['performance_percentage'] = bench_players[player]['avg']
                bench_stats['unlucky_player']['pos'] = bench_players[player]['pos']
        bench_stats['num_lucky'] = len([i for i in bench_players if 1.15 < bench_players[i]['avg'] <= 1.4])
        bench_stats['num_very_lucky'] = len([i for i in bench_players if 1.4 < bench_players[i]['avg'] <= 1.8])
        bench_stats['num_extremely_lucky'] = len([i for i in bench_players if bench_players[i]['avg'] > 1.8])
        bench_stats['num_unlucky'] = len([i for i in bench_players if 0.85 > bench_players[i]['avg'] >= 0.6])
        bench_stats['num_very_unlucky'] = len([i for i in bench_players if 0.6 > bench_players[i]['avg'] >= 0.4])
        bench_stats['num_extremely_unlucky'] = len([i for i in bench_players if bench_players[i]['avg'] < 0.4])
        league_luckiness[luck_team.id] = (skating_stats, bench_stats, skating_players, bench_players)
    return league_luckiness


def build_note(note_str, result, team_id):
    return {'note': note_str, 'res': result, 'team': team_id}


def find_notes(league_teams, week_matchup, weekly_averages):
    notes_list = []
    for team in league_teams:
        # MVP on the bench
        if team.mvp['player'] in team.bench.keys():
            notes_list.append(build_note("Team MVP ({}) was on the bench.".format(team.mvp['player']), "bad", team.id))
        num_bad_picks = len([player for player in team.opt_bench if player not in team.bench])
        # 5 or more bad picks
        if num_bad_picks >= 5:
            notes_list.append(build_note("Every benched player should have been in the lineup", "bad", team.id))
        # Team highest/lowest ever week score
        team_scores_hist = [score for score in weekly_averages[team.id].values()]
        try:
            if team.calc_total_score() >= max(team_scores_hist):
                notes_list.append(build_note("Highest ever weekly score!", "good", team.id))
            elif team.calc_total_score() <= min(team_scores_hist):
                notes_list.append(build_note("Lowest ever weekly score...", "bad", team.id))
        except ValueError:
            pass
        # Played 2 or more injured players
        num_injured_players = len([player for player in team.raw_player_data if team.raw_player_data[player]['injured']
                                  and player not in team.bench])
        if num_injured_players >= 2:
            notes_list.append(build_note("Played {} injured players".format(num_injured_players), "bad", team.id))
        # Players who scored 0 or less points
        num_useless_players = len([player for player in team.scores['total'] if team.scores['total'][player] <= 0
                                   and player not in team.bench])
        if num_useless_players >= 2:
            notes_list.append(build_note("{} players got 0 or fewer points this week".format(num_useless_players),
                                         "bad", team.id))
        # List all players who scored negative in the week
        negative_players = [{'name': player, 'score': team.scores['total'][player]} for player in team.scores['total']
                            if team.scores['total'][player] < 0 and player not in team.bench]
        if len(negative_players):
            for player in negative_players:
                note = "{} scored negative points this week ({})".format(player['name'], round(player['score'], 1))
                notes_list.append(build_note(note, "bad", team.id))
        # Did not play a complete lineup
        num_players = len([player for player in team.raw_player_data])
        if num_players < 22:
            notes_list.append(build_note("Did not play a complete lineup", "bad", team.id))
        # Find high/low score of the week
        matchup_scores = [team.calc_total_score() for team in league_teams]
        if team.calc_total_score() == max(matchup_scores):
            notes_list.append(build_note("Highest score for this matchup", "good", team.id))
        elif team.calc_total_score() == min(matchup_scores):
            notes_list.append(build_note("Lowest score for this matchup", "bad", team.id))
        # League MVP
        league_mvp_scores = [team.mvp['score'] for team in league_teams]
        if team.mvp['score'] == max(league_mvp_scores):
            notes_list.append(build_note("League MVP ({})".format(team.mvp['player']), "good", team.id))
        # Team's maximum possible score wouldnt have beat opponent
        matchup = [find_matchup for find_matchup in week_matchup.matchups if team.id in
                   [find_matchup['home'], find_matchup['away']]][0]
        matchup_opponent_id = matchup['home'] if team.id != matchup['home'] else matchup['away']
        matchup_opponent_score = league_teams[matchup_opponent_id - 1].calc_total_score()
        if team.calc_opt_total_score() < matchup_opponent_score:
            notes_list.append(build_note("Maximum possible score still wouldn't have won the matchup", "bad", team.id))
        # Note ideas:
        # Team never held the lead
    return notes_list
