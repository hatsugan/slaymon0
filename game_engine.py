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
        self.image = self.generate_image_filename()

    def generate_image_filename(self):
        return f"{self.name.lower().replace(' ', '_')}.png"

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        if self.health > self.max_health:
            self.health = self.max_health
        if damage >= 0:
            logger.debug(f"{self.name} should take {damage:.1f} damage, health is now {self.health:.1f}")
        else:
            logger.debug(f"{self.name} should heal {-damage:.1f} health")

    def is_fainted(self):
        return self.health == 0

    def reset_health(self):
        self.health = self.max_health
        logger.debug(f"{self.name} health reset to {self.health:.1f}")


class Battle:
    def __init__(self, player, opponent):
        self.player = player
        self.opponent = opponent
        self.round_count = 0
        self.round_log = []
        self.log = []

    def calculate_damage(self, attacker, defender, move):
        if move['modality'] == 'BLUNT':
            factor = 1.3161 ** (attacker.strength - defender.toughness)
        elif move['modality'] == 'CUT':
            factor = (2/3 * (1.3161 ** (attacker.strength - defender.toughness)) +
                      1/3 * (1.3161 ** (attacker.strength - defender.hardness)))
        elif move['modality'] == 'PIERCE':
            factor = (1/3 * (1.3161 ** (attacker.strength - defender.toughness)) +
                      2/3 * (1.3161 ** (attacker.strength - defender.hardness)))
        else:
            factor = 1
        return move['base_damage'] * factor

    def calculate_healing(self, user, move):
        return - move['base_healing'] * user.toughness

    def slay_move(self, attacker, defender, move, attacker_prefix, defender_prefix):
        if move['modality'] in ['BLUNT', 'CUT', 'PIERCE']:
            damage = self.calculate_damage(attacker, defender, move)
            defender.take_damage(damage)
            self.round_log.append(
                f"<span class='move'>{attacker_prefix} {attacker.name} used {move['name']} on {defender_prefix} {defender.name}</span>")
            self.round_log.append(
                f"<span class='damage'>{defender_prefix} {defender.name} lost {damage:.1f} health</span>")
        elif move['modality'] == 'HEAL':
            healing = self.calculate_healing(attacker, move)
            attacker.take_damage(healing)
            self.round_log.append(f"<span class='move'>{attacker_prefix} {attacker.name} used {move['name']}</span>")
            self.round_log.append(
                f"<span class='damage'>{attacker_prefix} {attacker.name} gained {-healing:.1f} health</span>")

    def player_turn(self, move_index):
        self.player_move = self.player.moves[move_index]
        logging.debug(f"Player selected move: {self.player_move}")

    def opponent_CPU(self):
        self.opponent_move = random.choice(self.opponent.moves)
        logging.debug(f"Opponent selected move: {self.opponent_move}")

    def execute_round(self):
        self.round_log = []
        self.round_count += 1
        self.log.append(f"<div class='turn-heading'>Round {self.round_count}</div>")

        if self.player.speed >= self.opponent.speed:
            self.log.append(f"Player's {self.player.name} is faster than Opponent's {self.opponent.name}")
            self.slay_move(self.player, self.opponent, self.player_move, "Player's", "Opponent's")
            if not self.opponent.is_fainted():
                self.slay_move(self.opponent, self.player, self.opponent_move, "Opponent's", "Player's")
        else:
            self.log.append(f"Opponent's {self.opponent.name} is faster than Player's {self.player.name}")
            self.slay_move(self.opponent, self.player, self.opponent_move, "Opponent's", "Player's")
            if not self.player.is_fainted():
                self.slay_move(self.player, self.opponent, self.player_move, "Player's", "Opponent's")

        self.end_round()



    def end_round(self):
        if self.round_log:
            self.log.extend(self.round_log)
            self.round_log = []
        if self.is_battle_over():
            self.turn = 'over'
        else:
            self.turn = 'player'
    def is_battle_over(self):
        return self.player.is_fainted() or self.opponent.is_fainted()


# Example moves
slash = {'name': 'Slash', 'modality': 'CUT', 'base_damage': 5}
smash = {'name': 'Smash', 'modality': 'BLUNT', 'base_damage': 10}
stab = {'name': 'Stab', 'modality': 'PIERCE', 'base_damage': 5}
bite = {'name': 'Bite', 'modality': 'PIERCE', 'base_damage': 10}
heal = {'name': 'Heal', 'modality': 'HEAL', 'base_healing': 2}

# Example Slays
slay_list = [
    Slay('Cutting Beetle', 30, 3, 4, 2, 15, [slash, bite, heal]),
    Slay('Hydrypt', 15, 1, 3, 1, 30, [stab, heal]),
    Slay('Hard Crab', 40, 3, 4, 2, 10, [smash, heal]),
    Slay('Soft Crab', 50, 3, 2, 3, 20, [smash, heal]),
    Slay('Spider', 15, 3, 3, 1, 20, [bite, heal]),
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
