"""
Optimized simulation kernel for average_attack_round.

This kernel receives ALL pre-computed values from the original average_attack_round
function and just performs the fast simulation loop. This ensures:
1. No duplicated game logic
2. Original code remains the source of truth
3. Kernel is just a fast number cruncher

Author: Optimization of Kastra's original code
"""
import numpy as np
from numba import njit


# =============================================================================
# JIT-compiled helper functions
# =============================================================================

@njit(cache=True)
def get_pdif_melee_jit(player_attack, skill_type_id, pdl_trait, pdl_gear, enemy_defense, crit_rate,
                       rand_crit, rand_qratio, rand_mult):
    """
    Calculate PDIF for melee hits.
    
    skill_type_id mapping:
        0 = Katana, Dagger, Sword, Axe, Club (cap 3.25)
        1 = Great Katana, Hand-to-Hand (cap 3.5)
        2 = Great Sword, Staff, Great Axe, Polearm (cap 3.75)
        3 = Scythe (cap 4.0)
    """
    if skill_type_id == 0:
        pdif_base_cap = 3.25
    elif skill_type_id == 1:
        pdif_base_cap = 3.5
    elif skill_type_id == 2:
        pdif_base_cap = 3.75
    else:
        pdif_base_cap = 4.0

    pdif_cap = (pdif_base_cap + pdl_trait) * (1 + pdl_gear)
    
    crit = rand_crit < crit_rate
    
    ratio = player_attack / enemy_defense
    wratio = ratio + 1.0 if crit else ratio

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


@njit(cache=True)
def get_pdif_ranged_jit(player_ranged_attack, skill_type_id, pdl_trait, pdl_gear, enemy_defense, crit_rate,
                        rand_crit, rand_qratio):
    """
    Calculate PDIF for ranged hits.
    
    skill_type_id: 0 = Marksmanship (cap 3.5), 1 = other (cap 3.25)
    """
    pdif_base_cap = 3.5 if skill_type_id == 0 else 3.25
    
    crit = rand_crit < crit_rate
    
    ratio = player_ranged_attack / enemy_defense
    wratio = ratio

    if wratio < 0.9:
        upper_qlim = wratio * (10.0 / 9.0)
    elif wratio < 1.1:
        upper_qlim = 1.0
    else:
        upper_qlim = wratio

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


@njit(cache=True)
def get_tp_jit(mdelay, stp, zanshin_bonus=False):
    """Calculate TP for a single hit."""
    if mdelay <= 180.0:
        base_tp = 61.0 + ((mdelay - 180.0) * 63.0 / 360.0)
    elif mdelay <= 540.0:
        base_tp = 61.0 + ((mdelay - 180.0) * 88.0 / 360.0)
    elif mdelay <= 630.0:
        base_tp = 149.0 + ((mdelay - 540.0) * 20.0 / 360.0)
    elif mdelay <= 720.0:
        base_tp = 154.0 + ((mdelay - 630.0) * 28.0 / 360.0)
    elif mdelay <= 900.0:
        base_tp = 161.0 + ((mdelay - 720.0) * 24.0 / 360.0)
    else:
        base_tp = 173.0 + ((mdelay - 900.0) * 28.0 / 360.0)

    if zanshin_bonus:
        base_tp += 150.0  # 30 * 5 merits (Ikishoten)
    
    return int(base_tp * (1.0 + stp))


@njit(cache=True)
def get_phys_damage_jit(wpn_dmg, fstr_wpn, pdif, crit, crit_dmg):
    """Calculate physical damage for auto-attacks (no WSC, ftp=1, no WSD)."""
    base = int((wpn_dmg + fstr_wpn) * pdif)
    if crit:
        base = int(base * (1 + min(crit_dmg, 1.0)))
    return base


# =============================================================================
# Main simulation kernel
# =============================================================================

@njit(cache=True)
def simulate_attack_round_kernel(
    # Damage values
    main_dmg, sub_dmg, kick_dmg, ammo_dmg,
    fstr_main, fstr_sub, fstr_kick, fstr_ammo,
    
    # Attack values
    attack1, attack2, ranged_attack, zanshin_attack,
    
    # Skill type IDs (pre-converted to int)
    main_skill_id, sub_skill_id, ammo_skill_id,
    
    # PDL
    pdl_trait, pdl_gear,
    
    # Hit rates (all pre-computed)
    hit_rate11, hit_rate12, hit_rate21, hit_rate22,
    hit_rate_ranged, zanshin_hit_rate,
    
    # Crit (already adjusted for Tauret)
    crit_rate, crit_dmg,
    
    # Multi-attack rates (all as fractions 0-1)
    qa, ta, da,
    oa8_main, oa7_main, oa6_main, oa5_main, oa4_main, oa3_main, oa2_main,
    oa8_sub, oa7_sub, oa6_sub, oa5_sub, oa4_sub, oa3_sub, oa2_sub,
    
    # Special attacks
    kickattacks, daken, zanshin, zanhasso, zanshin_oa2,
    
    # TP calculation (stp already adjusted for Karambit)
    mdelay, ammo_delay, stp,
    
    # EnSpell damage (fully pre-calculated with all bonuses)
    main_enspell_damage, sub_enspell_damage, enspell_active,
    
    # Enemy defense
    enemy_defense,
    
    # DA/TA damage bonuses
    da_dmg, ta_dmg,
    
    # Weapon special procs - pre-computed rates and bonus multipliers
    # Relic: rate is 0.13/0.16/0.20, bonus is 2.0/1.5/1.0 (for 3x/2.5x/2x damage)
    relic_proc_rate, relic_bonus_mult,
    # Prime: rate is 0.3, bonus is 2.0/1.0 (for 3x/2x damage)
    prime_proc_rate, prime_bonus_mult,
    # Empyrean: rate is 0.3/0.4/0.5 based on AM level, bonus is always 2.0 (3x damage)
    empyrean_proc_rate, empyrean_bonus_mult,
    
    # Dragon Fangs kick bonus
    dragon_fangs_proc_rate,
    
    # Flags
    dual_wield, is_h2h, is_two_handed,
    is_sam_main,  # For zanshin TP bonus
    
    # Pre-generated random values
    randoms
):
    """
    Simulate a single attack round and return (physical_damage, tp_return, magical_damage).
    
    All game logic for computing the input values is done in the original Python code.
    This kernel just performs the fast simulation using those pre-computed values.
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
    
    # ===================
    # Pre-roll DA/TA procs for first hit damage bonus
    # ===================
    qa_proc_main = randoms[idx] < qa
    idx += 1
    ta_proc_main = (randoms[idx] < ta) and (not qa_proc_main)
    idx += 1
    da_proc_main = (randoms[idx] < da) and (not qa_proc_main) and (not ta_proc_main)
    idx += 1
    
    qa_proc_sub = randoms[idx] < qa
    idx += 1
    ta_proc_sub = (randoms[idx] < ta) and (not qa_proc_sub)
    idx += 1
    da_proc_sub = (randoms[idx] < da) and (not qa_proc_sub) and (not ta_proc_sub)
    idx += 1
    
    # ===================
    # Main-hand first hit
    # ===================
    attempted_hits += 1
    if randoms[idx] < hit_rate11:
        idx += 1
        main_hit_connects = True
        
        pdif, crit = get_pdif_melee_jit(attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                         crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
        idx += 3
        
        phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, pdif, crit, crit_dmg)
        
        # Weapon special procs (each checked independently)
        if randoms[idx] < relic_proc_rate:
            phys_dmg = int(phys_dmg * (1.0 + relic_bonus_mult))
        idx += 1
        
        if randoms[idx] < prime_proc_rate:
            phys_dmg = int(phys_dmg * (1.0 + prime_bonus_mult))
        idx += 1
        
        if randoms[idx] < empyrean_proc_rate:
            phys_dmg = int(phys_dmg * (1.0 + empyrean_bonus_mult))
        idx += 1
        
        # DA/TA damage bonus on first hit
        phys_dmg = int(phys_dmg * (1.0 + da_dmg * da_proc_main) * (1.0 + ta_dmg * ta_proc_main))
        
        physical_damage += phys_dmg
        tp_return += get_tp_jit(tp_delay, stp, False)
        
        if enspell_active:
            magical_damage += main_enspell_damage
    else:
        idx += 7  # Skip randoms we would have used
    
    # ===================
    # Off-hand first hit
    # ===================
    if dual_wield:
        attempted_hits += 1
        if randoms[idx] < hit_rate21:
            idx += 1
            
            pdif, crit = get_pdif_melee_jit(attack2, sub_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                             crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
            idx += 3
            
            phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, pdif, crit, crit_dmg)
            
            # DA/TA damage bonus on first hit
            phys_dmg = int(phys_dmg * (1.0 + da_dmg * da_proc_sub) * (1.0 + ta_dmg * ta_proc_sub))
            
            physical_damage += phys_dmg
            tp_return += get_tp_jit(tp_delay, stp, False)
            
            if enspell_active:
                magical_damage += sub_enspell_damage
        else:
            idx += 4
    
    # ===================
    # Main-hand multi-attack cascade: QA > TA > DA > OA8 > OA7 > OA6 > OA5 > OA4 > OA3 > OA2
    # ===================
    if qa_proc_main:
        main_ma_proc = True
        for _ in range(3):  # QA = 3 extra hits
            if attempted_hits < 8:
                attempted_hits += 1
                if randoms[idx] < hit_rate12:
                    idx += 1
                    pdif, crit = get_pdif_melee_jit(attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                     crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                    idx += 3
                    
                    phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, pdif, crit, crit_dmg)
                    
                    # Empyrean AM proc on multi-attacks
                    if randoms[idx] < empyrean_proc_rate:
                        phys_dmg = int(phys_dmg * (1.0 + empyrean_bonus_mult))
                    idx += 1
                    
                    physical_damage += phys_dmg
                    tp_return += get_tp_jit(tp_delay, stp, False)
                    
                    if enspell_active:
                        magical_damage += main_enspell_damage
                else:
                    idx += 5
            else:
                idx += 5
                
    elif ta_proc_main:
        main_ma_proc = True
        for _ in range(2):  # TA = 2 extra hits
            if attempted_hits < 8:
                attempted_hits += 1
                if randoms[idx] < hit_rate12:
                    idx += 1
                    pdif, crit = get_pdif_melee_jit(attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                     crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                    idx += 3
                    
                    phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, pdif, crit, crit_dmg)
                    
                    if randoms[idx] < empyrean_proc_rate:
                        phys_dmg = int(phys_dmg * (1.0 + empyrean_bonus_mult))
                    idx += 1
                    
                    # TA damage bonus applies to all TA hits
                    phys_dmg = int(phys_dmg * (1.0 + ta_dmg))
                    
                    physical_damage += phys_dmg
                    tp_return += get_tp_jit(tp_delay, stp, False)
                    
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
                                                 crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                idx += 3
                
                phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, pdif, crit, crit_dmg)
                
                if randoms[idx] < empyrean_proc_rate:
                    phys_dmg = int(phys_dmg * (1.0 + empyrean_bonus_mult))
                idx += 1
                
                # DA damage bonus
                phys_dmg = int(phys_dmg * (1.0 + da_dmg))
                
                physical_damage += phys_dmg
                tp_return += get_tp_jit(tp_delay, stp, False)
                
                if enspell_active:
                    magical_damage += main_enspell_damage
            else:
                idx += 5
        else:
            idx += 5
    else:
        # Check OA8 through OA2 for main hand
        oa_main_rates = (oa8_main, oa7_main, oa6_main, oa5_main, oa4_main, oa3_main, oa2_main)
        oa_main_hits = (7, 6, 5, 4, 3, 2, 1)
        
        proc_found = False
        for oa_idx in range(7):
            if not proc_found and randoms[idx] < oa_main_rates[oa_idx]:
                idx += 1
                proc_found = True
                main_ma_proc = True
                for _ in range(oa_main_hits[oa_idx]):
                    if attempted_hits < 8:
                        attempted_hits += 1
                        if randoms[idx] < hit_rate12:
                            idx += 1
                            pdif, crit = get_pdif_melee_jit(attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                             crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                            idx += 3
                            
                            phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, pdif, crit, crit_dmg)
                            
                            if randoms[idx] < empyrean_proc_rate:
                                phys_dmg = int(phys_dmg * (1.0 + empyrean_bonus_mult))
                            idx += 1
                            
                            physical_damage += phys_dmg
                            tp_return += get_tp_jit(tp_delay, stp, False)
                            
                            if enspell_active:
                                magical_damage += main_enspell_damage
                        else:
                            idx += 5
                    else:
                        idx += 5
            elif not proc_found:
                idx += 1

    # ===================
    # Off-hand multi-attack cascade
    # ===================
    if dual_wield:
        if qa_proc_sub:
            for _ in range(3):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if randoms[idx] < hit_rate22:
                        idx += 1
                        pdif, crit = get_pdif_melee_jit(attack2, sub_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                         crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                        idx += 3
                        
                        phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, pdif, crit, crit_dmg)
                        physical_damage += phys_dmg
                        tp_return += get_tp_jit(tp_delay, stp, False)
                        
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
                                                         crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                        idx += 3
                        
                        phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, pdif, crit, crit_dmg)
                        phys_dmg = int(phys_dmg * (1.0 + ta_dmg))
                        physical_damage += phys_dmg
                        tp_return += get_tp_jit(tp_delay, stp, False)
                        
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
                                                     crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                    idx += 3
                    
                    phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, pdif, crit, crit_dmg)
                    phys_dmg = int(phys_dmg * (1.0 + da_dmg))
                    physical_damage += phys_dmg
                    tp_return += get_tp_jit(tp_delay, stp, False)
                    
                    if enspell_active:
                        magical_damage += sub_enspell_damage
                else:
                    idx += 4
            else:
                idx += 4
        else:
            # Check OA8 through OA2 for off-hand
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
                                                                 crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                                idx += 3
                                
                                phys_dmg = get_phys_damage_jit(sub_dmg, fstr_sub, pdif, crit, crit_dmg)
                                physical_damage += phys_dmg
                                tp_return += get_tp_jit(tp_delay, stp, False)
                                
                                if enspell_active:
                                    magical_damage += sub_enspell_damage
                            else:
                                idx += 4
                        else:
                            idx += 4
                elif not proc_found:
                    idx += 1

    # ===================
    # Zanshin (two-handed weapons only, no multi-attack, miss or ZanHasso)
    # ===================
    if is_two_handed and (not dual_wield) and (not main_ma_proc):
        zanshin_triggers = (not main_hit_connects) or (randoms[idx] < zanhasso)
        idx += 1
        
        if zanshin_triggers and attempted_hits < 8:
            # Check Zanshin OA2 first
            if randoms[idx] < zanshin_oa2:
                idx += 1
                for _ in range(2):
                    if attempted_hits < 8:
                        attempted_hits += 1
                        if randoms[idx] < zanshin_hit_rate:
                            idx += 1
                            pdif, crit = get_pdif_melee_jit(zanshin_attack, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                             crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                            idx += 3
                            
                            phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, pdif, crit, crit_dmg)
                            
                            if randoms[idx] < empyrean_proc_rate:
                                phys_dmg = int(phys_dmg * (1.0 + empyrean_bonus_mult))
                            idx += 1
                            
                            physical_damage += phys_dmg
                            tp_return += get_tp_jit(tp_delay, stp, is_sam_main)
                            
                            if enspell_active:
                                magical_damage += main_enspell_damage
                        else:
                            idx += 5
                    else:
                        idx += 5
            else:
                idx += 1
                # Regular Zanshin (single hit)
                if randoms[idx] < zanshin:
                    idx += 1
                    if attempted_hits < 8:
                        attempted_hits += 1
                        if randoms[idx] < zanshin_hit_rate:
                            idx += 1
                            pdif, crit = get_pdif_melee_jit(zanshin_attack, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                             crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                            idx += 3
                            
                            phys_dmg = get_phys_damage_jit(main_dmg, fstr_main, pdif, crit, crit_dmg)
                            
                            if randoms[idx] < empyrean_proc_rate:
                                phys_dmg = int(phys_dmg * (1.0 + empyrean_bonus_mult))
                            idx += 1
                            
                            physical_damage += phys_dmg
                            tp_return += get_tp_jit(tp_delay, stp, is_sam_main)
                            
                            if enspell_active:
                                magical_damage += main_enspell_damage
                        else:
                            idx += 5
                    else:
                        idx += 5
                else:
                    idx += 1

    # ===================
    # Kick Attacks (Hand-to-Hand only)
    # ===================
    if is_h2h and attempted_hits < 8:
        if randoms[idx] < kickattacks:
            idx += 1
            attempted_hits += 1
            if randoms[idx] < hit_rate11:  # Kick attacks use main hit rate
                idx += 1
                pdif, crit = get_pdif_melee_jit(attack1, main_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                 crit_rate, randoms[idx], randoms[idx+1], randoms[idx+2])
                idx += 3
                
                phys_dmg = get_phys_damage_jit(kick_dmg, fstr_kick, pdif, crit, crit_dmg)
                
                # Dragon Fangs proc
                if randoms[idx] < dragon_fangs_proc_rate:
                    phys_dmg = phys_dmg * 2  # Double damage on proc
                idx += 1
                
                physical_damage += phys_dmg
                tp_return += get_tp_jit(tp_delay, stp, False)
                
                if enspell_active:
                    magical_damage += main_enspell_damage
            else:
                idx += 5
        else:
            idx += 1

    # ===================
    # Daken (NIN shuriken throw)
    # ===================
    if daken > 0 and attempted_hits < 8:
        if randoms[idx] < daken:
            idx += 1
            attempted_hits += 1
            if randoms[idx] < hit_rate_ranged:
                idx += 1
                pdif, crit = get_pdif_ranged_jit(ranged_attack, ammo_skill_id, pdl_trait, pdl_gear, enemy_defense,
                                                  crit_rate, randoms[idx], randoms[idx+1])
                idx += 2
                
                phys_dmg = get_phys_damage_jit(ammo_dmg, fstr_ammo, pdif, crit, crit_dmg)
                physical_damage += phys_dmg
                tp_return += get_tp_jit(ammo_delay, stp, False)  # Daken uses ammo_delay for TP
            else:
                idx += 3
        else:
            idx += 1

    return physical_damage, tp_return, magical_damage


# =============================================================================
# Skill type ID conversion helpers (called from Python side)
# =============================================================================

def get_skill_type_id(skill_type):
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


def get_ranged_skill_type_id(skill_type):
    """Convert ranged skill type to numeric ID."""
    return 0 if skill_type == "Marksmanship" else 1


# =============================================================================
# Pre-compile the kernel
# =============================================================================

def _warmup():
    """Pre-compile the JIT functions with dummy data."""
    randoms = np.random.uniform(0, 1, 500)
    simulate_attack_round_kernel(
        # Damage values
        100.0, 90.0, 50.0, 30.0,
        15.0, 13.0, 10.0, 8.0,
        # Attack values
        1500.0, 1400.0, 1000.0, 1550.0,
        # Skill type IDs
        0, 0, 1,
        # PDL
        0.25, 0.1,
        # Hit rates
        0.95, 0.92, 0.90, 0.88, 0.85, 0.93,
        # Crit
        0.15, 0.25,
        # Multi-attack
        0.05, 0.15, 0.30,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        # Special attacks
        0.0, 0.0, 0.0, 0.0, 0.0,
        # TP
        320.0, 240.0, 0.30,
        # EnSpell
        0.0, 0.0, False,
        # Enemy defense
        1300.0,
        # DA/TA dmg
        0.0, 0.0,
        # Weapon procs
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        # Dragon Fangs
        0.0,
        # Flags
        True, False, False, False,
        # Randoms
        randoms
    )

# Warm up on import
_warmup()


# =============================================================================
# Monte Carlo Time-to-WS simulation
# =============================================================================

@njit(cache=True)
def run_monte_carlo_kernel(
    n_rounds,
    # All the same parameters as simulate_attack_round_kernel
    main_dmg, sub_dmg, kick_dmg, ammo_dmg,
    fstr_main, fstr_sub, fstr_kick, fstr_ammo,
    attack1, attack2, ranged_attack, zanshin_attack,
    main_skill_id, sub_skill_id, ammo_skill_id,
    pdl_trait, pdl_gear,
    hit_rate11, hit_rate12, hit_rate21, hit_rate22,
    hit_rate_ranged, zanshin_hit_rate,
    crit_rate, crit_dmg,
    qa, ta, da,
    oa8_main, oa7_main, oa6_main, oa5_main, oa4_main, oa3_main, oa2_main,
    oa8_sub, oa7_sub, oa6_sub, oa5_sub, oa4_sub, oa3_sub, oa2_sub,
    kickattacks, daken, zanshin, zanhasso, zanshin_oa2,
    mdelay, ammo_delay, stp,
    main_enspell_damage, sub_enspell_damage, enspell_active,
    enemy_defense,
    da_dmg, ta_dmg,
    relic_proc_rate, relic_bonus_mult,
    prime_proc_rate, prime_bonus_mult,
    empyrean_proc_rate, empyrean_bonus_mult,
    dragon_fangs_proc_rate,
    dual_wield, is_h2h, is_two_handed, is_sam_main,
    # Large pre-generated random array for all rounds
    all_randoms
):
    """
    Run n_rounds of attack round simulations and return totals.
    Returns: (total_physical, total_tp, total_magical)
    """
    total_physical = 0.0
    total_tp = 0.0
    total_magical = 0.0
    
    for i in range(n_rounds):
        # Get the random slice for this round (500 randoms per round)
        start_idx = i * 500
        randoms = all_randoms[start_idx:start_idx + 500]
        
        phys, tp, magic = simulate_attack_round_kernel(
            main_dmg, sub_dmg, kick_dmg, ammo_dmg,
            fstr_main, fstr_sub, fstr_kick, fstr_ammo,
            attack1, attack2, ranged_attack, zanshin_attack,
            main_skill_id, sub_skill_id, ammo_skill_id,
            pdl_trait, pdl_gear,
            hit_rate11, hit_rate12, hit_rate21, hit_rate22,
            hit_rate_ranged, zanshin_hit_rate,
            crit_rate, crit_dmg,
            qa, ta, da,
            oa8_main, oa7_main, oa6_main, oa5_main, oa4_main, oa3_main, oa2_main,
            oa8_sub, oa7_sub, oa6_sub, oa5_sub, oa4_sub, oa3_sub, oa2_sub,
            kickattacks, daken, zanshin, zanhasso, zanshin_oa2,
            mdelay, ammo_delay, stp,
            main_enspell_damage, sub_enspell_damage, enspell_active,
            enemy_defense,
            da_dmg, ta_dmg,
            relic_proc_rate, relic_bonus_mult,
            prime_proc_rate, prime_bonus_mult,
            empyrean_proc_rate, empyrean_bonus_mult,
            dragon_fangs_proc_rate,
            dual_wield, is_h2h, is_two_handed, is_sam_main,
            randoms
        )
        
        total_physical += phys
        total_tp += tp
        total_magical += magic
    
    return total_physical, total_tp, total_magical


def simulate_time_to_ws(
    # Number of Monte Carlo rounds
    n_rounds,
    # Time per attack round (pre-calculated)
    time_per_attack_round,
    # Starting TP and threshold
    starting_tp,
    ws_threshold,
    # Regain TP per attack round
    regain_tp_per_round,
    # All kernel parameters
    main_dmg, sub_dmg, kick_dmg, ammo_dmg,
    fstr_main, fstr_sub, fstr_kick, fstr_ammo,
    attack1, attack2, ranged_attack, zanshin_attack,
    main_skill_id, sub_skill_id, ammo_skill_id,
    pdl_trait, pdl_gear,
    hit_rate11, hit_rate12, hit_rate21, hit_rate22,
    hit_rate_ranged, zanshin_hit_rate,
    crit_rate, crit_dmg,
    qa, ta, da,
    oa8_main, oa7_main, oa6_main, oa5_main, oa4_main, oa3_main, oa2_main,
    oa8_sub, oa7_sub, oa6_sub, oa5_sub, oa4_sub, oa3_sub, oa2_sub,
    kickattacks, daken, zanshin, zanhasso, zanshin_oa2,
    mdelay, ammo_delay, stp,
    main_enspell_damage, sub_enspell_damage, enspell_active,
    enemy_defense,
    da_dmg, ta_dmg,
    relic_proc_rate, relic_bonus_mult,
    prime_proc_rate, prime_bonus_mult,
    empyrean_proc_rate, empyrean_bonus_mult,
    dragon_fangs_proc_rate,
    dual_wield, is_h2h, is_two_handed, is_sam_main
):
    """
    Run Monte Carlo simulation to calculate time_to_ws.
    
    Returns in the same format as average_attack_round with simulation=False:
        (time_to_ws, [damage, tp_per_attack_round, time_per_attack_round, invert], magical_damage)
    """
    # Pre-generate all random values for all rounds
    all_randoms = np.random.uniform(0, 1, n_rounds * 500)
    
    # Run Monte Carlo simulation
    total_physical, total_tp, total_magical = run_monte_carlo_kernel(
        n_rounds,
        main_dmg, sub_dmg, kick_dmg, ammo_dmg,
        fstr_main, fstr_sub, fstr_kick, fstr_ammo,
        attack1, attack2, ranged_attack, zanshin_attack,
        main_skill_id, sub_skill_id, ammo_skill_id,
        pdl_trait, pdl_gear,
        hit_rate11, hit_rate12, hit_rate21, hit_rate22,
        hit_rate_ranged, zanshin_hit_rate,
        crit_rate, crit_dmg,
        qa, ta, da,
        oa8_main, oa7_main, oa6_main, oa5_main, oa4_main, oa3_main, oa2_main,
        oa8_sub, oa7_sub, oa6_sub, oa5_sub, oa4_sub, oa3_sub, oa2_sub,
        kickattacks, daken, zanshin, zanhasso, zanshin_oa2,
        mdelay, ammo_delay, stp,
        main_enspell_damage, sub_enspell_damage, enspell_active,
        enemy_defense,
        da_dmg, ta_dmg,
        relic_proc_rate, relic_bonus_mult,
        prime_proc_rate, prime_bonus_mult,
        empyrean_proc_rate, empyrean_bonus_mult,
        dragon_fangs_proc_rate,
        dual_wield, is_h2h, is_two_handed, is_sam_main,
        all_randoms
    )
    
    # Calculate averages
    avg_physical = total_physical / n_rounds
    avg_tp = total_tp / n_rounds
    avg_magical = total_magical / n_rounds
    
    # Add regain TP
    tp_per_attack_round = avg_tp + regain_tp_per_round
    
    # Calculate time to WS
    if tp_per_attack_round > 0:
        attacks_per_ws = (ws_threshold - starting_tp) / tp_per_attack_round
        time_to_ws = time_per_attack_round * attacks_per_ws
    else:
        time_to_ws = 9999.0
    
    # Total damage per attack round
    damage = avg_physical + avg_magical
    
    # Return in the same format as simulation=False
    # (metric, [damage, tp_per_attack_round, time_per_attack_round, invert], magical_damage)
    invert = -1  # For "Time to WS", lower is better
    
    return (time_to_ws, [damage, tp_per_attack_round, time_per_attack_round, invert], avg_magical)
