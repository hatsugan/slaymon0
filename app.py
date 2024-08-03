from flask import Flask, render_template, request, redirect, url_for
from game_engine import Slay, Battle, get_random_slay, slay_list
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

battle = None

@app.route('/')
def index():
    logger.debug("Index route hit")
    return render_template('index.html', slay_list=slay_list)

@app.route('/select/<int:slay_index>')
def select_slay(slay_index):
    global battle
    player_slay = slay_list[slay_index]
    opponent_slay = get_random_slay()
    while opponent_slay.name == player_slay.name:
        opponent_slay = get_random_slay()
    player_slay = Slay(
        player_slay.name,
        player_slay.max_health,
        player_slay.strength,
        player_slay.hardness,
        player_slay.toughness,
        player_slay.speed,
        player_slay.moves
    )
    battle = Battle(player_slay, opponent_slay)
    logger.debug(f"Selected {player_slay.name}, opponent is {opponent_slay.name}")
    return redirect(url_for('battle_view'))

@app.route('/battle')
def battle_view():
    logging.debug('Battle view route hit')
    return render_template('battle.html', player=battle.player, opponent=battle.opponent, battle=battle)

@app.route('/move/<int:move_index>')
def move(move_index):
    logging.debug('Move route hit with move index %d', move_index)
    if battle.turn == 'player' and not battle.is_battle_over():
        battle.player_turn(move_index)
        if not battle.is_battle_over():
            battle.opponent_turn()
    return redirect(url_for('battle_view'))

@app.route('/rematch')
def rematch():
    global battle
    logger.debug("Rematch route hit")
    if battle:
        player_slay = Slay(
            battle.player.name,
            battle.player.max_health,
            battle.player.strength,
            battle.player.hardness,
            battle.player.toughness,
            battle.player.speed,
            battle.player.moves
        )
        opponent_slay = get_random_slay()
        while opponent_slay.name == player_slay.name:
            opponent_slay = get_random_slay()
        battle = Battle(player_slay, opponent_slay)
        logger.debug(f"Rematch: {battle.player.name} vs {battle.opponent.name}")
        logger.debug(f"{battle.player.name} starting health: {battle.player.health}")
        logger.debug(f"{battle.opponent.name} starting health: {battle.opponent.health}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
