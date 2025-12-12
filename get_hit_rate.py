'''
File containing calculations for physical hit rate from the accuracy stat.
    
Author: Kastra (Asura server)
'''
from numba import njit

@njit
def get_hit_rate(player_accuracy, enemy_evasion, hit_rate_cap):
    #
    # Calculate hit rates based on player and enemy stats.
    # https://www.bg-wiki.com/ffxi/Hit_Rate
    # The first main- and sub-hits gain +100 accuracy (https://www.bg-wiki.com/ffxi/Category:Weapon_Skills), which was added on the function call in the main code.
    #        
    hit_rate = (75 + 0.5*(player_accuracy - enemy_evasion))/100

    hit_rate_floor = 0.2 # Melee WSs have a 20% hit rate floor.
    # I'm also using a floor of 20% for ranged WS to allow the code to recover from starting at 0% hit rate.
    # Without this lower limit, the code will not escape from 0% hit rate and never find the best set (or any set since no swaps change the damage when severely under the accuracy requirement).

    hit_rate = hit_rate_cap if hit_rate > hit_rate_cap else hit_rate_floor if hit_rate < hit_rate_floor else hit_rate

    return(hit_rate)
