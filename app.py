from flask import Flask, render_template, jsonify
import requests
from config import Config
from models import db, Match, Team, CacheStatus
from datetime import datetime, date, timedelta
import json
import os

# Import static data from separate file
from static_data import STATIC_MATCHES, STATIC_LINEUPS

app = Flask(__name__)
app.config.from_object(Config)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///football_stats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize database
with app.app_context():
    db.create_all()


# API Usage Tracker Class
class APIUsageTracker:
    def __init__(self, max_calls_per_day=100):
        self.max_calls_per_day = max_calls_per_day
        self.usage_file = 'api_usage.json'

    def can_make_call(self):
        usage = self.get_today_usage()
        return usage < self.max_calls_per_day

    def record_api_call(self):
        today = datetime.now().strftime('%Y-%m-%d')
        usage_data = self.load_usage_data()

        if today not in usage_data:
            usage_data[today] = 0
        usage_data[today] += 1

        self.save_usage_data(usage_data)

    def get_today_usage(self):
        today = datetime.now().strftime('%Y-%m-%d')
        usage_data = self.load_usage_data()
        return usage_data.get(today, 0)

    def load_usage_data(self):
        if os.path.exists(self.usage_file):
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        return {}

    def save_usage_data(self, data):
        with open(self.usage_file, 'w') as f:
            json.dump(data, f)


# Create API tracker instance
api_tracker = APIUsageTracker(max_calls_per_day=100)


def get_api_headers():
    return {
        'X-RapidAPI-Key': app.config['API_FOOTBALL_KEY'],
        'X-RapidAPI-Host': app.config['API_FOOTBALL_HOST']
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/refresh-cache')
def refresh_cache():
    """REAL API REFRESH with rate limiting"""

    # Check if we can make API calls today
    if not api_tracker.can_make_call():
        return jsonify({
            'success': False,
            'error': f'Daily API limit reached ({api_tracker.max_calls_per_day} calls/day)',
            'usage_today': api_tracker.get_today_usage(),
            'remaining_calls': api_tracker.max_calls_per_day - api_tracker.get_today_usage()
        })

    try:
        # Clear existing matches
        db.session.query(Match).delete()

        # Record that we're making API calls
        api_tracker.record_api_call()

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
        cache_status.api_calls_made = 1

        db.session.add(cache_status)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'✅ LIVE data refreshed! Loaded {total_matches} real matches from API.',
            'matches_count': total_matches,
            'last_updated': cache_status.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
            'data_source': 'live_api',
            'usage_today': api_tracker.get_today_usage(),
            'remaining_calls': api_tracker.max_calls_per_day - api_tracker.get_today_usage()
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

            for match_data in data.get('response', [])[:15]:
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

            for match_data in data.get('response', [])[:25]:
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
            'message': f'⚠️ API failed ({error_message}). Loaded {matches_added} static matches for testing.',
            'matches_count': matches_added,
            'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'data_source': 'static_fallback'
        })

    except Exception as fallback_error:
        return jsonify({
            'success': False,
            'error': f'Both API and static fallback failed: {fallback_error}'
        })


@app.route('/api/usage-stats')
def get_usage_stats():
    """Get current API usage statistics"""
    return jsonify({
        'daily_limit': api_tracker.max_calls_per_day,
        'usage_today': api_tracker.get_today_usage(),
        'remaining_calls': api_tracker.max_calls_per_day - api_tracker.get_today_usage(),
        'usage_percentage': (api_tracker.get_today_usage() / api_tracker.max_calls_per_day) * 100
    })


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
            print(f"✅ Initialized with {matches_added} static matches")

    app.run(debug=True)
