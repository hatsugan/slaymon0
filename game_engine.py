import random
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_moves_from_csv(filepath):
    moves_df = pd.read_csv(filepath)
    return moves_df

def convert_moves_to_dict(moves):
    # Ensure moves are converted to a list of dictionaries
    return [{'name': move} for move in moves]

# Load the moves.csv from the 'slaipedia' directory
moves_df = load_moves_from_csv('slaipedia/moves.csv')


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
            logger.debug(f"{self.name} should take {damage:.1f} damage, health is now {self.health:.1f}")
        else:
            logger.debug(f"{self.name} should heal {-damage:.1f} health")

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
    def __init__(self, player, opponent):
        self.player = player
        self.opponent = opponent
        self.round_count = 0
        self.round_log = []
        self.log = []

    def calc_move_damage(self, attacker, defender, move_df):
        damage = move_df['target_direct_damage']
        move_name = move_df['name']
        attacker_abilities = attacker.abilities
        print(attacker_abilities)
        defender_abilities = defender.abilities

        move_additional_cut_damage = False
        move_additional_pierce_damage = False

        logging.debug(f"{move_name} damage being calculated.")

        # Appendage attacks
        if move_name in ['Strike', 'Jab', 'Slash', 'Stab', 'Bludgeon']:
            logger.debug(f"This is an appendage attack")
            if 'Blade' in attacker_abilities:
                move_additional_cut_damage = True
                logger.debug(f"This is a cutting appendage attack")
            else:
                move_additional_cut_damage = False
            if 'Point' in attacker_abilities:
                move_additional_pierce_damage = True
                logger.debug(f"This is a piercing appendage attack")
            else:
                move_additional_pierce_damage = False

        # Biting attacks
        if move_name in ['Bite']:
            logger.debug(f"This is a biting attack")
            if {'Fangs', 'Beak'} & set(attacker_abilities):
                move_additional_pierce_damage = True
                logger.debug(f"This is a piercing biting attack")
            else:
                move_additional_pierce_damage = False

        # Body attacks
        if move_name in ['Tackle', 'Body Slam']:
            logger.debug(f"This is a body attack")
            if 'Sharp Body' in attacker_abilities:
                move_additional_cut_damage = True
                logger.debug(f"This is a cutting body attack")
            else:
                move_additional_cut_damage = False
            if 'Spiked Body' in attacker_abilities:
                move_additional_pierce_damage = True
                logger.debug(f"This is a piercing body attack")
            else:
                move_additional_pierce_damage = False

        # Calculate damages
        if damage > 0:
            logging.debug(f"Move will do {damage:.1f} direct damage.")  # Direct Damage Log
        if move_df['target_blunt_damage'] > 0:  # Blunt Damage
            damage += self.calc_damage_blunt(attacker, defender, move_df)
            logging.debug(f"Move will do {damage:.1f} blunt damage.")
        if move_df['target_cut_damage'] > 0 and move_additional_cut_damage:  # Cut Damage
            damage += self.calc_damage_cut(attacker, defender, move_df)
            logging.debug(f"Move will do {damage:.1f} cut damage.")
        if move_df['target_pierce_damage'] > 0 and move_additional_pierce_damage:  # Pierce Damage
            damage += self.calc_damage_pierce(attacker, defender, move_df)
            logging.debug(f"Move will do {damage:.1f} pierce damage.")
        return damage


    def calc_damage_blunt(self, attacker, defender, move_df):
        factor = 1.3161 ** (attacker.strength - defender.toughness)
        return move_df['target_blunt_damage'] * factor


    def calc_damage_cut(self, attacker, defender, move_df):
        if attacker.hardness - defender.hardness >= 0:
            factor = (2 / 3 * (1.3161 ** (attacker.strength - defender.toughness)) +
                  1 / 3 * (1.3161 ** (attacker.strength - defender.hardness)))
        else:
            factor = 0
            logging.debug("Defender could not be pierced")
        return move_df['target_cut_damage'] * factor

    def calc_damage_pierce(self, attacker, defender, move_df):
        if attacker.hardness - defender.hardness >= 2:
            factor = (1 / 3 * (1.3161 ** (attacker.strength - defender.toughness)) +
                      2 / 3 * (1.3161 ** (attacker.strength - defender.hardness)))
        else:
            factor = 0
            logging.debug("Defender could not be pierced")
        return move_df['target_pierce_damage'] * factor


    def slay_move(self, attacker, defender, move, attacker_prefix, defender_prefix):
        move_df = moves_df.loc[moves_df['name'] == move].iloc[0]

        hurt_self = False

        # Damage
        damage = self.calc_move_damage(attacker, defender, move_df)
        defender.take_damage(damage)
        # Tackle Self Damage
        if move_df['name'] in ['Tackle', 'Body Slam', 'Bludgeon']:
            self_damage = self.calc_damage_blunt(defender, attacker, move_df)
            if 'Sharp Body' in defender.abilities:
                self_damage += self.calc_damage_cut(defender, attacker, move_df)
                logging.debug(f"Defender will cut reckless attacker")
            if 'Spiny Body' in defender.abilities:
                self_damage += self.calc_damage_pierce(defender, attacker, move_df)
                logging.debug(f"Defender will pierce reckless attacker")
            attacker.take_damage(damage)
            hurt_self = True

        # Healing
        healing = move_df['self_healing']

        # Apply Damage, Healing, Add to Log
        if healing > 0:
            self.round_log.append(
                f"<span class='move'>{attacker_prefix} {attacker.name} used {move}</span>")
            if attacker.health < attacker.max_health:
                logging.debug(f"Move will do {healing} healing")
                attacker.take_damage(-healing)
                self.round_log.append(
                    f"<span class='damage'>{attacker_prefix} {attacker.name} gained {healing:.1f} health</span>")
            else:
                logging.debug(f"User health is at max. Healing failed")
                self.round_log.append(
                    f"<span class='damage'>{attacker_prefix} {attacker.name}'s healing failed</span>")
        else:
            self.round_log.append(
                f"<span class='move'>{attacker_prefix} {attacker.name} used {move} on "
                f"{defender_prefix} {defender.name}</span>")
            self.round_log.append(
                f"<span class='damage'>{defender_prefix} {defender.name} lost {damage:.1f} health</span>")
            if hurt_self:
                self.round_log.append(f"<span class='damage'>{attacker_prefix} {attacker.name} hurt itself, taking {self_damage:.1f} damage</span>")

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

# Example Slays
slay_list = [
    Slay('Cutting Beetle', 30, 3, 4, 2, 15,
         ['Bite', 'Tackle'], ['Sharp Body']),
    Slay('Hydrypt', 15, 1, 3, 1, 30,
         ['Jab', 'Stab'], ['Point']),
    Slay('Hard Crab', 40, 3, 4, 2, 10,
         ['Strike', 'Jab', 'Bludgeon', 'Tackle', 'Body Slam', 'Rest'], []),
    Slay('Razor Crab', 20, 3, 3, 2, 25,
         ['Strike', 'Jab', 'Slash', 'Tackle', 'Body Slam', 'Rest'],
         ['Sharp Body', 'Blade']),
    Slay('Soft Crab', 50, 3, 2, 3, 20,
         ['Strike', 'Jab', 'Bludgeon', 'Tackle', 'Body Slam', 'Rest'], []),
    Slay('Spider', 15, 2, 3, 1, 20,
         ['Jab', 'Bite'], ['Fangs']),
    Slay('Tarantula', 30, 3, 2, 2, 30,
         ['Strike', 'Jab', 'Bite'], ['Fangs']),
    Slay('Blade Squid', 35, 2, 1, 1, 35,
         ['Strike', 'Jab', 'Slash', 'Bite', 'Rest'], ['Blade', 'Beak']),
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
        random_slay.moves,
        random_slay.abilities
    )
