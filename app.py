from flask import Flask, render_template, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/matches')
def get_matches():
    # Placeholder for API integration
    sample_matches = [
        {
            'id': 1,
            'home_team': 'Dortmund',
            'away_team': 'Monterrey',
            'home_score': 2,
            'away_score': 1,
            'status': 'FT',
            'competition': 'FIFA Club World Cup'
        }
    ]
    return jsonify(sample_matches)

if __name__ == '__main__':
    app.run(debug=True)