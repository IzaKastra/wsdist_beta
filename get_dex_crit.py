#
# Created by Kastra on Asura.
# Feel free to /tell in game or send a PM on FFXIAH you have questions, comments, or suggestions.
#
# Version date: 2022 January 22
#
from numba import njit

@njit
def get_dex_crit(player_dex, enemy_agi):
    #
    # Calculate DEX-based crit using the equation from BG wiki
    # https://www.bg-wiki.com/ffxi/Critical_Hit_Rate
    #
    ddex = player_dex - enemy_agi

    if ddex <= 6:
        dex_crit = 0.00
    elif ddex <=13:
        dex_crit = 0.01
    elif ddex <= 19:
        dex_crit = 0.02
    elif ddex <= 29:
        dex_crit = 0.03
    elif ddex <=39:
        dex_crit = 0.04
    else:
        ddex_check = (ddex-35)/100
        dex_crit = ddex_check if ddex_check <= 0.15 else 0.15

    return(dex_crit)
