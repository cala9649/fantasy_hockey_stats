# fantasy_hockey_stats

A program for interfacing with ESPN's fantasy hockey API (fantasy.espn.com/apis/v3)

### Dependencies: 
- wkhtmltopdf ([installation instructions](https://github.com/pdfkit/pdfkit/wiki/Installing-WKHTMLTOPDF))
- python3

### cookies.cfg setup

To set up authenticated requests, use `example_cookies.cfg` to make `cookies.cfg`. 
Using a browser, log in to fantasy.espn.com normally, then navigate to your fantasy hockey league page. 
Open the developer tools to view your cookies. Find and copy the cookies `SWID` and `espn_s2` in to `cookies.cfg`.
Locate the league ID either in the requests or the 8 digit number in the URL and add that to `cookies.cfg`.

### Running

1. Navigate to the `fantasy_hockey_stats/` directory
1. Copy `style.css` and `Chart.min.js` in to `/tmp`. (this is an annoying wkhtmltopdf requirement)
1. `$ python3` - Start the python interpreter:
1. `>>> import main` - Import `main.py`
1. `>>> main.generate_weekly_report(8)` - Generate the week 8 report PDF 
