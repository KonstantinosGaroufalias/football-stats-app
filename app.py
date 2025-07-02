from flask import Flask, render_template, jsonify
import requests
from config import Config
from datetime import datetime, date
import json

app = Flask(__name__)
app.config.from_object(Config)


def get_api_headers():
    return {
        'X-RapidAPI-Key': app.config['API_FOOTBALL_KEY'],
        'X-RapidAPI-Host': app.config['API_FOOTBALL_HOST']
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/live-matches')
def get_live_matches():
    """Get live matches from API-Football"""
    try:
        url = f"{app.config['API_FOOTBALL_URL']}/fixtures"
        params = {
            'live': 'all',
            'timezone': 'Europe/Athens'
        }

        response = requests.get(url, headers=get_api_headers(), params=params)

        if response.status_code == 200:
            data = response.json()
            matches = []

            for match in data.get('response', [])[:10]:  # Limit to 10 matches
                match_data = {
                    'id': match['fixture']['id'],
                    'home_team': match['teams']['home']['name'],
                    'away_team': match['teams']['away']['name'],
                    'home_logo': match['teams']['home']['logo'],
                    'away_logo': match['teams']['away']['logo'],
                    'home_score': match['goals']['home'],
                    'away_score': match['goals']['away'],
                    'status': match['fixture']['status']['short'],
                    'elapsed': match['fixture']['status']['elapsed'],
                    'league': match['league']['name'],
                    'venue': match['fixture']['venue']['name']
                }
                matches.append(match_data)

            return jsonify({'matches': matches, 'success': True})
        else:
            return jsonify({'error': 'Failed to fetch data', 'success': False})

    except Exception as e:
        return jsonify({'error': str(e), 'success': False})


@app.route('/api/team-lineup/<int:fixture_id>')
def get_team_lineup(fixture_id):
    """Get team lineup for a specific match"""
    try:
        url = f"{app.config['API_FOOTBALL_URL']}/fixtures/lineups"
        params = {'fixture': fixture_id}

        response = requests.get(url, headers=get_api_headers(), params=params)

        if response.status_code == 200:
            data = response.json()
            lineups = []

            for team_lineup in data.get('response', []):
                team_data = {
                    'team_name': team_lineup['team']['name'],
                    'team_logo': team_lineup['team']['logo'],
                    'formation': team_lineup['formation'],
                    'coach': team_lineup['coach']['name'] if team_lineup['coach'] else 'Unknown',
                    'players': []
                }

                for player in team_lineup['startXI']:
                    player_data = {
                        'id': player['player']['id'],
                        'name': player['player']['name'],
                        'number': player['player']['number'],
                        'position': player['player']['pos'],
                        'grid': player['player']['grid']
                    }
                    team_data['players'].append(player_data)

                lineups.append(team_data)

            return jsonify({'lineups': lineups, 'success': True})
        else:
            return jsonify({'error': 'Lineup not available', 'success': False})

    except Exception as e:
        return jsonify({'error': str(e), 'success': False})


@app.route('/api/today-matches')
def get_today_matches():
    """Get today's matches"""
    try:
        today = date.today().strftime('%Y-%m-%d')
        url = f"{app.config['API_FOOTBALL_URL']}/fixtures"
        params = {
            'date': today,
            'timezone': 'Europe/Athens'
        }

        response = requests.get(url, headers=get_api_headers(), params=params)

        if response.status_code == 200:
            data = response.json()
            matches = []

            for match in data.get('response', [])[:15]:  # Limit to 15 matches
                match_data = {
                    'id': match['fixture']['id'],
                    'home_team': match['teams']['home']['name'],
                    'away_team': match['teams']['away']['name'],
                    'home_logo': match['teams']['home']['logo'],
                    'away_logo': match['teams']['away']['logo'],
                    'home_score': match['goals']['home'],
                    'away_score': match['goals']['away'],
                    'status': match['fixture']['status']['short'],
                    'time': match['fixture']['date'],
                    'league': match['league']['name'],
                    'league_logo': match['league']['logo']
                }
                matches.append(match_data)

            return jsonify({'matches': matches, 'success': True})
        else:
            return jsonify({'error': 'Failed to fetch data', 'success': False})

    except Exception as e:
        return jsonify({'error': str(e), 'success': False})


if __name__ == '__main__':
    app.run(debug=True)
