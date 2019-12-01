import pdfkit

playerPositions = {"forward": 3, "defense": 4, "goalie": 5, "util": 6, "bench": 7,
                   3: "forward", 4: "defense", 5: "goalie", 6: "util", 7: "bench"}

pdfkit_options = {
    'page-size': 'A4',
    'margin-top': '0in',
    'margin-right': '0in',
    'margin-bottom': '0in',
    'margin-left': '0in',
    'encoding': "UTF-8",
    'no-outline': None
}


def display_roster_html(html_team):
    roster_skeleton = "\n<div class='player-position'>{}</div>\n<div class='player-names'>{}</div>\n"
    roster_formatted = ""
    picked_skaters = html_team.roster[playerPositions["forward"]] + html_team.roster[playerPositions["defense"]] \
                            + html_team.roster[playerPositions["goalie"]] + html_team.roster[playerPositions["util"]]
    for pos in [playerPositions["forward"], playerPositions["defense"], playerPositions["util"]]:
        skaters_html_list = []
        for player in html_team.opt_roster[pos]:
            if player not in picked_skaters:
                skaters_html_list.append("<span class='bad_pick'>{}</span>".format(player))
            else:
                skaters_html_list.append("{}".format(player))
        roster_formatted += roster_skeleton.format(playerPositions[pos][0].capitalize(), ', '.join(skaters_html_list)
                                                   + "<br>\n")
    goalies_html_list = []
    for player in html_team.opt_roster[playerPositions["goalie"]]:
        if player not in picked_skaters:
            goalies_html_list.append("<span class='bad_pick'>{}</span>".format(player))
        else:
            goalies_html_list.append("{}".format(player))
    roster_formatted += roster_skeleton.format("G", ', '.join(goalies_html_list) + "<br>\n")
    bench_html_list = []
    for player in html_team.opt_roster[playerPositions["bench"]]:
        if player in picked_skaters:
            bench_html_list.append("<span class='bad_pick'>{} ({})</span>"
                                   .format(player, playerPositions[html_team.opt_bench[player]][0].capitalize()))
        else:
            bench_html_list.append("{} ({})".format(player,
                                                    playerPositions[html_team.opt_bench[player]][0].capitalize()))
    roster_formatted += roster_skeleton.format("B", ', '.join(bench_html_list) + "\n")
    return roster_formatted


def build_daily_score_line_chart(home_team, away_team):
    chart = ""
    chart += "<div>\n<canvas id='daily_score_line_chart_{}_{}'></canvas>\n</div>\n".format(home_team.loc, away_team.loc)
    chart += "<script>\n"
    chart += "var daily_score_line_chart_{0}_{1}_config = ".format(home_team.loc, away_team.loc)
    chart += "{type: 'line',\n" \
             "options: {responsive: false, aspectRatio: 1.5, title: {text: 'Scores by Day', display: true}," \
             "animation: {duration: 0}},\n" \
             "data: {\nlabels: "
    day_numbers = []
    for i in home_team.scores.keys():
        try:
            int(i)
            day_numbers.append(str(i))
        except ValueError:
            pass
    day_numbers.sort()
    chart += "['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],\n"
    chart += "datasets: ["
    for team in [home_team, away_team]:
        chart += "{"
        chart += "label: '{} {}', ".format(team.loc, team.nick)
        chart += "lineTension: 0.1, "
        if team == home_team:
            chart += "backgroundColor: 'rgb(255,0,0)',\nborderColor: 'rgb(255,0,0)', "
        else:
            chart += "backgroundColor: 'rgb(0,0,255)',\nborderColor: 'rgb(0,0,255)', "
        chart += "fill: false, "
        chart += "data: "
        scores = []
        weekly_total = 0
        for day in day_numbers:
            weekly_total += team.calc_daily_score(int(day))
            scores.append(str(weekly_total))
        chart += "[" + ", ".join(scores) + "], "
        chart += "},\n"
    chart += "]\n}\n};\n"
    chart += "</script>\n"
    on_load = "var daily_score_line_chart_{0}_{1}_ctx = document.getElementById('daily_score_line_chart_{0}_{1}')" \
              ".getContext('2d');\n".format(home_team.loc, away_team.loc)
    on_load += "var line_{0}_{1} = new Chart(daily_score_line_chart_{0}_{1}_ctx, " \
               "daily_score_line_chart_{0}_{1}_config);\n".format(home_team.loc, away_team.loc)
    return chart, on_load


def build_player_luck_dist_chart(league_luckiness, home_team, away_team):
    chart = ""
    chart += "<div>\n<canvas id='player_luck_dist_chart_{}_{}'></canvas>\n</div>\n".format(home_team.loc, away_team.loc)
    chart += "<script>\n"
    chart += "var player_luck_dist_chart_{}_{}_config = ".format(home_team.loc, away_team.loc)
    chart += "{type: 'line',\n" \
             "options: {responsive: false, aspectRatio: 1.5, animation: {duration: 0}, title: {text: '"
    chart += "Player Luck Distribution"
    chart += "', display: true}, scales: { yAxes: [{ ticks: { suggestedMin: 0, suggestedMax: 20}}]}},\n"
    chart += "data: { labels: ['-100%', '-50%', '-25%', 'avg', '+25%', '+50%', '+100%'], datasets: ["
    for team in [home_team, away_team]:
        team_luck = league_luckiness[team.id][0]
        data = [team_luck['num_extremely_unlucky'], team_luck['num_very_unlucky'], team_luck['num_unlucky'],
                team_luck['num_lucky'], team_luck['num_very_lucky'], team_luck['num_extremely_lucky']]
        data.insert(3, 22 - sum(data))
        chart += "{"
        chart += "label: '{} {}', ".format(team.loc, team.nick)
        if team == home_team:
            chart += "backgroundColor: 'rgb(255,0,0)', borderColor: 'rgb(255,0,0)', "
        else:
            chart += "backgroundColor: 'rgb(0,0,255)', borderColor: 'rgb(0,0,255)', "
        chart += "fill: false, "
        chart += "data: {}".format(str(data))
        chart += "}, "
    # chart += "]}"
    chart += "]}\n};\n"
    chart += "</script>\n"
    on_load = "var player_luck_dist_chart_{0}_{1}_ctx = document.getElementById('player_luck_dist_chart_{0}_{1}')" \
              ".getContext('2d');\n".format(home_team.loc, away_team.loc)
    on_load += "var bar_{0} = new Chart(player_luck_dist_chart_{0}_{1}_ctx, player_luck_dist_chart_{0}_{1}_config);" \
               "\n".format(home_team.loc, away_team.loc)
    return chart, on_load


def display_averages_html(team_weekly_scores, team_avg):
    return "<b>Avg Pts/Wk</b>: {}<br>".format(round(team_avg, 1))


def build_matchup_row(matchup, league_name, week_num, html_teams, html_league_luckiness, html_weekly_averages):
    row = "<div class='matchup_row'>\n"
    row += "<h1>\n{} - Week {}</h1>".format(league_name, week_num)
    for team in ['away', 'home']:
        row += "<div class='matchup_cell_wrapper {}'>\n".format(team)
        row += "<div class='matchup_cell'>"
        luck_info = "<b>Luck:</b> <span class='right'>{}%</span>\n".format(
            int(html_league_luckiness[html_teams[matchup[team] - 1].id][0]['mean_luck'] * 100) - 100)
        max_score_info = "<b>Max: </b><span class='right'>{}</span>" \
                         "\n".format(html_teams[matchup[team] - 1].calc_opt_total_score())
        team_avg_info = display_averages_html(html_weekly_averages[matchup[team]], html_weekly_averages['avg'][matchup[team]])
        team_info_float = "<div class='team-info-float'>\n"
        team_info_float += "{}<br>{}<br>\n<hr>\n{}\n".format(max_score_info, luck_info, team_avg_info)
        team_info_float += "</div>\n"
        row += team_info_float
        row += "<img src='{}' class='logo_icon'/>\n".format(html_teams[matchup[team] - 1].logo)
        row += "<h3>\n{} {} [{}]\n</h3>\n".format(html_teams[matchup[team] - 1].loc,
                                                  html_teams[matchup[team] - 1].nick,
                                                  html_teams[matchup[team] - 1].calc_total_score())
        row += "<div class='team-highlight'><b>MVP: </b>{} ({}) - {}</div>\n".format(
            html_teams[matchup[team] - 1].mvp['player'], html_teams[matchup[team] - 1].mvp['pos'][0].capitalize(),
            html_teams[matchup[team] - 1].mvp['score'])
        luck_dict = html_league_luckiness[html_teams[matchup[team] - 1].id][0]
        row += "<div class='team-highlight'><b>Luckiest: </b>{} ({}) - {}%</div>\n".format(
            luck_dict['lucky_player']['name'], playerPositions[luck_dict['lucky_player']['pos']][0].capitalize(),
            int(luck_dict['lucky_player']['performance_percentage'] * 100) - 100)
        row += "\n</div>\n"
        row += "</div>\n"
        if team == 'away':
            row += "<div class='vs-div'>vs</div>\n"
    row += "</div>\n"
    row += "<div>\n"
    chart, on_load = build_player_luck_dist_chart(html_league_luckiness, html_teams[matchup['home'] - 1],
                                                  html_teams[matchup['away'] - 1])
    row += "<div class='right'>{}</div>".format(chart)
    window_on_load = on_load
    chart, on_load = build_daily_score_line_chart(html_teams[matchup['home'] - 1], html_teams[matchup['away'] - 1])
    row += chart
    window_on_load += on_load
    row += "</div>\n"
    for team in ['away', 'home']:
        row += "<div class='matchup_cell_wrapper {}'>\n".format(team)
        row += "<div class='matchup_cell'>"
        row += "<h3>Optimum Lineup:</h3>"
        row += display_roster_html(html_teams[matchup[team] - 1])
        row += "</div>"
        row += "</div>"
    row += "<div class='page_break'></div>"
    return row, window_on_load


def format_html(html_week_number, html_week_matchup, html_teams, html_league_luckiness, html_weekly_averages):
    html_skeleton = "<html>\n<head>\n<link rel='stylesheet' type='text/css' href='style.css'>\n" \
                    "<script src='Chart.min.js'></script></head>\n<body>\n{}\n</body>\n</html>"
    body_skeleton = "<div id='container'>\n{}</div>\n{}\n"
    window_on_load_vars = ""
    endscript = ""
    body = "<div>\n"
    for matchup in html_week_matchup.matchups:
        body_tmp, on_load_tmp = build_matchup_row(matchup, html_week_matchup.name, html_week_number, html_teams,
                                                  html_league_luckiness, html_weekly_averages)
        body += body_tmp
        window_on_load_vars += on_load_tmp
    body += "</div>\n"
    endscript += "<script>\nwindow.onload = function() {\n"
    endscript += window_on_load_vars
    endscript += "};\n</script>\n"
    return html_skeleton.format(body_skeleton.format(body, endscript))


def format_prediction_html(html_week_number, html_week_matchup, html_teams):
    # TODO: format prediction
    html_skeleton = "<html>\n<head>\n<link rel='stylesheet' type='text/css' href='style.css'>\n" \
                    "</head>\n<body>\n{}</body>\n</html>"
    return "yay"


def generate_weekly_report(week_number, week_matchup, teams, league_luckiness, weekly_averages):
    html_output = format_html(week_number, week_matchup, teams, league_luckiness, weekly_averages)
    # TODO: throws an error if style.css or Chart.min.js is not in /tmp
    pdfkit.from_string(html_output, "out.pdf", options=pdfkit_options)
    with open("out.html", 'w') as f:
        f.write(html_output)


def generate_weekly_prediction(week_number, week_matchup, teams):
    html_output = format_prediction_html(week_number, week_matchup, teams)
    pdfkit.from_string(html_output, "out.pdf", options=pdfkit_options)
    with open("out_predict.html", 'w') as f:
        f.write(html_output)
