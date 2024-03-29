#
# Created by Kastra on Asura.
# Feel free to /tell in game or send a PM on FFXIAH you have questions, comments, or suggestions.
#
import numpy as np
from get_dex_crit import *

def weaponskill_info(ws_name, tp, player, enemy, wsc_bonus, dual_wield):
    #
    # Setup weaponskill statistics (TP scaling, # of hits, ftp replication, WSC, etc)
    #
    # wsc_bonus is the WSC bonus from Utu Grip and Crepuscular Knife. The format is wsc_bonus = [["DEX", 0.10],["CHR",0.03],] etc
    #
    #
    player_str = player.stats["STR"]
    player_dex = player.stats["DEX"]
    player_vit = player.stats["VIT"]
    player_agi = player.stats["AGI"]
    player_int = player.stats["INT"]
    player_mnd = player.stats["MND"]
    player_chr = player.stats["CHR"]

    player_accuracy1 = player.stats["Accuracy1"]
    player_accuracy2 = player.stats["Accuracy2"]
    player_rangedaccuracy = player.stats["Ranged Accuracy"]

    player_attack1 = player.stats["Attack1"]
    player_attack2 = player.stats["Attack2"]
    player_rangedattack = player.stats["Ranged Attack"]

    enemy_def = enemy.stats["Defense"]
    enemy_vit = enemy.stats["VIT"]
    enemy_agi = enemy.stats["AGI"]
    enemy_int = enemy.stats["INT"]
    enemy_mnd = enemy.stats["MND"]
    enemy_chr = enemy.stats["MND"]


    crit_rate = 0 # Start from zero crit rate. We add crit rate if the weapon skill is a crit weapon skill and/or if Shining One is equipped.

    # Set default values. We will modify these for special cases.
    crit_ws = False # Used to ensure that we do not double-count dDEX on crit WSs when using Shining One.
    hybrid = False
    magical = False
    dSTAT = 0 # Magical WS dINT or dMND
    element = "None" # Magical/Hybrid WS element
    ftp_hybrid = 0 # Hybrid WSs have unique FTP rules.

    base_tp = [1000,2000,3000] # TP anchor points used for interpolation.


    if player.gearset["main"]["Name"] == "Naegling": # Naegling provides +1% attack per active buff. For now I assume this is +13% (protect, shell, haste, songx4, rollx2, signet). TODO: update later by counting buffs from the GUI

        ws_atk_modifier = 0.13
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        if player_attack2 > 0:
            player_attack2 -= player.stats.get("Food Attack",0)
            player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
            player_attack2 += player.stats.get("Food Attack",0)

    elif player.gearset["main"]["Name"] == "Nandaka": # Nandaka lowers enemy defense by 1% per debuff present on weapon skills. I assume this is only -3% (dia, slow, paralyze, )
        enemy_def *= (1 - 0.03) # I treat defense down debuffs as multiplicatively stacking. This alone gets around the potential for more than 100% defense reduction. A normal Idris Frailty is -40%. If we added Blade: Kamu, this would be -110% with additive stacking. Multiplicatively, it is -85%.



    # Sword Weapon skills
    if ws_name == "Fast Blade":
        base_ftp = [1.0, 1.5, 2.0] # Base TP bonuses for 1k, 2k, 3k TP
        ftp      = np.interp(tp, base_tp, base_ftp) # Effective TP at WS use
        ftp_rep  = False
        wsc      = 0.4*(player_str + player_dex) # Stat modifiers, including things like Utu Grip if applicable.
        nhits    = 2
        sc = ["Scission"]
    elif ws_name == "Burning Blade":
        base_ftp = [1.0, 2.09765625, 3.3984375]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_int)
        nhits = 1
        magical = True
        element = "Fire"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Liquefaction"]
    elif ws_name == "Red Lotus Blade":
        base_ftp = [1.0, 2.3828125, 3.75]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_int)
        nhits = 1
        magical = True
        element = "Fire"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Liquefaction","Detonation"]
    elif ws_name == "Shining Blade":
        base_ftp = [1.125, 2.22265625, 3.5234375] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_mnd)
        nhits = 1
        magical = True
        element = "Light"
        dSTAT = 0
        sc = ["Scission"]
    elif ws_name == "Seraph Blade":
        base_ftp = [1.125, 2.625, 4.125] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_mnd)
        nhits = 1
        magical = True
        element = "Light"
        dSTAT = 0
        sc = ["Scission"]
    elif ws_name == "Circle Blade":
        ftp  = 1.0
        ftp_rep = False
        wsc = 1.0*player_str
        nhits = 1
        sc = ["Reverberation","Impaction"]
    elif ws_name == "Swift Blade":
        acc_boost = [0, 20, 40] # I made these numbers up since I could not find published testing results.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_accuracy1 += acc_bonus
        player_accuracy2 += acc_bonus
        ftp  = 1.5
        ftp_rep = True
        wsc = 0.5*(player_str + player_mnd)
        nhits = 3
        sc = ["Gravitation"]
    elif ws_name == "Savage Blade":
        base_ftp = [4.0, 10.25, 13.75] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.5*(player_str + player_mnd)
        nhits = 2
        sc = ["Fragmentation","Scission"]
    elif ws_name == "Sanguine Blade":
        ftp  = 2.75
        ftp_rep = False
        wsc = 0.5*player_mnd + 0.3*player_str
        nhits = 1
        magical = True
        element = "Dark"
        dSTAT = (player_int - enemy_int)*2
        sc = ["None"]
    elif ws_name == "Requiescat":
        # Certain weapon skills increase/decrease attack by some percentage. We need to recalculate the player's attack when this happens.
        # Here, we simply remove attack from food, multiply by the ratio of the new/old attack% buff, and then re-add attack from food. 
        atk_boost = [-0.2, -0.1, 0.0] # Requiescat has an attack penalty
        ws_atk_modifier = np.interp(tp, base_tp, atk_boost)

        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        if player_attack2 > 0:
            player_attack2 -= player.stats.get("Food Attack",0)
            player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
            player_attack2 += player.stats.get("Food Attack",0)

        ftp = 1.0
        ftp_rep = True
        wsc = 0.85*player_mnd
        nhits = 5
        sc = ["Aeonic","Gravitation","Scission"]
    elif ws_name == "Knights of Round":
        ftp  = 5.0
        ftp_rep = False
        wsc = 0.4*(player_mnd + player_str)
        nhits = 1
        sc = ["Light","Fusion"]
    elif ws_name == "Chant du Cygne":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.15, 0.25, 0.40]
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += get_dex_crit(player_dex, enemy_agi)
        ftp = 1.6328125
        ftp_rep = True
        wsc = 0.8*player_dex
        nhits = 3
        sc = ["Light","Distortion"]
    elif ws_name == "Death Blossom":
        ftp  = 4.0
        ftp_rep = False
        wsc = 0.5*player_mnd + 0.3*player_str
        nhits = 3
        sc = ["Fragmentation","Distortion"]
    elif ws_name == "Expiacion":
        base_ftp = [3.796875,9.390625,12.1875] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.3*(player_str + player_int) + 0.2*player_dex
        nhits = 2
        sc = ["Distortion","Scission"]
    elif ws_name == "Fast Blade II":
        base_ftp = [1.8, 3.5, 5.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = True 
        wsc = 0.8*player_dex 
        nhits = 2
        sc = ["Fusion"]
    elif ws_name == "Imperator":    
        base_ftp = [3.75, 7.5, 11.75] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False 
        wsc = 0.7*(player_dex + player_mnd)
        nhits = 1
        sc = ["Detonation","Compression","Distortion"]


    # Katana weapon skills
    elif ws_name == "Blade: Retsu":
        base_ftp  = [0.5, 1.5, 2.5]
        ftp       = 1.0
        ftp_rep   = False
        wsc       = 0.6*player_dex + 0.2*player_str
        nhits     = 2
        sc = ["Scission"]
    elif ws_name == "Blade: Teki":
        hybrid    = True
        base_ftp  = [0.5, 1.375, 2.25]
        ftp_hybrid = np.interp(tp, base_tp, base_ftp)
        ftp       = 1.0
        ftp_rep   = False
        wsc       = 0.3*(player_str + player_int)
        nhits     = 1
        element   = "Water"
        sc = ["Reverberation"]
    elif ws_name == "Blade: To":
        hybrid    = True
        base_ftp  = [0.5, 1.5, 2.5]
        ftp_hybrid = np.interp(tp, base_tp, base_ftp)
        ftp       = 1.0
        ftp_rep   = False
        wsc       = 0.4*(player_str + player_int)
        nhits     = 1
        element   = "Ice"
        sc = ["Induration","Detonation"]
    elif ws_name == "Blade: Chi":
        hybrid    = True
        base_ftp  = [0.5, 1.375, 2.25]
        ftp_hybrid = np.interp(tp, base_tp, base_ftp)
        ftp       = 1.0
        ftp_rep   = False
        wsc       = 0.3*(player_str + player_int)
        nhits     = 2
        element   = "Earth"
        sc = ["Impaction","Transfixion"]
    elif ws_name == "Blade: Ei":
        base_ftp = [1.0, 3.0, 5.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_int)
        nhits = 1
        magical = True
        element = "Dark"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Compression"]
    elif ws_name == "Blade: Jin":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.1, 0.25, 0.5] # Copied Evisceration values due to FTP Scaling and Cyclopedia claiming first value is +10%
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += get_dex_crit(player_dex, enemy_agi)
        ftp = 1.375
        ftp_rep = True
        wsc = 0.3*(player_dex + player_str)
        nhits = 3
        sc = ["Detonation","Impaction"]
    elif ws_name == "Blade: Ten":
        base_ftp = [4.5, 11.5, 15.5]
        ftp      = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc      = 0.3*(player_str + player_dex)
        nhits    = 1
        sc = ["Gravitation"]
    elif ws_name == "Blade: Ku":
        acc_boost = [0, 20, 40] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_accuracy1 += acc_bonus
        player_accuracy2 += acc_bonus
        ftp  = 1.25
        ftp_rep = True
        wsc = 0.3*(player_str + player_dex)
        nhits = 5
        sc = ["Gravitation","Transfixion"]
    elif ws_name == "Blade: Yu":
        ftp = 3.0
        ftp_rep = False
        wsc = 0.4*(player_dex + player_int)
        nhits = 1
        magical = True
        element = "Water"
        dSTAT = 0
        sc = ["Reverberation","Scission"]
    elif ws_name == "Blade: Kamu":
        # Certain weapon skills reduce the enemy's defense and increase the player's attack. We need to update both values here.
        # Blade: Kamu could be treated as a (1 + 1.25)/(1 + -0.25) = 3.00 attack modifier. (with ws_atk_modifier = 2.0)
        ftp  = 1.0
        ftp_rep = False
        wsc = 0.6*(player_int + player_str)
        nhits = 1

        ws_atk_modifier = 1.25 # 125% bonus attack
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        if player_attack2 > 0:
            player_attack2 -= player.stats.get("Food Attack",0)
            player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
            player_attack2 += player.stats.get("Food Attack",0)

        # enemy.stats["Defense%"] = enemy.stats.get("Defense%",0) - 0.25 # Create a new enemy stat "Defense%" which works similar to the player's "Attack%". I'll use it immediately before calculating damage later.
        enemy_def *= (1 - 0.25) # I treat defense down debuffs as multiplicatively stacking. This alone gets around the potential for more than 100% defense reduction. A normal Idris Frailty is -40%. If we added Blade: Kamu, this would be -110% with additive stacking. Multiplicatively, it is -85%.
        sc = ["Fragmentation","Compression"]
    elif ws_name == "Blade: Shun":
        atk_boost = [1.0, 2.0, 3.0]
        ws_atk_modifier = np.interp(tp, base_tp, atk_boost) - 1.0

        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        if player_attack2 > 0:
            player_attack2 -= player.stats.get("Food Attack",0)
            player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
            player_attack2 += player.stats.get("Food Attack",0)

        ftp = 1.0
        ftp_rep = True
        wsc = 0.85*player_dex
        nhits = 5
        sc = ["Aeonic","Fusion","Impaction"]
    elif ws_name == "Blade: Metsu":
        ftp  = 5.0
        ftp_rep = False
        wsc = 0.8*player_dex
        nhits = 1
        sc = ["Darkness","Fragmentation"]
    elif ws_name == "Blade: Hi":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.15, 0.2, 0.25]
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += get_dex_crit(player_dex, enemy_agi)
        ftp = 5.0
        ftp_rep = False
        wsc = 0.8*player_agi
        nhits = 1
    elif ws_name == "Zesho Meppo":
        base_ftp = [4.0, 10.0, 18.715] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.25*(player_dex + player_agi)
        nhits = 4
        sc = ["Induration","Reverberation","Fusion"]


    # Dagger weapon skills
    elif ws_name == "Viper Bite":
        ftp = 1.0
        ftp_rep = False
        ws_atk_modifier = 1.0
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        if player_attack2 > 0:
            player_attack2 -= player.stats.get("Food Attack",0)
            player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
            player_attack2 += player.stats.get("Food Attack",0)
        wsc = 1.0*player_dex
        nhits = 2
        sc = ["Scission"]
    elif ws_name == "Dancing Edge":
        acc_boost = [0, 20, 40] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_accuracy1 += acc_bonus
        player_accuracy2 += acc_bonus
        ftp  = 1.1875 
        ftp_rep = False
        wsc = 0.4*(player_chr + player_dex)
        nhits = 5
        sc = ["Scission", "Detonation"]
    elif ws_name == "Shark Bite":
        base_ftp = [4.5, 6.8, 8.5] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_agi + player_dex) 
        nhits = 2
        sc = ["Fragmentation"]
    elif ws_name == "Evisceration":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.1, 0.25, 0.5]
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += get_dex_crit(player_dex, enemy_agi)
        ftp = 1.25
        ftp_rep = True
        wsc = 0.5*player_dex
        nhits = 5
        sc = ["Gravitation","Transfixion"]
    elif ws_name == "Aeolian Edge":
        base_ftp = [2.0, 3.0, 4.5] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_dex + player_int)
        nhits = 1
        magical = True
        element = "Wind"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Scission","Detonation","Impaction"]
    elif ws_name == "Exenterator":
        ftp = 1.0
        ftp_rep = True
        wsc = 0.85*player_agi
        nhits = 4
        sc = ["Aeonic","Gravitation","Transfixion"]
    elif ws_name == "Mercy Stroke":
        ftp  = 5.0
        ftp_rep = False
        wsc = 0.8*player_str
        nhits = 1
        sc = ["Darkness","Gravitation"]
    elif ws_name == "Rudra's Storm":
        base_ftp = [5.0, 10.19, 13.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.8*player_dex
        nhits = 1
        sc = ["Darkness","Distortion"]
    elif ws_name == "Mandalic Stab":
        base_ftp = [4.0, 6.09, 8.5]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        ws_atk_modifier = 0.75
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        if player_attack2 > 0:
            player_attack2 -= player.stats.get("Food Attack",0)
            player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
            player_attack2 += player.stats.get("Food Attack",0)
        wsc = 0.6*player_dex
        nhits = 1
        sc = ["Fusion","Compression"]
    elif ws_name == "Mordant Rime":
        acc_boost = [0, 20, 40] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_accuracy1 += acc_bonus
        player_accuracy2 += acc_bonus
        ftp  = 5.0
        ftp_rep = False
        wsc = 0.7*player_chr + 0.3*player_dex
        nhits = 2
        sc = ["Fragmentation","Distortion"]
    elif ws_name == "Pyrrhic Kleos":
        ftp  = 1.75
        ftp_rep = True
        wsc = 0.4*(player_str + player_dex)
        nhits = 4
        sc = ["Distortion","Scission"]
    elif ws_name == "Ruthless Stroke":
        base_ftp = [5.375, 14.0, 23.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False 
        wsc = 0.25*(player_dex + player_agi)
        nhits = 4
        sc = ["Liquefaction","Impaction","Fragmentation"]


    # Polearm weapon skills
    elif ws_name == "Double Thrust":
        base_ftp = [1.0, 1.5, 2.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.3*(player_str + player_dex)
        nhits = 2
        sc = ["Transfixion"]
    elif ws_name == "Thunder Thrust":
        base_ftp = [1.5, 2.0, 2.5] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_int)
        nhits = 1
        magical = True
        element = "Thunder"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Transfixion","Impaction"]
    elif ws_name == "Raiden Thrust":
        base_ftp = [1.0, 2.0, 3.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_int)
        nhits = 1
        magical = True
        element = "Thunder"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Transfixion","Impaction"]
    elif ws_name == "Penta Thrust":
        acc_boost = [0, 20, 40] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_accuracy1 += acc_bonus
        ftp  = 1.00
        ftp_rep = False
        wsc = 0.2*(player_str + player_dex)
        nhits = 5
        
        ws_atk_modifier = -0.125
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        sc = ["Compression"]
    elif ws_name == "Wheeling Thrust":
        ftp  = 1.75
        ftp_rep = False
        wsc = 0.8*player_str
        nhits = 1
        base_enemy_def_scaling = [0.50, 0.625, 0.75]
        enemy_def_scaling = np.interp(tp, base_tp, base_enemy_def_scaling)
        enemy_def *= (1-enemy_def_scaling)
        sc = ["Scission"]
    elif ws_name == "Impulse Drive":
        base_ftp = [1.0, 3.0, 5.5]
        ftp      = np.interp(tp, base_tp, base_ftp)
        ftp_rep  = False
        wsc      = 1.0*player_str
        nhits    = 2
        sc = ["Gravitation","Induration"]
    elif ws_name == "Sonic Thrust":
        base_ftp = [3.0, 3.7, 4.5]
        ftp      = np.interp(tp, base_tp, base_ftp)
        ftp_rep  = False
        wsc      = 0.4*(player_dex + player_str)
        nhits    = 1
        sc = ["Transfixion","Scission"]
    elif ws_name == "Stardiver":
        base_ftp = [0.75, 1.25, 1.75]
        ftp      = np.interp(tp, base_tp, base_ftp)
        ftp_rep  = True
        wsc      = 0.85*player_str
        nhits    = 4
        sc = ["Aeonic","Gravitation","Transfixion"]
    elif ws_name == "Geirskogul":
        ftp      = 3.0
        ftp_rep  = False
        wsc      = 0.8*player_dex
        nhits    = 1
        sc = ["Light","Distortion"]
    elif ws_name == "Camlann's Torment":
        ftp  = 3.0
        ftp_rep = False
        wsc = 0.6*(player_vit + player_str)
        nhits = 1
        base_enemy_def_scaling = [0.125, 0.375, 0.625]
        enemy_def_scaling = np.interp(tp, base_tp, base_enemy_def_scaling)
        enemy_def *= (1-enemy_def_scaling)
        sc = ["Light","Fragmentation"]
    elif ws_name == "Drakesbane":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.1, 0.25, 0.40]
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += get_dex_crit(player_dex, enemy_agi)
        ftp = 1.0
        ftp_rep = False
        wsc = 0.5*player_str
        nhits = 4
        ws_atk_modifier = 0.8125 - 1.0
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        sc = ["Fusion","Transfixion"]
    elif ws_name == "Diarmuid":
        base_ftp = [2.17, 5.36, 8.55] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False 
        wsc = 0.55*(player_str + player_vit)
        nhits = 2
        sc = ["Transfixion","Scission","Gravitation"]

    # Great Katana weapon skills
    elif ws_name == "Tachi: Enpi":
        base_ftp = [1.0, 1.5, 2.0]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.6*player_str
        nhits = 2
        sc = ["Transfixion","Scission"]
    elif ws_name == "Tachi: Goten":
        hybrid    = True
        base_ftp  = [0.5, 1.5, 2.5]
        ftp_hybrid = np.interp(tp, base_tp, base_ftp)
        ftp       = 1.0
        ftp_rep   = False
        wsc       = 0.6*player_str
        nhits     = 1
        element   = "Thunder"
        sc = ["Transfixion","Impaction"]
    elif ws_name == "Tachi: Kagero":
        hybrid    = True
        base_ftp  = [0.5, 1.5, 2.5]
        ftp_hybrid = np.interp(tp, base_tp, base_ftp)
        ftp       = 1.0
        ftp_rep   = False
        wsc       = 0.75*player_str
        nhits     = 1
        element   = "Fire"
        sc = ["Liquefaction"]
    elif ws_name == "Tachi: Koki":
        hybrid    = True
        base_ftp  = [0.5, 1.5, 2.5]
        ftp_hybrid = np.interp(tp, base_tp, base_ftp)
        ftp       = 1.0
        ftp_rep   = False
        wsc       = 0.3*player_mnd + 0.5*player_str
        nhits     = 1
        element   = "Light"
        sc = ["Reverberation","Impaction"]
    elif ws_name == "Tachi: Jinpu":
        hybrid    = True
        base_ftp  = [0.5, 1.5, 2.5]
        ftp_hybrid = np.interp(tp, base_tp, base_ftp)
        ftp       = 1.0
        ftp_rep   = False
        wsc       = 0.3*player_str
        nhits     = 2
        element   = "Wind"
        sc = ["Scission","Detonation"]
    elif ws_name == "Tachi: Yukikaze":
        base_ftp = [1.5625, 2.6875, 4.125]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        ws_atk_modifier = 0.5
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        wsc = 0.75*player_str
        nhits = 1
        sc = ["Induration","Detonation"]
    elif ws_name == "Tachi: Gekko":
        base_ftp = [1.5625, 2.6875, 4.125]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        ws_atk_modifier = 1.0
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        wsc = 0.75*player_str
        nhits = 1
        sc = ["Distortion","Reverberation"]
    elif ws_name == "Tachi: Kasha":
        base_ftp = [1.5625, 2.6875, 4.125]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        ws_atk_modifier = 0.65
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        wsc = 0.75*player_str
        nhits = 1
        sc = ["Fusion","Compression"]
    elif ws_name == "Tachi: Ageha":
        ftp       = 2.625
        ftp_rep   = False
        wsc       = 0.6*player_chr + 0.4*player_str
        nhits     = 1
        sc = ["Compression","Scission"]
    elif ws_name == "Tachi: Shoha":
        base_ftp = [1.375, 2.1875, 2.6875]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        ws_atk_modifier = 1.375
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        wsc = 0.85*player_str
        nhits = 2
        sc = ["Aeonic","Fragmentation","Compression"]
    elif ws_name == "Tachi: Kaiten":
        ftp  = 3.0
        ftp_rep = False
        wsc = 0.8*player_str
        nhits = 1
        sc = ["Light","Fragmentation"]
    elif ws_name == "Tachi: Fudo":
        base_ftp = [3.75, 5.75, 8.0]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.8*player_str
        nhits = 1
        sc = ["Light","Distortion"]
    elif ws_name == "Tachi: Rana":
        acc_boost = [0, 20, 40] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_accuracy1 += acc_bonus
        ftp  = 1.0
        ftp_rep = False
        wsc = 0.5*player_str
        nhits = 3
        sc = ["Gravitation","Induration"]
    elif ws_name == "Tachi: Mumei":
        base_ftp = [3.66, 7.33, 11.0]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.5*(player_str + player_dex)
        nhits = 1
        sc = ["Detonation","Compression","Distortion"]

    # Scythe weapon skills
    elif ws_name == "Slice":
        base_ftp = [1.5, 1.75, 2.0]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 1.0*player_str
        nhits = 1
        sc = ["Scission"]
    elif ws_name == "Dark Harvest":
        base_ftp = [1.0, 2.0, 2.5] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_int)
        nhits = 1
        magical = True
        element = "Dark"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Reverberation"]
    elif ws_name == "Shadow of Death":
        base_ftp = [1.0, 4.17, 8.6] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_int)
        nhits = 1
        magical = True
        element = "Dark"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Induration","Reverberation"]
    elif ws_name == "Nightmare Scythe":
        ftp = 1.0
        ftp_rep = False 
        wsc = 0.6*(player_str + player_mnd) 
        nhits = 1
        sc = ["Compression","Scission"]
    elif ws_name == "Spinning Scythe":
        ftp = 1.0
        ftp_rep = False
        wsc = 1.0*player_str
        nhits = 1
        sc = ["Reverberation","Scission"]
    elif ws_name == "Cross Reaper":
        base_ftp = [2.0, 4.0, 7.0]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.6*(player_str + player_mnd)
        nhits = 2
        sc = ["Distortion"]
    elif ws_name == "Guillotine":
        ftp = 0.875
        ftp_rep = False
        wsc = 0.3*player_str + 0.5*player_mnd
        nhits = 4
        sc = ["Induration"]
    elif ws_name == "Spiral Hell":
        base_ftp = [1.375,2.75,4.75]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.5*(player_str + player_int)
        nhits = 1
        sc = ["Distortion","Scission"]
    elif ws_name == "Infernal Scythe":
        ftp = 3.5
        ftp_rep = False
        wsc = 0.7*player_int + 0.3*player_str
        nhits = 1
        magical = True
        element = "Dark"
        dSTAT = 0
        sc = ["Compression","Reverberation"]
    elif ws_name == "Entropy":
        base_ftp = [0.75, 1.25, 2.0]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = True
        wsc = 0.85*(player_int)
        nhits = 4
        sc = ["Aeonic","Gravitation","Reverberation"]
    elif ws_name == "Catastrophe":
        ftp  = 2.75
        ftp_rep = False
        wsc = 0.4*(player_str + player_int)
        nhits = 1
        sc = ["Darkness","Gravitation"]
    elif ws_name == "Quietus":
        ftp  = 3.0
        ftp_rep = False
        wsc = 0.6*(player_mnd + player_str)
        nhits = 1
        base_enemy_def_scaling = [0.10, 0.30, 0.50]
        enemy_def_scaling = np.interp(tp, base_tp, base_enemy_def_scaling)
        enemy_def *= (1-enemy_def_scaling)
        sc = ["Darkness","Distortion"]
    elif ws_name == "Insurgency":
        base_ftp = [0.5, 3.25, 6.0]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.2*(player_str + player_int)
        nhits = 4
        sc = ["Fusion","Compression"]
    elif ws_name == "Origin":
        base_ftp = [3.0, 6.25, 9.5] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False 
        wsc = 0.6*(player_int + player_str)
        nhits = 1
        sc = ["Induration","Reverberation","Fusion"]

    # Great Sword weapon skills
    elif ws_name == "Hard Slash":
        base_ftp = [1.5, 1.75, 2.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_agi)
        nhits = 2
        sc = ["Scission"]
    elif ws_name == "Freezebite":
        base_ftp = [1.5, 3.5, 6.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_int)
        nhits = 1
        magical = True
        element = "Ice"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Induration","Detonation"]
    elif ws_name == "Shockwave":
        ftp = 1.0
        ftp_rep = False
        wsc = 0.3*(player_str + player_mnd)
        nhits = 1
        sc = ["Reverberation"]
    elif ws_name == "Sickle Moon":
        base_ftp = [1.5, 2.0, 2.75] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_agi)
        nhits = 1
        sc = ["Scission","Impaction"]
    elif ws_name == "Spinning Slash":
        base_ftp = [2.5,3.0,3.5]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        ws_atk_modifier = 0.5
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        wsc = 0.3*(player_str + player_int)
        nhits = 1
        sc = ["Fragmentation"]
    elif ws_name == "Ground Strike":
        base_ftp = [1.5, 1.75, 3.0]
        ftp      = np.interp(tp, base_tp, base_ftp)
        ftp_rep  = False
        wsc      = 0.5*(player_int + player_str)
        nhits    = 1
        ws_atk_modifier = 0.75
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        sc = ["Fragmentation","Distortion"]
    elif ws_name == "Herculean Slash":
        ftp = 3.5
        ftp_rep = False
        wsc = 0.8*player_vit
        nhits = 1
        magical = True
        element = "Ice"
        dSTAT = 0
        sc = ["Induration","Impaction","Detonation"]
    elif ws_name == "Resolution":
        base_ftp = [0.71875, 1.5, 2.25]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = True
        wsc = 0.85*(player_str)
        nhits = 5
        ws_atk_modifier = -0.15
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        sc = ["Aeonic","Light","Fragmentation","Scission"]
    elif ws_name == "Scourge":
        ftp  = 3.0
        ftp_rep = False
        wsc = 0.4*(player_str + player_vit)
        nhits = 1
        sc = ["Light","Fusion"]
    elif ws_name == "Torcleaver":
        base_ftp = [4.75, 7.5, 9.765625]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.8*(player_vit)
        nhits = 1
        sc = ["Light","Distortion"]
    elif ws_name == "Dimidiation":
        base_ftp = [2.25, 4.5, 6.75]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        ws_atk_modifier = 0.25
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        wsc = 0.8*player_dex
        nhits = 2
        sc = ["Light","Fragmentation"]
    elif ws_name == "Fimbulvetr":
        base_ftp = [3.3, 6.6, 9.9] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False 
        wsc = 0.6*(player_str + player_vit)
        sc = ["Detonation","Compression","Distortion"]
        nhits = 1

    # Club weapon skills
    elif ws_name == "Shining Strike":
        base_ftp = [1.625, 3.0, 4.625] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_mnd)
        nhits = 1
        magical = True
        element = "Light"
        dSTAT = 0
        sc = ["Impaction"]
    elif ws_name == "Seraph Strike":
        base_ftp = [2.125, 3.675, 6.125] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_mnd)
        nhits = 1
        magical = True
        element = "Light"
        dSTAT = 0
        sc = ["Impaction"]
    elif ws_name == "Skullbreaker":
        ftp = 1.0
        ftp_rep = False
        wsc = 1.0*player_str
        nhits = 1
        sc = ["Induration","Reverberation"]
    elif ws_name == "True Strike":
        crit_ws = True
        crit_rate = 1.0
        acc_boost = [-60, -30, 0] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_accuracy1 += acc_bonus
        player_accuracy2 += acc_bonus
        ftp  = 1.0
        ftp_rep = False
        wsc = 1.0*player_str
        nhits = 1
        ws_atk_modifier = 1.0
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        if player_attack2 > 0:
            player_attack2 -= player.stats.get("Food Attack",0)
            player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
            player_attack2 += player.stats.get("Food Attack",0)
        sc = ["Detonation","Impaction"]
    elif ws_name == "Judgment":
        base_ftp = [3.5, 8.75, 12.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.5*(player_mnd + player_str)
        nhits = 1
        sc = ["Impaction"]
    elif ws_name == "Hexa Strike":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.1, 0.175, 0.25] # Middle value unknown. I just picked the half-way point to force linear scaling.
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += get_dex_crit(player_dex, enemy_agi)
        ftp = 1.125
        ftp_rep = True
        wsc = 0.3*(player_mnd + player_str)
        nhits = 6
        sc = ["Fusion"]
    elif ws_name == "Black Halo":
        base_ftp = [3.0, 7.25, 9.75] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.7*player_mnd + 0.3*player_str
        nhits = 2
        sc = ["Fragmentation","Compression"]
    elif ws_name == "Realmrazer":
        acc_boost = [0, 20, 40] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_accuracy1 += acc_bonus
        player_accuracy2 += acc_bonus
        ftp  = 0.9
        ftp_rep = True
        wsc = 0.85*player_mnd
        nhits = 7
        sc = ["Aeonic","Fusion","Impaction"]
    elif ws_name == "Randgrith":
        ftp  = 4.25
        ftp_rep = False
        wsc = 0.4*(player_str + player_mnd)
        nhits = 1
        sc = ["Light","Fragmentation"]
    elif ws_name == "Mystic Boon":
        base_ftp = [2.5, 4.0, 7.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.7*player_mnd + 0.3*player_str
        nhits = 1
        sc = ["None"]
    elif ws_name == "Exudation":
        atk_boost = [1.5, 3.625, 4.750]
        ws_atk_modifier = np.interp(tp, base_tp, atk_boost) - 1.0
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        if player_attack2 > 0:
            player_attack2 -= player.stats.get("Food Attack",0)
            player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
            player_attack2 += player.stats.get("Food Attack",0)
        ftp = 2.8
        ftp_rep = False
        wsc = 0.5*(player_mnd + player_int)
        nhits = 1
        sc = ["Darkness","Fragmentation"]
    elif ws_name == "Dagda":
        base_ftp = [1, 2, 3] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False 
        wsc = 0.0*player_dex 
        nhits = 2
        sc = ["Transfixion","Scission","Gravitation"]

    # Great Axe weapon skills
    elif ws_name == "Shield Break":
        ftp = 1.0
        ftp_rep = False 
        wsc = 0.6*(player_str + player_vit) 
        nhits = 1
        sc = ["Impaction"]
    elif ws_name == "Iron Tempest":
        atk_boost = [1.0, 1.2, 1.5]
        ws_atk_modifier = np.interp(tp, base_tp, atk_boost) - 1.0
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        ftp = 1.0
        ftp_rep = False
        wsc = 0.6*player_str
        nhits = 1
        sc = ["Scission"]
    elif ws_name == "Armor Break":
        ftp = 1.0
        ftp_rep = False 
        wsc = 0.6*(player_str + player_vit) 
        nhits = 1
        sc = ["Impaction"]
    elif ws_name == "Weapon Break":
        ftp = 1.0
        ftp_rep = False 
        wsc = 0.6*(player_str + player_vit) 
        nhits = 1
        sc = ["Impaction"]
    elif ws_name == "Raging Rush":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.15, 0.30, 0.50]
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += get_dex_crit(player_dex, enemy_agi)
        ftp = 1.0
        ftp_rep = False
        wsc = 0.5*player_str
        nhits = 3
        sc = ["Induration","Reverberation"]
    elif ws_name == "Full Break":
        ftp = 1.0
        ftp_rep = False 
        wsc = 0.5*(player_str + player_vit) 
        nhits = 1
        sc = ["Distortion"]
    elif ws_name == "Steel Cyclone":
        base_ftp = [1.5, 2.5, 4.0]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        ws_atk_modifier = 0.5
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        wsc = 0.6*(player_str + player_vit)
        nhits = 1
        sc = ["Distortion","Detonation"]
    elif ws_name == "Fell Cleave":
        ftp  = 2.75
        ftp_rep = False
        wsc = 0.6*player_str
        nhits = 1
        sc = ["Impaction","Scission","detonation"]
    elif ws_name == "Upheaval":
        base_ftp = [1.0, 3.5, 6.5] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.85*player_vit
        nhits = 4
        sc = ["Aeonic","Fusion","Compression"]
    elif ws_name == "Metatron Torment":
        ftp  = 2.75
        ftp_rep = False
        wsc = 0.8*player_str
        nhits = 1
        sc = ["Light","Fusion"]
    elif ws_name == "Ukko's Fury":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.2, 0.35, 0.55] # Middle value unknown. I just picked the half-way point to force linear scaling.
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += get_dex_crit(player_dex, enemy_agi)
        ftp = 2.0
        ftp_rep = False
        wsc = 0.8*player_str
        nhits = 2
        sc = ["Light","Fragmentation"]
    elif ws_name == "King's Justice":
        base_ftp = [1.0, 3.0, 5.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.5*player_str
        nhits = 3
        sc = ["Fragmentation","Scission"]
    elif ws_name == "Disaster":
        base_ftp = [3.05, 6.10, 9.15] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False 
        wsc = 0.6*(player_str + player_vit) 
        nhits = 1
        sc = ["Transfixion","Scission","Gravitation"]

    # Axe weapon skills
    elif ws_name == "Raging Axe":
        base_ftp = [1.0, 1.5, 2.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.6*player_str
        nhits = 2
        sc = ["Detonation","Impaction"]
    elif ws_name == "Spinning Axe":
        base_ftp = [2.0, 2.5, 3.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.6*player_str
        nhits = 2
        sc = ["Liquefaction","Scission","Impaction"]
    elif ws_name == "Rampage":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.0, 0.20, 0.40] # Middle value unknown. I just picked the half-way point to force linear scaling.
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += get_dex_crit(player_dex, enemy_agi)
        ftp = 1.0
        ftp_rep = True
        wsc = 0.5*player_str
        nhits = 5
        sc = ["Scission"]
    elif ws_name == "Calamity":
        base_ftp = [2.5, 6.5, 10.375] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.5*(player_str + player_vit)
        nhits = 1
        sc = ["Scission","Impaction"]
    elif ws_name == "Mistral Axe":
        base_ftp = [4.0, 10.5, 13.625]
        ftp      = np.interp(tp, base_tp, base_ftp)
        ftp_rep  = False
        wsc      = 0.5*player_str
        nhits    = 1
        sc = ["Fusion"]
    elif ws_name == "Decimation":
        acc_boost = [0, 20, 40] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_accuracy1 += acc_bonus
        player_accuracy2 += acc_bonus
        ftp = 1.75
        ftp_rep = True
        wsc = 0.5*player_str
        nhits = 3
        sc = ["Fusion","Reverberation"]
    elif ws_name == "Bora Axe":
        acc_boost = [0, 20, 40] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_accuracy1 += acc_bonus
        player_accuracy2 += acc_bonus
        ftp  = 4.5
        ftp_rep = False
        wsc = 1.0*player_dex
        nhits = 1
        sc = ["Scission","Detonation"]
    elif ws_name == "Ruinator":
        acc_boost = [0, 20, 40] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_accuracy1 += acc_bonus
        player_accuracy2 += acc_bonus
        ftp  = 1.08
        ws_atk_modifier = 0.1
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        if player_attack2 > 0:
            player_attack2 -= player.stats.get("Food Attack",0)
            player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
            player_attack2 += player.stats.get("Food Attack",0)
        ftp = 1.0
        ftp_rep = True
        wsc = 0.85*player_str
        nhits = 4
        sc = ["Aeonic","Distortion","Detonation"]
    elif ws_name == "Onslaught":
        ftp  = 2.75
        ftp_rep = False
        wsc = 0.8*player_dex
        nhits = 1
        sc = ["Darkness","Gravitation"]
    elif ws_name == "Cloudsplitter":
        base_ftp = [3.75, 6.69921875, 8.5 ] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_mnd)
        nhits = 1
        magical = True
        element = "Thunder"
        dSTAT = 0
        sc = ["Darkness","Fragmentation"]
    elif ws_name == "Primal Rend":
        base_ftp = [3.0625,5.8359375,7.5625 ] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.6*player_chr + 0.3*player_dex
        nhits = 1
        magical = True
        element = "Light"
        dSTAT = 651 if (player_chr - enemy_int)*1.5 > 651 else (player_chr - enemy_int)*1.5
        sc = ["Gravitation","Reverberation"]
    elif ws_name == "Blitz":
        base_ftp = [1.5, 7.0, 12.5] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False 
        wsc = 0.32*(player_dex + player_str)
        nhits = 5
        sc = ["Liquefaction","Impaction","Fragmentation"]

    # Archery weapon skills
    elif ws_name == "Flaming Arrow":
        hybrid    = True
        base_ftp  = [0.5, 1.55, 2.1]
        ftp_hybrid = np.interp(tp, base_tp, base_ftp)
        ftp       = 1.0
        ftp_rep   = False
        wsc       = 0.5*player_agi + 0.2*player_str
        nhits     = 1
        element   = "Fire"
        sc = ["Liquefaction","Transfixion"]
    elif ws_name == "Piercing Arrow":
        ftp  = 1.0
        ftp_rep = True
        wsc = 0.5*player_agi + 0.2*player_str
        nhits = 1
        def_multiplier = [1.0, 0.65, 0.50]
        enemy_def *= np.interp(tp, base_tp, def_multiplier)
        sc = ["Reverberation","Transfixion"]
    elif ws_name == "Dulling Arrow":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.10, 0.20, 0.25] # I made these numbers up
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += ((player_agi - enemy_agi)/10)/100 # Ranged attacks gain crit rate from AGI, not DEX
        ftp = 1.0
        ftp_rep = False
        wsc = 0.5*player_agi + 0.2*player_str
        nhits = 1
        sc = ["Liquefaction","Transfixion"]
    elif ws_name == "Sidewinder":
        acc_boost = [-50, -20, 0] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_rangedaccuracy += acc_bonus
        ftp  = 5.0
        ftp_rep = False
        wsc = 0.5*player_agi + 0.2*player_str
        nhits = 1
        sc = ["Reverberation","Transfixion","Detonation"]
    elif ws_name == "Blast Arrow":
        acc_boost = [0, 20, 40] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_rangedaccuracy += acc_bonus
        ftp  = 2.0
        ftp_rep = False
        wsc = 0.5*player_agi + 0.2*player_str
        nhits = 1
        sc = ["Induration","Transfixion"]
    elif ws_name == "Empyreal Arrow":
        ws_atk_modifier = 1.0
        player_rangedattack -= player.stats["Food Ranged Attack"]
        player_rangedattack *= (1+player.stats.get("Ranged Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Ranged Attack%",0))
        player_rangedattack += player.stats["Food Ranged Attack"]
        base_ftp = [1.5, 2.5, 5.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.5*player_agi + 0.2*player_str
        nhits = 1
        sc = ["Fusion","Transfixion"]
    elif ws_name == "Refulgent Arrow":
        base_ftp = [3.0, 4.25, 7.0]
        ftp      = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc      = 0.6*player_str
        nhits    = 1 # BG states this is a 1-hit attack. Could use some testing to confirm since the description on BG says "twofold attack"
        sc = ["Reverberation","Transfixion"]
    elif ws_name == "Apex Arrow":
        ftp  = 3.0
        ftp_rep = False
        wsc = 0.85*player_agi
        nhits = 1
        base_enemy_def_scaling = [0.15, 0.30, 0.45] # First number is known. I made up the other two
        enemy_def_scaling = np.interp(tp, base_tp, base_enemy_def_scaling)
        enemy_def *= (1-enemy_def_scaling)
        sc = ["Aeonic","Fragmentation","Transfixion"]
    elif ws_name == "Namas Arrow":
        ftp  = 2.75
        ftp_rep = False
        wsc = 0.4*(player_str + player_agi)
        nhits = 1
        sc = ["Light","Distortion"]
    elif ws_name == "Jishnu's Radiance":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.15, 0.2, 0.25] # No values are known for Jishu's crits. I copied these values from Blade: Hi
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += ((player_agi - enemy_agi)/10)/100 # Ranged attacks gain crit rate from AGI, not DEX
        ftp = 1.75
        ftp_rep = True
        wsc = 0.8*player_dex
        nhits = 3
        sc = ["Light","Fusion"]
    elif ws_name == "Sarv":
        base_ftp = [2.75, 5.5, 8.25] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False 
        wsc = 0.65*(player_str + player_agi)
        nhits = 1
        sc = ["Transfixion","Scission","Gravitation"]

    # Marksmanship weapon skills
    elif ws_name == "Hot Shot":
        hybrid    = True
        base_ftp  = [0.5, 1.55, 2.1]
        ftp_hybrid = np.interp(tp, base_tp, base_ftp)
        ftp       = 1.0
        ftp_rep   = False
        wsc       = 0.7*player_agi
        nhits     = 1
        element   = "Fire"
        sc = ["Liquefaction","Transfixion"]
    elif ws_name == "Split Shot":
        ftp  = 1.0
        ftp_rep = False
        wsc = 0.7*player_agi
        nhits = 1
        def_multiplier = [1.0, 0.65, 0.50]
        enemy_def *= np.interp(tp, base_tp, def_multiplier)
        sc = ["Reverberation","Transfixion"]
    elif ws_name == "Sniper Shot":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.10, 0.20, 0.25] # I made these numbers up
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += ((player_agi - enemy_agi)/10)/100 # Ranged attacks gain crit rate from AGI, not DEX
        ftp = 1.0
        ftp_rep = False
        wsc = 0.7*player_agi
        nhits = 1
        sc = ["Liquefaction","Transfixion"]
    elif ws_name == "Slug Shot":
        acc_boost = [-50, -20, 0] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_rangedaccuracy += acc_bonus
        ftp  = 5.0
        ftp_rep = False
        wsc = 0.7*player_agi
        nhits = 1
        sc = ["Reverberation","Transfixion","Detonation"]
    elif ws_name == "Blast Shot":
        acc_boost = [0, 20, 40] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_rangedaccuracy += acc_bonus
        ftp  = 2.0
        ftp_rep = False
        wsc = 0.7*player_agi
        nhits = 1
        sc = ["Induration","Transfixion"]
    elif ws_name == "Detonator":
        ws_atk_modifier = 1.0
        player_rangedattack -= player.stats["Food Ranged Attack"]
        player_rangedattack *= (1+player.stats.get("Ranged Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Ranged Attack%",0))
        player_rangedattack += player.stats["Food Ranged Attack"]
        base_ftp = [1.5, 2.5, 5.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.7*player_agi
        nhits = 1
        sc = ["Fusion","Transfixion"]
    elif ws_name == "Last Stand":
        base_ftp  = [2.0, 3.0, 4.0]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep   = True
        wsc       = 0.85*player_agi
        nhits     = 2
        sc = ["Aeonic","Fusion","Reverberation"]
    elif ws_name == "Coronach":
        ftp  = 3.0
        ftp_rep = False
        wsc = 0.4*(player_dex + player_agi)
        nhits = 1
        sc = ["Darkness","Fragmentation"]
    elif ws_name == "Wildfire":
        ftp = 5.5
        ftp_rep = False
        wsc = 0.6*player_agi
        nhits = 1
        magical = True
        element = "Fire"
        dSTAT = 1276 if (player_agi - enemy_int)*2 > 1276 else (player_agi - enemy_int)*2 
        sc = ["Darkness","Gravitation"]
    elif ws_name == "Trueflight":
        base_ftp = [3.890625,6.4921875,9.671875] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 1.0*player_agi
        nhits = 1
        magical = True
        element = "Light"
        dSTAT = (player_agi - enemy_int)*2 # No known cap.
        sc = ["Fragmentation","Scission"]
    elif ws_name == "Leaden Salute":
        base_ftp = [4.0,6.7,10.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 1.0*player_agi
        nhits = 1
        magical = True
        element = "Dark"
        dSTAT = (player_agi - enemy_int)*2 # No known cap.
        sc = ["Gravitation","Transfixion"]
    elif ws_name == "Terminus":
        base_ftp = [2.5, 5.0, 7.5] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False 
        wsc = 0.7*(player_dex + player_agi)
        nhits = 1
        sc = ["Induration","Reverberation","Fusion"]

    # Staff weapon skills
    elif ws_name == "Heavy Swing":
        base_ftp = [1.0, 1.25, 2.25] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 1.0*player_str
        nhits = 1
        sc = ["Impaction"]
    elif ws_name == "Rock Crusher":
        base_ftp = [1.0, 2.0, 2.5] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_int)
        nhits = 1
        magical = True
        element = "Earth"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Impaction"]
    elif ws_name == "Earth Crusher":
        base_ftp = [1.0, 2.3125, 3.625] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_int)
        nhits = 1
        magical = True
        element = "Earth"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Detonation","Impaction"]
    elif ws_name == "Starburst":
        base_ftp = [1.0, 2.0, 2.5] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_mnd)
        nhits = 1
        magical = True
        element = "Light"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Compression","Reverberation"]
    elif ws_name == "Sunburst":
        base_ftp = [1.0, 2.5, 4.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.4*(player_str + player_mnd)
        nhits = 1
        magical = True
        element = "Light"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Compression","Reverberation"]
    elif ws_name == "Shell Crusher":
        ftp = 1.0
        ftp_rep = False
        wsc = 1.0*player_str
        nhits = 1
        sc = ["Detonation"]
    elif ws_name == "Full Swing":
        base_ftp = [1.0, 3.0, 5.0]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.5*player_str
        nhits = 1
        sc = ["Liquefaction","Impaction"]
    elif ws_name == "Retribution":
        base_ftp = [2.0,2.5,3.0]
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        ws_atk_modifier = 0.5
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        wsc = 0.5*player_mnd + 0.3*player_str
        nhits = 1
        sc = ["Gravitation","Reverberation"]
    elif ws_name == "Cataclysm":
        base_ftp = [2.75, 4.0, 5.0] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False
        wsc = 0.3*(player_str + player_int)
        nhits = 1
        magical = True
        element = "Dark"
        dSTAT = 32 if (player_int - enemy_int)/2 + 8 > 32 else (player_int - enemy_int)/2 + 8
        sc = ["Compression","Reverberation"]
    elif ws_name == "Shattersoul":
        ftp = 1.375
        ftp_rep = False
        wsc = 0.85*player_int
        nhits = 3
        sc = ["Aeonic","Gravitation","Induration"]
    elif ws_name == "Vidohunir":
        ftp = 1.75
        ftp_rep = False
        wsc = 0.8*player_int
        nhits = 1
        magical = True
        element = "Dark"
        dSTAT = (player_int - enemy_int)*2 # No known cap
        sc = ["Fragmentation","Distortion"]
    elif ws_name == "Omniscience":
        ftp = 2.0
        ftp_rep = False
        wsc = 0.8*player_mnd
        nhits = 1
        magical = True
        element = "Dark"
        dSTAT = (player_mnd - enemy_mnd)*2 # No known cap
        sc = ["Gravitation","Transfixion"]
    elif ws_name == "Gate of Tartarus":
        ftp = 3.0
        ftp_rep = False
        wsc = 0.8*player_int
        nhits = 1
        sc = ["Darkness","Distortion"]
    elif ws_name == "Oshala":
        base_ftp = [1, 2, 3] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = False 
        wsc = 0.0*player_dex 
        nhits = 1
        sc = ["Induration","Reverberation","Fusion"]

    # Hand-to-Hand weapon skills
    # Notice that each weapon skill has "-1" nhits.
    # This is to allow us to fit in an "off-hand" attack to get full TP, as observed in game.
    # Technically, the off-hand attack does not get any MA procs, but it does get full TP.
    # You could instead think of this as H2H is dual-wielding, with full TP and MA procs for first main+sub hits, but the sub-hit uses the same stats as the main hit since it's the same weapon.
    # Or you could say the first two main-hits get full TP, and there are no sub hits.
    # I treat it as dual-wield so the empyrean/mythic Aftermaths are treated properly in the code and so it's easy to calculate TP return from WSs
    elif ws_name == "Combo":
        base_ftp = [1.0, 2.4, 3.4]
        ftp      = np.interp(tp, base_tp, base_ftp)
        ftp_rep  = True
        wsc      = 0.3*(player_str + player_dex)
        nhits    = 3-1
        sc = ["Impaction"]
    elif ws_name == "One Inch Punch":
        ftp  = 1.0
        ftp_rep = True
        wsc = 1.0*player_vit
        nhits = 2-1
        def_multiplier = [1.0, 0.75, 0.50]
        enemy_def *= np.interp(tp, base_tp, def_multiplier) # TODO: This should be additive with Dia, Frailty, etc? I think it's fine as is.
        sc = ["Compression"]
    elif ws_name == "Raging Fists":
        base_ftp = [1.0, 2.1875, 3.75]
        ftp      = np.interp(tp, base_tp, base_ftp)
        ftp_rep  = True
        wsc      = 0.3*(player_str + player_dex)
        nhits    = 5-1
        sc = ["Impaction"]
    elif ws_name == "Spinning Attack":
        ftp  = 1.0
        ftp_rep = True
        wsc = 1.0*player_str
        nhits = 2-1
        sc = ["Liquefaction","Impaction"]
    elif ws_name == "Howling Fist":
        base_ftp = [2.05, 3.55, 5.75]
        ftp      = np.interp(tp, base_tp, base_ftp)
        ftp_rep  = True
        wsc      = 0.5*player_vit + 0.2*player_str
        nhits    = 2-1
        ws_atk_modifier = 0.5
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        player_attack2 -= player.stats.get("Food Attack",0)
        player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack2 += player.stats.get("Food Attack",0)
        sc = ["Tranfixion","Impaction"]
    elif ws_name == "Dragon Kick":
        # This is a kick weaponskill that may benefit from Footwork. We re-calculate player attack using the "Kick Attacks Attack%" stat, which is 0% without Footwork, or ~26% with Footwork.
        base_ftp = [1.7, 3.0, 5.0]
        ftp      = np.interp(tp, base_tp, base_ftp)
        ftp_rep  = True
        wsc      = 0.5*(player_vit + player_str)
        nhits    = 2-1

        ws_atk_modifier = player.stats.get("Kick Attacks Attack%",0)
        player_attack1 -= player.stats.get("Food Attack",0) # Remove food bonuses
        player_attack1 /= (1+player.stats.get("Attack%",0)) # Remove multiplicative bonuses
        player_attack1 += player.stats.get("Kick Attacks Attack",0) if player.abilities.get("Footwork",False) else 0 # Add "Kick Attacks Attack" stat if Footwork is active
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) # Repply the multiplicative buffs, but include the +26% from Footwork. Note that this is defined to be zero if Footwork is disabled in the set_stats file.
        player_attack1 += player.stats.get("Food Attack",0) # Reapply food

        player_attack2 -= player.stats.get("Food Attack",0)
        player_attack2 /= (1+player.stats.get("Attack%",0))
        player_attack2 += player.stats.get("Kick Attacks Attack",0) if player.abilities.get("Footwork",False) else 0
        player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier)
        player_attack2 += player.stats.get("Food Attack",0)
        sc = ["Fragmentation"]
    elif ws_name == "Asuran Fists":
        acc_boost = [0, 20, 40] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_accuracy1 += acc_bonus
        player_accuracy2 += acc_bonus
        ftp       = 1.25
        ftp_rep   = True
        wsc       = 0.15*(player_vit + player_str)
        nhits     = 8-1 # -1 for the off-hand hit
        sc = ["Gravitation","Liquefaction"]
    elif ws_name == "Tornado Kick":
        # This is a kick weaponskill that may benefit from Footwork. We re-calculate player attack using the "Kick Attacks Attack%" stat, which is 0% without Footwork, or ~26% with Footwork.
        base_ftp = [1.7, 2.8, 4.5]
        ftp      = np.interp(tp, base_tp, base_ftp)
        ftp_rep  = True
        wsc      = 0.4*(player_vit + player_str)
        nhits    = 3-1
        ws_atk_modifier = player.stats.get("Kick Attacks Attack%",0)
        player_attack1 -= player.stats.get("Food Attack",0) # Remove food bonuses
        player_attack1 /= (1+player.stats.get("Attack%",0)) # Remove multiplicative bonuses
        player_attack1 += player.stats.get("Kick Attacks Attack",0) if player.abilities.get("Footwork",False) else 0 # Add "Kick Attacks Attack" stat if Footwork is active
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) # Repply the multiplicative buffs, but include the +26% from Footwork. Note that this is defined to be zero if Footwork is disabled in the set_stats file.
        player_attack1 += player.stats.get("Food Attack",0) # Reapply food

        player_attack2 -= player.stats.get("Food Attack",0)
        player_attack2 /= (1+player.stats.get("Attack%",0))
        player_attack2 += player.stats.get("Kick Attacks Attack",0) if player.abilities.get("Footwork",False) else 0
        player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier)
        player_attack2 += player.stats.get("Food Attack",0)
        sc = ["Induration","Impaction","Detonation"]
    elif ws_name == "Shijin Spiral":
        acc_boost = [0, 20, 40] # I made these numbers up since it isn't known.
        acc_bonus = np.interp(tp, base_tp, acc_boost)
        player_accuracy1 += acc_bonus
        player_accuracy2 += acc_bonus
        ftp  = 1.5
        ftp_rep = True
        wsc = 0.85*player_dex
        nhits = 5-1
        ws_atk_modifier = 0.05
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        player_attack2 -= player.stats.get("Food Attack",0)
        player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack2 += player.stats.get("Food Attack",0)
        sc = ["Aeonic","Fusion","Reverberation"]
    elif ws_name == "Final Heaven":
        ftp  = 3.0
        ftp_rep = False
        wsc = 0.8*player_vit
        nhits = 2-1
        sc = ["Light","Fusion"]
    elif ws_name == "Victory Smite":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.10, 0.25, 0.45]
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += get_dex_crit(player_dex, enemy_agi)
        ftp = 1.5
        ftp_rep = True
        wsc = 0.8*player_str
        nhits = 4-1
        sc = ["Light","Fragmentation"]
    elif ws_name == "Ascetic's Fury":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100
        crit_boost = [0.20, 0.30, 0.50]
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += get_dex_crit(player_dex, enemy_agi)
        ftp = 1.0
        ftp_rep = True
        wsc = 0.5*(player_str + player_vit)
        nhits = 2-1
        ws_atk_modifier = 1.0
        player_attack1 -= player.stats.get("Food Attack",0)
        player_attack1 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack1 += player.stats.get("Food Attack",0)
        player_attack2 -= player.stats.get("Food Attack",0)
        player_attack2 *= (1+player.stats.get("Attack%",0) + ws_atk_modifier) / (1+player.stats.get("Attack%",0))
        player_attack2 += player.stats.get("Food Attack",0)
        sc = ["Fusion","Transfixion"]
    elif ws_name == "Stringing Pummel":
        crit_ws = True
        crit_rate += player.stats["Crit Rate"]/100 
        crit_boost = [0.15, 0.30, 0.45] # Upper limits. Middle value was made up to force linear scaling
        crit_bonus = np.interp(tp, base_tp, crit_boost)
        crit_rate += crit_bonus
        crit_rate += get_dex_crit(player_dex, enemy_agi)
        ftp = 1.0
        ftp_rep = True
        wsc = 0.32*(player_str + player_vit)
        nhits = 6-1
        sc = ["Gravitation","Liquefaction"]
    elif ws_name == "Maru Kala":
        base_ftp = [1, 2, 3] 
        ftp = np.interp(tp, base_tp, base_ftp)
        ftp_rep = True 
        wsc = 0.0*player_dex 
        nhits = 2
        sc = ["Detonation","Compression","Distortion"]

    if player.gearset["main"]["Name"] == "Shining One" and not (ws_name in ["Flaming Arrow", "Namas Arrow", "Apex Arrow", "Refulgent Arrow","Empyreal Arrow", "Sidewinder", "Piercing Arrow", "Jishnu's Radiance", "Blast Arrow", "Hot Shot", "Coronach","Last Stand","Detonator", "Blast Shot", "Slug Shot", "Split Shot", ]):
    
        # # Shining One allows all weapon skills to crit. Seems pretty OP, but here we are...
        # https://www.bg-wiki.com/ffxi/Shining_One

        if not crit_ws:
            # Add gear and dDEX crit rate if the selected WS did not already do it.
            crit_rate += player.stats['Crit Rate']/100
            crit_rate += get_dex_crit(player.stats['DEX'], enemy_agi)

        crit_boost = [0.05, 0.10, 0.15] # Crit rate bonuses based on TP for wielding Shining One
        crit_bonus = np.interp(tp, [1000,2000,3000], crit_boost)
        crit_rate += crit_bonus


    crit_rate = 1.0 if player.abilities.get("Mighty Strikes", False) else crit_rate

    wsc += sum([ player.stats[k[0]] * k[1]/100 for k in wsc_bonus]) # Add WSC bonuses from things like Utu Grip and Crepuscular Knife, which use the "WSC" stat in their gear entry.

    scaling = {"hybrid":hybrid,
               "magical":magical,
               "dSTAT":dSTAT,
               "wsc":wsc,
               "nhits":nhits,
               "element":element,
               "ftp":ftp,
               "ftp_rep":ftp_rep,
               "player_attack1":player_attack1,
               "player_attack2":player_attack2,
               "player_accuracy1":player_accuracy1,
               "player_accuracy2":player_accuracy2,
               "player_rangedattack":player_rangedattack,
               "player_rangedaccuracy":player_rangedaccuracy,
               "enemy_def":enemy_def,
               "crit_rate":crit_rate,
               "ftp_hybrid":ftp_hybrid,
               }
    return(scaling)
