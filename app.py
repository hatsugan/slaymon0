from flask import Flask, render_template, request, redirect, url_for
from game_engine import Pokemon, Battle, get_random_pokemon, pokemon_list
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

battle = None

@app.route('/')
def index():
    logger.debug("Index route hit")
    return render_template('index.html', pokemon_list=pokemon_list)

@app.route('/select/<int:pokemon_index>')
def select_pokemon(pokemon_index):
    global battle
    player_pokemon = pokemon_list[pokemon_index]
    opponent_pokemon = get_random_pokemon()
    while opponent_pokemon.name == player_pokemon.name:
        opponent_pokemon = get_random_pokemon()
    player_pokemon = Pokemon(
        player_pokemon.name,
        player_pokemon.max_health,
        player_pokemon.attack,
        player_pokemon.defense,
        player_pokemon.speed,
        player_pokemon.moves
    )
    battle = Battle(player_pokemon, opponent_pokemon)
    logger.debug(f"Selected {player_pokemon.name}, opponent is {opponent_pokemon.name}")
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
        player_pokemon = Pokemon(
            battle.player_pokemon.name,
            battle.player_pokemon.max_health,
            battle.player_pokemon.attack,
            battle.player_pokemon.defense,
            battle.player_pokemon.speed,
            battle.player_pokemon.moves
        )
        opponent_pokemon = get_random_pokemon()
        while opponent_pokemon.name == player_pokemon.name:
            opponent_pokemon = get_random_pokemon()
        battle = Battle(player_pokemon, opponent_pokemon)
        logger.debug(f"Rematch: {battle.player_pokemon.name} vs {battle.opponent_pokemon.name}")
        logger.debug(f"{battle.player_pokemon.name} starting health: {battle.player_pokemon.health}")
        logger.debug(f"{battle.opponent_pokemon.name} starting health: {battle.opponent_pokemon.health}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
