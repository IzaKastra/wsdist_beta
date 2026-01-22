"""
Optimized simulation kernels for average_attack_round and average_ws.

These use pre-generated random vectors and Numba JIT compilation
for significant performance improvements over the original Python loops.

Author: Optimization of Kastra's original code
"""
import numpy as np
from numba import njit

# =============================================================================
# Modified PDIF functions that accept random values instead of generating them
# =============================================================================

@njit
def get_pdif_melee_jit(player_attack, wpn_type_skill_id, pdl_trait, pdl_gear, enemy_defense, crit_rate, rand_crit, rand_qratio, rand_mult):
    """
    Calculate PDIF for physical melee hits.
    
    wpn_type_skill_id: 0=Katana/Dagger/Sword/Axe/Club, 1=GKT/H2H, 2=GS/Staff/GA/Polearm, 3=Scythe
    rand_crit, rand_qratio, rand_mult: pre-generated uniform(0,1) values
    """
    # Base PDIF cap based on weapon type
    if wpn_type_skill_id == 0:  # Katana, Dagger, Sword, Axe, Club
        pdif_base_cap = 3.25
    elif wpn_type_skill_id == 1:  # Great Katana, Hand-to-Hand
        pdif_base_cap = 3.5
    elif wpn_type_skill_id == 2:  # Great Sword, Staff, Great Axe, Polearm
        pdif_base_cap = 3.75
    else:  # Scythe
        pdif_base_cap = 4.0

    pdif_cap = (pdif_base_cap + pdl_trait) * (1 + pdl_gear)
    
    crit = rand_crit < crit_rate
    
    ratio = player_attack / enemy_defense
    cratio = ratio
    wratio = cratio + 1.0 if crit else cratio

    # Upper qRatio limit
    if wratio < 0.5:
        upper_qlim = wratio + 0.5
    elif wratio < 0.7:
        upper_qlim = 1.0
    elif wratio < 1.2:
        upper_qlim = wratio + 0.3
    elif wratio < 1.5:
        upper_qlim = 1.25 * wratio
    else:
        upper_qlim = wratio + 0.375

    # Lower qRatio limit
    if wratio < 0.38:
        lower_qlim = 0.0
    elif wratio < 1.25:
        lower_qlim = (1176.0 / 1024.0) * wratio - (448.0 / 1024.0)
    elif wratio < 1.51:
        lower_qlim = 1.0
    elif wratio < 2.44:
        lower_qlim = (1176.0 / 1024.0) * wratio - (755.0 / 1024.0)
    else:
        lower_qlim = wratio - 0.375

    qratio = lower_qlim + rand_qratio * (upper_qlim - lower_qlim)

    # Clamp PDIF
    if qratio <= 0:
        pdif = 0.0
    elif qratio >= pdif_cap:
        pdif = pdif_cap
    else:
        pdif = qratio

    if crit:
        pdif += 1.0

    # Random multiplier 1.00-1.05
    pdif *= 1.0 + rand_mult * 0.05

    return pdif, crit


@njit
def get_pdif_ranged_jit(player_ranged_attack, wpn_type_skill_id, pdl_trait, pdl_gear, enemy_defense, crit_rate, rand_crit, rand_qratio):
    """
    Calculate PDIF for ranged hits.
    
    wpn_type_skill_id: 0=Marksmanship, 1=other (Archery, Throwing)
    """
    pdif_base_cap = 3.5 if wpn_type_skill_id == 0 else 3.25
    
    crit = rand_crit < crit_rate
    
    ratio = player_ranged_attack / enemy_defense
    wratio = ratio

    # Upper qRatio limit
    if wratio < 0.9:
        upper_qlim = wratio * (10.0 / 9.0)
    elif wratio < 1.1:
        upper_qlim = 1.0
    else:
        upper_qlim = wratio

    # Lower qRatio limit
    if wratio < 0.9:
        lower_qlim = wratio
    elif wratio < 1.1:
        lower_qlim = 1.0
    else:
        lower_qlim = wratio * (20.0 / 19.0) - (3.0 / 19.0)

    qratio = lower_qlim + rand_qratio * (upper_qlim - lower_qlim)

    pdif_cap = (pdif_base_cap + pdl_trait) * (1 + pdl_gear)
    
    if qratio <= 0:
        pdif = 0.0
    elif qratio >= pdif_cap:
        pdif = pdif_cap
    else:
        pdif = qratio

    if crit:
        pdif *= 1.25

    return pdif, crit


@njit
def get_tp_jit(swings, mdelay, stp, zanshin=False):
    """JIT-compiled TP calculation."""
    if mdelay <= 180.0:
        base_tp = int(61.0 + ((mdelay - 180.0) * 63.0 / 360.0))
    elif mdelay <= 540.0:
        base_tp = int(61.0 + ((mdelay - 180.0) * 88.0 / 360.0))
    elif mdelay <= 630.0:
        base_tp = int(149.0 + ((mdelay - 540.0) * 20.0 / 360.0))
    elif mdelay <= 720.0:
        base_tp = int(154.0 + ((mdelay - 630.0) * 28.0 / 360.0))
    elif mdelay <= 900.0:
        base_tp = int(161.0 + ((mdelay - 720.0) * 24.0 / 360.0))
    else:
        base_tp = int(173.0 + ((mdelay - 900.0) * 28.0 / 360.0))

    if zanshin:
        base_tp += 150  # 30 * 5 merits
    
    return swings * int(base_tp * (1.0 + stp))


@njit
def get_phys_damage_jit(wpn_dmg, fstr_wpn, wsc, pdif, ftp, crit, crit_dmg, wsd, ws_bonus, ws_trait, is_first_hit,
                        sneak_attack_bonus=0.0, trick_attack_bonus=0.0, climactic_flourish_bonus=0.0,
                        striking_flourish_bonus=0.0, ternary_flourish_bonus=0.0):
    """JIT-compiled physical damage calculation."""
    first_hit_mult = 1.0 if is_first_hit else 0.0
    phys = int(((wpn_dmg + fstr_wpn + wsc) * ftp * (1 + wsd * first_hit_mult) * (1 + ws_bonus) * (1 + ws_trait) +
                (sneak_attack_bonus + trick_attack_bonus + climactic_flourish_bonus + 
                 striking_flourish_bonus + ternary_flourish_bonus) * first_hit_mult) * 
               pdif * (1 + crit * min(crit_dmg, 1.0)))
    return phys


# =============================================================================
# Helper to convert weapon skill type string to numeric ID for JIT
# =============================================================================

def get_weapon_skill_id(skill_type):
    """Convert weapon skill type string to numeric ID for JIT functions."""
    if skill_type in ("Katana", "Dagger", "Sword", "Axe", "Club"):
        return 0
    elif skill_type in ("Great Katana", "Hand-to-Hand"):
        return 1
    elif skill_type in ("Great Sword", "Staff", "Great Axe", "Polearm"):
        return 2
    elif skill_type == "Scythe":
        return 3
    else:
        return 0  # Default


def get_ranged_skill_id(skill_type):
    """Convert ranged skill type to numeric ID."""
    return 0 if skill_type == "Marksmanship" else 1


# =============================================================================
# Main simulation kernel for attack rounds
# =============================================================================

@njit
def simulate_attack_round_kernel(
    # Weapon/damage parameters
    main_dmg, sub_dmg, fstr_main, fstr_sub, kick_dmg, fstr_kick, ammo_dmg, fstr_ammo,
    # Attack values
    attack1, attack2, ranged_attack, kick_attack,
    # Skill type IDs (pre-converted)
    main_skill_id, sub_skill_id, ammo_skill_id,
    # PDL
    pdl_trait, pdl_gear,
    # Hit rates
    hit_rate11, hit_rate12, hit_rate21, hit_rate22, hit_rate_ranged, zanshin_hit_rate,
    # Crit
    crit_rate, crit_dmg,
    # Multi-attack rates (all as fractions 0-1)
    qa, ta, da,
    oa3_main, oa2_main,
    oa8_sub, oa7_sub, oa6_sub, oa5_sub, oa4_sub, oa3_sub, oa2_sub,
    # Special attacks
    daken, kickattacks, zanshin, zanhasso, zanshin_oa2,
    # Flags
    dual_wield, is_h2h, is_two_handed,
    # TP calculation
    mdelay, stp, is_sam_main,
    # EnSpell damage (pre-calculated)
    main_enspell_damage, sub_enspell_damage,
    enspell_active,
    # Enemy defense
    enemy_defense,
    # Special weapon flags and multipliers
    relic_proc_rate, relic_damage_mult,  # e.g., 0.13 and 3.0 for Mandau
    prime_proc_rate, prime_damage_mult,
    empyrean_am_rate, empyrean_damage_mult,
    tauret_crit_bonus,  # Extra crit rate from Tauret based on TP
    # DA/TA damage bonuses
    da_dmg, ta_dmg,
    # Dragon Fangs kick bonus
    dragon_fangs_kick_mult,
    # Random vector
    randoms
):
    """
    Simulate a single attack round and return (physical_damage, magical_damage, tp_return).
    
    All random values come from the pre-generated `randoms` array.
    """
    idx = 0  # Index into random vector
    
    physical_damage = 0.0
    magical_damage = 0.0
    tp_return = 0.0
    
    attempted_hits = 0
    main_hit_connects = False
    main_ma_proc = False
    
    # Effective delay for TP calculation
    tp_delay = mdelay / 2.0 if is_h2h else mdelay
    
    # Adjusted crit rate (including Tauret bonus)
    effective_crit_rate = min(1.0, crit_rate + tauret_crit_bonus)
    
    # Pre-check DA/TA procs for first hit damage bonus
    da_proc_main = False
    ta_proc_main = False
    qa_proc_main = randoms[idx] < qa
    idx += 1
    if not qa_proc_main:
        ta_proc_main = randoms[idx] < ta
        idx += 1
        if not ta_proc_main:
            da_proc_main = randoms[idx] < da
            idx += 1
        else:
            idx += 1  # Consume the DA random anyway
    else:
        idx += 2  # Consume TA and DA randoms
    
    da_proc_sub = False
    ta_proc_sub = False
    qa_proc_sub = randoms[idx] < qa
    idx += 1
    if not qa_proc_sub:
        ta_proc_sub = randoms[idx] < ta
        idx += 1
        if not ta_proc_sub:
            da_proc_sub = randoms[idx] < da
            idx += 1
        else:
            idx += 1
    else:
        idx += 2
    
    # ===================
    # Main-hand hit
    # ===================
    attempted_hits += 1
    if randoms[idx] < hit_rate11:
        idx += 1
        main_hit_connects = True
        pdif, crit = get_pdif_melee_jit(attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense, 
                                         effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
        idx += 3
        
        # Special weapon proc checks
        special_mult = 1.0
        if randoms[idx] < relic_proc_rate:
            special_mult *= relic_damage_mult
        idx += 1
        if randoms[idx] < prime_proc_rate:
            special_mult *= prime_damage_mult
        idx += 1
        if randoms[idx] < empyrean_am_rate:
            special_mult *= empyrean_damage_mult
        idx += 1
        
        # DA/TA damage bonus on first hit
        first_hit_bonus = (1.0 + da_dmg * da_proc_main) * (1.0 + ta_dmg * ta_proc_main)
        
        phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, True)
        phys_dmg *= special_mult * first_hit_bonus
        physical_damage += phys_dmg
        
        tp_return += get_tp_jit(1, tp_delay, stp, False)
        
        if enspell_active:
            magical_damage += main_enspell_damage
    else:
        idx += 10  # Consume randoms we would have used
    
    # ===================
    # Off-hand hit
    # ===================
    if dual_wield:
        attempted_hits += 1
        if randoms[idx] < hit_rate21:
            idx += 1
            pdif, crit = get_pdif_melee_jit(attack2, sub_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                             effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
            idx += 3
            
            first_hit_bonus = (1.0 + da_dmg * da_proc_sub) * (1.0 + ta_dmg * ta_proc_sub)
            
            phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, True)
            phys_dmg *= first_hit_bonus
            physical_damage += phys_dmg
            
            tp_return += get_tp_jit(1, tp_delay, stp, False)
            
            if enspell_active:
                magical_damage += sub_enspell_damage
        else:
            idx += 4
    
    # ===================
    # Main-hand multi-attack cascade
    # ===================
    if qa_proc_main:
        main_ma_proc = True
        for _ in range(3):
            if attempted_hits < 8:
                attempted_hits += 1
                if randoms[idx] < hit_rate12:
                    idx += 1
                    pdif, crit = get_pdif_melee_jit(attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                     effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                    idx += 3
                    
                    special_mult = 1.0
                    if randoms[idx] < empyrean_am_rate:
                        special_mult *= empyrean_damage_mult
                    idx += 1
                    
                    phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, False)
                    phys_dmg *= special_mult
                    physical_damage += phys_dmg
                    tp_return += get_tp_jit(1, tp_delay, stp, False)
                    
                    if enspell_active:
                        magical_damage += main_enspell_damage
                else:
                    idx += 5
            else:
                idx += 5
                
    elif ta_proc_main:
        main_ma_proc = True
        for _ in range(2):
            if attempted_hits < 8:
                attempted_hits += 1
                if randoms[idx] < hit_rate12:
                    idx += 1
                    pdif, crit = get_pdif_melee_jit(attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                     effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                    idx += 3
                    
                    special_mult = 1.0
                    if randoms[idx] < empyrean_am_rate:
                        special_mult *= empyrean_damage_mult
                    idx += 1
                    
                    phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, False)
                    phys_dmg *= special_mult * (1.0 + ta_dmg)
                    physical_damage += phys_dmg
                    tp_return += get_tp_jit(1, tp_delay, stp, False)
                    
                    if enspell_active:
                        magical_damage += main_enspell_damage
                else:
                    idx += 5
            else:
                idx += 5
                
    elif da_proc_main:
        main_ma_proc = True
        if attempted_hits < 8:
            attempted_hits += 1
            if randoms[idx] < hit_rate12:
                idx += 1
                pdif, crit = get_pdif_melee_jit(attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                 effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                idx += 3
                
                special_mult = 1.0
                if randoms[idx] < empyrean_am_rate:
                    special_mult *= empyrean_damage_mult
                idx += 1
                
                phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, False)
                phys_dmg *= special_mult * (1.0 + da_dmg)
                physical_damage += phys_dmg
                tp_return += get_tp_jit(1, tp_delay, stp, False)
                
                if enspell_active:
                    magical_damage += main_enspell_damage
            else:
                idx += 5
        else:
            idx += 5
    else:
        # OA3 main check
        if randoms[idx] < oa3_main:
            idx += 1
            main_ma_proc = True
            for _ in range(2):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if randoms[idx] < hit_rate12:
                        idx += 1
                        pdif, crit = get_pdif_melee_jit(attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                         effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                        idx += 3
                        
                        special_mult = 1.0
                        if randoms[idx] < empyrean_am_rate:
                            special_mult *= empyrean_damage_mult
                        idx += 1
                        
                        phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, False)
                        phys_dmg *= special_mult
                        physical_damage += phys_dmg
                        tp_return += get_tp_jit(1, tp_delay, stp, False)
                        
                        if enspell_active:
                            magical_damage += main_enspell_damage
                    else:
                        idx += 5
                else:
                    idx += 5
        else:
            idx += 1
            # OA2 main check
            if randoms[idx] < oa2_main:
                idx += 1
                main_ma_proc = True
                if attempted_hits < 8:
                    attempted_hits += 1
                    if randoms[idx] < hit_rate12:
                        idx += 1
                        pdif, crit = get_pdif_melee_jit(attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                         effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                        idx += 3
                        
                        special_mult = 1.0
                        if randoms[idx] < empyrean_am_rate:
                            special_mult *= empyrean_damage_mult
                        idx += 1
                        
                        phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, False)
                        phys_dmg *= special_mult
                        physical_damage += phys_dmg
                        tp_return += get_tp_jit(1, tp_delay, stp, False)
                        
                        if enspell_active:
                            magical_damage += main_enspell_damage
                    else:
                        idx += 5
                else:
                    idx += 5
            else:
                idx += 1

    # ===================
    # Off-hand multi-attack cascade (if dual wield)
    # ===================
    if dual_wield:
        if qa_proc_sub:
            for _ in range(3):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if randoms[idx] < hit_rate22:
                        idx += 1
                        pdif, crit = get_pdif_melee_jit(attack2, sub_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                         effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                        idx += 3
                        
                        phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, False)
                        physical_damage += phys_dmg
                        tp_return += get_tp_jit(1, tp_delay, stp, False)
                        
                        if enspell_active:
                            magical_damage += sub_enspell_damage
                    else:
                        idx += 4
                else:
                    idx += 4
                    
        elif ta_proc_sub:
            for _ in range(2):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if randoms[idx] < hit_rate22:
                        idx += 1
                        pdif, crit = get_pdif_melee_jit(attack2, sub_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                         effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                        idx += 3
                        
                        phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, False)
                        phys_dmg *= (1.0 + ta_dmg)
                        physical_damage += phys_dmg
                        tp_return += get_tp_jit(1, tp_delay, stp, False)
                        
                        if enspell_active:
                            magical_damage += sub_enspell_damage
                    else:
                        idx += 4
                else:
                    idx += 4
                    
        elif da_proc_sub:
            if attempted_hits < 8:
                attempted_hits += 1
                if randoms[idx] < hit_rate22:
                    idx += 1
                    pdif, crit = get_pdif_melee_jit(attack2, sub_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                     effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                    idx += 3
                    
                    phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, False)
                    phys_dmg *= (1.0 + da_dmg)
                    physical_damage += phys_dmg
                    tp_return += get_tp_jit(1, tp_delay, stp, False)
                    
                    if enspell_active:
                        magical_damage += sub_enspell_damage
                else:
                    idx += 4
            else:
                idx += 4
        else:
            # Off-hand OA8 through OA2 cascade
            oa_sub_rates = (oa8_sub, oa7_sub, oa6_sub, oa5_sub, oa4_sub, oa3_sub, oa2_sub)
            oa_sub_hits = (7, 6, 5, 4, 3, 2, 1)
            
            proc_found = False
            for oa_idx in range(7):
                if not proc_found and randoms[idx] < oa_sub_rates[oa_idx]:
                    idx += 1
                    proc_found = True
                    for _ in range(oa_sub_hits[oa_idx]):
                        if attempted_hits < 8:
                            attempted_hits += 1
                            if randoms[idx] < hit_rate22:
                                idx += 1
                                pdif, crit = get_pdif_melee_jit(attack2, sub_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                                 effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                                idx += 3
                                
                                phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, False)
                                physical_damage += phys_dmg
                                tp_return += get_tp_jit(1, tp_delay, stp, False)
                                
                                if enspell_active:
                                    magical_damage += sub_enspell_damage
                            else:
                                idx += 4
                        else:
                            idx += 4
                elif not proc_found:
                    idx += 1

    # ===================
    # Zanshin (two-handed, no multi-attack, miss or ZanHasso)
    # ===================
    if attempted_hits < 8 and is_two_handed and not dual_wield and not main_ma_proc:
        zanshin_triggers = (not main_hit_connects) or (randoms[idx] < zanhasso)
        idx += 1
        
        if zanshin_triggers:
            # Check Zanshin OA2 first
            if randoms[idx] < zanshin_oa2:
                idx += 1
                for _ in range(2):
                    if attempted_hits < 8:
                        attempted_hits += 1
                        if randoms[idx] < zanshin_hit_rate:
                            idx += 1
                            pdif, crit = get_pdif_melee_jit(attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                             effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                            idx += 3
                            
                            special_mult = 1.0
                            if randoms[idx] < empyrean_am_rate:
                                special_mult *= empyrean_damage_mult
                            idx += 1
                            
                            phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, False)
                            phys_dmg *= special_mult
                            physical_damage += phys_dmg
                            tp_return += get_tp_jit(1, tp_delay, stp, is_sam_main)
                            
                            if enspell_active:
                                magical_damage += main_enspell_damage
                        else:
                            idx += 5
                    else:
                        idx += 5
            else:
                idx += 1
                # Regular Zanshin
                if randoms[idx] < zanshin:
                    idx += 1
                    if attempted_hits < 8:
                        attempted_hits += 1
                        if randoms[idx] < zanshin_hit_rate:
                            idx += 1
                            pdif, crit = get_pdif_melee_jit(attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                             effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                            idx += 3
                            
                            special_mult = 1.0
                            if randoms[idx] < empyrean_am_rate:
                                special_mult *= empyrean_damage_mult
                            idx += 1
                            
                            phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, False)
                            phys_dmg *= special_mult
                            physical_damage += phys_dmg
                            tp_return += get_tp_jit(1, tp_delay, stp, is_sam_main)
                            
                            if enspell_active:
                                magical_damage += main_enspell_damage
                        else:
                            idx += 5
                    else:
                        idx += 5
                else:
                    idx += 1

    # ===================
    # Kick Attacks (MNK)
    # ===================
    if attempted_hits < 8 and kickattacks > 0:
        if randoms[idx] < kickattacks:
            idx += 1
            attempted_hits += 1
            if randoms[idx] < hit_rate12:  # Uses melee hit rate
                idx += 1
                pdif, crit = get_pdif_melee_jit(kick_attack, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                 effective_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                idx += 3
                
                phys_dmg = get_phys_damage_jit(kick_dmg, fstr_kick, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, False)
                phys_dmg *= dragon_fangs_kick_mult
                physical_damage += phys_dmg
                tp_return += get_tp_jit(1, tp_delay, stp, False)
            else:
                idx += 4
        else:
            idx += 1

    # ===================
    # Daken (NIN shuriken throw)
    # ===================
    if attempted_hits < 8 and daken > 0:
        if randoms[idx] < daken:
            idx += 1
            attempted_hits += 1
            if randoms[idx] < hit_rate_ranged:
                idx += 1
                pdif, crit = get_pdif_ranged_jit(ranged_attack, ammo_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                  effective_crit_rate, randoms[idx], randoms[idx+1])
                idx += 2
                
                phys_dmg = get_phys_damage_jit(ammo_dmg, fstr_ammo, 0.0, pdif, 1.0, crit, crit_dmg, 0.0, 0.0, 0.0, False)
                physical_damage += phys_dmg
                tp_return += get_tp_jit(1, tp_delay, stp, False)
            else:
                idx += 3
        else:
            idx += 1

    return physical_damage, magical_damage, tp_return


# =============================================================================
# Wrapper function that extracts parameters and calls the kernel
# =============================================================================

def simulate_attack_round(player, enemy, starting_tp, ws_threshold):
    """
    Wrapper that extracts all needed parameters from player/enemy objects
    and calls the JIT-compiled kernel.
    
    Returns: (physical_damage, tp_return, magical_damage)
    """
    # Pre-generate random vector
    randoms = np.random.uniform(0, 1, 200)
    
    # Extract stats
    dual_wield = (player.gearset["sub"].get("Type", None) == "Weapon") or (player.gearset["main"]["Skill Type"] == "Hand-to-Hand")
    main_skill_type = player.gearset["main"]["Skill Type"]
    sub_skill_type = player.gearset["sub"].get("Skill Type", None) if main_skill_type != "Hand-to-Hand" else "Hand-to-Hand"
    
    # Convert skill types to IDs
    main_skill_id = get_weapon_skill_id(main_skill_type)
    sub_skill_id = get_weapon_skill_id(sub_skill_type) if sub_skill_type else 0
    ammo_skill_type = player.gearset["ammo"].get("Skill Type", "None")
    ammo_skill_id = get_ranged_skill_id(ammo_skill_type)
    
    # Damage values
    main_dmg = player.stats["DMG1"]
    sub_dmg = player.stats["DMG2"]
    kick_dmg = player.stats.get("Kick DMG", 0)
    ammo_dmg = player.stats.get("Ammo DMG", 0)
    
    # fSTR (import from get_fstr)
    from get_fstr import get_fstr, get_fstr2
    fstr_main = get_fstr(main_dmg, player.stats["STR"], enemy.stats["VIT"])
    fstr_sub = get_fstr(sub_dmg, player.stats["STR"], enemy.stats["VIT"])
    fstr_kick = get_fstr(kick_dmg, player.stats["STR"], enemy.stats.get("VIT", 0))
    fstr_ammo = get_fstr2(ammo_dmg, player.stats["STR"], enemy.stats["VIT"])
    
    # Attack values
    attack1 = player.stats["Attack1"]
    attack2 = player.stats["Attack2"]
    if main_skill_type == "Hand-to-Hand":
        attack2 = attack1
    ranged_attack = player.stats.get("Ranged Attack", 0)
    kick_attack = attack1 + player.stats.get("Kick Attacks Attack", 0)
    
    # PDL
    pdl_trait = player.stats.get("PDL Trait", 0) / 100
    pdl_gear = player.stats.get("PDL", 0) / 100
    
    # Hit rates
    from get_hit_rate import get_hit_rate
    enemy_evasion = enemy.stats["Evasion"]
    enemy_defense = enemy.stats["Defense"]
    
    one_handed = ["Axe", "Club", "Dagger", "Sword", "Katana"]
    hit_rate_cap_main = 0.99 if main_skill_type in one_handed or main_skill_type == "Hand-to-Hand" else 0.95
    hit_rate_cap_sub = 0.99 if sub_skill_type == "Hand-to-Hand" else 0.95
    
    accuracy1 = player.stats["Accuracy1"]
    accuracy2 = player.stats["Accuracy2"]
    
    hit_rate11 = get_hit_rate(accuracy1, enemy_evasion, hit_rate_cap_main)
    hit_rate12 = get_hit_rate(accuracy1, enemy_evasion, hit_rate_cap_main)
    hit_rate21 = get_hit_rate(accuracy2, enemy_evasion, hit_rate_cap_sub) if dual_wield else 0.0
    hit_rate22 = get_hit_rate(accuracy2, enemy_evasion, hit_rate_cap_sub) if dual_wield else 0.0
    
    ranged_accuracy = player.stats.get("Ranged Accuracy", 0) + 100 * (player.stats.get("Daken", 0) > 0)
    hit_rate_ranged = get_hit_rate(ranged_accuracy, enemy_evasion, 0.95)
    
    zanshin_hit_rate = get_hit_rate(accuracy1 + 34, enemy_evasion, 0.95)
    
    # Crit
    from get_dex_crit import get_dex_crit
    crit_rate = player.stats.get("Crit Rate", 0) / 100 + get_dex_crit(player.stats["DEX"], enemy.stats["AGI"])
    crit_rate = min(1.0, crit_rate)
    crit_dmg = player.stats.get("Crit Damage", 0) / 100
    
    # Tauret crit bonus
    tauret_crit_bonus = 0.5 * (1 - starting_tp / 3000) if player.gearset["main"]["Name"] == "Tauret" else 0.0
    
    # Multi-attack rates
    qa = min(1.0, player.stats.get("QA", 0) / 100)
    ta = min(1.0, player.stats.get("TA", 0) / 100)
    da = min(1.0, player.stats.get("DA", 0) / 100)
    
    oa3_main = player.stats.get("OA3 main", 0) / 100
    oa2_main = player.stats.get("OA2 main", 0) / 100
    oa8_sub = player.stats.get("OA8 sub", 0) / 100
    oa7_sub = player.stats.get("OA7 sub", 0) / 100
    oa6_sub = player.stats.get("OA6 sub", 0) / 100
    oa5_sub = player.stats.get("OA5 sub", 0) / 100
    oa4_sub = player.stats.get("OA4 sub", 0) / 100
    oa3_sub = player.stats.get("OA3 sub", 0) / 100
    oa2_sub = player.stats.get("OA2 sub", 0) / 100
    
    # Special attacks
    daken = min(1.0, player.stats.get("Daken", 0) / 100)
    kickattacks = min(1.0, player.stats.get("Kick Attacks", 0) / 100)
    zanshin = min(1.0, player.stats.get("Zanshin", 0) / 100)
    zanhasso = player.stats.get("Zanhasso", 0) / 100
    zanshin_oa2 = player.stats.get("Zanshin OA2", 0) / 100
    
    # Flags
    is_h2h = main_skill_type == "Hand-to-Hand"
    two_handed = ["Great Sword", "Great Katana", "Great Axe", "Polearm", "Scythe", "Staff"]
    is_two_handed = main_skill_type in two_handed
    
    # Delay/TP
    base_delay = (player.stats["Delay1"] + player.stats["Delay2"]) / 2
    mdelay = (base_delay - player.stats.get("Martial Arts", 0)) * (1 - player.stats.get("Dual Wield", 0) / 100)
    stp = player.stats.get("Store TP", 0) / 100
    
    # Karambit STP bonus
    if player.gearset["main"]["Name"] == "Karambit":
        stp += 0.5 * crit_rate
    
    is_sam_main = player.main_job.lower() == "sam"
    
    # EnSpell damage
    enspell_active = player.abilities.get("EnSpell", False) or player.abilities.get("Endark II", False) or player.abilities.get("Enlight II", False)
    main_enspell_damage = 0.0
    sub_enspell_damage = 0.0
    if enspell_active:
        # Simplified - you'd want to compute actual enspell damage here
        enhancing_skill = player.abilities.get("Enhancing Skill", 0)
        main_enspell_damage = 3 + enhancing_skill * 0.1  # Placeholder
        sub_enspell_damage = main_enspell_damage * 0.5 if dual_wield else 0.0
    
    # Special weapon procs
    relic_weapons30 = ["Mandau", "Excalibur", "Ragnarok", "Guttler", "Bravura", "Apocalypse", 
                       "Gungnir", "Kikoku", "Amanomurakumo", "Mjollnir", "Claustrum", "Yoichinoyumi"]
    relic_proc_rate = 0.13 if player.gearset["main"]["Name"] in relic_weapons30 else 0.0
    relic_damage_mult = 3.0 if relic_proc_rate > 0 else 1.0
    
    prime_weapons3 = ["Varga Purnikawa V", "Mpu Gandring V", "Caliburnus V", "Helheim V", "Spalirisos V",
                      "Laphria V", "Foenaria V", "Gae Buide V", "Dokoku V", "Kusanagi no Tsurugi V",
                      "Lorg Mor V", "Opashoro V"]
    prime_weapons2 = ["Varga Purnikawa IV", "Mpu Gandring IV", "Caliburnus IV", "Helheim IV", "Spalirisos IV",
                      "Laphria IV", "Foenaria IV", "Gae Buide IV", "Dokoku IV", "Kusanagi no Tsurugi IV",
                      "Lorg Mor IV", "Opashoro IV"]
    main_name2 = player.gearset["main"].get("Name2", "")
    if main_name2 in prime_weapons3:
        prime_proc_rate = 0.3
        prime_damage_mult = 3.0
    elif main_name2 in prime_weapons2:
        prime_proc_rate = 0.3
        prime_damage_mult = 2.0
    else:
        prime_proc_rate = 0.0
        prime_damage_mult = 1.0
    
    # Empyrean aftermath
    empyrean_weapons = ["Twashtar", "Almace", "Caladbolg", "Farsha", "Ukonvasara", "Redemption",
                        "Rhongomiant", "Kannagi", "Masamune", "Gambanteinn", "Hvergelmir", "Gandiva"]
    aftermath = player.abilities.get("Aftermath", 0)
    empyrean_am = [0.3, 0.4, 0.5]  # AM1, AM2, AM3
    if player.gearset["main"]["Name"] in empyrean_weapons and aftermath > 0:
        empyrean_am_rate = empyrean_am[aftermath - 1]
        empyrean_damage_mult = 3.0
    else:
        empyrean_am_rate = 0.0
        empyrean_damage_mult = 1.0
    
    # DA/TA damage bonuses
    da_dmg = player.stats.get("DA Damage%", 0) / 100
    ta_dmg = player.stats.get("TA Damage%", 0) / 100
    
    # Dragon Fangs kick bonus
    dragon_fangs_kick_mult = 1.0
    if player.gearset["main"].get("Name2", "") == "Dragon Fangs":
        dragon_fangs_kick_mult = 1.0 + 1.0 * 0.2  # 20% chance to double
    
    # Call the kernel
    physical_damage, magical_damage, tp_return = simulate_attack_round_kernel(
        main_dmg, sub_dmg, fstr_main, fstr_sub, kick_dmg, fstr_kick, ammo_dmg, fstr_ammo,
        attack1, attack2, ranged_attack, kick_attack,
        main_skill_id, sub_skill_id, ammo_skill_id,
        pdl_trait, pdl_gear,
        hit_rate11, hit_rate12, hit_rate21, hit_rate22, hit_rate_ranged, zanshin_hit_rate,
        crit_rate, crit_dmg,
        qa, ta, da,
        oa3_main, oa2_main,
        oa8_sub, oa7_sub, oa6_sub, oa5_sub, oa4_sub, oa3_sub, oa2_sub,
        daken, kickattacks, zanshin, zanhasso, zanshin_oa2,
        dual_wield, is_h2h, is_two_handed,
        mdelay, stp, is_sam_main,
        main_enspell_damage, sub_enspell_damage, enspell_active,
        enemy_defense,
        relic_proc_rate, relic_damage_mult,
        prime_proc_rate, prime_damage_mult,
        empyrean_am_rate, empyrean_damage_mult,
        tauret_crit_bonus,
        da_dmg, ta_dmg,
        dragon_fangs_kick_mult,
        randoms
    )
    
    return physical_damage, tp_return, magical_damage


# =============================================================================
# Time to WS Monte Carlo simulation
# =============================================================================

def simulate_time_to_ws(player, enemy, starting_tp, ws_threshold, n_rounds=1000):
    """
    Calculate time_to_ws using Monte Carlo simulation.
    
    Runs n_rounds simulations of attack rounds and averages the TP return
    to calculate the expected time to reach WS threshold.
    
    Args:
        player: Player object with stats and gearset
        enemy: Enemy object with stats
        starting_tp: Starting TP value
        ws_threshold: TP threshold for using WS (usually 1000)
        n_rounds: Number of simulation rounds (default 1000)
    
    Returns:
        Tuple matching average_attack_round's simulation=False format:
        (time_to_ws, [damage, tp_per_round, time_per_round, invert], magic_damage)
    """
    from get_fstr import get_fstr, get_fstr2
    from get_hit_rate import get_hit_rate
    from get_dex_crit import get_dex_crit
    from get_delay_timing import get_delay_timing
    
    # ===================
    # Extract parameters once (same as simulate_attack_round)
    # ===================
    
    dual_wield = (player.gearset["sub"].get("Type", None) == "Weapon") or (player.gearset["main"]["Skill Type"] == "Hand-to-Hand")
    main_skill_type = player.gearset["main"]["Skill Type"]
    sub_skill_type = player.gearset["sub"].get("Skill Type", None) if main_skill_type != "Hand-to-Hand" else "Hand-to-Hand"
    
    # Convert skill types to IDs
    main_skill_id = get_weapon_skill_id(main_skill_type)
    sub_skill_id = get_weapon_skill_id(sub_skill_type) if sub_skill_type else 0
    ammo_skill_type = player.gearset["ammo"].get("Skill Type", "None")
    ammo_skill_id = get_ranged_skill_id(ammo_skill_type)
    
    # Damage values
    main_dmg = player.stats["DMG1"]
    sub_dmg = player.stats["DMG2"]
    kick_dmg = player.stats.get("Kick DMG", 0)
    ammo_dmg = player.stats.get("Ammo DMG", 0)
    
    # fSTR
    fstr_main = get_fstr(main_dmg, player.stats["STR"], enemy.stats["VIT"])
    fstr_sub = get_fstr(sub_dmg, player.stats["STR"], enemy.stats["VIT"])
    fstr_kick = get_fstr(kick_dmg, player.stats["STR"], enemy.stats.get("VIT", 0))
    fstr_ammo = get_fstr2(ammo_dmg, player.stats["STR"], enemy.stats["VIT"])
    
    # Attack values
    attack1 = player.stats["Attack1"]
    attack2 = player.stats["Attack2"]
    if main_skill_type == "Hand-to-Hand":
        attack2 = attack1
    ranged_attack = player.stats.get("Ranged Attack", 0)
    kick_attack = attack1 + player.stats.get("Kick Attacks Attack", 0)
    
    # PDL
    pdl_trait = player.stats.get("PDL Trait", 0) / 100
    pdl_gear = player.stats.get("PDL", 0) / 100
    
    # Hit rates
    enemy_evasion = enemy.stats["Evasion"]
    enemy_defense = enemy.stats["Defense"]
    
    one_handed = ["Axe", "Club", "Dagger", "Sword", "Katana"]
    hit_rate_cap_main = 0.99 if main_skill_type in one_handed or main_skill_type == "Hand-to-Hand" else 0.95
    hit_rate_cap_sub = 0.99 if sub_skill_type == "Hand-to-Hand" else 0.95
    
    accuracy1 = player.stats["Accuracy1"]
    accuracy2 = player.stats["Accuracy2"]
    
    hit_rate11 = get_hit_rate(accuracy1, enemy_evasion, hit_rate_cap_main)
    hit_rate12 = get_hit_rate(accuracy1, enemy_evasion, hit_rate_cap_main)
    hit_rate21 = get_hit_rate(accuracy2, enemy_evasion, hit_rate_cap_sub) if dual_wield else 0.0
    hit_rate22 = get_hit_rate(accuracy2, enemy_evasion, hit_rate_cap_sub) if dual_wield else 0.0
    
    ranged_accuracy = player.stats.get("Ranged Accuracy", 0) + 100 * (player.stats.get("Daken", 0) > 0)
    hit_rate_ranged = get_hit_rate(ranged_accuracy, enemy_evasion, 0.95)
    
    zanshin_hit_rate = get_hit_rate(accuracy1 + 34, enemy_evasion, 0.95)
    
    # Crit
    crit_rate = player.stats.get("Crit Rate", 0) / 100 + get_dex_crit(player.stats["DEX"], enemy.stats["AGI"])
    crit_rate = min(1.0, crit_rate)
    crit_dmg = player.stats.get("Crit Damage", 0) / 100
    
    # Tauret crit bonus
    tauret_crit_bonus = 0.5 * (1 - starting_tp / 3000) if player.gearset["main"]["Name"] == "Tauret" else 0.0
    
    # Multi-attack rates
    qa = min(1.0, player.stats.get("QA", 0) / 100)
    ta = min(1.0, player.stats.get("TA", 0) / 100)
    da = min(1.0, player.stats.get("DA", 0) / 100)
    
    oa3_main = player.stats.get("OA3 main", 0) / 100
    oa2_main = player.stats.get("OA2 main", 0) / 100
    oa8_sub = player.stats.get("OA8 sub", 0) / 100
    oa7_sub = player.stats.get("OA7 sub", 0) / 100
    oa6_sub = player.stats.get("OA6 sub", 0) / 100
    oa5_sub = player.stats.get("OA5 sub", 0) / 100
    oa4_sub = player.stats.get("OA4 sub", 0) / 100
    oa3_sub = player.stats.get("OA3 sub", 0) / 100
    oa2_sub = player.stats.get("OA2 sub", 0) / 100
    
    # Special attacks
    daken = min(1.0, player.stats.get("Daken", 0) / 100)
    kickattacks = min(1.0, player.stats.get("Kick Attacks", 0) / 100)
    zanshin = min(1.0, player.stats.get("Zanshin", 0) / 100)
    zanhasso = player.stats.get("Zanhasso", 0) / 100
    zanshin_oa2 = player.stats.get("Zanshin OA2", 0) / 100
    
    # Flags
    is_h2h = main_skill_type == "Hand-to-Hand"
    two_handed = ["Great Sword", "Great Katana", "Great Axe", "Polearm", "Scythe", "Staff"]
    is_two_handed = main_skill_type in two_handed
    
    # Delay/TP
    base_delay = (player.stats["Delay1"] + player.stats["Delay2"]) / 2
    mdelay = (base_delay - player.stats.get("Martial Arts", 0)) * (1 - player.stats.get("Dual Wield", 0) / 100)
    stp = player.stats.get("Store TP", 0) / 100
    
    # Karambit STP bonus
    if player.gearset["main"]["Name"] == "Karambit":
        stp += 0.5 * crit_rate
    
    is_sam_main = player.main_job.lower() == "sam"
    
    # EnSpell damage
    enspell_active = player.abilities.get("EnSpell", False) or player.abilities.get("Endark II", False) or player.abilities.get("Enlight II", False)
    main_enspell_damage = 0.0
    sub_enspell_damage = 0.0
    if enspell_active:
        enhancing_skill = player.abilities.get("Enhancing Skill", 0)
        main_enspell_damage = 3 + enhancing_skill * 0.1  # Placeholder
        sub_enspell_damage = main_enspell_damage * 0.5 if dual_wield else 0.0
    
    # Special weapon procs
    relic_weapons30 = ["Mandau", "Excalibur", "Ragnarok", "Guttler", "Bravura", "Apocalypse", 
                       "Gungnir", "Kikoku", "Amanomurakumo", "Mjollnir", "Claustrum", "Yoichinoyumi"]
    relic_proc_rate = 0.13 if player.gearset["main"]["Name"] in relic_weapons30 else 0.0
    relic_damage_mult = 3.0 if relic_proc_rate > 0 else 1.0
    
    prime_weapons3 = ["Varga Purnikawa V", "Mpu Gandring V", "Caliburnus V", "Helheim V", "Spalirisos V",
                      "Laphria V", "Foenaria V", "Gae Buide V", "Dokoku V", "Kusanagi no Tsurugi V",
                      "Lorg Mor V", "Opashoro V"]
    prime_weapons2 = ["Varga Purnikawa IV", "Mpu Gandring IV", "Caliburnus IV", "Helheim IV", "Spalirisos IV",
                      "Laphria IV", "Foenaria IV", "Gae Buide IV", "Dokoku IV", "Kusanagi no Tsurugi IV",
                      "Lorg Mor IV", "Opashoro IV"]
    main_name2 = player.gearset["main"].get("Name2", "")
    if main_name2 in prime_weapons3:
        prime_proc_rate = 0.3
        prime_damage_mult = 3.0
    elif main_name2 in prime_weapons2:
        prime_proc_rate = 0.3
        prime_damage_mult = 2.0
    else:
        prime_proc_rate = 0.0
        prime_damage_mult = 1.0
    
    # Empyrean aftermath
    empyrean_weapons = ["Twashtar", "Almace", "Caladbolg", "Farsha", "Ukonvasara", "Redemption",
                        "Rhongomiant", "Kannagi", "Masamune", "Gambanteinn", "Hvergelmir", "Gandiva"]
    aftermath = player.abilities.get("Aftermath", 0)
    empyrean_am = [0.3, 0.4, 0.5]  # AM1, AM2, AM3
    if player.gearset["main"]["Name"] in empyrean_weapons and aftermath > 0:
        empyrean_am_rate = empyrean_am[aftermath - 1]
        empyrean_damage_mult = 3.0
    else:
        empyrean_am_rate = 0.0
        empyrean_damage_mult = 1.0
    
    # DA/TA damage bonuses
    da_dmg = player.stats.get("DA Damage%", 0) / 100
    ta_dmg = player.stats.get("TA Damage%", 0) / 100
    
    # Dragon Fangs kick bonus
    dragon_fangs_kick_mult = 1.0
    if player.gearset["main"].get("Name2", "") == "Dragon Fangs":
        dragon_fangs_kick_mult = 1.0 + 1.0 * 0.2  # 20% chance to double
    
    # ===================
    # Calculate time_per_round (deterministic)
    # ===================
    delay2_for_timing = player.stats["Delay2"] if dual_wield and main_skill_type != "Hand-to-Hand" else 0
    time_per_round = get_delay_timing(
        player.stats["Delay1"],
        delay2_for_timing,
        player.stats.get("Dual Wield", 0) / 100,
        player.stats.get("Martial Arts", 0),
        player.stats.get("Magic Haste", 0),
        player.stats.get("JA Haste", 0),
        player.stats.get("Gear Haste", 0),
    )
    time_per_round = max(0, time_per_round)
    
    # ===================
    # Pre-generate random numbers for all rounds
    # ===================
    all_randoms = np.random.uniform(0, 1, (n_rounds, 200))
    
    # ===================
    # Run simulation loop
    # ===================
    tp_returns = np.empty(n_rounds)
    phys_damages = np.empty(n_rounds)
    magic_damages = np.empty(n_rounds)
    
    for i in range(n_rounds):
        phys, magic, tp_ret = simulate_attack_round_kernel(
            main_dmg, sub_dmg, fstr_main, fstr_sub, kick_dmg, fstr_kick, ammo_dmg, fstr_ammo,
            attack1, attack2, ranged_attack, kick_attack,
            main_skill_id, sub_skill_id, ammo_skill_id,
            pdl_trait, pdl_gear,
            hit_rate11, hit_rate12, hit_rate21, hit_rate22, hit_rate_ranged, zanshin_hit_rate,
            crit_rate, crit_dmg,
            qa, ta, da,
            oa3_main, oa2_main,
            oa8_sub, oa7_sub, oa6_sub, oa5_sub, oa4_sub, oa3_sub, oa2_sub,
            daken, kickattacks, zanshin, zanhasso, zanshin_oa2,
            dual_wield, is_h2h, is_two_handed,
            mdelay, stp, is_sam_main,
            main_enspell_damage, sub_enspell_damage, enspell_active,
            enemy_defense,
            relic_proc_rate, relic_damage_mult,
            prime_proc_rate, prime_damage_mult,
            empyrean_am_rate, empyrean_damage_mult,
            tauret_crit_bonus,
            da_dmg, ta_dmg,
            dragon_fangs_kick_mult,
            all_randoms[i]
        )
        tp_returns[i] = tp_ret
        phys_damages[i] = phys
        magic_damages[i] = magic
    
    # ===================
    # Calculate averages
    # ===================
    avg_tp_return = np.mean(tp_returns)
    avg_phys_damage = np.mean(phys_damages)
    avg_magic_damage = np.mean(magic_damages)
    
    # ===================
    # Add regain contribution
    # ===================
    regain = player.stats.get("Regain", 0)
    # Gokotai special case
    regain += player.stats.get("Dual Wield", 0) * (player.gearset["main"]["Name"] == "Gokotai")
    # Regain ticks every 3 seconds
    regain_per_round = (time_per_round / 3) * regain
    avg_tp_return += regain_per_round
    
    # ===================
    # Calculate time to WS
    # ===================
    tp_needed = ws_threshold - starting_tp
    if avg_tp_return > 0:
        attacks_to_ws = tp_needed / avg_tp_return
        time_to_ws = time_per_round * attacks_to_ws
    else:
        time_to_ws = 9999  # Fallback for zero TP return
    
    # ===================
    # Calculate total damage per round
    # ===================
    damage_per_round = avg_phys_damage + avg_magic_damage
    
    # ===================
    # Return in expected format: (metric, [damage, tp_per_round, time_per_round, invert], magic_damage)
    # For "Time to WS", invert = -1 (lower is better)
    # ===================
    return (time_to_ws, [damage_per_round, avg_tp_return, time_per_round, -1], avg_magic_damage)


# =============================================================================
# Weapon Skill simulation kernel
# =============================================================================

@njit
def simulate_ws_melee_kernel(
    # Weapon/damage parameters
    main_dmg, sub_dmg, fstr_main, fstr_sub, wsc,
    # Attack values
    player_attack1, player_attack2,
    # Skill type IDs
    main_skill_id, sub_skill_id,
    # PDL
    pdl_trait, pdl_gear,
    # Hit rates
    hit_rate11, hit_rate12, hit_rate21, hit_rate22,
    # Crit
    crit_rate, crit_dmg,
    first_main_hit_crit_rate, adjusted_crit_dmg,
    # WS modifiers
    ftp, ftp2, wsd, ws_bonus, ws_trait,
    nhits,
    # Multi-attack rates
    qa, ta, da,
    oa3_main, oa2_main,
    oa8_sub, oa7_sub, oa6_sub, oa5_sub, oa4_sub, oa3_sub, oa2_sub,
    # Flags
    dual_wield, is_h2h,
    # TP calculation
    mdelay, stp,
    # Enemy defense
    enemy_defense,
    # SA/TA/Flourish bonuses (pre-calculated flat damage)
    sneak_attack_bonus, trick_attack_bonus,
    climactic_flourish_bonus, striking_flourish_bonus, ternary_flourish_bonus,
    # Random vector
    randoms
):
    """
    Simulate a single melee weapon skill and return (physical_damage, tp_return).
    """
    idx = 0
    
    physical_damage = 0.0
    tp_return = 0.0
    attempted_hits = 0
    
    tp_delay = mdelay / 2.0 if is_h2h else mdelay
    
    # ===================
    # First main-hand hit (with full bonuses)
    # ===================
    attempted_hits += 1
    if randoms[idx] < hit_rate11:
        idx += 1
        pdif, crit = get_pdif_melee_jit(player_attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                         first_main_hit_crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
        idx += 3
        
        phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, wsc, pdif, ftp, crit, adjusted_crit_dmg, 
                                        wsd, ws_bonus, ws_trait, True,
                                        sneak_attack_bonus, trick_attack_bonus,
                                        climactic_flourish_bonus, striking_flourish_bonus, ternary_flourish_bonus)
        physical_damage += phys_dmg
        tp_return += get_tp_jit(1, tp_delay, stp, False)
    else:
        idx += 4
    
    # ===================
    # First off-hand hit
    # ===================
    if dual_wield:
        attempted_hits += 1
        if randoms[idx] < hit_rate21:
            idx += 1
            pdif, crit = get_pdif_melee_jit(player_attack2, sub_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                             crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
            idx += 3
            
            phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg,
                                            0.0, ws_bonus, ws_trait, False)
            physical_damage += phys_dmg
            tp_return += get_tp_jit(1, tp_delay, stp, False)
        else:
            idx += 4
    
    # ===================
    # Additional nhits-1 main-hand hits
    # ===================
    for _ in range(nhits - 1):
        if attempted_hits < 8:
            attempted_hits += 1
            if randoms[idx] < hit_rate12:
                idx += 1
                pdif, crit = get_pdif_melee_jit(player_attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                 crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                idx += 3
                
                phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg,
                                                0.0, ws_bonus, ws_trait, False)
                physical_damage += phys_dmg
                tp_return += 10.0 * (1.0 + stp)
            else:
                idx += 4
        else:
            idx += 4
    
    # ===================
    # Main-hand multi-attack checks
    # Number of MA checks: 2 if (not dual_wield and nhits > 1) else 1
    # ===================
    main_hand_ma_checks = 2 if (not dual_wield) and (nhits > 1) else 1
    
    for _ in range(main_hand_ma_checks):
        if attempted_hits >= 8:
            idx += 20  # Skip all the random consumption for this check
            continue
            
        # QA check
        if randoms[idx] < qa:
            idx += 1
            for _ in range(3):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if randoms[idx] < hit_rate12:
                        idx += 1
                        pdif, crit = get_pdif_melee_jit(player_attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                         crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                        idx += 3
                        
                        phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg,
                                                        0.0, ws_bonus, ws_trait, False)
                        physical_damage += phys_dmg
                        tp_return += 10.0 * (1.0 + stp)
                    else:
                        idx += 4
                else:
                    idx += 4
        else:
            idx += 1
            # TA check
            if randoms[idx] < ta:
                idx += 1
                for _ in range(2):
                    if attempted_hits < 8:
                        attempted_hits += 1
                        if randoms[idx] < hit_rate12:
                            idx += 1
                            pdif, crit = get_pdif_melee_jit(player_attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                             crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                            idx += 3
                            
                            phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg,
                                                            0.0, ws_bonus, ws_trait, False)
                            physical_damage += phys_dmg
                            tp_return += 10.0 * (1.0 + stp)
                        else:
                            idx += 4
                    else:
                        idx += 4
            else:
                idx += 1
                # DA check
                if randoms[idx] < da:
                    idx += 1
                    if attempted_hits < 8:
                        attempted_hits += 1
                        if randoms[idx] < hit_rate12:
                            idx += 1
                            pdif, crit = get_pdif_melee_jit(player_attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                             crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                            idx += 3
                            
                            phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg,
                                                            0.0, ws_bonus, ws_trait, False)
                            physical_damage += phys_dmg
                            tp_return += 10.0 * (1.0 + stp)
                        else:
                            idx += 4
                    else:
                        idx += 4
                else:
                    idx += 1
                    # OA3 main
                    if randoms[idx] < oa3_main:
                        idx += 1
                        for _ in range(2):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if randoms[idx] < hit_rate12:
                                    idx += 1
                                    pdif, crit = get_pdif_melee_jit(player_attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                                     crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                                    idx += 3
                                    
                                    phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg,
                                                                    0.0, ws_bonus, ws_trait, False)
                                    physical_damage += phys_dmg
                                    tp_return += 10.0 * (1.0 + stp)
                                else:
                                    idx += 4
                            else:
                                idx += 4
                    else:
                        idx += 1
                        # OA2 main
                        if randoms[idx] < oa2_main:
                            idx += 1
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if randoms[idx] < hit_rate12:
                                    idx += 1
                                    pdif, crit = get_pdif_melee_jit(player_attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                                     crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                                    idx += 3
                                    
                                    phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg,
                                                                    0.0, ws_bonus, ws_trait, False)
                                    physical_damage += phys_dmg
                                    tp_return += 10.0 * (1.0 + stp)
                                else:
                                    idx += 4
                            else:
                                idx += 4
                        else:
                            idx += 1
    
    # ===================
    # Off-hand multi-attack (if dual wield)
    # ===================
    if dual_wield:
        # QA check
        if randoms[idx] < qa:
            idx += 1
            for _ in range(3):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if randoms[idx] < hit_rate22:
                        idx += 1
                        pdif, crit = get_pdif_melee_jit(player_attack2, sub_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                         crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                        idx += 3
                        
                        phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg,
                                                        0.0, ws_bonus, ws_trait, False)
                        physical_damage += phys_dmg
                        tp_return += 10.0 * (1.0 + stp)
                    else:
                        idx += 4
                else:
                    idx += 4
        else:
            idx += 1
            # TA check
            if randoms[idx] < ta:
                idx += 1
                for _ in range(2):
                    if attempted_hits < 8:
                        attempted_hits += 1
                        if randoms[idx] < hit_rate22:
                            idx += 1
                            pdif, crit = get_pdif_melee_jit(player_attack2, sub_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                             crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                            idx += 3
                            
                            phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg,
                                                            0.0, ws_bonus, ws_trait, False)
                            physical_damage += phys_dmg
                            tp_return += 10.0 * (1.0 + stp)
                        else:
                            idx += 4
                    else:
                        idx += 4
            else:
                idx += 1
                # DA check
                if randoms[idx] < da:
                    idx += 1
                    if attempted_hits < 8:
                        attempted_hits += 1
                        if randoms[idx] < hit_rate22:
                            idx += 1
                            pdif, crit = get_pdif_melee_jit(player_attack2, sub_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                             crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                            idx += 3
                            
                            phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg,
                                                            0.0, ws_bonus, ws_trait, False)
                            physical_damage += phys_dmg
                            tp_return += 10.0 * (1.0 + stp)
                        else:
                            idx += 4
                    else:
                        idx += 4
                else:
                    idx += 1
                    # Off-hand OA8 through OA2 cascade
                    oa_sub_rates = (oa8_sub, oa7_sub, oa6_sub, oa5_sub, oa4_sub, oa3_sub, oa2_sub)
                    oa_sub_hits = (7, 6, 5, 4, 3, 2, 1)
                    
                    proc_found = False
                    for oa_idx in range(7):
                        if not proc_found and randoms[idx] < oa_sub_rates[oa_idx]:
                            idx += 1
                            proc_found = True
                            for _ in range(oa_sub_hits[oa_idx]):
                                if attempted_hits < 8:
                                    attempted_hits += 1
                                    if randoms[idx] < hit_rate22:
                                        idx += 1
                                        pdif, crit = get_pdif_melee_jit(player_attack2, sub_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                                         crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                                        idx += 3
                                        
                                        phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg,
                                                                        0.0, ws_bonus, ws_trait, False)
                                        physical_damage += phys_dmg
                                        tp_return += 10.0 * (1.0 + stp)
                                    else:
                                        idx += 4
                                else:
                                    idx += 4
                        elif not proc_found:
                            idx += 1
    
    return physical_damage, tp_return


def simulate_ws(player, enemy, ws_name, input_tp, ws_type):
    """
    Wrapper that extracts parameters and calls the JIT-compiled WS kernel.
    
    Returns: (total_damage, tp_return)
    
    Note: This only handles the physical portion for melee WS.
    Hybrid/magical portions should be calculated separately and added.
    """
    # Pre-generate random vector
    randoms = np.random.uniform(0, 1, 200)
    
    # Import required functions
    from get_fstr import get_fstr
    from get_hit_rate import get_hit_rate
    from get_dex_crit import get_dex_crit
    from weaponskill_info import weaponskill_info
    from weapon_bonus import get_weapon_bonus
    
    # Basic setup
    tp_bonus = player.stats.get("TP Bonus", 0)
    tp = max(1000, min(3000, input_tp + tp_bonus))
    
    dual_wield = (player.gearset["sub"].get("Type", None) == "Weapon") or (player.gearset["main"]["Skill Type"] == "Hand-to-Hand")
    
    # Get WS info
    ws_info = weaponskill_info(ws_name, tp, player, enemy, player.stats.get("WSC", []), dual_wield)
    
    nhits = ws_info["nhits"]
    wsc = ws_info["wsc"]
    ftp = ws_info["ftp"] + player.stats.get("ftp", 0)
    ftp_rep = ws_info["ftp_rep"]
    crit_rate = min(1.0, ws_info["crit_rate"])
    enemy_defense = ws_info["enemy_def"]
    
    ftp2 = ftp if ftp_rep else 1.0
    
    # Skill types
    main_skill_type = player.gearset["main"]["Skill Type"]
    sub_skill_type = player.gearset["sub"].get("Skill Type", None) if main_skill_type != "Hand-to-Hand" else "Hand-to-Hand"
    main_skill_id = get_weapon_skill_id(main_skill_type)
    sub_skill_id = get_weapon_skill_id(sub_skill_type) if sub_skill_type else 0
    
    # Damage values
    main_dmg = player.stats["DMG1"]
    sub_dmg = player.stats["DMG2"]
    
    fstr_main = get_fstr(main_dmg, player.stats["STR"], enemy.stats["VIT"])
    fstr_sub = get_fstr(sub_dmg, player.stats["STR"], enemy.stats["VIT"])
    
    # Attack
    player_attack1 = player.stats["Attack1"]
    player_attack2 = player.stats["Attack2"]
    if main_skill_type == "Hand-to-Hand":
        player_attack2 = player_attack1
    
    # PDL
    pdl_trait = player.stats.get("PDL Trait", 0) / 100
    pdl_gear = player.stats.get("PDL", 0) / 100
    
    # Hit rates
    enemy_evasion = enemy.stats["Evasion"]
    one_handed = ["Axe", "Club", "Dagger", "Sword", "Katana"]
    hit_rate_cap_main = 0.99 if main_skill_type in one_handed or main_skill_type == "Hand-to-Hand" else 0.95
    hit_rate_cap_sub = 0.99 if sub_skill_type == "Hand-to-Hand" else 0.95
    
    accuracy1 = player.stats["Accuracy1"]
    accuracy2 = player.stats["Accuracy2"]
    
    hit_rate11 = get_hit_rate(accuracy1 + 100, enemy_evasion, hit_rate_cap_main)  # +100 for first WS hit
    hit_rate12 = get_hit_rate(accuracy1, enemy_evasion, hit_rate_cap_main)
    hit_rate21 = get_hit_rate(accuracy2 + 100, enemy_evasion, hit_rate_cap_sub) if dual_wield else 0.0
    hit_rate22 = get_hit_rate(accuracy2, enemy_evasion, hit_rate_cap_sub) if dual_wield else 0.0
    
    # Crit
    crit_dmg = player.stats.get("Crit Damage", 0) / 100
    
    # First hit special crit handling (SA/TA/Flourishes)
    # For normal simulation, these are disabled
    sneak_attack = False
    trick_attack = False
    climactic_flourish = False
    striking_flourish = False
    ternary_flourish = False
    
    first_main_hit_crit_rate = crit_rate
    adjusted_crit_dmg = crit_dmg
    
    sneak_attack_bonus = 0.0
    trick_attack_bonus = 0.0
    climactic_flourish_bonus = 0.0
    striking_flourish_bonus = 0.0
    ternary_flourish_bonus = 0.0
    
    # WS modifiers
    wsd = player.stats.get("Weapon Skill Damage", 0) / 100
    ws_trait = player.stats.get("Weapon Skill Damage Trait", 0) / 100
    ws_bonus = get_weapon_bonus(player.gearset["main"]["Name2"], player.gearset["ranged"]["Name2"], ws_name)
    
    # Multi-attack rates
    qa = min(1.0, player.stats.get("QA", 0) / 100)
    ta = min(1.0, player.stats.get("TA", 0) / 100)
    da = min(1.0, player.stats.get("DA", 0) / 100)
    
    oa3_main = player.stats.get("OA3 main", 0) / 100
    oa2_main = player.stats.get("OA2 main", 0) / 100
    oa8_sub = player.stats.get("OA8 sub", 0) / 100
    oa7_sub = player.stats.get("OA7 sub", 0) / 100
    oa6_sub = player.stats.get("OA6 sub", 0) / 100
    oa5_sub = player.stats.get("OA5 sub", 0) / 100
    oa4_sub = player.stats.get("OA4 sub", 0) / 100
    oa3_sub = player.stats.get("OA3 sub", 0) / 100
    oa2_sub = player.stats.get("OA2 sub", 0) / 100
    
    # Delay/TP
    is_h2h = main_skill_type == "Hand-to-Hand"
    base_delay = (player.stats["Delay1"] + player.stats["Delay2"]) / 2
    mdelay = (base_delay - player.stats.get("Martial Arts", 0)) * (1 - player.stats.get("Dual Wield", 0) / 100)
    stp = player.stats.get("Store TP", 0) / 100
    
    # Call the kernel
    physical_damage, tp_return = simulate_ws_melee_kernel(
        main_dmg, sub_dmg, fstr_main, fstr_sub, wsc,
        player_attack1, player_attack2,
        main_skill_id, sub_skill_id,
        pdl_trait, pdl_gear,
        hit_rate11, hit_rate12, hit_rate21, hit_rate22,
        crit_rate, crit_dmg,
        first_main_hit_crit_rate, adjusted_crit_dmg,
        ftp, ftp2, wsd, ws_bonus, ws_trait,
        nhits,
        qa, ta, da,
        oa3_main, oa2_main,
        oa8_sub, oa7_sub, oa6_sub, oa5_sub, oa4_sub, oa3_sub, oa2_sub,
        dual_wield, is_h2h,
        mdelay, stp,
        enemy_defense,
        sneak_attack_bonus, trick_attack_bonus,
        climactic_flourish_bonus, striking_flourish_bonus, ternary_flourish_bonus,
        randoms
    )
    
    # Note: Hybrid/magical damage would need to be added here
    # For now, just return physical
    return physical_damage, tp_return


if __name__ == "__main__":
    # Quick compilation test
    print("Compiling JIT functions...")
    randoms = np.random.uniform(0, 1, 200)
    
    # Test pdif
    pdif, crit = get_pdif_melee_jit(1500, 0, 0.25, 0.1, 1300, 0.1, 0.5, 0.5, 0.5)
    print(f"PDIF test: {pdif:.3f}, crit: {crit}")
    
    # Test TP
    tp = get_tp_jit(1, 480, 0.3, False)
    print(f"TP test: {tp}")
    
    # Test attack round kernel with dummy values
    print("Testing attack round kernel...")
    phys, magic, tp_ret = simulate_attack_round_kernel(
        # Weapon/damage
        150.0, 140.0, 20.0, 18.0, 0.0, 0.0, 0.0, 0.0,
        # Attack
        1500, 1400, 0, 1500,
        # Skill IDs
        0, 0, 1,
        # PDL
        0.25, 0.1,
        # Hit rates
        0.95, 0.92, 0.90, 0.88, 0.0, 0.95,
        # Crit
        0.15, 0.25,
        # Multi-attack
        0.05, 0.15, 0.30,
        0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        # Special attacks
        0.0, 0.0, 0.0, 0.0, 0.0,
        # Flags
        True, False, False,
        # TP
        320.0, 0.30, False,
        # EnSpell
        0.0, 0.0, False,
        # Enemy defense
        1300,
        # Special weapons
        0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0,
        # DA/TA dmg
        0.0, 0.0,
        # Dragon Fangs
        1.0,
        # Randoms
        randoms
    )
    print(f"Attack round: phys={phys:.0f}, magic={magic:.0f}, tp={tp_ret:.1f}")
    
    # Test WS kernel
    print("Testing WS kernel...")
    phys, tp_ret = simulate_ws_melee_kernel(
        # Weapon/damage
        150.0, 140.0, 20.0, 18.0, 200.0,
        # Attack
        1500, 1400,
        # Skill IDs
        0, 0,
        # PDL
        0.25, 0.1,
        # Hit rates
        0.99, 0.95, 0.95, 0.92,
        # Crit
        0.15, 0.25, 0.15, 0.25,
        # WS modifiers
        2.0, 1.0, 0.12, 0.0, 0.0,
        5,  # nhits
        # Multi-attack
        0.05, 0.15, 0.30,
        0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        # Flags
        True, False,
        # TP
        320.0, 0.30,
        # Enemy defense
        1300,
        # SA/TA/Flourish
        0.0, 0.0, 0.0, 0.0, 0.0,
        # Randoms
        randoms
    )
    print(f"WS: phys={phys:.0f}, tp={tp_ret:.1f}")
    
    print("\nCompilation successful!")
