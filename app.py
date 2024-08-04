from flask import Flask, render_template, request, redirect, url_for, jsonify
from game_engine import Slay, Battle, get_random_slay, get_random_team, slay_list, Player
from move_handler import MoveHandler
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

moves_df = pd.read_csv('slaipedia/moves.csv')
move_handler = MoveHandler(moves_df)

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
    player_team = get_random_team()
    opponent_team = get_random_team()
    player_team[0] = player_slay  # Ensure the selected Slay is part of the player's team
    player = Player("Player", player_team)
    opponent = Player("Opponent", opponent_team)
    logging.debug("Player 1 team is:")
    for slay in player_team:
        logging.debug(slay.name)
    logging.debug("Player 2 team is:")
    for slay in opponent_team:
        logging.debug(slay.name)
    battle = Battle(player, opponent, move_handler)
    logger.debug(f"Selected {player.active_slay.name}, opponent is {opponent.active_slay.name}")
    return redirect(url_for('battle_view'))

@app.route('/battle')
def battle_view():
    logging.debug('Battle view route hit')
    return render_template('battle.html', player=battle.player1.active_slay, opponent=battle.player2.active_slay, battle=battle)

@app.route('/move/<int:move_index>')
def move(move_index):
    logging.debug('Move route hit with move index %d', move_index)
    if not battle.is_battle_over():
        battle.player1.chosen_action = 'Move'
        battle.player1.chosen_move_index = move_index
        battle.execute_round()
    return redirect(url_for('battle_view'))

@app.route('/switch/<int:slay_index>')
def switch_to(slay_index):
    logging.debug(f'Switch to slay {slay_index}')
    if not battle.is_battle_over():
        battle.player1.chosen_action = 'Switch'
        battle.player1.chosen_switch_index = slay_index
        battle.execute_round()
    return redirect(url_for('battle_view'))

@app.route('/switch')
def switch():
    logging.debug('Switch route hit')
    return render_template('switch.html', player=battle.player1, battle=battle)

@app.route('/rematch')
def rematch():
    global battle
    logger.debug("Rematch route hit")
    if battle:
        player_team = get_random_team()
        opponent_team = get_random_team()
        player_team[0] = Slay(
            battle.player1.active_slay.name,
            battle.player1.active_slay.max_health,
            battle.player1.active_slay.strength,
            battle.player1.active_slay.hardness,
            battle.player1.active_slay.toughness,
            battle.player1.active_slay.speed,
            battle.player1.active_slay.moves,
            battle.player1.active_slay.abilities
        )
        for slay in player_team:
            slay.reset_to_base()
        for slay in opponent_team:
            slay.reset_to_base()
        logger.debug("Slays all reset")

        player = Player("Aures", player_team)
        opponent = Player("Robo Aaron", opponent_team)
        battle = Battle(player, opponent, move_handler)
        logger.debug(f"Rematch: {battle.player1.active_slay.name} vs {battle.player2.active_slay.name}")
        logger.debug(f"{battle.player1.active_slay.name} starting health: {battle.player1.active_slay.health}")
        logger.debug(f"{battle.player2.active_slay.name} starting health: {battle.player2.active_slay.health}")
    return redirect(url_for('index'))

@app.route('/moves_json')
def get_moves():
    # Convert DataFrame to dictionary
    moves_dict = moves_df.to_dict(orient='records')
    return jsonify(moves_dict)

if __name__ == '__main__':
    app.run(debug=True)
