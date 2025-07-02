class FootballApp {
    constructor() {
        this.currentView = 'live';
        this.selectedMatch = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadMatches('live');
        this.updateStatus('Ready');
    }

    bindEvents() {
        document.getElementById('live-tab').addEventListener('click', () => this.switchTab('live'));
        document.getElementById('today-tab').addEventListener('click', () => this.switchTab('today'));
        document.getElementById('refresh-btn').addEventListener('click', () => this.refreshData());
    }

    switchTab(view) {
        this.currentView = view;

        document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
        document.getElementById(`${view}-tab`).classList.add('active');

        this.loadMatches(view);
    }

    async refreshData() {
        const btn = document.getElementById('refresh-btn');
        btn.disabled = true;
        btn.textContent = 'Refreshing...';

        try {
            const response = await fetch('/api/refresh-cache');
            const data = await response.json();

            if (data.success) {
                this.updateStatus(`Updated: ${data.matches_count} matches`);
                this.loadMatches(this.currentView);
            } else {
                this.updateStatus('Error: ' + data.error);
            }
        } catch (error) {
            this.updateStatus('Connection error');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Refresh Data';
        }
    }

    async loadMatches(type) {
        const container = document.getElementById('matches');
        container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading matches...</p></div>';

        try {
            const endpoint = type === 'live' ? '/api/live-matches' : '/api/today-matches';
            const response = await fetch(endpoint);
            const data = await response.json();

            if (data.success) {
                this.renderMatches(data.matches);
                this.updateStatus(`${data.matches.length} matches loaded`);
            } else {
                container.innerHTML = `<div class="empty-state"><div class="empty-icon">📊</div><h3>No matches</h3><p>No matches found</p></div>`;
            }
        } catch (error) {
            container.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div><h3>Error</h3><p>Failed to load matches</p></div>`;
        }
    }

    renderMatches(matches) {
        const container = document.getElementById('matches');

        if (matches.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-icon">📊</div><h3>No matches</h3><p>No matches available</p></div>';
            return;
        }

        container.innerHTML = matches.map(match => this.createMatchHTML(match)).join('');

        container.querySelectorAll('.match').forEach(element => {
            element.addEventListener('click', () => this.selectMatch(element.dataset.id, element));
        });
    }

    createMatchHTML(match) {
        const statusClass = this.getStatusClass(match.status);
        const timeDisplay = this.formatTime(match.time);

        return `
            <div class="match" data-id="${match.id}">
                <div class="match-header">
                    <div class="match-teams">
                        <div class="team">
                            <img src="${match.home_logo}" alt="${match.home_team}" class="team-logo">
                            <span class="team-name">${match.home_team}</span>
                        </div>
                        <div class="team">
                            <img src="${match.away_logo}" alt="${match.away_team}" class="team-logo">
                            <span class="team-name">${match.away_team}</span>
                        </div>
                    </div>

                    <div class="match-score">
                        <div class="score">${match.home_score ?? '-'}</div>
                        <div class="score">${match.away_score ?? '-'}</div>
                    </div>

                    <div class="match-status">
                        <span class="status-badge ${statusClass}">
                            ${match.status}${match.elapsed ? ` ${match.elapsed}'` : ''}
                        </span>
                        ${timeDisplay ? `<div class="match-time">${timeDisplay}</div>` : ''}
                    </div>
                </div>

                <div class="match-footer">
                    ${match.league}${match.venue ? ` • ${match.venue}` : ''}
                </div>
            </div>
        `;
    }

    getStatusClass(status) {
        if (['1H', '2H', 'HT', 'ET', 'P', 'LIVE'].includes(status)) return 'status-live';
        if (['FT', 'AET', 'PEN'].includes(status)) return 'status-finished';
        return 'status-scheduled';
    }

    formatTime(time) {
        if (!time) return '';
        return new Date(time).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
    }

    selectMatch(matchId, element) {
        document.querySelectorAll('.match').forEach(el => el.classList.remove('selected'));
        element.classList.add('selected');
        this.selectedMatch = matchId;
        this.loadMatchDetails(matchId);
    }

    async loadMatchDetails(matchId) {
        const container = document.getElementById('details');
        container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading lineup...</p></div>';

        try {
            const response = await fetch(`/api/team-lineup/${matchId}`);
            const data = await response.json();

            if (data.success && data.lineups.length > 0) {
                this.renderLineup(data.lineups);
            } else {
                container.innerHTML = '<div class="empty-state"><div class="empty-icon">👥</div><h3>No lineup available</h3><p>Team lineup not available for this match</p></div>';
            }
        } catch (error) {
            container.innerHTML = '<div class="empty-state"><div class="empty-icon">⚠️</div><h3>Error</h3><p>Failed to load lineup</p></div>';
        }
    }

    renderLineup(lineups) {
        const container = document.getElementById('details');

        const html = lineups.map(lineup => {
            const teamId = lineup.team_name.replace(/\s+/g, '');
            return `
                <div class="team-section">
                    <div class="team-header">
                        <img src="${lineup.team_logo}" alt="${lineup.team_name}">
                        <div class="team-info">
                            <h3>${lineup.team_name}</h3>
                            <p>Formation: ${lineup.formation} • Coach: ${lineup.coach}</p>
                        </div>
                    </div>
                    <div class="formation" id="formation-${teamId}">
                        <div class="goal-area-top"></div>
                        <div class="goal-area-bottom"></div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = `<div class="lineup">${html}</div>`;

        // Position players with formation-specific logic
        lineups.forEach(lineup => {
            this.positionPlayersInFormation(lineup);
        });
    }

    // FORMATION-SPECIFIC POSITIONING SYSTEM
    positionPlayersInFormation(lineup) {
        const container = document.getElementById(`formation-${lineup.team_name.replace(/\s+/g, '')}`);
        if (!container) return;

        const formation = lineup.formation;
        const players = lineup.players;

        console.log(`Positioning ${lineup.team_name} in ${formation} formation`);

        // Sort players by their grid/position for consistent ordering
        const sortedPlayers = players.sort((a, b) => {
            if (a.grid && b.grid) {
                const [aRow, aCol] = a.grid.split(':').map(Number);
                const [bRow, bCol] = b.grid.split(':').map(Number);
                if (aRow !== bRow) return aRow - bRow;
                return aCol - bCol;
            }
            return 0;
        });

        // Use formation-specific positioning
        if (formation === '4-3-3') {
            this.position433Formation(container, sortedPlayers);
        } else if (formation === '4-2-3-1') {
            this.position4231Formation(container, sortedPlayers);
        } else if (formation === '4-4-2') {
            this.position442Formation(container, sortedPlayers);
        } else if (formation === '3-5-2') {
            this.position352Formation(container, sortedPlayers);
        } else if (formation === '5-3-2') {
            this.position532Formation(container, sortedPlayers);
        } else if (formation === '3-4-3') {
            this.position343Formation(container, sortedPlayers);
        } else {
            // Default/fallback formation
            this.positionDefaultFormation(container, sortedPlayers);
        }
    }

    // 4-3-3 Formation
    position433Formation(container, players) {
        const positions = [
            // GK
            { x: 50, y: 10 },
            // Defense (4)
            { x: 15, y: 25 }, { x: 35, y: 25 }, { x: 65, y: 25 }, { x: 85, y: 25 },
            // Midfield (3)
            { x: 25, y: 50 }, { x: 50, y: 50 }, { x: 75, y: 50 },
            // Attack (3)
            { x: 20, y: 80 }, { x: 50, y: 80 }, { x: 80, y: 80 }
        ];

        this.positionPlayersAtCoordinates(container, players, positions);
    }

    // 4-2-3-1 Formation
    position4231Formation(container, players) {
        const positions = [
            // GK
            { x: 50, y: 10 },
            // Defense (4)
            { x: 15, y: 25 }, { x: 35, y: 25 }, { x: 65, y: 25 }, { x: 85, y: 25 },
            // Defensive Midfield (2)
            { x: 35, y: 45 }, { x: 65, y: 45 },
            // Attacking Midfield (3)
            { x: 20, y: 65 }, { x: 50, y: 65 }, { x: 80, y: 65 },
            // Striker (1)
            { x: 50, y: 85 }
        ];

        this.positionPlayersAtCoordinates(container, players, positions);
    }

    // 4-4-2 Formation
    position442Formation(container, players) {
        const positions = [
            // GK
            { x: 50, y: 10 },
            // Defense (4)
            { x: 15, y: 25 }, { x: 35, y: 25 }, { x: 65, y: 25 }, { x: 85, y: 25 },
            // Midfield (4)
            { x: 15, y: 50 }, { x: 35, y: 50 }, { x: 65, y: 50 }, { x: 85, y: 50 },
            // Attack (2)
            { x: 35, y: 80 }, { x: 65, y: 80 }
        ];

        this.positionPlayersAtCoordinates(container, players, positions);
    }

    // 3-5-2 Formation
    position352Formation(container, players) {
        const positions = [
            // GK
            { x: 50, y: 10 },
            // Defense (3)
            { x: 25, y: 25 }, { x: 50, y: 25 }, { x: 75, y: 25 },
            // Midfield (5)
            { x: 10, y: 50 }, { x: 30, y: 50 }, { x: 50, y: 50 }, { x: 70, y: 50 }, { x: 90, y: 50 },
            // Attack (2)
            { x: 35, y: 80 }, { x: 65, y: 80 }
        ];

        this.positionPlayersAtCoordinates(container, players, positions);
    }

    // 5-3-2 Formation
    position532Formation(container, players) {
        const positions = [
            // GK
            { x: 50, y: 10 },
            // Defense (5)
            { x: 10, y: 25 }, { x: 30, y: 25 }, { x: 50, y: 25 }, { x: 70, y: 25 }, { x: 90, y: 25 },
            // Midfield (3)
            { x: 25, y: 50 }, { x: 50, y: 50 }, { x: 75, y: 50 },
            // Attack (2)
            { x: 35, y: 80 }, { x: 65, y: 80 }
        ];

        this.positionPlayersAtCoordinates(container, players, positions);
    }

    // 3-4-3 Formation
    position343Formation(container, players) {
        const positions = [
            // GK
            { x: 50, y: 10 },
            // Defense (3)
            { x: 25, y: 25 }, { x: 50, y: 25 }, { x: 75, y: 25 },
            // Midfield (4)
            { x: 15, y: 50 }, { x: 35, y: 50 }, { x: 65, y: 50 }, { x: 85, y: 50 },
            // Attack (3)
            { x: 20, y: 80 }, { x: 50, y: 80 }, { x: 80, y: 80 }
        ];

        this.positionPlayersAtCoordinates(container, players, positions);
    }

    // Default formation for unknown formations
    positionDefaultFormation(container, players) {
        const positions = [
            // GK
            { x: 50, y: 10 },
            // Back line
            { x: 20, y: 25 }, { x: 40, y: 25 }, { x: 60, y: 25 }, { x: 80, y: 25 },
            // Mid line
            { x: 25, y: 50 }, { x: 50, y: 50 }, { x: 75, y: 50 },
            // Front line
            { x: 30, y: 75 }, { x: 50, y: 75 }, { x: 70, y: 75 }
        ];

        this.positionPlayersAtCoordinates(container, players, positions);
    }

    // Helper function to position players at specific coordinates
    positionPlayersAtCoordinates(container, players, positions) {
        players.forEach((player, index) => {
            if (index < positions.length) {
                const playerEl = this.createPlayerElement(player);
                const pos = positions[index];

                playerEl.style.left = pos.x + '%';
                playerEl.style.top = pos.y + '%';
                playerEl.style.transform = 'translate(-50%, -50%)';

                container.appendChild(playerEl);

                console.log(`Player ${player.number} (${player.name}) positioned at ${pos.x}%, ${pos.y}%`);
            }
        });
    }

    createPlayerElement(player) {
        const playerEl = document.createElement('div');
        playerEl.className = 'player';
        playerEl.textContent = player.number;
        playerEl.title = `${player.name} (${player.position})`;
        return playerEl;
    }

    updateStatus(message) {
        document.querySelector('.status-text').textContent = message;
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    new FootballApp();
});
