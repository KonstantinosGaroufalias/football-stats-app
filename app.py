from flask import Flask, render_template, jsonify
from models import db, Match, Team, CacheStatus
from datetime import datetime, date, timedelta
import json

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///football_stats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize database with static data
with app.app_context():
    db.create_all()

# Static data for testing (avoiding API calls) DELETE ME LATER !!!!!!!!!!!!!!
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
    },
    {
        "id": 3,
        "home_team": "PSG",
        "away_team": "Bayern Munich",
        "home_logo": "https://logos-world.net/wp-content/uploads/2020/06/PSG-Logo.png",
        "away_logo": "https://logos-world.net/wp-content/uploads/2020/06/Bayern-Munich-Logo.png",
        "home_score": 0,
        "away_score": 1,
        "status": "1H",
        "elapsed": 34,
        "time": "2025-07-02T22:00:00Z",
        "league": "Champions League",
        "league_logo": "https://logos-world.net/wp-content/uploads/2020/06/UEFA-Champions-League-Logo.png",
        "venue": "Parc des Princes",
        "is_live": True
    },
    {
        "id": 4,
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "home_logo": "https://logos-world.net/wp-content/uploads/2020/06/Arsenal-Logo.png",
        "away_logo": "https://logos-world.net/wp-content/uploads/2020/06/Chelsea-Logo.png",
        "home_score": None,
        "away_score": None,
        "status": "NS",
        "elapsed": None,
        "time": "2025-07-03T15:00:00Z",
        "league": "Premier League",
        "league_logo": "https://logos-world.net/wp-content/uploads/2020/06/Premier-League-Logo.png",
        "venue": "Emirates Stadium",
        "is_live": False
    },
    {
        "id": 5,
        "home_team": "Juventus",
        "away_team": "AC Milan",
        "home_logo": "https://logos-world.net/wp-content/uploads/2020/06/Juventus-Logo.png",
        "away_logo": "https://logos-world.net/wp-content/uploads/2020/06/AC-Milan-Logo.png",
        "home_score": 1,
        "away_score": 1,
        "status": "HT",
        "elapsed": None,
        "time": "2025-07-02T19:45:00Z",
        "league": "Serie A",
        "league_logo": "https://logos-world.net/wp-content/uploads/2020/06/Serie-A-Logo.png",
        "venue": "Allianz Stadium",
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
                {"id": 2, "name": "Dani Carvajal", "number": 2, "position": "RB", "grid": "2:1"},
                {"id": 3, "name": "Éder Militão", "number": 3, "position": "CB", "grid": "2:2"},
                {"id": 4, "name": "David Alaba", "number": 4, "position": "CB", "grid": "2:3"},
                {"id": 5, "name": "Ferland Mendy", "number": 23, "position": "LB", "grid": "2:4"},
                {"id": 6, "name": "Casemiro", "number": 14, "position": "CDM", "grid": "3:1"},
                {"id": 7, "name": "Luka Modrić", "number": 10, "position": "CM", "grid": "3:2"},
                {"id": 8, "name": "Toni Kroos", "number": 8, "position": "CM", "grid": "3:3"},
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
            "formation": "4-3-3",
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
    """Refresh database with static data"""
    try:
        # Clear existing matches
        db.session.query(Match).delete()

        # Add static matches to database
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

        # Update cache status
        cache_status = CacheStatus.query.filter_by(cache_type='static_refresh').first()
        if not cache_status:
            cache_status = CacheStatus(cache_type='static_refresh')

        cache_status.last_updated = datetime.utcnow()
        cache_status.total_matches = matches_added
        cache_status.api_calls_made = 0  # No API calls for static data

        db.session.add(cache_status)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Database refreshed with static data! Loaded {matches_added} matches.',
            'matches_count': matches_added,
            'last_updated': cache_status.last_updated.strftime('%Y-%m-%d %H:%M:%S')
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
    """Get team lineup from static data"""
    try:
        if fixture_id in STATIC_LINEUPS:
            return jsonify({
                'lineups': STATIC_LINEUPS[fixture_id],
                'success': True
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
        cache_status = CacheStatus.query.filter_by(cache_type='static_refresh').first()
        live_count = Match.query.filter_by(is_live=True).count()
        today_count = Match.query.count()

        return jsonify({
            'success': True,
            'last_updated': cache_status.last_updated.strftime('%Y-%m-%d %H:%M:%S') if cache_status else 'Never',
            'live_matches': live_count,
            'today_matches': today_count,
            'total_matches': today_count,
            'api_calls': 0  # No API calls for static data
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})


if __name__ == '__main__':
    app.run(debug=True)
