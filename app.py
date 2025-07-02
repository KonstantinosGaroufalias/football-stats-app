from flask import Flask, render_template, jsonify
import requests
from config import Config
from models import db, Match, Team, CacheStatus
from datetime import datetime, date, timedelta
import json

app = Flask(__name__)
app.config.from_object(Config)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///football_stats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize database
with app.app_context():
    db.create_all()


def get_api_headers():
    return {
        'X-RapidAPI-Key': app.config['API_FOOTBALL_KEY'],
        'X-RapidAPI-Host': app.config['API_FOOTBALL_HOST']
    }


# Static data for fallback (when not refreshing)
STATIC_MATCHES = [
    {
        "id": 1,
        "home_team": "Real Madrid",
        "away_team": "Barcelona",
        "home_logo": "https://logos-world.net/wp-content/uploads/2020/06/Real-Madrid-Logo.png",
        "away_logo": "https://logos-world.net/wp-content/uploads/2020/06/Barcelona-Logo.png",
        "home_score": 2,
        "away_score": 1,
        "status": "FT",
        "elapsed": None,
        "time": "2025-07-02T20:00:00Z",
        "league": "La Liga",
        "league_logo": "https://logos-world.net/wp-content/uploads/2020/06/La-Liga-Logo.png",
        "venue": "Santiago Bernabéu",
        "is_live": False
    },
    {
        "id": 2,
        "home_team": "Manchester City",
        "away_team": "Liverpool",
        "home_logo": "https://logos-world.net/wp-content/uploads/2020/06/Manchester-City-Logo.png",
        "away_logo": "https://logos-world.net/wp-content/uploads/2020/06/Liverpool-Logo.png",
        "home_score": 1,
        "away_score": 2,
        "status": "2H",
        "elapsed": 67,
        "time": "2025-07-02T21:00:00Z",
        "league": "Premier League",
        "league_logo": "https://logos-world.net/wp-content/uploads/2020/06/Premier-League-Logo.png",
        "venue": "Etihad Stadium",
        "is_live": True
    }
]

STATIC_LINEUPS = {
    1: [  # Real Madrid vs Barcelona
        {
            "team_name": "Real Madrid",
            "team_logo": "https://logos-world.net/wp-content/uploads/2020/06/Real-Madrid-Logo.png",
            "formation": "4-3-3",
            "coach": "Carlo Ancelotti",
            "players": [
                {"id": 1, "name": "Thibaut Courtois", "number": 1, "position": "GK", "grid": "1:1"},
                {"id": 2, "name": "Ferland Mendy", "number": 23, "position": "LB", "grid": "2:1"},
                {"id": 3, "name": "David Alaba", "number": 4, "position": "CB", "grid": "2:2"},
                {"id": 4, "name": "Éder Militão", "number": 3, "position": "CB", "grid": "2:3"},
                {"id": 5, "name": "Dani Carvajal", "number": 2, "position": "RB", "grid": "2:4"},
                {"id": 6, "name": "Toni Kroos", "number": 8, "position": "CM", "grid": "3:1"},
                {"id": 7, "name": "Casemiro", "number": 14, "position": "CDM", "grid": "3:2"},
                {"id": 8, "name": "Luka Modrić", "number": 10, "position": "CM", "grid": "3:3"},
                {"id": 9, "name": "Vinícius Jr.", "number": 20, "position": "LW", "grid": "4:1"},
                {"id": 10, "name": "Karim Benzema", "number": 9, "position": "ST", "grid": "4:2"},
                {"id": 11, "name": "Rodrygo", "number": 21, "position": "RW", "grid": "4:3"}
            ]
        },
        {
            "team_name": "Barcelona",
            "team_logo": "https://logos-world.net/wp-content/uploads/2020/06/Barcelona-Logo.png",
            "formation": "4-2-3-1",
            "coach": "Xavi Hernández",
            "players": [
                {"id": 12, "name": "Marc-André ter Stegen", "number": 1, "position": "GK", "grid": "1:1"},
                {"id": 13, "name": "Sergi Roberto", "number": 20, "position": "RB", "grid": "2:1"},
                {"id": 14, "name": "Ronald Araújo", "number": 4, "position": "CB", "grid": "2:2"},
                {"id": 15, "name": "Gerard Piqué", "number": 3, "position": "CB", "grid": "2:3"},
                {"id": 16, "name": "Jordi Alba", "number": 18, "position": "LB", "grid": "2:4"},
                {"id": 17, "name": "Sergio Busquets", "number": 5, "position": "CDM", "grid": "3:1"},
                {"id": 18, "name": "Frenkie de Jong", "number": 21, "position": "CM", "grid": "3:2"},
                {"id": 19, "name": "Pedri", "number": 16, "position": "CAM", "grid": "4:1"},
                {"id": 20, "name": "Ousmane Dembélé", "number": 7, "position": "RW", "grid": "4:2"},
                {"id": 21, "name": "Ansu Fati", "number": 10, "position": "LW", "grid": "4:3"},
                {"id": 22, "name": "Memphis Depay", "number": 9, "position": "ST", "grid": "5:1"}
            ]
        }
    ],
    2: [  # Manchester City vs Liverpool
        {
            "team_name": "Manchester City",
            "team_logo": "https://logos-world.net/wp-content/uploads/2020/06/Manchester-City-Logo.png",
            "formation": "4-2-3-1",
            "coach": "Pep Guardiola",
            "players": [
                {"id": 23, "name": "Ederson", "number": 31, "position": "GK", "grid": "1:1"},
                {"id": 24, "name": "Kyle Walker", "number": 2, "position": "RB", "grid": "2:1"},
                {"id": 25, "name": "Rúben Dias", "number": 3, "position": "CB", "grid": "2:2"},
                {"id": 26, "name": "John Stones", "number": 5, "position": "CB", "grid": "2:3"},
                {"id": 27, "name": "João Cancelo", "number": 27, "position": "LB", "grid": "2:4"},
                {"id": 28, "name": "Rodri", "number": 16, "position": "CDM", "grid": "3:1"},
                {"id": 29, "name": "Kevin De Bruyne", "number": 17, "position": "CM", "grid": "3:2"},
                {"id": 30, "name": "Bernardo Silva", "number": 20, "position": "CM", "grid": "3:3"},
                {"id": 31, "name": "Riyad Mahrez", "number": 26, "position": "RW", "grid": "4:1"},
                {"id": 32, "name": "Erling Haaland", "number": 9, "position": "ST", "grid": "4:2"},
                {"id": 33, "name": "Jack Grealish", "number": 10, "position": "LW", "grid": "4:3"}
            ]
        },
        {
            "team_name": "Liverpool",
            "team_logo": "https://logos-world.net/wp-content/uploads/2020/06/Liverpool-Logo.png",
            "formation": "4-3-3",
            "coach": "Jürgen Klopp",
            "players": [
                {"id": 34, "name": "Alisson", "number": 1, "position": "GK", "grid": "1:1"},
                {"id": 35, "name": "Trent Alexander-Arnold", "number": 66, "position": "RB", "grid": "2:1"},
                {"id": 36, "name": "Virgil van Dijk", "number": 4, "position": "CB", "grid": "2:2"},
                {"id": 37, "name": "Joel Matip", "number": 32, "position": "CB", "grid": "2:3"},
                {"id": 38, "name": "Andy Robertson", "number": 26, "position": "LB", "grid": "2:4"},
                {"id": 39, "name": "Fabinho", "number": 3, "position": "CDM", "grid": "3:1"},
                {"id": 40, "name": "Jordan Henderson", "number": 14, "position": "CM", "grid": "3:2"},
                {"id": 41, "name": "Thiago", "number": 6, "position": "CM", "grid": "3:3"},
                {"id": 42, "name": "Mohamed Salah", "number": 11, "position": "RW", "grid": "4:1"},
                {"id": 43, "name": "Darwin Núñez", "number": 27, "position": "ST", "grid": "4:2"},
                {"id": 44, "name": "Luis Díaz", "number": 23, "position": "LW", "grid": "4:3"}
            ]
        }
    ]
}



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/refresh-cache')
def refresh_cache():
    """REAL API REFRESH - Fetch live data from Football API"""
    try:
        # Clear existing matches
        db.session.query(Match).delete()

        # Fetch REAL data from API
        live_matches = fetch_live_matches_from_api()
        today_matches = fetch_today_matches_from_api()

        total_matches = len(live_matches) + len(today_matches)

        # Update cache status with REAL API call info
        cache_status = CacheStatus.query.filter_by(cache_type='live_refresh').first()
        if not cache_status:
            cache_status = CacheStatus(cache_type='live_refresh')

        cache_status.last_updated = datetime.utcnow()
        cache_status.total_matches = total_matches
        cache_status.api_calls_made = 2  # live + today API calls

        db.session.add(cache_status)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'✅ LIVE data refreshed! Loaded {total_matches} real matches from API.',
            'matches_count': total_matches,
            'last_updated': cache_status.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
            'data_source': 'live_api'
        })

    except Exception as e:
        # If API fails, fallback to static data
        return fallback_to_static_data(str(e))


def fetch_live_matches_from_api():
    """Fetch REAL live matches from Football API"""
    try:
        url = f"{app.config['API_FOOTBALL_URL']}/fixtures"
        params = {'live': 'all', 'timezone': 'Europe/Athens'}

        response = requests.get(url, headers=get_api_headers(), params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            matches = []

            for match_data in data.get('response', [])[:15]:  # Limit to 15 matches
                match = Match(
                    fixture_id=match_data['fixture']['id'],
                    home_team=match_data['teams']['home']['name'],
                    away_team=match_data['teams']['away']['name'],
                    home_logo=match_data['teams']['home']['logo'],
                    away_logo=match_data['teams']['away']['logo'],
                    home_score=match_data['goals']['home'],
                    away_score=match_data['goals']['away'],
                    status=match_data['fixture']['status']['short'],
                    elapsed=match_data['fixture']['status']['elapsed'],
                    match_time=datetime.fromisoformat(match_data['fixture']['date'].replace('Z', '+00:00')),
                    league=match_data['league']['name'],
                    league_logo=match_data['league']['logo'],
                    venue=match_data['fixture']['venue']['name'] if match_data['fixture']['venue'] else '',
                    is_live=True
                )

                db.session.add(match)
                matches.append(match)

            db.session.commit()
            return matches
        else:
            raise Exception(f"API returned status code {response.status_code}")

    except Exception as e:
        print(f"Error fetching live matches from API: {e}")
        raise e


def fetch_today_matches_from_api():
    """Fetch REAL today's matches from Football API"""
    try:
        today = date.today().strftime('%Y-%m-%d')
        url = f"{app.config['API_FOOTBALL_URL']}/fixtures"
        params = {'date': today, 'timezone': 'Europe/Athens'}

        response = requests.get(url, headers=get_api_headers(), params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            matches = []

            for match_data in data.get('response', [])[:25]:  # Limit to 25 matches
                # Skip if already exists (live matches)
                existing = Match.query.filter_by(fixture_id=match_data['fixture']['id']).first()
                if existing:
                    continue

                match = Match(
                    fixture_id=match_data['fixture']['id'],
                    home_team=match_data['teams']['home']['name'],
                    away_team=match_data['teams']['away']['name'],
                    home_logo=match_data['teams']['home']['logo'],
                    away_logo=match_data['teams']['away']['logo'],
                    home_score=match_data['goals']['home'],
                    away_score=match_data['goals']['away'],
                    status=match_data['fixture']['status']['short'],
                    elapsed=match_data['fixture']['status']['elapsed'],
                    match_time=datetime.fromisoformat(match_data['fixture']['date'].replace('Z', '+00:00')),
                    league=match_data['league']['name'],
                    league_logo=match_data['league']['logo'],
                    venue=match_data['fixture']['venue']['name'] if match_data['fixture']['venue'] else '',
                    is_live=False
                )

                db.session.add(match)
                matches.append(match)

            db.session.commit()
            return matches
        else:
            raise Exception(f"API returned status code {response.status_code}")

    except Exception as e:
        print(f"Error fetching today matches from API: {e}")
        raise e


def fallback_to_static_data(error_message):
    """Fallback to static data if API fails"""
    try:
        # Clear and add static data
        db.session.query(Match).delete()

        matches_added = 0
        for match_data in STATIC_MATCHES:
            match = Match(
                fixture_id=match_data['id'],
                home_team=match_data['home_team'],
                away_team=match_data['away_team'],
                home_logo=match_data['home_logo'],
                away_logo=match_data['away_logo'],
                home_score=match_data['home_score'],
                away_score=match_data['away_score'],
                status=match_data['status'],
                elapsed=match_data['elapsed'],
                match_time=datetime.fromisoformat(match_data['time'].replace('Z', '+00:00')),
                league=match_data['league'],
                league_logo=match_data['league_logo'],
                venue=match_data['venue'],
                is_live=match_data['is_live']
            )
            db.session.add(match)
            matches_added += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'⚠️ API failed ({error_message}). Loaded {matches_added} static matches for testing and showcase purposes',
            'matches_count': matches_added,
            'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'data_source': 'static_fallback'
        })

    except Exception as fallback_error:
        return jsonify({
            'success': False,
            'error': f'Both API and static fallback failed: {fallback_error}'
        })


@app.route('/api/initialize-static-data')
def initialize_static_data():
    """Initialize with static data for testing (separate from refresh)"""
    try:
        # Only add static data if database is empty
        existing_matches = Match.query.count()
        if existing_matches > 0:
            return jsonify({
                'success': True,
                'message': 'Database already has data. Use refresh to get live data.',
                'matches_count': existing_matches,
                'data_source': 'existing'
            })

        # Add static data for initial testing
        matches_added = 0
        for match_data in STATIC_MATCHES:
            match = Match(
                fixture_id=match_data['id'],
                home_team=match_data['home_team'],
                away_team=match_data['away_team'],
                home_logo=match_data['home_logo'],
                away_logo=match_data['away_logo'],
                home_score=match_data['home_score'],
                away_score=match_data['away_score'],
                status=match_data['status'],
                elapsed=match_data['elapsed'],
                match_time=datetime.fromisoformat(match_data['time'].replace('Z', '+00:00')),
                league=match_data['league'],
                league_logo=match_data['league_logo'],
                venue=match_data['venue'],
                is_live=match_data['is_live']
            )
            db.session.add(match)
            matches_added += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'📊 Initialized with {matches_added} static matches for testing.',
            'matches_count': matches_added,
            'data_source': 'static_initial'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/live-matches')
def get_live_matches():
    """Get live matches from database"""
    try:
        matches = Match.query.filter_by(is_live=True).order_by(Match.updated_at.desc()).all()
        return jsonify({
            'matches': [match.to_dict() for match in matches],
            'success': True,
            'from_cache': True,
            'count': len(matches)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})


@app.route('/api/today-matches')
def get_today_matches():
    """Get today's matches from database"""
    try:
        matches = Match.query.order_by(Match.match_time.asc()).all()
        return jsonify({
            'matches': [match.to_dict() for match in matches],
            'success': True,
            'from_cache': True,
            'count': len(matches)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})


@app.route('/api/team-lineup/<int:fixture_id>')
def get_team_lineup(fixture_id):
    """Get team lineup - try API first, fallback to static"""
    try:
        # Try to get lineup from real API
        if app.config.get('API_FOOTBALL_KEY'):
            try:
                url = f"{app.config['API_FOOTBALL_URL']}/fixtures/lineups"
                params = {'fixture': fixture_id}

                response = requests.get(url, headers=get_api_headers(), params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('response'):
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

                        return jsonify({'lineups': lineups, 'success': True, 'source': 'live_api'})
            except Exception as api_error:
                print(f"API lineup failed: {api_error}")

        # Fallback to static lineups
        if fixture_id in STATIC_LINEUPS:
            return jsonify({
                'lineups': STATIC_LINEUPS[fixture_id],
                'success': True,
                'source': 'static_fallback'
            })
        else:
            return jsonify({
                'error': 'Lineup not available for this match',
                'success': False
            })

    except Exception as e:
        return jsonify({'error': str(e), 'success': False})


@app.route('/api/cache-status')
def get_cache_status():
    """Get cache status information"""
    try:
        cache_status = CacheStatus.query.order_by(CacheStatus.last_updated.desc()).first()
        live_count = Match.query.filter_by(is_live=True).count()
        today_count = Match.query.count()

        return jsonify({
            'success': True,
            'last_updated': cache_status.last_updated.strftime('%Y-%m-%d %H:%M:%S') if cache_status else 'Never',
            'live_matches': live_count,
            'today_matches': today_count,
            'total_matches': today_count,
            'api_calls': cache_status.api_calls_made if cache_status else 0,
            'cache_type': cache_status.cache_type if cache_status else 'none'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})


if __name__ == '__main__':
    # Initialize with static data on startup if database is empty
    with app.app_context():
        if Match.query.count() == 0:
            print("🚀 Initializing database with static data for testing...")
            initialize_static_data()

    app.run(debug=True)
