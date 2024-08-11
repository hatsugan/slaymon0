import random
import logging
import pandas as pd


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Battle:
    def __init__(self, mode, slays_dict, traits_dict, moves_dict=None, move_handler=None, player_1_name='Player 1',
                 player_2_name='Opponent'):
        self.player_1 = Player(player_1_name)
        self.player_2 = Player(player_2_name)
        self.slays_dict = slays_dict
        self.slays_list = list(self.slays_dict.keys())
        self.traits_dict = traits_dict
        self.moves_dict = moves_dict
        self.round_count = 0
        self.round_log = []
        self.log = []
        self.move_handler = move_handler

        # if mode == 'vs Computer':
        #     pass
        # elif mode == 'Multiplayer':
        #     pass


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


class Player:
    def __init__(self, name):
        self.name = name
        self.slay_prototypes = []
        self.slay_team = []
        self.active_slay = None
        self.primordial_biomass = 0
        self.player_effects = []


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


class Slay:
    def __init__(self, battle, player, name, nickname=None):
        self.battle = battle
        self.player = player
        logger.info(f'{name} slay created for {player.name}')
        if nickname is None:
            self.nickname = name
        logger.info(f'   Nickname is: {self.nickname} ')
        self.turns_alive = 0
        self.effects = []
        slay_species_dict = battle.slays_dict[name]

        self.base_stats = {
            'biomass': slay_species_dict['biomass'],
            'biomass_cost': slay_species_dict['biomass_cost'],
            'health': slay_species_dict['species_health'],
            'STR': slay_species_dict['body_strength'],
            'HAR': 0,
            'DUR': slay_species_dict['body_durability'],
            'SPE': slay_species_dict['body_speed'],
        }
        self.current_stats = self.base_stats
        print(slay_species_dict)
        self.base_traits = slay_species_dict['species_traits']
        self.base_moves = []

        print(f'Stas before traits{self.base_stats}')

        self.compute_stats_from_traits(self.base_stats)
        self.populate_moves_from_traits()

        print(f'Stas after traits{self.base_stats}')

        self.current_traits = self.base_traits
        self.current_moves = self.base_moves

    def compute_stats_from_traits(self, stats):
        # dont forget minimums
        logger.debug(f"Computing {self.nickname}'s stats based on its traits")
        traits_dict = self.battle.traits_dict
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
        traits_dict = self.battle.traits_dict

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

        move = Move(self.battle.moves_dict[move_name])
        if is_body_move:
            move.move_long_name = f'{move_name} with body'
        else:
            move.move_long_name = f'{move_name} with {trait['name']}'
        if not trait:
            stats_when_using = get_stats_when_using(self, trait)
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

    def get_effect(self, effect):
        pass

    def new_round(self):
        pass


def get_stats_when_using(slay, trait_dict=None):
    slay_stats = slay.current_stats
    if not trait_dict:
        base_stats_when_using = {
                'STR': slay_stats['STR'],
                'HAR': slay_stats['HAR'],
                'DUR': slay_stats['DUR'],
                'SPE': slay_stats['SPE'],
            }
    else:
        base_stats_when_using = {
                'STR': slay_stats['STR'] + trait_dict['strength_modifier'],
                'HAR': slay_stats['HAR'] + trait_dict['hardness_modifier'],
                'DUR': slay_stats['DUR'] + trait_dict['durability_modifier'],
                'SPE': slay_stats['SPE'] + trait_dict['speed_modifier'],
            }
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



class Move:
    def __init__(self, move_dict):
        self.move_dict = move_dict
        self.move_long_name = ''
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



# class Slay:
#     def __init__(self, name, health, strength, hardness, durability, speed, moves, abilities):
#         self.name = name
#         self.image = self.generate_image_filename()
#
#         self.base_max_health = health
#
#         # Base stats
#         self.base_strength = strength
#         self.base_hardness = hardness
#         self.base_durability = durability
#         self.base_speed = speed
#         self.base_moves = moves
#         self.base_abilities = abilities
#
#         # Current stats
#         self.max_health = self.base_max_health
#         self.health = self.max_health
#         self.strength = self.base_strength
#         self.hardness = self.base_hardness
#         self.durability = self.base_durability
#         self.speed = self.base_speed
#         self.moves = self.base_moves
#         self.moves_dict = convert_moves_to_dict(moves)
#         self.abilities = self.base_abilities
#
#     def generate_image_filename(self):
#         return f"{self.name.lower().replace(' ', '_')}.png"
#
#
#     def take_damage(self, damage):
#         self.health -= damage
#         if self.health < 0.1:
#             self.health = 0
#         if self.health > self.max_health:
#             self.health = self.max_health
#         if damage >= 0:
#             logger.debug(f"{self.name} will take {damage:.1f} damage, health is now {self.health:.1f}")
#         else:
#             logger.debug(f"{self.name} will heal {-damage:.1f} health")
#
#     def is_fainted(self):
#         return self.health < 0.1
#
#     def reset_to_base(self):
#         self.max_health = self.base_max_health
#         self.health = self.max_health
#         self.strength = self.base_strength
#         self.hardness = self.base_hardness
#         self.durability = self.base_durability
#         self.speed = self.base_speed
#         self.moves = self.base_moves
#         logger.debug(f"{self.name} reset completely")
#
# class Player:
#     def __init__(self, name, slays):
#         self.name = name
#         self.slays = slays
#         self.active_slay = slays[0]  # Start with the first Slay in the team
#         self.chosen_action = None
#         self.chosen_move_index = None
#         self.chosen_switch_index = None
#
#     def reset_actions(self):
#         self.chosen_action = None
#         self.chosen_move_index = None
#         self.chosen_switch_index = None
#
#     def switch_slay(self):
#         if self.chosen_switch_index < len(self.slays):
#             self.active_slay = self.slays[self.chosen_switch_index]
#
#     def switch_next_living_slay(self):
#         for i, slay in enumerate(self.slays):
#             if not slay.is_fainted():
#                 self.chosen_switch_index = i
#                 logging.debug(f"{self.name} will switch to slay #{i}")
#                 self.switch_slay()
#                 return
#             logging.debug(f"{slay.name} is dead, cannot switch")
#         logging.debug(f"{self.name} has no remaining Slays to switch to")
#
#
#     def is_defeated(self):
#         return all(slay.is_fainted() for slay in self.slays)
#
# class Battle:
#     def __init__(self, player1, player2, move_handler):
#         self.player1 = player1
#         self.player2 = player2
#         self.round_count = 0
#         self.round_log = []
#         self.log = []
#         self.move_handler = move_handler
#
#     def slay_move(self, attacker, defender, move, attacker_prefix, defender_prefix):
#         self.move_handler.slay_move(attacker, defender, move, attacker_prefix, defender_prefix, self.round_log)
#
#     def player_action_move(self, player, move_index):
#         self.player1_move = player.active_slay.moves[move_index]
#         self.player1_switch = None
#         logging.debug(f"{player.name} selected move: {self.player1_move}")
#
#
#     # def opponent_action_move(self, opponent):
#     #     if opponent.active_slay.is_fainted():
#     #         self.opponent_action_switch(opponent)
#     #     else:
#     #         self.player2_move = random.choice(opponent.active_slay.moves)
#     #         self.player2_switch = None
#     #         logging.debug(f"{opponent.name} selected move: {self.player2_move}")
#     #
#     # def opponent_action_switch(self, opponent):
#     #     for i, slay in enumerate(opponent.slays):
#     #         if not slay.is_fainted():
#     #             self.player2_switch = i
#     #             self.player2_move = None
#     #             self.round_log.append(f"{opponent.name} switched to {slay.name}")
#     #             logging.debug(f"{opponent.name} switched to {slay.name}")
#     #             return
#     #     logging.debug(f"{opponent.name} has no remaining Slays to switch to")
#
#     def execute_round(self):
#         self.round_log = []
#         self.round_count += 1
#         self.log.append(f"<div class='turn-heading'>Round {self.round_count}</div>")
#         logging.info(f"------------ ROUND {self.round_count} ------------")
#
#         # Select random action for opponent
#         self.player2.chosen_action = 'Move'
#         self.player2.chosen_move_index = random.randint(0, len(self.player2.active_slay.moves)-1)
#
#
#         if self.player1.chosen_action == 'Move':
#             logging.debug(f"{self.player1.name} chose to have {self.player1.active_slay.name} use move #{self.player1.chosen_move_index} ({self.player1.active_slay.moves[self.player1.chosen_move_index]})")
#         elif self.player1.chosen_action == 'Switch':
#             logging.debug(f"{self.player1.name} chose to switch {self.player1.active_slay.name} to {self.player1.slays[self.player1.chosen_switch_index].name}")
#
#         if self.player2.chosen_action == 'Move':
#             logging.debug(f"{self.player2.name} chose to have {self.player2.active_slay.name} use move #{self.player2.chosen_move_index} ({self.player2.active_slay.moves[self.player2.chosen_move_index]})")
#         elif self.player2.chosen_action == 'Switch':
#             logging.debug(f"{self.player2.name} chose to switch {self.player2.active_slay.name} to {self.player2.slays[self.player2.chosen_switch_index].name}")
#
#
#         # Switch Phase
#         if self.player1.chosen_action == 'Switch':  # Switch Player 1
#             self.player1.switch_slay()
#             logging.debug(f"{self.player1.name} switched to {self.player1.active_slay.name}")
#
#         if self.player2.chosen_action == 'Switch':  # Switch Player 1
#             self.player2.switch_slay()
#             logging.debug(f"{self.player2.name} switched to {self.player2.active_slay.name}")
#
#         # Combat Phase
#         # turn_order list - 1:[Attacker, Defender], 2:[Attacker, Defender]
#         if self.player1.active_slay.speed >= self.player2.active_slay.speed:
#             self.log.append(
#                 f"{self.player1.name}'s {self.player1.active_slay.name} is faster than {self.player2.name}'s {self.player2.active_slay.name}")
#             turn_order = [[self.player1, self.player2],[self.player2, self.player1]]
#         else:
#             self.log.append(
#                 f"{self.player2.name}'s {self.player2.active_slay.name} is faster than {self.player1.name}'s {self.player1.active_slay.name}")
#             turn_order = [[self.player2, self.player1], [self.player1, self.player2]]
#
#         for attacker_defender in turn_order:
#             attacker, defender = attacker_defender
#             if attacker.chosen_action == 'Move':  # Catches if switching
#                 logging.debug(
#                     f"{attacker.name} selected index: {attacker.chosen_move_index} from move list len {len(attacker.active_slay.moves)}, slay is {attacker.active_slay.name}")
#
#                 chosen_move = attacker.active_slay.moves[attacker.chosen_move_index]
#                 self.slay_move(attacker.active_slay, defender.active_slay, chosen_move, f"{attacker.name}'s",
#                                f"{defender.name}'s")
#
#                 # Handle slay death
#                 if attacker.active_slay.is_fainted() and defender.active_slay.is_fainted():
#                     self.round_log.append(
#                         f"Both slays died! Yeesh!")
#                     break
#                 elif attacker.active_slay.is_fainted():
#                     self.round_log.append(f"{attacker.name}'s {attacker.active_slay.name} died!")
#                     break
#                 elif defender.active_slay.is_fainted():
#                     self.round_log.append(f"{defender.name}'s {defender.active_slay.name} died!")
#                     break
#
#         # Check win condition, otherwise switch
#         if not self.player1.is_defeated() or not self.player2.is_defeated():
#             if self.player1.active_slay.is_fainted():
#                 self.player1.switch_next_living_slay()
#                 self.round_log.append(f"{self.player1.name} switched to {self.player1.active_slay.name}")
#             if self.player2.active_slay.is_fainted():
#                 self.player2.switch_next_living_slay()
#                 self.round_log.append(f"{self.player2.name} switched to {self.player2.active_slay.name}")
#
#         self.end_round()
#
#
#     def end_round(self):
#         if self.round_log:
#             self.log.extend(self.round_log)
#             self.round_log = []
#         if self.is_battle_over():
#             self.turn = 'over'
#         else:
#             logging.info(f"------ END of ROUND {self.round_count} ------")
#             self.player1.reset_actions()
#             self.player2.reset_actions()
#             self.turn = 'player'
#
#     def is_battle_over(self):
#         return self.player1.is_defeated() or self.player2.is_defeated()

