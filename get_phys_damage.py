#
# Created by Kastra on Asura.
# Feel free to /tell in game or send a PM on FFXIAH you have questions, comments, or suggestions.
#
# Version date: 2023 March 02
#
# This code contains the function used to calculate physical damage dealt from a single weapon swing.
#
from numba import njit

@njit
def get_phys_damage(wpn_dmg, fstr_wpn, wsc, pdif, ftp, crit, crit_dmg, wsd, ws_bonus, ws_trait, n, sneak_attack_bonus=0, trick_attack_bonus=0, climactic_flourish_bonus=0,striking_flourish_bonus=0,ternary_flourish_bonus=0):
    #
    # Calculate physical damage dealt for a single attack of a weapon skill.
    # https://www.bg-wiki.com/ffxi/Weapon_Skill_Damage
    #
    phys = int(  ((wpn_dmg + fstr_wpn + wsc)*ftp*(1+wsd*(n==0))*(1+ws_bonus)*(1+ws_trait)) + sneak_attack_bonus*(n==0) + trick_attack_bonus*(n==0) + climactic_flourish_bonus*(n==0) + striking_flourish_bonus*(n==0) + ternary_flourish_bonus*(n==0)) * pdif * (1 + crit*min(crit_dmg,1.0)) # crit = True/False
    return(phys)

@njit
def get_avg_phys_damage(wpn_dmg, fstr_wpn, wsc, pdif, ftp, crit_rate, crit_dmg, wsd, ws_bonus, ws_trait, sneak_attack_bonus=0, trick_attack_bonus=0 ,climactic_flourish_bonus=0, striking_flourish_bonus=0,ternary_flourish_bonus=0):
    #
    # Calculate average physical damage dealt for a single attack of a weapon skill.
    # https://www.bg-wiki.com/ffxi/Weapon_Skill_Damage
    #
    phys = int(  ((wpn_dmg + fstr_wpn + wsc)*ftp  * (1+wsd)*(1+ws_bonus)*(1+ws_trait)) + sneak_attack_bonus + trick_attack_bonus + climactic_flourish_bonus + striking_flourish_bonus + ternary_flourish_bonus) * pdif * (1 + min(crit_rate,1.0)*min(crit_dmg,1.0))
    return(phys)
