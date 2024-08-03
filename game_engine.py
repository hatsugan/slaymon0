import random
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Pokemon:
    def __init__(self, name, health, attack, defense, speed, moves):
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.moves = moves

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        logger.debug(f"{self.name} takes {damage} damage, health is now {self.health}")

    def is_fainted(self):
        return self.health == 0

    def reset_health(self):
        self.health = self.max_health
        logger.debug(f"{self.name} health reset to {self.health}")

class Battle:
    def __init__(self, player_pokemon, opponent_pokemon):
        self.player_pokemon = player_pokemon
        self.opponent_pokemon = opponent_pokemon
        self.turn = 'player' if player_pokemon.speed >= opponent_pokemon.speed else 'opponent'
        logger.debug(f"Battle started: {self.player_pokemon.name} vs {self.opponent_pokemon.name}")
        logger.debug(f"{self.player_pokemon.name} starting health: {self.player_pokemon.health}")
        logger.debug(f"{self.opponent_pokemon.name} starting health: {self.opponent_pokemon.health}")

    def player_turn(self, move_index):
        if not self.is_battle_over():
            move = self.player_pokemon.moves[move_index]
            damage = self.calculate_damage(self.player_pokemon, self.opponent_pokemon, move)
            self.opponent_pokemon.take_damage(damage)
            logger.debug(f"{self.player_pokemon.name} uses {move['name']}, deals {damage} damage")
            self.turn = 'opponent'
            if self.is_battle_over():
                logger.debug("Battle over after player's turn")

    def opponent_turn(self):
        if not self.is_battle_over():
            move = random.choice(self.opponent_pokemon.moves)
            damage = self.calculate_damage(self.opponent_pokemon, self.player_pokemon, move)
            self.player_pokemon.take_damage(damage)
            logger.debug(f"{self.opponent_pokemon.name} uses {move['name']}, deals {damage} damage")
            self.turn = 'player'
            if self.is_battle_over():
                logger.debug("Battle over after opponent's turn")

    def calculate_damage(self, attacker, defender, move):
        return max(1, (attacker.attack + move['power']) - defender.defense)

    def is_battle_over(self):
        return self.player_pokemon.is_fainted() or self.opponent_pokemon.is_fainted()

# Example moves
tackle = {'name': 'Tackle', 'power': 5}
scratch = {'name': 'Scratch', 'power': 4}
ember = {'name': 'Ember', 'power': 6}
water_gun = {'name': 'Water Gun', 'power': 6}

# Example Pokémon
pokemon_list = [
    Pokemon('Pikachu', 35, 55, 40, 90, [tackle, scratch]),
    Pokemon('Charmander', 39, 52, 43, 65, [scratch, ember]),
    Pokemon('Squirtle', 44, 48, 65, 43, [tackle, water_gun]),
    Pokemon('Bulbasaur', 45, 49, 49, 45, [tackle, scratch])
]

def get_random_pokemon():
    random_pokemon = random.choice(pokemon_list)
    return Pokemon(
        random_pokemon.name,
        random_pokemon.max_health,
        random_pokemon.attack,
        random_pokemon.defense,
        random_pokemon.speed,
        random_pokemon.moves
    )
