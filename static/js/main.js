// Load matches on page load
document.addEventListener('DOMContentLoaded', function() {
    loadMatches();
});

function loadMatches() {
    fetch('/api/matches')
        .then(response => response.json())
        .then(matches => {
            const container = document.getElementById('matches-container');
            container.innerHTML = '';

            matches.forEach(match => {
                const matchCard = createMatchCard(match);
                container.appendChild(matchCard);
            });
        });
}

function createMatchCard(match) {
    const card = document.createElement('div');
    card.className = 'bg-gray-700 p-3 rounded mb-2 match-card cursor-pointer';
    card.innerHTML = `
        <div class="flex justify-between items-center">
            <div class="flex-1">
                <p class="text-sm font-medium">${match.home_team}</p>
                <p class="text-sm font-medium">${match.away_team}</p>
            </div>
            <div class="text-right">
                <p class="text-lg font-bold">${match.home_score}</p>
                <p class="text-lg font-bold">${match.away_score}</p>
            </div>
            <div class="ml-2">
                <span class="text-xs bg-gray-600 px-2 py-1 rounded">${match.status}</span>
            </div>
        </div>
        <p class="text-xs text-gray-400 mt-1">${match.competition}</p>
    `;
    return card;
}
