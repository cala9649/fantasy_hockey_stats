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
                if playerPositions[pos] == "bench":
                    bench_players[player] = {'avg': (luck_team.scores['total'][player] /
                                                     luck_team.player_num_games[player]) /
                                             luck_team.averages[player], 'pos': playerPositions['bench']}
                else:
                    try:
                        skating_players[player] = {'avg': (luck_team.scores['total'][player] /
                                                           luck_team.player_num_games[player]) /
                                                   luck_team.averages[player], 'pos': pos}
                    except KeyError:    # TODO: this catches the case where a player did not play at all during the week
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


def find_notes(league_teams, league_luckiness, weekly_averages):
    notes_list = []
    for team in league_teams:
        if team.mvp['player'] in team.bench.keys():                                                   # MVP on the bench
            notes_list.append(build_note("Team MVP ({}) was on the bench.".format(team.mvp['player']), "bad", team.id))
        num_bad_picks = len([player for player in team.opt_bench if player not in team.bench])
        if num_bad_picks >= 5:                                                                             # 5 bad picks
            notes_list.append(build_note("Every benched player should have been in the lineup", "bad", team.id))
        team_scores = [score for score in weekly_averages[team.id].values()]
        if team.calc_total_score() >= max(team_scores):                                   # Team highest ever week score
            notes_list.append(build_note("Highest ever weekly score!", "good", team.id))
        if team.calc_total_score() <= min(team_scores):                                  # Team lowest ever weekly score
            notes_list.append(build_note("Lowest ever weekly score...", "bad", team.id))
        num_injured_players = len([player for player in team.raw_player_data if team.raw_player_data[player]['injured']
                           and player not in team.bench])
        if num_injured_players >= 2:                                                # Played more than 2 injured players
            notes_list.append(build_note("Played {} injured players".format(num_injured_players), "bad", team.id))
        num_useless_players = len([player for player in team.scores['total'] if team.scores['total'][player] <= 0
                                   and player not in team.bench])
        if num_useless_players >= 2:                                               # Players who scored 0 or less points
            notes_list.append(build_note("{} players got 0 or fewer points this week".format(num_useless_players),
                                         "bad", team.id))
        negative_players = [{'name': player, 'score': team.scores['total'][player]} for player in team.scores['total']
                            if team.scores['total'][player] < 0 and player not in team.bench]
        if len(negative_players):                                     # List all players who scored negative in the week
            for player in negative_players:
                note = "{} scored negative points this week ({})".format(player['name'], round(player['score'], 1))
                notes_list.append(build_note(note, "bad", team.id))
    return notes_list
