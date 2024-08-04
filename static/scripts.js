// Auto-scroll the battle log to the end
window.onload = function() {
    var battleLog = document.getElementById("battle-log");
    if (battleLog) {
        battleLog.scrollTop = battleLog.scrollHeight;
    }
};

document.addEventListener('DOMContentLoaded', function() {
    const tooltip = document.getElementById('tooltip');
    let movesData = {};

    // Fetch moves data
    fetch('/moves')
        .then(response => response.json())
        .then(data => {
            movesData = data.reduce((acc, move) => {
                acc[move.name] = move;
                return acc;
            }, {});
        })
        .catch(error => console.error('Error fetching moves:', error));

    document.querySelectorAll('.moves a, .moves_opponent a').forEach(move => {
        move.addEventListener('contextmenu', function(event) {
            event.preventDefault();
            const moveName = this.textContent;
            const moveData = movesData[moveName];
            if (moveData) {
                tooltip.innerHTML = `<strong>Type:</strong> ${moveData.type}<br><strong>Description:</strong> ${moveData.description}`;
                tooltip.style.display = 'block';
                tooltip.style.left = `${event.pageX + 10}px`;
                tooltip.style.top = `${event.pageY + 10}px`;
            } else {
                tooltip.style.display = 'none';
            }
        });
    });

    document.addEventListener('click', function() {
        tooltip.style.display = 'none';
    });
});
