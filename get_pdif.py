#
# Created by Kastra on Asura.
# Feel free to /tell in game or send a PM on FFXIAH you have questions, comments, or suggestions.
#
# Version date: 2022 January 22
#
# Calculate PDIF using equations from BG Wiki
#
import random
from numba import njit

@njit
def get_pdif_melee(player_attack, wpn_type_skill, pdl_trait, pdl_gear=0, enemy_defense=1300, crit_rate=0): # Values defined in this line use the Python format for: "Use these values as defaults if the user doesn't provide them"
    #
    # Calculate PDIF for physical melee hits using the process described on BG wiki
    # https://www.bg-wiki.com/ffxi/PDIF
    #
    if wpn_type_skill=='Katana' or wpn_type_skill=="Dagger" or wpn_type_skill=="Sword" or wpn_type_skill=="Axe" or wpn_type_skill=="Club":
        pdif_base_cap = 3.25
    elif wpn_type_skill=="Great Katana" or wpn_type_skill=="Hand-to-Hand":
        pdif_base_cap = 3.5
    elif wpn_type_skill=="Great Sword" or wpn_type_skill=="Staff" or wpn_type_skill=="Great Axe" or wpn_type_skill=="Polearm":
        pdif_base_cap = 3.75
    elif wpn_type_skill=="Scythe":
        pdif_base_cap = 4.0



    crit = random.uniform(0,1) < crit_rate  # True or False  (1 or 0)

    ratio = player_attack / enemy_defense

    cratio = ratio # Ignore Level Differences for now

    wratio = cratio+1 if crit else cratio # Add 1.0 if crit

    # qRatio stuff taken from BG
    if wratio >= 0.0 and wratio < 0.5:
        upper_qlim = wratio + 0.5
    elif wratio >= 0.5 and wratio < 0.7:
        upper_qlim = 1
    elif wratio >= 0.7 and wratio < 1.2:
        upper_qlim = wratio + 0.3
    elif wratio >= 1.2 and wratio < 1.5:
        upper_qlim = 1.25*wratio
    elif wratio >= 1.5:
        upper_qlim = wratio + 0.375

    if wratio >= 0.0 and wratio < 0.38:
        lower_qlim = 0
    elif wratio >= 0.38 and wratio < 1.25:
        lower_qlim = (1176./1024.)*wratio - (448./1024.)
    elif wratio >= 1.25 and wratio < 1.51:
        lower_qlim = 1
    elif wratio >= 1.51 and wratio < 2.44:
        lower_qlim = (1176./1024.)*wratio - (755./1024.)
    elif wratio >= 2.44:
        lower_qlim = wratio - 0.375

    qratio = random.uniform(lower_qlim, upper_qlim)

    # Define your capped PDIF value
    pdif_cap = (pdif_base_cap+pdl_trait)*(1+pdl_gear)

    # Limit PDIF to between 0 and cap.
    if qratio <= 0:
        pdif = 0
    elif qratio >= pdif_cap:
        pdif = pdif_cap
    else:
        pdif = qratio

    # Add 1.0 to PDIF value if crit.
    if crit:
        pdif += 1.0

    # Random multiplier to final PDIF value
    pdif *= random.uniform(1.00, 1.05)

    return(pdif, crit)


@njit
def get_avg_pdif_melee(player_attack, wpn_type_skill, pdl_trait, pdl_gear=0, enemy_defense=1300, crit_rate=0): # Values defined in this line use the Python format for: "Use these values as defaults if the user doesn't provide them"
    #
    # Calculate PDIF for physical melee hits using the process described on BG wiki, but assuming the average random value is drawn.
    # https://www.bg-wiki.com/ffxi/PDIF
    #
    if wpn_type_skill=='Katana' or wpn_type_skill=="Dagger" or wpn_type_skill=="Sword" or wpn_type_skill=="Axe" or wpn_type_skill=="Club": # TODO: "if_wpn_skill in [a,b,c,]"
        pdif_base_cap = 3.25
    elif wpn_type_skill=="Great Katana" or wpn_type_skill=="Hand-to-Hand":
        pdif_base_cap = 3.5
    elif wpn_type_skill=="Great Sword" or wpn_type_skill=="Staff" or wpn_type_skill=="Great Axe" or wpn_type_skill=="Polearm":
        pdif_base_cap = 3.75
    elif wpn_type_skill=="Scythe":
        pdif_base_cap = 4.0

    ratio = player_attack / enemy_defense

    cratio = ratio # Ignore Level Differences

    crit_rate = 1.0 if crit_rate > 1.0 else crit_rate # Limit crit rate to 100%
    wratio = cratio + 1.0*crit_rate

    # qRatio stuff taken from BG
    if wratio >= 0.0 and wratio < 0.5:
        upper_qlim = wratio + 0.5
    elif wratio >= 0.5 and wratio < 0.7:
        upper_qlim = 1
    elif wratio >= 0.7 and wratio < 1.2:
        upper_qlim = wratio + 0.3
    elif wratio >= 1.2 and wratio < 1.5:
        upper_qlim = 1.25*wratio
    elif wratio >= 1.5:
        upper_qlim = wratio + 0.375

    if wratio >= 0.0 and wratio < 0.38:
        lower_qlim = 0
    elif wratio >= 0.38 and wratio < 1.25:
        lower_qlim = (1176./1024.)*wratio - (448./1024.)
    elif wratio >= 1.25 and wratio < 1.51:
        lower_qlim = 1
    elif wratio >= 1.51 and wratio < 2.44:
        lower_qlim = (1176./1024.)*wratio - (755./1024.)
    elif wratio >= 2.44:
        lower_qlim = wratio - 0.375

    qratio = 0.5*(upper_qlim+lower_qlim)

    # Define your capped PDIF value
    pdif_cap = (pdif_base_cap+pdl_trait)*(1+pdl_gear)

    # Limit PDIF to between 0 and cap.
    if qratio <= 0:
        pdif = 0
    elif qratio >= pdif_cap:
        pdif = pdif_cap
    else:
        pdif = qratio

    # Add 1.0 to PDIF value if crit.
    pdif += 1.0*crit_rate
    # Average multiplier to final PDIF value
    pdif *= 1.025

    return(pdif)



@njit
def get_pdif_ranged(player_ranged_attack, wpn_type_skill, pdl_trait, pdl_gear, enemy_defense=1300, crit_rate=0):

    pdif_base_cap = 3.5 if wpn_type_skill=="Marksmanship" else 3.25

    crit = random.uniform(0,1) < crit_rate

    ratio = player_ranged_attack / enemy_defense

    cratio = ratio # Ignore Level Differences for now

    wratio = cratio # There is no wratio term for ranged.

    if wratio >= 0.0 and wratio < 0.9:
        upper_qlim = wratio * (10./9.)
    elif wratio >= 0.9 and wratio < 1.1:
        upper_qlim = 1
    elif wratio >= 1.1:
        upper_qlim = wratio

    if wratio >= 0.0 and wratio < 0.9:
        lower_qlim = wratio
    elif wratio >= 0.9 and wratio < 1.1:
        lower_qlim = 1
    elif wratio >= 1.1:
        lower_qlim = wratio*(20./19) - (3./19)

    qratio = random.uniform(lower_qlim, upper_qlim)

    pdif_cap = (pdif_base_cap+pdl_trait)*(1+pdl_gear)
    if qratio <= 0:
        pdif = 0
    elif qratio >= pdif_cap:
        pdif = pdif_cap
    else:
        pdif = qratio

    if crit:
        pdif *= 1.25 # Dead Aim (crit damage) is applied in get_phys_dmg. This is all multiplied together, so it doesn't matter where it gets applied

    return(pdif, crit)

@njit
def get_avg_pdif_ranged(player_ranged_attack, wpn_type_skill, pdl_trait, pdl_gear, enemy_defense=1300, crit_rate=0):

    pdif_base_cap = 3.5 if wpn_type_skill=="Marksmanship" else 3.25

    ratio = player_ranged_attack / enemy_defense

    cratio = ratio # Ignore Level Differences for now

    wratio = cratio # There is no wratio term for ranged.

    if wratio >= 0.0 and wratio < 0.9:
        upper_qlim = wratio * (10./9.)
    elif wratio >= 0.9 and wratio < 1.1:
        upper_qlim = 1
    elif wratio >= 1.1:
        upper_qlim = wratio

    if wratio >= 0.0 and wratio < 0.9:
        lower_qlim = wratio
    elif wratio >= 0.9 and wratio < 1.1:
        lower_qlim = 1
    elif wratio >= 1.1:
        lower_qlim = wratio*(20./19) - (3./19)

    qratio = 0.5*(lower_qlim+upper_qlim)

    pdif_cap = (pdif_base_cap+pdl_trait)*(1+pdl_gear)
    if qratio <= 0:
        pdif = 0
    elif qratio >= pdif_cap:
        pdif = pdif_cap
    else:
        pdif = qratio

    crit_rate = 1.0 if crit_rate > 1.0 else crit_rate # Limit crit rate to 100% so we don't over-multiply
    pdif *= (1+0.25*crit_rate)

    return(pdif)
