#
# Created by Kastra on Asura.
# Feel free to /tell in game or send a PM on FFXIAH you have questions, comments, or suggestions.
#
# Version date: 2023 February 11
#
# This code contains the function used to calculate the player's fSTR stat.
#
from numba import njit

@njit
def get_fstr(dmg, player_str, enemy_vit):
    #
    # Calculate fSTR using equation from BG wiki
    # https://www.bg-wiki.com/ffxi/FSTR
    #
    dstr = player_str - enemy_vit
    if dstr <= -22:
        fstr = (dstr+13)/4
    elif dstr <= -16:
        fstr = (dstr+12)/4
    elif dstr <= -8:
        fstr = (dstr+10)/4
    elif dstr <= -3:
        fstr = (dstr+9)/4
    elif dstr <= 0:
        fstr = (dstr+8)/4
    elif dstr <= 5:
        fstr = (dstr+7)/4
    elif dstr < 12:
        fstr = (dstr+6)/4
    elif dstr >= 12:
        fstr = (dstr+4)/4

    if fstr < -1*dmg/9.:
        fstr = -1*dmg/9.

    elif fstr > 8+(dmg/9.):
        fstr = 8+(dmg/9.)

    return(fstr)

@njit
def get_fstr2(rng_dmg, player_str, enemy_vit):
    #
    # Calculate fSTR using equation from BG wiki
    # https://www.bg-wiki.com/ffxi/FSTR
    #
    wpn_rank = rng_dmg/9.

    dstr = player_str - enemy_vit

    dstr_lower = -(7+2*wpn_rank)*2
    dstr_upper = (14+2*wpn_rank)*2

    dstr = dstr_lower if dstr < dstr_lower else dstr
    dstr = dstr_upper if dstr > dstr_upper else dstr

    if dstr <= -22:
        fstr = (dstr+13)/2
    elif dstr <= -16:
        fstr = (dstr+12)/2
    elif dstr <= -8:
        fstr = (dstr+10)/2
    elif dstr <= -3:
        fstr = (dstr+9)/2
    elif dstr <= 0:
        fstr = (dstr+8)/2
    elif dstr <= 5:
        fstr = (dstr+7)/2
    elif dstr < 12:
        fstr = (dstr+6)/2
    elif dstr >= 12:
        fstr = (dstr+4)/2

    fstr = -2.0*wpn_rank if fstr < -2.0*wpn_rank else fstr
    fstr = 2.0*(wpn_rank+8) if fstr > 2.0*(wpn_rank+8) else fstr

    return(fstr)
