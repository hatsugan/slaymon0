import random
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Slay:
    def __init__(self, name, health, strength, hardness, toughness, speed, moves):
        self.name = name
        self.max_health = health
        self.health = health
        self.strength = strength
        self.hardness = hardness
        self.toughness = toughness
        self.speed = speed
        self.moves = moves

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        logger.debug(f"{self.name} takes {damage:.1f} damage, health is now {self.health:.1f}")

    def is_fainted(self):
        return self.health == 0

    def reset_health(self):
        self.health = self.max_health
        logger.debug(f"{self.name} health reset to {self.health:.1f}")


class Battle:
    def __init__(self, player, opponent):
        self.player = player
        self.opponent = opponent
        self.turn_count = 0
        self.turn_log = []
        self.log = []

    def calculate_damage(self, attacker, defender, move):
        return move['base_damage'] * 1.3161 ** (attacker.strength - defender.toughness)

    def player_turn(self, move_index):
        move = self.player.moves[move_index]
        damage = self.calculate_damage(self.player, self.opponent, move)
        self.opponent.take_damage(damage)
        self.turn_log.append(f"<span class='move'>{self.player.name} used {move['name']} on {self.opponent.name}</span>")
        self.turn_log.append(f"<span class='damage'>{self.opponent.name} lost {damage:.1f} health</span>")

    def opponent_turn(self):
        move = random.choice(self.opponent.moves)
        damage = self.calculate_damage(self.opponent, self.player, move)
        self.player.take_damage(damage)
        self.turn_log.append(f"<span class='move'>{self.opponent.name} used {move['name']} on {self.player.name}</span>")
        self.turn_log.append(f"<span class='damage'>{self.player.name} lost {damage:.1f} health</span>")

    def end_turn(self):
        if self.turn_log:
            self.turn_count += 1
            self.log.append(f"<div class='turn-heading'>Turn {self.turn_count}</div>")
            self.log.extend(self.turn_log)
            self.turn_log = []
        if not self.is_battle_over():
            self.turn = 'player'

    def is_battle_over(self):
        return self.player.is_fainted() or self.opponent.is_fainted()






# Example moves
slash = {'name': 'Slash', 'base_damage': 5}
smash = {'name': 'Smash', 'base_damage': 10}
stab = {'name': 'Stab', 'base_damage': 5}
bite = {'name': 'Bite', 'base_damage': 10}

# Example Pokémon
slay_list = [
    Slay('Cutting Beetle', 30, 3, 3, 2, 10, [slash, bite]),
    Slay('Hydrypt', 15, 1, 3, 1, 30, [stab]),
    Slay('Hard Crab', 40, 3, 3, 2, 10, [smash]),
    Slay('Soft Crab', 50, 3, 2, 3, 20, [smash]),
    Slay('Spider', 15, 3, 3, 1, 20, [bite]),
]

def get_random_slay():
    random_slay = random.choice(slay_list)
    return Slay(
        random_slay.name,
        random_slay.max_health,
        random_slay.strength,
        random_slay.hardness,
        random_slay.toughness,
        random_slay.speed,
        random_slay.moves
    )
