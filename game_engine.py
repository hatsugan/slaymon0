import random
import logging
import pandas as pd


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def convert_moves_to_dict(moves):
    # Ensure moves are converted to a list of dictionaries
    return [{'name': move} for move in moves]

class Slay:
    def __init__(self, name, health, strength, hardness, toughness, speed, moves, abilities):
        self.name = name
        self.image = self.generate_image_filename()

        self.base_max_health = health

        # Base stats
        self.base_strength = strength
        self.base_hardness = hardness
        self.base_toughness = toughness
        self.base_speed = speed
        self.base_moves = moves
        self.base_abilities = abilities

        # Current stats
        self.max_health = self.base_max_health
        self.health = self.max_health
        self.strength = self.base_strength
        self.hardness = self.base_hardness
        self.toughness = self.base_toughness
        self.speed = self.base_speed
        self.moves = self.base_moves
        self.moves_dict = convert_moves_to_dict(moves)
        self.abilities = self.base_abilities

    def generate_image_filename(self):
        return f"{self.name.lower().replace(' ', '_')}.png"

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        if self.health > self.max_health:
            self.health = self.max_health
        if damage >= 0:
            logger.debug(f"{self.name} will take {damage:.1f} damage, health is now {self.health:.1f}")
        else:
            logger.debug(f"{self.name} will heal {-damage:.1f} health")

    def is_fainted(self):
        return self.health == 0

    def reset_to_base(self):
        self.max_health = self.base_max_health
        self.health = self.max_health
        self.strength = self.base_strength
        self.hardness = self.base_hardness
        self.toughness = self.base_toughness
        self.speed = self.base_speed
        self.moves = self.base_moves
        logger.debug(f"{self.name} reset completely")


class Battle:
    def __init__(self, player, opponent, move_handler):
        self.player = player
        self.opponent = opponent
        self.round_count = 0
        self.round_log = []
        self.log = []
        self.move_handler = move_handler

    def slay_move(self, attacker, defender, move, attacker_prefix, defender_prefix):
        self.move_handler.slay_move(attacker, defender, move, attacker_prefix, defender_prefix, self.round_log)

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
        logging.info(f"------ ROUND {self.round_count} ------")

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

def load_slays_from_csv(filepath):
    slays_df = pd.read_csv(filepath)
    slays_list = []
    for _, row in slays_df.iterrows():
        moves = eval(row['moves'])
        abilities = eval(row['abilities'])
        slay = Slay(
            row['name'],
            row['max_health'],
            row['strength'],
            row['hardness'],
            row['toughness'],
            row['speed'],
            moves,
            abilities
        )
        slays_list.append(slay)
    return slays_list

# Load the moves.csv from the 'slaipedia' directory
slay_list = load_slays_from_csv('slaipedia/slays.csv')


def get_random_slay():
    random_slay = random.choice(slay_list)
    return Slay(
        random_slay.name,
        random_slay.max_health,
        random_slay.strength,
        random_slay.hardness,
        random_slay.toughness,
        random_slay.speed,
        random_slay.moves,
        random_slay.abilities
    )
