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
    def __init__(self, name, health, strength, hardness, durability, speed, moves, abilities):
        self.name = name
        self.image = self.generate_image_filename()

        self.base_max_health = health

        # Base stats
        self.base_strength = strength
        self.base_hardness = hardness
        self.base_durability = durability
        self.base_speed = speed
        self.base_moves = moves
        self.base_abilities = abilities

        # Current stats
        self.max_health = self.base_max_health
        self.health = self.max_health
        self.strength = self.base_strength
        self.hardness = self.base_hardness
        self.durability = self.base_durability
        self.speed = self.base_speed
        self.moves = self.base_moves
        self.moves_dict = convert_moves_to_dict(moves)
        self.abilities = self.base_abilities

    def generate_image_filename(self):
        return f"{self.name.lower().replace(' ', '_')}.png"


    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0.1:
            self.health = 0
        if self.health > self.max_health:
            self.health = self.max_health
        if damage >= 0:
            logger.debug(f"{self.name} will take {damage:.1f} damage, health is now {self.health:.1f}")
        else:
            logger.debug(f"{self.name} will heal {-damage:.1f} health")

    def is_fainted(self):
        return self.health < 0.1

    def reset_to_base(self):
        self.max_health = self.base_max_health
        self.health = self.max_health
        self.strength = self.base_strength
        self.hardness = self.base_hardness
        self.durability = self.base_durability
        self.speed = self.base_speed
        self.moves = self.base_moves
        logger.debug(f"{self.name} reset completely")

class Player:
    def __init__(self, name, slays):
        self.name = name
        self.slays = slays
        self.active_slay = slays[0]  # Start with the first Slay in the team
        self.chosen_action = None
        self.chosen_move_index = None
        self.chosen_switch_index = None

    def reset_actions(self):
        self.chosen_action = None
        self.chosen_move_index = None
        self.chosen_switch_index = None

    def switch_slay(self):
        if self.chosen_switch_index < len(self.slays):
            self.active_slay = self.slays[self.chosen_switch_index]

    def switch_next_living_slay(self):
        for i, slay in enumerate(self.slays):
            if not slay.check_is_dead():
                self.chosen_switch_index = i
                logging.debug(f"{self.name} will switch to slay #{i}")
                self.switch_slay()
                return
            logging.debug(f"{slay.name} is dead, cannot switch")
        logging.debug(f"{self.name} has no remaining Slays to switch to")


    def is_defeated(self):
        return all(slay.check_is_dead() for slay in self.slays)

class Battle:
    def __init__(self, player1, player2, move_handler):
        self.player1 = player1
        self.player2 = player2
        self.round_count = 0
        self.round_log = []
        self.log = []
        self.move_handler = move_handler

    def slay_move(self, attacker, defender, move, attacker_prefix, defender_prefix):
        self.move_handler.slay_move(attacker, defender, move, attacker_prefix, defender_prefix, self.round_log)

    def player_action_move(self, player, move_index):
        self.player1_move = player.active_slay.moves[move_index]
        self.player1_switch = None
        logging.debug(f"{player.name} selected move: {self.player1_move}")


    # def opponent_action_move(self, opponent):
    #     if opponent.active_slay.is_fainted():
    #         self.opponent_action_switch(opponent)
    #     else:
    #         self.player2_move = random.choice(opponent.active_slay.moves)
    #         self.player2_switch = None
    #         logging.debug(f"{opponent.name} selected move: {self.player2_move}")
    #
    # def opponent_action_switch(self, opponent):
    #     for i, slay in enumerate(opponent.slays):
    #         if not slay.is_fainted():
    #             self.player2_switch = i
    #             self.player2_move = None
    #             self.round_log.append(f"{opponent.name} switched to {slay.name}")
    #             logging.debug(f"{opponent.name} switched to {slay.name}")
    #             return
    #     logging.debug(f"{opponent.name} has no remaining Slays to switch to")

    def execute_round(self):
        self.round_log = []
        self.round_count += 1
        self.log.append(f"<div class='turn-heading'>Round {self.round_count}</div>")
        logging.info(f"------------ ROUND {self.round_count} ------------")

        # Select random action for opponent
        self.player2.chosen_action = 'Move'
        self.player2.chosen_move_index = random.randint(0, len(self.player2.active_slay.moves)-1)


        if self.player1.chosen_action == 'Move':
            logging.debug(f"{self.player1.name} chose to have {self.player1.active_slay.name} use move #{self.player1.chosen_move_index} ({self.player1.active_slay.moves[self.player1.chosen_move_index]})")
        elif self.player1.chosen_action == 'Switch':
            logging.debug(f"{self.player1.name} chose to switch {self.player1.active_slay.name} to {self.player1.slays[self.player1.chosen_switch_index].name}")
            
        if self.player2.chosen_action == 'Move':
            logging.debug(f"{self.player2.name} chose to have {self.player2.active_slay.name} use move #{self.player2.chosen_move_index} ({self.player2.active_slay.moves[self.player2.chosen_move_index]})")
        elif self.player2.chosen_action == 'Switch':
            logging.debug(f"{self.player2.name} chose to switch {self.player2.active_slay.name} to {self.player2.slays[self.player2.chosen_switch_index].name}")


        # Switch Phase
        if self.player1.chosen_action == 'Switch':  # Switch Player 1
            self.player1.switch_slay()
            logging.debug(f"{self.player1.name} switched to {self.player1.active_slay.name}")

        if self.player2.chosen_action == 'Switch':  # Switch Player 1
            self.player2.switch_slay()
            logging.debug(f"{self.player2.name} switched to {self.player2.active_slay.name}")

        # Combat Phase
        # turn_order list - 1:[Attacker, Defender], 2:[Attacker, Defender]
        if self.player1.active_slay.speed >= self.player2.active_slay.speed:
            self.log.append(
                f"{self.player1.name}'s {self.player1.active_slay.name} is faster than {self.player2.name}'s {self.player2.active_slay.name}")
            turn_order = [[self.player1, self.player2],[self.player2, self.player1]]
        else:
            self.log.append(
                f"{self.player2.name}'s {self.player2.active_slay.name} is faster than {self.player1.name}'s {self.player1.active_slay.name}")
            turn_order = [[self.player2, self.player1], [self.player1, self.player2]]

        for attacker_defender in turn_order:
            attacker, defender = attacker_defender
            if attacker.chosen_action == 'Move':  # Catches if switching
                logging.debug(
                    f"{attacker.name} selected index: {attacker.chosen_move_index} from move list len {len(attacker.active_slay.moves)}, slay is {attacker.active_slay.name}")

                chosen_move = attacker.active_slay.moves[attacker.chosen_move_index]
                self.slay_move(attacker.active_slay, defender.active_slay, chosen_move, f"{attacker.name}'s",
                               f"{defender.name}'s")

                # Handle slay death
                if attacker.active_slay.check_is_dead() and defender.active_slay.check_is_dead():
                    self.round_log.append(
                        f"Both slays died! Yeesh!")
                    break
                elif attacker.active_slay.check_is_dead():
                    self.round_log.append(f"{attacker.name}'s {attacker.active_slay.name} died!")
                    break
                elif defender.active_slay.check_is_dead():
                    self.round_log.append(f"{defender.name}'s {defender.active_slay.name} died!")
                    break

        # Check win condition, otherwise switch
        if not self.player1.is_defeated() or not self.player2.is_defeated():
            if self.player1.active_slay.check_is_dead():
                self.player1.switch_next_living_slay()
                self.round_log.append(f"{self.player1.name} switched to {self.player1.active_slay.name}")
            if self.player2.active_slay.check_is_dead():
                self.player2.switch_next_living_slay()
                self.round_log.append(f"{self.player2.name} switched to {self.player2.active_slay.name}")

        self.end_round()


    def end_round(self):
        if self.round_log:
            self.log.extend(self.round_log)
            self.round_log = []
        if self.is_battle_over():
            self.turn = 'over'
        else:
            logging.info(f"------ END of ROUND {self.round_count} ------")
            self.player1.reset_actions()
            self.player2.reset_actions()
            self.turn = 'player'

    def is_battle_over(self):
        return self.player1.is_defeated() or self.player2.is_defeated()




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
            row['durability'],
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
        random_slay.durability,
        random_slay.speed,
        random_slay.moves,
        random_slay.abilities
    )

def get_random_team():
    return random.sample(slay_list, 3)
