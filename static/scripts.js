// Auto-scroll the battle log to the end
window.onload = function() {
    var battleLog = document.getElementById("battle-log");
    if (battleLog) {
        battleLog.scrollTop = battleLog.scrollHeight;
    }
};