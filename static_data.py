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
