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
