from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fixture_id = db.Column(db.Integer, unique=True, nullable=False)
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    home_logo = db.Column(db.String(255))
    away_logo = db.Column(db.String(255))
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    status = db.Column(db.String(20), nullable=False)
    elapsed = db.Column(db.Integer)
    match_time = db.Column(db.DateTime)
    league = db.Column(db.String(100))
    league_logo = db.Column(db.String(255))
    venue = db.Column(db.String(100))
    is_live = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.fixture_id,
            'home_team': self.home_team,
            'away_team': self.away_team,
            'home_logo': self.home_logo,
            'away_logo': self.away_logo,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'status': self.status,
            'elapsed': self.elapsed,
            'time': self.match_time.isoformat() if self.match_time else None,
            'league': self.league,
            'league_logo': self.league_logo,
            'venue': self.venue,
            'is_live': self.is_live
        }

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    logo = db.Column(db.String(255))
    country = db.Column(db.String(50))
    founded = db.Column(db.Integer)
    venue = db.Column(db.String(100))

class CacheStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cache_type = db.Column(db.String(50), nullable=False)  # 'live', 'today'
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    total_matches = db.Column(db.Integer, default=0)
    api_calls_made = db.Column(db.Integer, default=0)
