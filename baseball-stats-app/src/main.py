import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template_string, request, url_for, send_from_directory
import pytz
from datetime import datetime
import os

app = Flask(__name__)

# Add a mapping of team abbreviations to their time zones (partial example, expand as needed)
TEAM_TIMEZONES = {
    "ARI": "America/Phoenix",         # Arizona Diamondbacks
    "ATL": "America/New_York",        # Atlanta Braves
    "BAL": "America/New_York",        # Baltimore Orioles
    "BOS": "America/New_York",        # Boston Red Sox
    "CHC": "America/Chicago",         # Chicago Cubs
    "CWS": "America/Chicago",         # Chicago White Sox
    "CIN": "America/New_York",        # Cincinnati Reds
    "CLE": "America/New_York",        # Cleveland Guardians
    "COL": "America/Denver",          # Colorado Rockies
    "DET": "America/Detroit",         # Detroit Tigers
    "HOU": "America/Chicago",         # Houston Astros
    "KC":  "America/Chicago",         # Kansas City Royals
    "LAA": "America/Los_Angeles",     # Los Angeles Angels
    "LAD": "America/Los_Angeles",     # Los Angeles Dodgers
    "MIA": "America/New_York",        # Miami Marlins
    "MIL": "America/Chicago",         # Milwaukee Brewers
    "MIN": "America/Chicago",         # Minnesota Twins
    "NYM": "America/New_York",        # New York Mets
    "NYY": "America/New_York",        # New York Yankees
    "OAK": "America/Los_Angeles",     # Oakland Athletics
    "PHI": "America/New_York",        # Philadelphia Phillies
    "PIT": "America/New_York",        # Pittsburgh Pirates
    "SD":  "America/Los_Angeles",     # San Diego Padres
    "SF":  "America/Los_Angeles",     # San Francisco Giants
    "SEA": "America/Los_Angeles",     # Seattle Mariners
    "STL": "America/Chicago",         # St. Louis Cardinals
    "TB":  "America/New_York",        # Tampa Bay Rays
    "TEX": "America/Chicago",         # Texas Rangers
    "TOR": "America/Toronto",         # Toronto Blue Jays
    "WSH": "America/New_York",        # Washington Nationals
}

TEAM_ROSTER_API = {
    "ARI": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/29/roster",
    "ATL": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/15/roster",
    "BAL": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/1/roster",
    "BOS": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/2/roster",
    "CHC": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/16/roster",
    "CWS": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/4/roster",
    "CIN": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/17/roster",
    "CLE": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/5/roster",
    "COL": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/27/roster",
    "DET": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/6/roster",
    "HOU": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/18/roster",
    "KC":  "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/7/roster",
    "LAA": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/3/roster",
    "LAD": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/19/roster",
    "MIA": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/28/roster",
    "MIL": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/8/roster",
    "MIN": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/9/roster",
    "NYM": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/21/roster",
    "NYY": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/10/roster",
    "ATH": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/11/roster",
    "PHI": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/22/roster",
    "PIT": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/23/roster",
    "SD":  "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/25/roster",
    "SF":  "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/26/roster",
    "SEA": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/12/roster",
    "STL": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/24/roster",
    "TB":  "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/30/roster",
    "TEX": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/13/roster",
    "TOR": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/14/roster",
    "WSH": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/20/roster",
}

def get_team_timezone(team_abbr):
    return TEAM_TIMEZONES.get(team_abbr, "America/New_York")

def fetch_api_data(url):
    """Fetch data from the given ESPN MLB API endpoint."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def load_teams():
    """Return a DataFrame of MLB teams with their city, name, id, abbreviation, and logo URL."""
    url = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams"
    data = fetch_api_data(url)
    teams = []
    for team_entry in data.get("sports", [])[0].get("leagues", [])[0].get("teams", []):
        team = team_entry.get("team", {})
        # Get logo URL if available
        logo_url = ""
        if team.get("logos"):
            logo_url = team["logos"][0].get("href", "")
        teams.append({
            "id": team.get("id"),
            "city": team.get("location"),
            "name": team.get("name"),
            "displayName": team.get("displayName"),
            "abbreviation": team.get("abbreviation"),
            "logo": logo_url  # Placeholder for logo
        })
    return pd.DataFrame(teams)

def load_scoreboard():
    """Return a DataFrame of games with teams, scores, status, and start time."""
    url = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
    data = fetch_api_data(url)
    games = []
    for event in data.get("events", []):
        event_time_utc = event.get("date")
        for comp in event.get("competitions", []):
            status = comp.get("status", {}).get("type", {}).get("description", "")
            for team in comp.get("competitors", []):
                games.append({
                    "game_id": comp.get("id"),
                    "status": status,
                    "team_name": team['team']['displayName'],
                    "team_abbr": team['team']['abbreviation'],
                    "score": int(team['score']),
                    "event_time_utc": event_time_utc,
                })
    return pd.DataFrame(games)

def load_news():
    """Return a DataFrame of news headlines and links."""
    url = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/news"
    data = fetch_api_data(url)
    news_list = []
    for article in data.get("articles", []):
        news_list.append({
            "headline": article.get("headline"),
            "link": article.get("links", {}).get("web", {}).get("href"),
            "published": article.get("published"),
        })
    return pd.DataFrame(news_list)

def load_team_details(team_id):
    """Return a dictionary of details for a specific MLB team."""
    url = f"http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/{team_id}"
    data = fetch_api_data(url)
    team = data.get("team", {})
    return {
        "id": team.get("id"),
        "location": team.get("location"),
        "name": team.get("name"),
        "displayName": team.get("displayName"),
        "abbreviation": team.get("abbreviation"),
        "record": team.get("record", {}).get("items", []),
        "links": team.get("links", []),
    }

# --- Section: MLB Team Name Definitions ---
def get_mlb_team_names():
    """
    Returns a dictionary mapping 'City_TeamName' (e.g., 'Atlanta_Braves') to the official team display name.
    """
    teams_df = load_teams()
    team_dict = {}
    for _, team in teams_df.iterrows():
        if pd.notnull(team["city"]) and pd.notnull(team["name"]):
            key = f"{team['city'].replace(' ', '')}_{team['name'].replace(' ', '')}"
            team_dict[key] = team["displayName"]
    return team_dict

# --- Section: Display all games' scores using live data ---
def display_all_scores():
    """Fetch and display live scores for all MLB games."""
    games_df = load_scoreboard()
    if games_df.empty:
        print("No games found.")
        return
    print("All MLB Games' Scores:")
    for game_id in games_df['game_id'].unique():
        game = games_df[games_df['game_id'] == game_id]
        matchup = " vs. ".join([f"{row['team_name']} ({row['score']})" for _, row in game.iterrows()])
        status = game['status'].iloc[0]
        print(f"{matchup} - {status}")
    print("-" * 40)

# --- Section: Display scores for a specific team using live data ---
def display_team_score(team_name):
    """Fetch and display live scores for games involving a specific team."""
    games_df = load_scoreboard()
    if games_df.empty:
        print("No games found.")
        return
    print(f"Scores for {team_name}:")
    found = False
    for game_id in games_df['game_id'].unique():
        game = games_df[games_df['game_id'] == game_id]
        if team_name in game['team_name'].values:
            matchup = " vs. ".join([f"{row['team_name']} ({row['score']})" for _, row in game.iterrows()])
            status = game['status'].iloc[0]
            print(f"{matchup} - {status}")
            found = True
    if not found:
        print(f"No games found for {team_name}.")
    print("-" * 40)

# --- Section: Visualizations ---

def plot_team_abbreviations_count():
    """Visualize the number of teams by abbreviation (example bar chart)."""
    teams_df = load_teams()
    plt.figure(figsize=(10, 6))
    teams_df['abbreviation'].value_counts().plot(kind='bar')
    plt.title('Number of Teams by Abbreviation')
    plt.xlabel('Team Abbreviation')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.show()

def plot_scoreboard_scores():
    """Visualize the distribution of scores in the current scoreboard (histogram)."""
    games_df = load_scoreboard()
    plt.figure(figsize=(10, 6))
    games_df['score'].plot(kind='hist', bins=range(0, 20), rwidth=0.8)
    plt.title('Distribution of Team Scores in Current Games')
    plt.xlabel('Score')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.show()

# --- Section: News Display ---
def display_latest_news(n=5):
    """Display the latest MLB news headlines."""
    news_df = load_news()
    print("Latest MLB News:")
    for _, row in news_df.head(n).iterrows():
        print(f"- {row['headline']} ({row['published']})")
        print(f"  Link: {row['link']}")
    print("-" * 40)

# --- Example Classes (unchanged) ---
class PlayerStats:
    def __init__(self, name, team):
        self.name = name
        self.team = team
        self.stats = {}

    def add_stat(self, stat_name, value):
        self.stats[stat_name] = value

    def get_stat(self, stat_name):
        return self.stats.get(stat_name, None)

    def display_stats(self):
        print(f"Stats for {self.name} ({self.team}):")
        for stat_name, value in self.stats.items():
            print(f"{stat_name}: {value}")

class TeamStats:
    def __init__(self, team_name):
        self.team_name = team_name
        self.players = {}

    def add_player(self, player):
        self.players[player.name] = player

    def get_player(self, player_name):
        return self.players.get(player_name, None)

    def display_team_stats(self):
        print(f"Team Stats for {self.team_name}:")
        for player in self.players.values():
            player.display_stats()

# Homepage with dropdown to select favorite team
@app.route("/", methods=["GET"])
def home():
    teams_df = load_teams()
    teams = teams_df.sort_values("displayName")[["displayName", "abbreviation", "logo"]].to_dict(orient="records")
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Earley First Pitch</title>
        <!-- Reference the minimalist, modern CSS -->
        <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    </head>
    <body>
    <header class="navbar">
        <div class="navbar-container">
            <a href="/" class="navbar-item">Home</a>
            <div class="navbar-item dropdown">
                <span>Teams</span>
                <div class="scrollable-menu">
                    {% for team in teams %}
                        <a href="/team?team={{ team.abbreviation }}" class="team-item">
                            {{ team.displayName }}
                        </a>
                    {% endfor %}
                </div>
            </div>
            <a href="/news" class="navbar-item">News</a>
            <!-- Seasons dropdown moved here -->
            <div class="navbar-item dropdown season-dropdown">
                <span>Seasons</span>
                <div class="scrollable-menu">
                    {% for year in range(2024, 2014, -1) %}
                        <a href="/season/{{ year }}" class="team-item">
                            {{ year }}
                        </a>
                    {% endfor %}
                </div>
            </div>
            <a href="/about" class="navbar-item">About Us</a>
        </div>
    </header>
    <div class="container">
            <h1>Earley First Pitch</h1>
            <h2>Today's Games</h2>
            <div class="games-table-container">
                <table class="games-table">
                    <thead>
                        <tr>
                            <th>Matchup</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for game in games %}
                            <tr>
                                <td class="matchup-cell">
                                    {% for t in game.teams %}
                                        {% set logo = None %}
                                        {% for team in teams %}
                                            {% if team['displayName'] == t %}
                                                {% set logo = team['logo'] %}
                                            {% endif %}
                                        {% endfor %}
                                        {% if logo %}
                                            <img src="{{logo}}" alt="{{t}} logo" class="team-logo">
                                        {% endif %}
                                        <span>{{t}}</span>
                                        {% if not loop.last %}
                                            <span class="vs-text">vs.</span>
                                        {% endif %}
                                    {% endfor %}
                                </td>
                                <td style="min-width:180px; text-align:center;">
                                    {% if game.start_time_str %}
                                        <span class="game-start-time">{{ game.start_time_str }}</span>
                                    {% else %}
                                        {{ game.scores[0] }} - {{ game.scores[1] }}
                                        {% if game.winner %}
                                            <span class="winner-rect">
                                                {{ game.winner }} Win
                                            </span>
                                        {% elif game.leader %}
                                            <span class="leader-rect">
                                                {{ game.leader }}
                                            </span>
                                        {% endif %}
                                    {% endif %}
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """, teams=teams, news=get_news_list(), games=get_games_list())

# Team page with logo and today's games for that team
@app.route("/team", methods=["GET"])
def team_page():
    abbr = request.args.get("team")
    teams_df = load_teams()
    team = teams_df[teams_df["abbreviation"] == abbr].iloc[0]
    games_df = load_scoreboard()
    team_games = []
    for game_id in games_df['game_id'].unique():
        game = games_df[games_df['game_id'] == game_id]
        if abbr in game['team_abbr'].values:
            teams = [row['team_name'] for _, row in game.iterrows()]
            scores = [row['score'] for _, row in game.iterrows()]
            abbrs = [row['team_abbr'] for _, row in game.iterrows()]
            matchup = " vs. ".join([f"{row['team_name']} ({row['score']})" for _, row in game.iterrows()])
            status = game['status'].iloc[0]
            event_time_utc = game['event_time_utc'].iloc[0]
            # Determine score display
            score_display = ""
            start_time_str = None
            if status.lower() in ["scheduled", "pre-game", "pre"]:
                tz = pytz.timezone(get_team_timezone(abbrs[0]))
                try:
                    dt_utc = datetime.strptime(event_time_utc, "%Y-%m-%dT%H:%MZ")
                except ValueError:
                    dt_utc = datetime.strptime(event_time_utc, "%Y-%m-%dT%H:%M:%SZ")
                dt_local = dt_utc.replace(tzinfo=pytz.utc).astimezone(tz)
                hour = dt_local.strftime("%I").lstrip('0')
                minute = dt_local.strftime("%M")
                ampm = dt_local.strftime("%p")
                tzname = dt_local.strftime("%Z")
                start_time_str = f"Starts @ {hour}:{minute} {ampm} {tzname}"
                score_display = start_time_str
            elif status.lower() == "final" and len(teams) == 2 and len(scores) == 2:
                if scores[0] > scores[1]:
                    score_display = f"{scores[0]} - {scores[1]} ({teams[0]} Win)"
                elif scores[1] > scores[0]:
                    score_display = f"{scores[0]} - {scores[1]} ({teams[1]} Win)"
                else:
                    score_display = f"{scores[0]} - {scores[1]} (Currently Tied)"
            elif len(teams) == 2 and len(scores) == 2:
                if scores[0] > scores[1]:
                    score_display = f"{scores[0]} - {scores[1]} ({teams[0]} Leading)"
                elif scores[1] > scores[0]:
                    score_display = f"{scores[0]} - {scores[1]} ({teams[1]} Leading)"
                else:
                    score_display = f"{scores[0]} - {scores[1]} (Currently Tied)"
            else:
                score_display = "N/A"
            team_games.append({"matchup": " vs. ".join(teams), "score": score_display})

    # --- Roster Section ---
    roster_url = TEAM_ROSTER_API.get(abbr)
    roster_data = fetch_api_data(roster_url) if roster_url else {}
    players = roster_data.get("athletes", []) if roster_data else []

    # Organize players
    position_players = []
    pitchers_sp = []
    pitchers_rp = []

    # Helper to extract last name for sorting
    def get_last_name(full_name):
        return full_name.split()[-1] if full_name else ""

    # Infield and outfield position abbreviations
    infield_positions = {"1B", "2B", "3B", "SS", "C"}
    outfield_positions = {"LF", "CF", "RF", "OF"}

    for group in players:
        if not isinstance(group, dict):
            continue
        for player in group.get("items", []):
            pos = player.get("position", {}).get("abbreviation", "")
            # Always use the abbreviation for display
            display_pos = pos
            player_info = {
                "name": player.get("fullName"),
                "number": player.get("jersey"),
                "pos": pos,
                "display_pos": display_pos,
                "headshot": player.get("headshot", {}).get("href") if player.get("headshot") else None,
            }
            # Pitchers
            if pos == "SP":
                pitchers_sp.append(player_info)
            elif pos == "RP":
                pitchers_rp.append(player_info)
            # Position Players
            elif pos in infield_positions or pos in outfield_positions or pos not in ["SP", "RP", "P"]:
                position_players.append(player_info)

    # Sort pitchers: SPs then RPs, each A-Z by last name
    pitchers_sp = sorted(pitchers_sp, key=lambda x: get_last_name(x["name"]))
    pitchers_rp = sorted(pitchers_rp, key=lambda x: get_last_name(x["name"]))
    pitchers = pitchers_sp + pitchers_rp

    # Sort position players: infielders A-Z by last name, then outfielders A-Z by last name, then others
    infielders = [p for p in position_players if p["pos"] in infield_positions]
    outfielders = [p for p in position_players if p["pos"] in outfield_positions]
    others = [p for p in position_players if p["pos"] not in infield_positions and p["pos"] not in outfield_positions]
    infielders = sorted(infielders, key=lambda x: get_last_name(x["name"]))
    outfielders = sorted(outfielders, key=lambda x: get_last_name(x["name"]))
    others = sorted(others, key=lambda x: get_last_name(x["name"]))
    position_players = infielders + outfielders + others

    # Helper to extract a sortable jersey number (handles None and non-integer gracefully)
    def get_number(num):
        try:
            return int(num)
        except (TypeError, ValueError):
            return 999  # Put players without a number at the end

    # Define position order for sorting (infielders, outfielders, then others)
    position_order = {
        "C": 0, "1B": 1, "2B": 2, "3B": 3, "SS": 4,  # Infielders
        "LF": 5, "CF": 6, "RF": 7, "OF": 8,          # Outfielders
        "DH": 9,                                     # Designated Hitter
        "UT": 10,                                    # Utility
        "SP": 11, "RP": 12, "P": 13                  # Pitchers (if any in position_players)
    }

    # Sort position players by position, then by jersey number
    position_players = sorted(
        position_players,
        key=lambda x: (position_order.get(x["pos"], 99), get_number(x["number"]))
    )

    # Sort pitchers by position (SP first, then RP), then by jersey number
    pitchers = sorted(
        pitchers_sp + pitchers_rp,
        key=lambda x: (position_order.get(x["pos"], 99), get_number(x["number"]))
    )

    return render_template_string("""
    <!DOCTYPE html>
<html>
<head>
    <title>{{team.displayName}} - MLB Team Info</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
    <div class="container">
        <a href="/" class="back-home-btn back-home-btn-top">Back to Home</a>
        <div class="team-header-row">
    {% if team.logo %}
        <img src="{{team.logo}}" alt="{{team.displayName}} logo" class="team-header-logo">
    {% endif %}
    <h1 class="team-header-name team-color-{{team.abbreviation}}">
        {{team.displayName}}
    </h1>
</div>
            <h2>Today's Games</h2>
            <div class="games-table-container">
                <table class="games-table">
                    <thead>
                        <tr>
                            <th>Matchup</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for game in team_games %}
                        <tr>
                            <td>{{game.matchup}}</td>
                            <td>
                                {{game.score}}
                            </td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>
            <h2>Roster</h2>

<h3 style="margin-top:32px; margin-bottom:10px;">Position Players</h3>
<table class="games-table" style="margin-bottom: 36px;">
    <thead>
        <tr>
            <th>#</th>
            <th></th>
            <th>Name</th>
            <th>Position</th>
        </tr>
    </thead>
    <tbody>
    {% for player in position_players %}
        <tr>
            <td>{{ player.number }}</td>
            <td>
                {% if player.headshot %}
                    <img src="{{ player.headshot }}" alt="{{ player.name }} headshot" style="width:48px; height:48px; object-fit:cover; vertical-align:middle;">
                {% endif %}
            </td>
            <td>{{ player.name }}</td>
            <td>{{ player.display_pos }}</td>
        </tr>
    {% endfor %}
    </tbody>
</table>

<h3 style="margin-top:32px; margin-bottom:10px;">Pitchers</h3>
<table class="games-table">
    <thead>
        <tr>
            <th>#</th>
            <th></th>
            <th>Name</th>
            <th>Position</th>
        </tr>
    </thead>
    <tbody>
    {% for player in pitchers %}
        <tr>
            <td>{{ player.number }}</td>
            <td>
                {% if player.headshot %}
                    <img src="{{ player.headshot }}" alt="{{ player.name }} headshot" style="width:48px; height:48px; object-fit:cover; vertical-align:middle;">
                {% endif %}
            </td>
            <td>{{ player.name }}</td>
            <td>{{ player.display_pos }}</td>
        </tr>
    {% endfor %}
    </tbody>
</table>
            <a href="/" class="back-home-btn">Back to Home</a>
        </div>
    </body>
    </html>
    """, team=team, team_games=team_games,
         position_players=position_players, pitchers=pitchers)

def get_news_list():
    news_df = load_news()
    return news_df.head(5).to_dict(orient="records")

def get_games_list():
    games_df = load_scoreboard()
    teams_df = load_teams()
    games = []
    for game_id in games_df['game_id'].unique():
        game = games_df[games_df['game_id'] == game_id]
        teams = []
        scores = []
        abbrs = []
        inning_status = ""
        inning_number = ""
        balls = 0
        strikes = 0
        outs = 0
        on_base = False
        for _, row in game.iterrows():
            teams.append(row['team_name'])
            scores.append(row['score'])
            abbrs.append(row['team_abbr'])
            # Extract ball, strike, outs, and on-base data if available
            balls = row.get('balls', balls)
            strikes = row.get('strikes', strikes)
            outs = row.get('outs', outs)
            on_base = row.get('on_base', on_base)
        matchup = " vs. ".join(teams)
        score_str = " - ".join(str(s) for s in scores)
        status = game['status'].iloc[0]
        event_time_utc = game['event_time_utc'].iloc[0]
        winner = None
        winner_score = None
        leader = None
        start_time_str = None

        # Try to extract inning info from status (ESPN API may use "Top Xth", "Bottom Xth", etc.)
        import re
        match = re.search(r'(Top|Bottom)\s+(\d+)', status)
        if match:
            inning_status = match.group(1)  # "Top" or "Bottom"
            inning_number = match.group(2)  # inning number as string

        # Helper to get just the team "name" (not city) from abbreviation
        def get_short_name(abbr):
            row = teams_df[teams_df["abbreviation"] == abbr]
            if not row.empty:
                return row.iloc[0]["name"]
            return abbr

        # Determine winner if game is Final
        if status.lower() == "final" and len(teams) == 2 and len(scores) == 2:
            if scores[0] > scores[1]:
                winner = f"{get_short_name(abbrs[0])}"
                winner_score = scores[0]
            elif scores[1] > scores[0]:
                winner = f"{get_short_name(abbrs[1])}"
                winner_score = scores[1]
        # If not final, indicate leader or tie (capitalize first letter)
        elif len(teams) == 2 and len(scores) == 2:
            if status.lower() in ["scheduled", "pre-game", "pre"]:
                leader = None  # Do not display "Currently Tied" if game has not started
            elif scores[0] > scores[1]:
                leader = f"{get_short_name(abbrs[0])} Leading"
            elif scores[1] > scores[0]:
                leader = f"{get_short_name(abbrs[1])} Leading"
            else:
                leader = "Currently Tied"

            # If in progress and we have inning info, append arrow and inning number
            if leader and inning_status and inning_number and leader != "Currently Tied":
                arrow = "↑" if inning_status.lower() == "top" else "↓"
                leader += f" {arrow}{inning_number}"

        # If game has not started, show start time in local time zone of first team
        if status.lower() in ["scheduled", "pre-game", "pre"]:
            tz = pytz.timezone(get_team_timezone(abbrs[0]))
            try:
                dt_utc = datetime.strptime(event_time_utc, "%Y-%m-%dT%H:%MZ")
            except ValueError:
                dt_utc = datetime.strptime(event_time_utc, "%Y-%m-%dT%H:%M:%SZ")
            dt_local = dt_utc.replace(tzinfo=pytz.utc).astimezone(tz)
            hour = dt_local.strftime("%I").lstrip('0')
            minute = dt_local.strftime("%M")
            ampm = dt_local.strftime("%p")
            tzname = dt_local.strftime("%Z")
            start_time_str = f"Starts @ {hour}:{minute} {ampm} {tzname}"
        games.append({
            "teams": teams,
            "scores": scores,
            "matchup": matchup,
            "score_str": score_str,
            "status": status,
            "winner": winner,
            "winner_score": winner_score,
            "leader": leader,
            "start_time_str": start_time_str,
            "balls": balls,  # Added balls tracker
            "strikes": strikes,  # Added strikes tracker
            "outs": outs,  # Added outs tracker
            "on_base": on_base  # Added on-base tracker
        })
    return games

# Convert published date string to a more readable format
def format_published_date(date_str):
    if not date_str:
        return ""
    try:
        # Parse the date string into a datetime object
        utc_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        # Convert UTC time to local time
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/New_York'))
        # Format the local time as a string
        return local_time.strftime("%B %d, %Y %I:%M %p")
    except Exception as e:
        print(f"Error parsing date: {e}")
        return date_str

# Custom Jinja filter to format the published date
@app.template_filter('format_date')
def format_date_filter(date_str):
    return format_published_date(date_str)

@app.route("/teams", methods=["GET"])
def teams_page():
    teams = load_teams()
    return render_template_string("""
    <!DOCTYPE html>
<html>
<head>
    <title>Teams - Earley First Pitch</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
    <header class="navbar">
        <div class="navbar-container">
            <a href="/" class="navbar-item">Home</a>
            <a href="/teams" class="navbar-item">Teams</a>
            <a href="/news" class="navbar-item">News</a>
            <a href="/about" class="navbar-item">About Us</a>
        </div>
    </header>
    <div class="container">
        <h1>Teams</h1>
        <ul class="teams-list">
        {% for team in teams %}
            <li><a href="/team?team={{ team.abbreviation }}">{{ team.displayName }}</a></li>
        {% endfor %}
        </ul>
    </div>
</body>
</html>
    """, teams=teams)

@app.route("/news", methods=["GET"])
def news_page():
    news = get_news_list()
    return render_template_string("""
    <!DOCTYPE html>
<html>
<head>
    <title>News - Earley First Pitch</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    <style>
        .news-container {
            background: #232526;
            border-radius: 18px;
            box-shadow: 0 4px 24px 0 rgba(0,0,0,0.25);
            padding: 36px 40px 40px 40px;
            margin: 40px auto;
            max-width: 800px;
            min-width: 340px;
            width: fit-content;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .news-list {
            list-style: none;
            padding: 0;
            margin: 0;
            width: 100%;
        }
        .news-list li {
            background: #2d2f31;
            margin-bottom: 18px;
            padding: 18px 22px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: background 0.2s;
            font-size: 1.08rem;
        }
        .news-list li:last-child {
            margin-bottom: 0;
        }
        .news-list a {
            color: #ffd54f;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.2s;
        }
        .news-list a:hover {
            color: #fff176;
            text-decoration: underline;
        }
        .news-date {
            display: block;
            color: #bdbdbd;
            font-size: 0.98rem;
            margin-top: 6px;
            font-weight: 400;
        }
        h1 {
            color: #ffd54f;
            margin-bottom: 28px;
            font-size: 2.1rem;
            font-weight: 700;
            letter-spacing: 1px;
        }
        @media (max-width: 900px) {
            .news-container {
                padding: 18px 6vw 24px 6vw;
                min-width: unset;
                max-width: 98vw;
            }
        }
    </style>
</head>
<body>
    <header class="navbar">
        <div class="navbar-container">
            <a href="/" class="navbar-item">Home</a>
            <div class="navbar-item dropdown">
                <span>Teams</span>
                <div class="scrollable-menu">
                    {% for team in teams %}
                        <a href="/team?team={{ team.abbreviation }}" class="team-item">
                            {{ team.displayName }}
                        </a>
                    {% endfor %}
                </div>
            </div>
            <a href="/news" class="navbar-item">News</a>
            <div class="navbar-item dropdown season-dropdown">
                <span>Seasons</span>
                <div class="scrollable-menu">
                    {% for y in range(2024, 2014, -1) %}
                        <a href="/season/{{ y }}" class="team-item">{{ y }}</a>
                    {% endfor %}
                </div>
            </div>
            <a href="/about" class="navbar-item">About Us</a>
        </div>
    </header>
    <div class="news-container">
        <h1>Latest MLB News</h1>
        <ul class="news-list">
        {% for item in news %}
            <li>
                <a href="{{ item.link }}" target="_blank">{{ item.headline }}</a>
                {% if item.published %}
                    <span class="news-date">{{ item.published|format_date }}</span>
                {% endif %}
            </li>
        {% endfor %}
        </ul>
    </div>
</body>
    """, news=news, teams=load_teams())

@app.route("/about", methods=["GET"])
def about_page():
    return render_template_string("""
    <!DOCTYPE html>
<html>
<head>
    <title>About Us - Earley First Pitch</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
    <header class="navbar">
        <div class="navbar-container">
            <a href="/" class="navbar-item">Home</a>
            <a href="/teams" class="navbar-item">Teams</a>
            <a href="/news" class="navbar-item">News</a>
            <a href="/about" class="navbar-item">About Us</a>
        </div>
    </header>
    <div class="container">
        <h1>About Us</h1>
        <p>Earley First Pitch is your one-stop destination for MLB stats, news, and updates. Stay tuned for the latest information on your favorite teams and players!</p>
    </div>
</body>
</html>
    """)

@app.route("/season/<int:year>")
def season_stats(year):
    # Path to your CSV files (adjust as needed)
    csv_folder = os.path.join(os.getcwd(), "CSV")
    csv_filename = f"batterstats{year}.csv"
    csv_path = os.path.join(csv_folder, csv_filename)
    if not os.path.exists(csv_path):
        return f"No data available for {year}", 404

    columns, rows = process_batter_stats_csv(csv_path)

    # Render as HTML table 1:1 with CSV
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Batter Stats {{ year }}</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
        <style>
            .season-table-container { overflow-x: auto; margin: 32px 0; }
            .season-table { border-collapse: collapse; width: 100%; font-size: 0.95rem; }
            .season-table th, .season-table td { border: 1px solid #444; padding: 6px 10px; text-align: center; }
            .season-table th { background: #232526; color: #fff; }
            .season-table tr:nth-child(even) { background: #2d2f31; }
        </style>
    </head>
    <body>
        <header class="navbar">
            <div class="navbar-container">
                <a href="/" class="navbar-item">Home</a>
                <div class="navbar-item dropdown">
                    <span>Teams</span>
                    <div class="scrollable-menu">
                        {% for team in teams %}
                            <a href="/team?team={{ team.abbreviation }}" class="team-item">
                                {{ team.displayName }}
                            </a>
                        {% endfor %}
                    </div>
                </div>
                <a href="/news" class="navbar-item">News</a>
                <div class="navbar-item dropdown season-dropdown">
                    <span>Seasons</span>
                    <div class="scrollable-menu">
                        {% for y in range(2024, 2014, -1) %}
                            <a href="/season/{{ y }}" class="team-item">{{ y }}</a>
                        {% endfor %}
                    </div>
                </div>
                <a href="/about" class="navbar-item">About Us</a>
            </div>
        </header>
        <div class="container">
            <h1>Batter Stats {{ year }}</h1>
            <div class="season-table-container">
                <table class="season-table">
                    <thead>
                        <tr>
                            {% for col in columns %}
                                <th>{{ col }}</th>
                            {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in rows %}
                            <tr>
                                {% for cell in row %}
                                    <td>{{ cell }}</td>
                                {% endfor %}
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """, year=year, columns=columns, rows=rows, teams=load_teams())

def process_batter_stats_csv(csv_path):
    df = pd.read_csv(csv_path)

    if "first_name" in df.columns and "last_name" in df.columns:
        df["Player Name"] = df["first_name"].astype(str) + " " + df["last_name"].astype(str)
        df = df.drop(columns=["first_name", "last_name"])

    if "player_id" in df.columns:
        df = df.drop(columns=["player_id"])

    if "batting_avg" in df.columns:
        df = df.sort_values("batting_avg", ascending=False)

    col_abbr = {
        "Last Name, First Name": "Player Name",
        "Ab": "AB",
        "Hit": "H",
        "Batting Avg": "Avg",
        "Single": "1B",
        "Double": "2B",
        "Triple": "3B",
        "Home Run": "HR",
        "K Percent": "K%",
        "Bb Percent": "BB%",
        "On Base Percent": "OBP",
        "On Base Plus Slg": "OPS",
        "B Rbi": "RBI",
        "Rbi": "RBI",
    }

    cols = list(df.columns)

    # Move Batting Avg after Year if both exist
    if "batting_avg" in cols and "year" in cols:
        cols.remove("batting_avg")
        year_idx = cols.index("year")
        cols.insert(year_idx + 1, "batting_avg")

    # Move RBI after HR if both exist
    # Accept both "rbi" and "b_rbi" as possible column names
    rbi_col = None
    for possible in ["rbi", "b_rbi"]:
        if possible in cols:
            rbi_col = possible
            break
    if rbi_col and "home_run" in cols:
        cols.remove(rbi_col)
        hr_idx = cols.index("home_run")
        cols.insert(hr_idx + 1, rbi_col)

    df = df[cols]

    if "batting_avg" in df.columns:
        df["batting_avg"] = df["batting_avg"].apply(
            lambda x: f".{str(x)[2:5].ljust(3, '0')}" if pd.notnull(x) and str(x).startswith("0.") else x
        )

    display_columns = [col_abbr.get(col.replace("_", " ").title(), col.replace("_", " ").title()) for col in df.columns]

    rows = [
        [str(cell).replace("_", " ") if isinstance(cell, str) else cell for cell in row]
        for row in df.values.tolist()
    ]

    return display_columns, rows

# Make sure to have a load_teams() function that returns your teams list for the navbar.

if __name__ == "__main__":
    app.run(debug=True)