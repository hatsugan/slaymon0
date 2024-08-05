from flask import Flask, render_template, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import pandas as pd
import logging
from game_engine import Slay, Battle, get_random_team, slay_list, Player
from move_handler import MoveHandler

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

moves_df = pd.read_csv('slaipedia/moves.csv')
move_handler = MoveHandler(moves_df)

app = Flask(__name__)
socketio = SocketIO(app)

battles = {}


@app.route('/')
def index():
    logger.debug("Index route hit")
    return render_template('index.html')


@app.route('/multiplayer')
def multiplayer():
    logger.debug("Multiplayer route hit")
    return render_template('multiplayer.html')


@app.route('/single_player')
def single_player():
    global battles
    logger.debug("Single player route hit")

    player_team = [Slay(
        slay.name,
        slay.base_max_health,
        slay.base_strength,
        slay.base_hardness,
        slay.base_toughness,
        slay.base_speed,
        slay.base_moves,
        slay.base_abilities
    ) for slay in get_random_team()]

    opponent_team = [Slay(
        slay.name,
        slay.base_max_health,
        slay.base_strength,
        slay.base_hardness,
        slay.base_toughness,
        slay.base_speed,
        slay.base_moves,
        slay.base_abilities
    ) for slay in get_random_team()]

    player = Player("Player", player_team)
    opponent = Player("Opponent", opponent_team)
    battle_id = "single_player"
    battles[battle_id] = Battle(player, opponent, move_handler)

    logger.debug(f"Selected {player.active_slay.name}, opponent is {opponent.active_slay.name}")
    return redirect(url_for('battle_view', battle_id=battle_id))


@app.route('/battle/<battle_id>')
def battle_view(battle_id):
    battle = battles.get(battle_id)
    if not battle:
        return "Battle not found", 404
    logging.debug('Battle view route hit')
    return render_template('battle.html', player=battle.player1.active_slay, opponent=battle.player2.active_slay,
                           battle=battle)


@app.route('/move/<battle_id>/<int:move_index>')
def move(battle_id, move_index):
    battle = battles.get(battle_id)
    if not battle:
        return "Battle not found", 404
    logging.debug('Move route hit with move index %d', move_index)
    if not battle.is_battle_over():
        battle.player1.chosen_action = 'Move'
        battle.player1.chosen_move_index = move_index
        battle.execute_round()
    return redirect(url_for('battle_view', battle_id=battle_id))


@app.route('/switch/<battle_id>/<int:slay_index>')
def switch_to(battle_id, slay_index):
    battle = battles.get(battle_id)
    if not battle:
        return "Battle not found", 404
    logging.debug(f'Switch to slay {slay_index}')
    if not battle.is_battle_over():
        battle.player1.chosen_action = 'Switch'
        battle.player1.chosen_switch_index = slay_index
        battle.execute_round()
    return redirect(url_for('battle_view', battle_id=battle_id))


# @app.route('/switch/<battle_id>')
# def switch(battle_id):
#     battle = battles.get(battle_id)
#     if not battle:
#         return "Battle not found", 404
#     logging.debug('Switch route hit')
#     return render_template('switch.html', player=battle.player1, battle=battle)'


@app.route('/rematch/<battle_id>')
def rematch(battle_id):
    battle = battles.get(battle_id)
    if not battle:
        return "Battle not found", 404
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

        player = Player("Player", player_team)
        opponent = Player("Opponent", opponent_team)
        battles[battle_id] = Battle(player, opponent, move_handler)
        logger.debug(
            f"Rematch: {battles[battle_id].player1.active_slay.name} vs {battles[battle_id].player2.active_slay.name}")
        logger.debug(
            f"{battles[battle_id].player1.active_slay.name} starting health: {battles[battle_id].player1.active_slay.health}")
        logger.debug(
            f"{battles[battle_id].player2.active_slay.name} starting health: {battles[battle_id].player2.active_slay.health}")
    return redirect(url_for('index'))


@app.route('/moves_json')
def get_moves():
    moves_dict = moves_df.to_dict(orient='records')
    return jsonify(moves_dict)


@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('message', f'{data["username"]} has entered the room.', to=room)


@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit('message', f'{data["username"]} has left the room.', to=room)


@socketio.on('start_battle')
def on_start_battle(data):
    room = data['room']
    player_team = [Slay(
        slay.name,
        slay.base_max_health,
        slay.base_strength,
        slay.base_hardness,
        slay.base_toughness,
        slay.base_speed,
        slay.base_moves,
        slay.base_abilities
    ) for slay in get_random_team()]

    opponent_team = [Slay(
        slay.name,
        slay.base_max_health,
        slay.base_strength,
        slay.base_hardness,
        slay.base_toughness,
        slay.base_speed,
        slay.base_moves,
        slay.base_abilities
    ) for slay in get_random_team()]

    player = Player(data['username'], player_team)
    opponent = Player('Opponent', opponent_team)
    battles[room] = Battle(player, opponent, move_handler)

    emit('battle_started', {
        'player': player.active_slay.to_dict(),
        'opponent': opponent.active_slay.to_dict()
    }, to=room)


@socketio.on('move')
def on_move(data):
    room = data['room']
    move_index = data['move_index']
    battle = battles.get(room)
    if not battle:
        emit('error', {'message': 'Battle not found'}, to=room)
        return
    if not battle.is_battle_over():
        battle.player1.chosen_action = 'Move'
        battle.player1.chosen_move_index = move_index
        battle.execute_round()

    emit('battle_update', {
        'player': battle.player1.active_slay.to_dict(),
        'opponent': battle.player2.active_slay.to_dict()
    }, to=room)


if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8000)
