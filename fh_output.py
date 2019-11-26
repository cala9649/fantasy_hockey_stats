import pdfkit

playerPositions = {"forward": 3, "defense": 4, "goalie": 5, "util": 6, "bench": 7, 3: "forward", 4: "defense", 5: "goalie", 6: "util", 7: "bench"}

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
    picked_skaters = html_team.roster[3] + html_team.roster[4] + html_team.roster[5] + html_team.roster[6]
    for pos in [3, 4, 6]:
        skaters_html_list = []
        for player in html_team.opt_roster[pos]:
            if player not in picked_skaters:
                skaters_html_list.append("<span class='bad_pick'>{}</span>".format(player))
            else:
                skaters_html_list.append("{}".format(player))
        roster_formatted += roster_skeleton.format(playerPositions[pos][0].capitalize(), ', '.join(skaters_html_list) + "<br>\n")
    goalies_html_list = []
    for player in html_team.opt_roster[5]:
        if player not in picked_skaters:
            goalies_html_list.append("<span class='bad_pick'>{}</span>".format(player))
        else:
            goalies_html_list.append("{}".format(player))
    roster_formatted += roster_skeleton.format("G", ', '.join(goalies_html_list) + "<br>\n")
    bench_html_list = []
    for player in html_team.opt_roster[7]:
        if player in picked_skaters:
            bench_html_list.append("<span class='bad_pick'>{} ({})</span>".format(player, playerPositions[html_team.opt_bench[player]][0].capitalize()))
        else:
            bench_html_list.append("{} ({})".format(player, playerPositions[html_team.opt_bench[player]][0].capitalize()))
    roster_formatted += roster_skeleton.format("B", ', '.join(bench_html_list) + "\n")
    return roster_formatted

def build_daily_score_line_chart(home_team, away_team):
    chart = ""
    chart += "<div>\n<canvas id='daily_score_line_chart_{}_{}'></canvas>\n</div>\n".format(home_team.loc, away_team.loc)
    chart += "<script>\n"
    chart += "var daily_score_line_chart_{0}_{1}_config = ".format(home_team.loc, away_team.loc)
    chart += "{type: 'line',\ndata: {\nlabels: "
    day_numbers = []
    for i in home_team.scores.keys():
        try:
            int(i)
            day_numbers.append(str(i))
        except ValueError:
            pass
    day_numbers.sort()
    chart += "['" + "', '".join(day_numbers) + "'],\n"
    chart += "datasets: [\n"
    for team in [home_team, away_team]:
        chart += "{"
        chart += "label: '{} {}',\n".format(team.loc, team.nick)
        chart += "lineTension: 0,\n"
        if team == home_team:
            chart += "backgroundColor: 'rgb(255,0,0)',\nborderColor: 'rgb(255,0,0)',\n"
        else:
            chart += "backgroundColor: 'rgb(0,0,255)',\nborderColor: 'rgb(0,0,255)',\n"
        chart += "fill: false,\n"
        chart += "data: "
        scores = []
        weekly_total = 0
        for day in day_numbers:
            for player in team.scores[int(day)]:
                weekly_total += team.scores[int(day)][player]
            scores.append(str(weekly_total))
        chart += "[" + ", ".join(scores) + "],\n"
        chart += "},\n"
    chart += "]\n}\n};\n"
    chart += "</script>\n"
    on_load = "var daily_score_line_chart_{0}_{1}_ctx = document.getElementById('daily_score_line_chart_{0}_{1}').getContext('2d');\n".format(home_team.loc, away_team.loc)
    on_load += "var line_{0}_{1} = new Chart(daily_score_line_chart_{0}_{1}_ctx, daily_score_line_chart_{0}_{1}_config);\n".format(home_team.loc, away_team.loc)
    return chart, on_load

def format_html(html_week_number, html_week_matchup, html_teams, html_league_luckiness):
    html_skeleton = "<html>\n<head>\n<link rel='stylesheet' type='text/css' href='style.css'>\n<script src='Chart.min.js'></script></head>\n<body>\n{}\n</body>\n</html>"
    body_skeleton = "<div id='container'>\n<h1>\n{} - Week {}</h1>\n{}</div>\n{}\n"
    window_on_load_vars = ""
    endscript = ""
    table = "<table>\n"
    for matchup in html_week_matchup.matchups:
        table += "<tr>\n"
        for team in matchup:
            table += "<td>\n"
            luck_info = "<b>Luck:</b> {}%\n".format(int(html_league_luckiness[html_teams[matchup[team]-1].id][0]['mean_luck']*100)-100)
            max_score_info = "<b>Max: </b>{}\n".format(html_teams[matchup[team]-1].calc_opt_total_score())
            team_info_float = "<div class='team-info-float'>\n{}&nbsp;&nbsp;{}\n</div>\n".format(luck_info, max_score_info)
            table += team_info_float
            table += "<img src='{}' class='logo_icon'/>\n".format(html_teams[matchup[team]-1].logo)
            table += "<h3>\n{} {} [{}]\n</h3>\n".format(html_teams[matchup[team]-1].loc, html_teams[matchup[team]-1].nick, html_teams[matchup[team]-1].calc_total_score())
            table += "<div class='team-highlight'><b>MVP: </b>{} ({}) - {}</div>\n".format(html_teams[matchup[team]-1].mvp['player'], html_teams[matchup[team]-1].mvp['pos'][0].capitalize(), html_teams[matchup[team]-1].mvp['score'])
            luck_dict = html_league_luckiness[html_teams[matchup[team]-1].id][0]
            table += "<div class='team-highlight'><b>Luckiest: </b>{} ({}) - {}%</div>\n<br>\n".format(luck_dict['lucky_player']['name'], playerPositions[luck_dict['lucky_player']['pos']][0].capitalize(), int(luck_dict['lucky_player']['performance_percentage']*100)-100)
            table += display_roster_html(html_teams[matchup[team]-1])
            table += "\n</td>\n"
            if team == 'home':
                table += "<td class='vs'><div class='vs-div'>vs</div></td>\n"
        table += "</tr>\n"
        table += "<tr>\n"
        chart, on_load = build_daily_score_line_chart(html_teams[matchup['home']-1], html_teams[matchup['away']-1])
        window_on_load_vars += on_load
        table += chart
        table += "</tr>\n"
    table += "</table>\n"
    endscript += "<script>\nwindow.onload = function() {\n"
    endscript += window_on_load_vars
    endscript += "};\n</script>\n"
    return html_skeleton.format(body_skeleton.format(html_week_matchup.name, html_week_number, table, endscript))

def format_prediction_html(html_week_number, html_week_matchup, html_teams):
    html_skeleton = "<html>\n<head>\n<link rel='stylesheet' type='text/css' href='style.css'>\n</head>\n<body>\n{}</body>\n</html>"
    return "yay"

def generate_weekly_report(week_number, week_matchup, teams, league_luckiness):
    html_output = format_html(week_number, week_matchup, teams, league_luckiness)
    # TODO: throws an error if style.css or Chart.min.js is not in /tmp
    pdfkit.from_string(html_output, "out.pdf", options=pdfkit_options)
    with open("out.html", 'w') as f:
        f.write(html_output)

def generate_weekly_prediction(week_number, week_matchup, teams):
    html_output = format_prediction_html(week_number, week_matchup, teams)
    pdfkit.from_string(html_output, "out.pdf", options=pdfkit_options)
    with open("out_predict.html", 'w') as f:
        f.write(html_output)
