import random
import logging
import pandas as pd
from contextlib import contextmanager


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MoveHandler:
    def __init__(self, moves_df):
        self.moves_df = moves_df

    @contextmanager
    def temp_stat_mod_by_ability(self, attacker, defender, move_df):
        original_hardness = attacker.hardness
        original_strength = attacker.strength

        # Appendage Moves
        if move_df['Implement'] == 'Appendage':
            if 'Blade' in attacker.abilities and original_hardness < 3:
                attacker.hardness = 3
            if 'Point' in attacker.abilities and original_hardness < 3:
                attacker.hardness = 3
        if move_df['Implement'] == 'Mouth':
            if 'Fangs' in attacker.abilities and original_hardness < 4:
                attacker.hardness = 4
            if 'Beak' in attacker.abilities and original_hardness < 3:
                attacker.hardness = 3
            if 'Power Mandibles' in attacker.abilities:
                attacker.strength += 2

        try:
            yield
        finally:
            attacker.hardness = original_hardness
            attacker.strength = original_strength


    def calc_move_damage(self, attacker, defender, move_df):
        damage = move_df['target_direct_damage']
        move_name = move_df['name']
        attacker_abilities = attacker.abilities
        defender_abilities = defender.abilities

        move_additional_cut_damage = False
        move_additional_pierce_damage = False

        logging.debug(f"--- {move_name} damage being calculated ---")

        # Appendage attacks
        if move_df['Implement'] == 'Appendage':
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
        if move_df['Implement'] == 'Mouth':
            logger.debug(f"This is a biting attack")
            if {'Fangs', 'Beak'} & set(attacker_abilities):
                move_additional_pierce_damage = True
                logger.debug(f"This is a piercing biting attack")
            else:
                move_additional_pierce_damage = False

        # Body attacks
        if move_df['Implement'] == 'Body':
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
        with self.temp_stat_mod_by_ability(attacker, defender, move_df):
            if damage > 0:
                logging.debug(f"Move will do {damage:.1f} direct damage.")  # Direct Damage Log
            if move_df['target_blunt_damage'] > 0:  # Blunt Damage
                blunt_damage = self.calc_damage_blunt(attacker, defender, move_df)
                damage += blunt_damage
                logging.debug(f"Move will do {blunt_damage:.1f} blunt damage.")
            if move_df['target_cut_damage'] > 0 and move_additional_cut_damage:  # Cut Damage
                cut_damage = self.calc_damage_cut(attacker, defender, move_df)
                damage += cut_damage
                logging.debug(f"Move will do {cut_damage:.1f} cut damage.")
            if move_df['target_pierce_damage'] > 0 and move_additional_pierce_damage:  # Pierce Damage
                pierce_damage = self.calc_damage_pierce(attacker, defender, move_df)
                damage += pierce_damage
                logging.debug(f"Move will do {pierce_damage:.1f} pierce damage.")

        return damage


    def calc_damage_blunt(self, attacker, defender, move_df, recoil=False):
        if not recoil:  # Target Damage
            base_damage = move_df['target_blunt_damage']
            factor = 1.3161 ** (attacker.strength - defender.toughness)

        else:  # Self Damage
            base_damage = move_df['self_blunt_damage']
            factor = 1.3161 ** (attacker.strength - attacker.toughness)

        logging.debug(
            f"BLUNT - Factor: {factor:.1f}, Base Damage: {base_damage:.1f}, Resulting: {base_damage * factor:.1f}")
        return base_damage * factor


    def calc_damage_cut(self, attacker, defender, move_df, recoil=False):
        if not recoil:  # Target Damage
            base_damage = move_df['target_cut_damage']
            if attacker.hardness - defender.hardness >= 0:
                factor = (2 / 3 * (1.3161 ** (attacker.strength - defender.toughness)) +
                          1 / 3 * (1.3161 ** (attacker.strength - defender.hardness)))
            else:
                factor = 0
                logging.debug("Defender could not be cut")

        else:  # Self Damage
            base_damage = move_df['self_cut_damage']
            if defender.hardness - attacker.hardness >= 0:
                factor = (2 / 3 * (1.3161 ** (attacker.strength - attacker.toughness)) +
                          1 / 3 * (1.3161 ** (attacker.strength - attacker.hardness)))
            else:
                factor = 0
                logging.debug("Attacker was not cut by recoil")

        logging.debug(f"CUT - Factor: {factor:.1f}, Base Damage: {base_damage:.1f}, Resulting: {base_damage * factor:.1f}")
        return base_damage * factor


    def calc_damage_pierce(self, attacker, defender, move_df, recoil=False):
        if not recoil:  # Target Damage
            base_damage = move_df['target_pierce_damage']
            if attacker.hardness - defender.hardness >= 2:
                factor = (1 / 3 * (1.3161 ** (attacker.strength - defender.toughness)) +
                          2 / 3 * (1.3161 ** (attacker.strength - defender.hardness)))
            else:
                factor = 0
                logging.debug("Defender could not be pierced")

        else:  # Self Damage
            base_damage = move_df['self_pierce_damage']
            if defender.hardness - attacker.hardness >= 2:
                factor = (1 / 3 * (1.3161 ** (attacker.strength - attacker.toughness)) +
                          2 / 3 * (1.3161 ** (attacker.strength - attacker.hardness)))
            else:
                factor = 0
                logging.debug("Attacker was not pierced by recoil")

        logging.debug(
            f"PIERCE - Factor: {factor:.1f}, Base Damage: {base_damage:.1f}, Resulting: {base_damage * factor:.1f}")
        return base_damage * factor


    def slay_move(self, attacker, defender, move, attacker_prefix, defender_prefix, round_log):
        move_df = self.moves_df.loc[self.moves_df['name'] == move].iloc[0]

        recoil = False
        self_damage = 0

        # Damage
        damage = self.calc_move_damage(attacker, defender, move_df)
        defender.take_damage(damage)

        # Self Damage
        if move_df['name'] in ['Tackle', 'Body Slam', 'Bludgeon']:
            recoil = True
            logging.debug(f"Attacker will take recoil damage")
            self_damage = self.calc_damage_blunt(attacker, defender, move_df, recoil)
            if 'Sharp Body' in defender.abilities:
                logging.debug(f"Defender may cut reckless attacker")
                self_damage += self.calc_damage_cut(defender, attacker, move_df)
            if 'Spiny Body' in defender.abilities:
                logging.debug(f"Defender may pierce reckless attacker")
                self_damage += self.calc_damage_pierce(defender, attacker, move_df)

            attacker.take_damage(self_damage)

        # Healing
        healing = move_df['self_healing']

        # Apply Damage, Healing, Add to Log
        if healing > 0:
            round_log.append(
                f"<span class='move'>{attacker_prefix} {attacker.name} used {move}</span>")
            if attacker.health < attacker.max_health:
                logging.debug(f"Move will do {healing} healing")
                attacker.take_damage(-healing)
                round_log.append(
                    f"<span class='damage'>{attacker_prefix} {attacker.name} gained {healing:.1f} health</span>")
            else:
                logging.debug(f"User health is at max. Healing failed")
                round_log.append(
                    f"<span class='damage'>{attacker_prefix} {attacker.name}'s healing failed</span>")
        else:
            round_log.append(
                f"<span class='move'>{attacker_prefix} {attacker.name} used {move} on "
                f"{defender_prefix} {defender.name}</span>")
            round_log.append(
                f"<span class='damage'>{defender_prefix} {defender.name} lost {damage:.1f} health</span>")
            if recoil:
                round_log.append(
                    f"<span class='damage'>{attacker_prefix} {attacker.name} hurt itself, taking {self_damage:.1f} damage</span>")
