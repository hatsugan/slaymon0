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
    def __init__(self, player, opponent):
        self.player = player
        self.opponent = opponent
        self.turn_count = 0
        self.turn = 'player'
        self.turn_log = []
        self.log = []

    def calculate_damage(self, attacker, defender, move):
        return (attacker.attack / defender.defense) * move['power']

    def player_turn(self, move_index):
        move = self.player.moves[move_index]
        damage = self.calculate_damage(self.player, self.opponent, move)
        self.opponent.health = max(0, self.opponent.health - damage)
        self.turn_log.append(f"<span class='move'>{self.player.name} used {move['name']} on {self.opponent.name}</span>")
        self.turn_log.append(f"<span class='damage'>{self.opponent.name} lost {damage:.1f} health</span>")
        self.turn = 'opponent'

    def opponent_turn(self):
        move = random.choice(self.opponent.moves)
        damage = self.calculate_damage(self.opponent, self.player, move)
        self.player.health = max(0, self.player.health - damage)
        self.turn_log.append(f"<span class='move'>{self.opponent.name} used {move['name']} on {self.player.name}</span>")
        self.turn_log.append(f"<span class='damage'>{self.player.name} lost {damage:.1f} health</span>")
        self.end_turn()

    def end_turn(self):
        self.turn_count += 1
        self.log.append(f"<div class='turn-heading'>Turn {self.turn_count}</div>")
        self.log.extend(self.turn_log)
        self.turn_log = []
        self.turn = 'player'

    def is_battle_over(self):
        return self.player.is_fainted() or self.opponent.is_fainted()





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
