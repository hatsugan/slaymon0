import random
import logging
import pandas as pd


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# BATTLE CLASS ---------------------------------------------------------------------------------------------------------
class Battle:
    def __init__(self, mode, slays_dict, traits_dict, moves_dict=None, move_handler=None, player1_name='Player 1',
                 player2_name='Opponent'):
        self.player1 = Player(player1_name)
        self.player2 = Player(player2_name)

        self.battle_slays_dict = slays_dict
        self.slays_list = list(self.battle_slays_dict.keys())
        self.battle_traits_dict = traits_dict
        self.battle_moves_dict = moves_dict
        self.move_handler = move_handler

        self.log = []
        self.game_over = False

        self.round_counter = 1
        self.round_log = []
        self.turn_order = []  # To store the order of actions in the round

        # if mode == 'vs Computer':
        #     pass
        # elif mode == 'Multiplayer':
        #     pass

    # Player Handling
    def get_random_team_name_list(self, n):
        return random.sample(self.slays_list, n)

    def give_player_random_team(self, player):
        player.slay_team = [Slay(
            self,
            player,
            name,
        ) for name in self.get_random_team_name_list(4)]

    def give_player_team_from_list(self, player, list_slay_names):
        player.slay_team = [Slay(
            self,
            player,
            name,
        ) for name in list_slay_names]

    def trigger_event(self, event_type, user=None, target=None, attacker=None, defender=None, player=None):
        pass

    # Round Handling
    def execute_round(self):
        # Initialize the round to determine the order of actions
        self.round_phase_action_select()

        # Execute each move in the determined order
        for attacker, move, defender in self.turn_order:
            if not attacker.check_is_dead():
                self.execute_move(attacker, move, defender)

                # After each move, check if the defender is still able to act
                if defender.check_is_dead():
                    self.round_log.append(f"{defender.p_name} fuckin died!")
                    break  # Stop further actions if a Slay faints

        # End the round, handle any post-round logic, check for fainted Slays
        self.end_round()

    def select_move(self, player, move_index):
        player.chosen_move_index = move_index
        move = player.active_slay.current_moves[move_index]
        self.log.append(f"{player.name} selected {move.move_long_name}.")

    def log_round_header(self, first_round=False):
        if first_round:
            round_counter = 1
        else:
            round_counter = self.round_counter
        self.log.append(f"<div class='turn-heading'>Round {round_counter}</div>")
        logging.info(f"------------ ROUND {round_counter} ------------")

    def round_phase_action_select(self):
        # Clear previous round's log

        # Get the selected moves and their speeds
        player1_move = self.player1.active_slay.current_moves[self.player1.chosen_move_index]
        player2_move = self.player2.active_slay.current_moves[self.player2.chosen_move_index]

        # Determine turn order based on move speed
        # [step 1, step 2]: [(user, move, target), (user, move, target)]
        if player1_move.stats_when_using['SPE'] >= player2_move.stats_when_using['SPE']:
            self.round_log.append(f"{self.player1.active_slay.p_name}'s move is faster than "
                                  f"{self.player2.active_slay.p_name}")
            self.turn_order = [(self.player1.active_slay, player1_move, self.player2.active_slay), (self.player2.active_slay, player2_move, self.player1.active_slay,)]
        else:
            self.round_log.append(f"{self.player1.active_slay.p_name}'s move is faster than "
                                  f"{self.player2.active_slay.p_name}")
            self.turn_order = [(self.player2.active_slay, player2_move, self.player1.active_slay,), (self.player1.active_slay, player1_move, self.player2.active_slay)]

        logging.info(f"Turn order set: {[(p.name, m.move_long_name) for p, m, _ in self.turn_order]}")

    def execute_move(self, user, move, target):
        # Handle the move execution
        self.round_log.append(f"{user.p_name} used {move.move_long_name} on {target.p_name}.")
        logging.debug(f"{user.p_name} uses {move.move_long_name} on {target.p_name}")
        damage = move.move_properties['POWER']
        target.take_damage(damage)
        self.round_log.append(f"{target.p_name} health is now {target.current_stats['health']}.")

        # Trigger an event (optional, based on your game design)
        self.trigger_event('DamageTakenEvent', target, damage)

        # Apply any move-specific effects (status, buffs, debuffs, etc.)
        # For example:
        # if move.has_status_effect():
        #     target.apply_status_effect(move.status_effect)

    def execute_switch(self, player, new_slay):
        pass
        # player.active_slay = new_slay
        # logging.debug(f"{player.name} switched to {new_slay.nickname}")
        # self.trigger_event('SwitchSelectedEvent', player, new_slay)

    def end_round(self):
        # Check if any Slays have fainted and handle the aftermath
        # self.check_for_fainted_slays()

        # Check if the game is over and determine the winner
        self.check_game_over()

        if self.game_over:
            self.log.append(f"<div class='turn-heading'>Simulation Ended</div>")
        else:
            logging.info(f"------ END of ROUND {self.round_counter} ------")
            self.round_counter += 1
            self.log_round_header()

        if self.round_log:
            self.log.extend(self.round_log)
            self.round_log = []

    def check_game_over(self):
        # Initially assume both players' teams are dead
        player1_team_dead = True
        player2_team_dead = True

        # Check if any "slay" in player 1's team is alive
        for slay in self.player1.slay_team:
            if not slay.check_is_dead():
                player1_team_dead = False
                break  # No need to check further if at least one is alive

        # Check if any "slay" in player 2's team is alive
        for slay in self.player2.slay_team:
            if not slay.check_is_dead():
                player2_team_dead = False
                break  # No need to check further if at least one is alive

        if player1_team_dead or player2_team_dead:
            self.game_over = True
            if player1_team_dead and player2_team_dead:
                self.round_log.append(f"<div class='lose'>Draw! Both Players are Defeated</div>")
                logger.debug(f"Draw! Both Players Lose")
            elif player1_team_dead:
                self.round_log.append(f"<div class='win'>{self.player2.name} is Victorious!</div>")
                logger.debug(f"{self.player1.name} Lost!")
            elif player2_team_dead:
                self.round_log.append(f"<div class='win'>{self.player1.name} is Victorious!</div>")
                logger.debug(f"{self.player2.name} Lost!")



# PLAYER CLASS ---------------------------------------------------------------------------------------------------------
class Player:
    def __init__(self, name):
        self.name = name
        self.slay_prototypes = []
        self.slay_team = []
        self.active_slay = None

        self.primordial_biomass = 0
        self.player_effects = []

        self.chosen_move_index = 0


    def reset_prototypes(self):
        self.slay_prototypes = []

    def reset_except_proto(self):
        self.slays = []
        self.active_slay = None
        self.primordial_biomass = 0

    def birth_slay(self):
        pass

    def resorb_slay(self, slay):
        pass

    def choose_random_move(self):
        self.chosen_move_index = random.randint(0, len(self.active_slay.current_moves) - 1)


# SLAY CLASS -----------------------------------------------------------------------------------------------------------
class Slay:
    def __init__(self, battle, player, name, nickname=None):
        self.battle = battle
        self.player = player
        self.name = name
        self.is_dead = False
        logger.info(f'{name} slay created for {player.name}')
        if nickname is None:
            self.nickname = f"{name} {len(self.player.slay_team)}"
        logger.info(f'   Nickname is: {self.nickname} ')
        self.p_name = f"{player.name}'s {self.nickname}"
        self.turns_alive = 0
        self.effects = []
        slay_species_dict = battle.battle_slays_dict[name]

        self.base_stats = {
            'biomass': slay_species_dict['biomass'],
            'biomass_cost': slay_species_dict['biomass_cost'],
            'health': slay_species_dict['species_health'],
            'STR': slay_species_dict['body_strength'],
            'HAR': 0,
            'DUR': slay_species_dict['body_durability'],
            'SPE': slay_species_dict['body_speed'],
        }
        self.current_stats = self.base_stats.copy()
        print(slay_species_dict)
        self.base_traits = slay_species_dict['species_traits']
        self.base_moves = []

        self.compute_stats_from_traits(self.base_stats)
        self.populate_moves_from_traits()

        self.current_traits = self.base_traits.copy()
        self.current_moves = self.base_moves.copy()

    def compute_stats_from_traits(self, stats):
        # dont forget minimums
        logger.debug(f"Computing {self.nickname}'s stats based on its traits")
        traits_dict = self.battle.battle_traits_dict
        for trait_name in self.base_traits:
            trait = traits_dict[trait_name]
            trait_tags = trait['trait_tags']
            if 'Body Modifier' in trait_tags:
                stats['STR'] += trait['strength_modifier']
                stats['HAR'] += trait['hardness_modifier']
                stats['DUR'] += trait['durability_modifier']
                stats['SPE'] += trait['speed_modifier']

    def populate_moves_from_traits(self):
        logger.debug(f"Populating {self.nickname}'s moves")
        traits_dict = self.battle.battle_traits_dict

        # Body Moves
        # Quality Augment from Trait
        if self.current_stats['biomass'] >= 10:
            trait_quality_augment = get_trait_quality_augment()
            augmenting_trait_tags = []
            has_body_augmenting_trait = False

            for trait_name in self.base_traits:
                trait = traits_dict[trait_name]
                trait_tags = trait['trait_tags']
                if ('Body Modifier' in trait_tags) and ({'Sharp Edge', 'Sharp Point'} & set(trait_tags)):
                    augmenting_trait_tags.append(trait_tags)
                    has_body_augmenting_trait = True

            if has_body_augmenting_trait:
                trait_quality_augment = get_trait_quality_augment(augmenting_trait_tags)
                logger.debug(f'      Trait quality augmentation: {trait_quality_augment}')

            logger.debug(f'         Adding Tackle')
            move = self.pre_add_move('Tackle', is_body_move=True)
            self.add_move(move, trait_quality_augment)

            if self.current_stats['biomass'] >= 20 and self.current_stats['STR'] >= 3 and self.current_stats['SPE'] >= 20:
                logger.debug(f'         Slay is strong, fast enough, and heavy enough, adding Body Slam')
                move = self.pre_add_move('Body Slam', trait, is_body_move=True)
                self.add_move(move, trait_quality_augment)

        if not self.base_traits:
            logger.warning(f"{self.nickname} has no traits. Please populate Slaipedia")
            return

        # Other Trait Moves
        logger.debug(f"   Populating {self.nickname}'s moves from its traits")
        logger.debug(f'   Traits are: {self.base_traits}')

        for trait_name in self.base_traits:
            trait = traits_dict[trait_name]
            trait_tags = trait['trait_tags']
            logger.debug(f'      Trait {trait_name} has tags: {trait_tags}')

            # Quality Augment from Trait
            trait_quality_augment = get_trait_quality_augment(trait_tags)
            logger.debug(f'      Trait quality augmentation: {trait_quality_augment}')

            # Appendage Moves
            if 'Appendage' in trait_tags:
                logger.debug(f'      This trait is an appendage {trait_name}')
                logger.debug(f'         Adding Strike, Jab')
                move = self.pre_add_move('Strike', trait)
                self.add_move(move, trait_quality_augment)

                move = self.pre_add_move('Jab', trait)
                self.add_move(move, trait_quality_augment)

                if self.current_stats['STR'] >= 3:
                    logger.debug(f'         Slay is strong. Adding Slash, Stab')
                    move = self.pre_add_move('Slash', trait)
                    self.add_move(move, trait_quality_augment)

                    move = self.pre_add_move('Stab', trait)
                    self.add_move(move, trait_quality_augment)

                if self.current_stats['STR'] >= 6:
                    logger.debug(f'         Slay is extremely strong. Adding Bludgeon')
                    move = self.pre_add_move('Bludgeon', trait)
                    self.add_move(move, trait_quality_augment)

    def pre_add_move(self, move_name, trait=None, is_body_move=False):

        move = Move(self.battle.battle_moves_dict[move_name])
        if is_body_move:
            move.move_long_name = f'{move_name} with body'
        else:
            move.move_long_name = f'{move_name} with {trait['name']}'
        if not trait:
            move.parent_trait = 'Body'
        else:
            move.parent_trait = trait['name']
        stats_when_using = get_stats_when_using(self, is_body_move, trait)
        move.stats_when_using = stats_when_using
        return move

    def add_move(self, move, trait_quality_augment=None):
        if trait_quality_augment:
            move.move_properties['BLUNT'] += trait_quality_augment['BLUNT']
            move.move_properties['CUT'] += trait_quality_augment['CUT']
            move.move_properties['PIERCE'] += trait_quality_augment['PIERCE']
        self.base_moves.append(move)

    def determine_move_results(self, move, target):
        pass

    def take_damage(self, damage, quality='Direct'):
        logger.debug(f"base is {self.base_stats['health']}")
        if damage >= 0.1:
            self.battle.round_log.append(f"{self.p_name} took {damage} {quality.lower()} damage.")
        elif damage <= -0.1:
            self.battle.round_log.append(f"{self.p_name} gained {damage} health.")
        else:
            damage = 0
            self.battle.round_log.append(f"{self.p_name} took no {quality.lower()} damage.")
        self.current_stats['health'] -= damage
        logger.debug(f"{self.p_name} takes {damage} {quality.lower()} damage.")
        logger.debug(f"base is {self.base_stats['health']}")
        logger.debug(f"current is {self.current_stats['health']}")

    def get_effect(self, effect):
        pass

    def new_round(self):
        pass

    def check_is_dead(self):
        if self.current_stats['health'] <= 0:
            self.is_dead = True
            return True
        else:
            self.is_dead = False
            return False


# MOVE CLASS -----------------------------------------------------------------------------------------------------------
class Move:
    def __init__(self, move_dict):
        self.move_dict = move_dict
        self.move_long_name = ''
        self.parent_trait = ''
        self.stats_when_using = {
            'STR': 0,
            'HAR': 0,
            'DUR': 0,
            'SPE': 0,
        }
        self.move_properties = {
            'POWER': move_dict['power'],
            'RECOIL': move_dict['recoil'],
            'BLUNT': move_dict['blunt_quality'],
            'CUT': move_dict['cut_quality'],
            'PIERCE': move_dict['pierce_quality']
        }
        self.self_effects = []
        self.target_effects = []


# Helper Functions
def get_stats_when_using(slay, is_body_move, trait_dict=None):
    slay_stats = slay.current_stats
    if trait_dict:
        if is_body_move:  # Body move with body modifier trait
            base_stats_when_using = {
                    'STR': slay_stats['STR'] + trait_dict['strength_modifier'],
                    'HAR': slay_stats['HAR'] + trait_dict['hardness_modifier'],
                    'DUR': slay_stats['DUR'] + trait_dict['durability_modifier'],
                    'SPE': slay_stats['SPE'] + trait_dict['speed_modifier'],
                }
        else:  # Non Body move with trait
            base_stats_when_using = {
                    'STR': slay_stats['STR'] + trait_dict['strength_modifier'],  # STR always comes from current slay STR
                    'HAR': trait_dict['hardness_modifier'],
                    'DUR': trait_dict['durability_modifier'],
                    'SPE': slay_stats['SPE'] + trait_dict['speed_modifier'],  # SPE always comes from current slay SPE
                }

    else: # Move without trait
        base_stats_when_using = {
                'STR': slay_stats['STR'],
                'HAR': slay_stats['HAR'],
                'DUR': slay_stats['DUR'],
                'SPE': slay_stats['SPE'],
            }

    # Ensure good data
    if base_stats_when_using['STR'] < 0:
        base_stats_when_using['STR'] = 0
    if base_stats_when_using['HAR'] < 0:
        base_stats_when_using['HAR'] = 0
    if base_stats_when_using['DUR'] < 0:
        base_stats_when_using['DUR'] = 0
    if base_stats_when_using['STR'] < 1:
        base_stats_when_using['SPE'] = 1

    return base_stats_when_using


def get_trait_quality_augment(trait_tags=None):
    # Quality Skew from Trait
    trait_quality_augment = {
        'BLUNT': 0,
        'CUT': 0,
        'PIERCE': 0
    }
    if trait_tags:
        if 'Sharp Edge' in trait_tags:
            trait_quality_augment['BLUNT'] += 0
            trait_quality_augment['CUT'] += 1
            trait_quality_augment['PIERCE'] += 0

        if 'Sharp Point' in trait_tags:
            trait_quality_augment['BLUNT'] += 0
            trait_quality_augment['CUT'] += 0
            trait_quality_augment['PIERCE'] += 1

    return trait_quality_augment

