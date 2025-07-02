let currentView = 'live';
let selectedMatchId = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize event listeners
    initializeEventListeners();

    // Load initial data
    loadMatches('live');

    // Auto-refresh live matches every 30 seconds
    setInterval(() => {
        if (currentView === 'live') {
            loadMatches('live');
        }
    }, 30000);
});

function initializeEventListeners() {
    document.getElementById('live-btn').addEventListener('click', () => switchView('live'));
    document.getElementById('today-btn').addEventListener('click', () => switchView('today'));
}

function switchView(view) {
    currentView = view;

    // Update button styles
    document.querySelectorAll('#live-btn, #today-btn').forEach(btn => {
        btn.classList.remove('bg-red-600', 'bg-blue-600');
        btn.classList.add('bg-gray-700');
    });

    if (view === 'live') {
        document.getElementById('live-btn').classList.remove('bg-gray-700');
        document.getElementById('live-btn').classList.add('bg-red-600');
    } else {
        document.getElementById('today-btn').classList.remove('bg-gray-700');
        document.getElementById('today-btn').classList.add('bg-blue-600');
    }

    loadMatches(view);
}

function loadMatches(type) {
    const container = document.getElementById('matches-container');
    container.innerHTML = '<div class="text-center text-gray-400 py-8"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>Loading matches...</div>';

    const endpoint = type === 'live' ? '/api/live-matches' : '/api/today-matches';

    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayMatches(data.matches);
            } else {
                container.innerHTML = `<div class="text-center text-red-400 py-8">Error: ${data.error}</div>`;
            }
        })
        .catch(error => {
            container.innerHTML = `<div class="text-center text-red-400 py-8">Connection error: ${error.message}</div>`;
        });
}

function displayMatches(matches) {
    const container = document.getElementById('matches-container');

    if (matches.length === 0) {
        container.innerHTML = '<div class="text-center text-gray-400 py-8">No matches found</div>';
        return;
    }

    container.innerHTML = '';

    matches.forEach(match => {
        const matchCard = createMatchCard(match);
        container.appendChild(matchCard);
    });
}

function createMatchCard(match) {
    const card = document.createElement('div');
    card.className = 'match-card p-4 rounded-lg';
    card.onclick = () => selectMatch(match.id, card);

    const statusClass = getStatusClass(match.status);
    const timeDisplay = getTimeDisplay(match);

    card.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex-1">
                <div class="flex items-center mb-2">
                    <img src="${match.home_logo}" alt="${match.home_team}" class="team-logo mr-2">
                    <span class="text-white font-medium">${match.home_team}</span>
                </div>
                <div class="flex items-center">
                    <img src="${match.away_logo}" alt="${match.away_team}" class="team-logo mr-2">
                    <span class="text-white font-medium">${match.away_team}</span>
                </div>
            </div>

            <div class="text-center mx-4">
                <div class="score-display text-white">
                    ${match.home_score !== null ? match.home_score : '-'}
                </div>
                <div class="score-display text-white">
                    ${match.away_score !== null ? match.away_score : '-'}
                </div>
            </div>

            <div class="text-right">
                <div class="px-3 py-1 rounded-full text-xs ${statusClass} mb-2">
                    ${match.status}${match.elapsed ? ` ${match.elapsed}'` : ''}
                </div>
                <div class="text-xs text-gray-400">${timeDisplay}</div>
            </div>
        </div>

        <div class="mt-3 pt-3 border-t border-gray-600">
            <div class="text-xs text-gray-400">${match.league}</div>
        </div>
    `;

    return card;
}

function getStatusClass(status) {
    switch(status) {
        case '1H':
        case '2H':
        case 'HT':
        case 'ET':
        case 'P':
            return 'status-live';
        case 'FT':
        case 'AET':
        case 'PEN':
            return 'status-ft';
        default:
            return 'status-scheduled';
    }
}

function getTimeDisplay(match) {
    if (match.time) {
        const matchTime = new Date(match.time);
        return matchTime.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
    }
    return '';
}

function selectMatch(matchId, cardElement) {
    // Remove previous selection
    document.querySelectorAll('.match-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Add selection to current card
    cardElement.classList.add('selected');
    selectedMatchId = matchId;

    // Load lineup
    loadTeamLineup(matchId);
}

function loadTeamLineup(fixtureId) {
    const container = document.getElementById('lineup-container');
    const noLineup = document.getElementById('no-lineup');

    noLineup.classList.add('hidden');
    container.classList.remove('hidden');
    container.innerHTML = '<div class="text-center text-gray-400 py-8"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>Loading lineup...</div>';

    fetch(`/api/team-lineup/${fixtureId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.lineups.length > 0) {
                displayLineup(data.lineups);
            } else {
                container.innerHTML = '<div class="text-center text-gray-400 py-8">Lineup not available for this match</div>';
            }
        })
        .catch(error => {
            container.innerHTML = `<div class="text-center text-red-400 py-8">Error loading lineup: ${error.message}</div>`;
        });
}

function displayLineup(lineups) {
    const container = document.getElementById('lineup-container');
    container.innerHTML = '';

    lineups.forEach((lineup, index) => {
        const teamSection = document.createElement('div');
        teamSection.className = 'mb-8';

        teamSection.innerHTML = `
            <div class="flex items-center mb-4">
                <img src="${lineup.team_logo}" alt="${lineup.team_name}" class="w-8 h-8 mr-3">
                <h3 class="text-xl font-bold text-white">${lineup.team_name}</h3>
                <span class="ml-auto text-sm text-gray-400">Formation: ${lineup.formation}</span>
            </div>

            <div class="football-pitch p-4 mb-4">
                <div class="pitch-lines">
                    <!-- Center circle -->
                    <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-20 h-20 border-2 border-white rounded-full"></div>
                    <!-- Center line -->
                    <div class="absolute top-0 bottom-0 left-1/2 w-0.5 bg-white"></div>
                    <!-- Goal areas -->
                    <div class="absolute top-1/4 left-0 w-8 h-1/2 border-2 border-white border-l-0"></div>
                    <div class="absolute top-1/4 right-0 w-8 h-1/2 border-2 border-white border-r-0"></div>
                </div>

                <div id="players-${index}" class="relative h-full">
                    <!-- Players will be positioned here -->
                </div>
            </div>

            <div class="text-sm text-gray-400">
                <strong>Coach:</strong> ${lineup.coach}
            </div>
        `;

        container.appendChild(teamSection);

        // Position players
        positionPlayers(lineup.players, index, lineup.formation);
    });
}

function positionPlayers(players, teamIndex, formation) {
    const playersContainer = document.getElementById(`players-${teamIndex}`);

    players.forEach(player => {
        const playerElement = document.createElement('div');
        playerElement.className = 'player-position';
        playerElement.textContent = player.number;
        playerElement.title = `${player.name} (${player.position})`;

        // Position based on grid (simplified positioning)
        const position = calculatePosition(player.grid, formation);
        playerElement.style.left = position.x + '%';
        playerElement.style.top = position.y + '%';

        playersContainer.appendChild(playerElement);
    });
}

function calculatePosition(grid, formation) {
    // Simplified positioning based on grid format like "1:1", "2:1", etc.
    const [row, col] = grid.split(':').map(Number);

    // Basic positioning logic (can be enhanced)
    const x = (col - 1) * 20 + 10; // Spread across width
    const y = (row - 1) * 15 + 10; // Spread across height

    return { x: Math.min(Math.max(x, 5), 85), y: Math.min(Math.max(y, 5), 85) };
}
