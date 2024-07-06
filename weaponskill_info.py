import numpy as np
from get_dex_crit import get_dex_crit

def adjust_attack(player_attack, food_attack, attack_percent, ws_atk_modifier):
    return ((player_attack - food_attack) * (1 + attack_percent + ws_atk_modifier) / (1 + attack_percent)) + food_attack

def setup_ws_stats(ws_name, tp, player, enemy):
    ws_data = {
        # Sword Weapon Skills
        "Fast Blade": {"base_ftp": [1.0, 1.5, 2.0], "ftp_rep": False, "wsc": 0.4*(player.stats["STR"] + player.stats["DEX"]), "nhits": 2, "sc": ["Scission"]},
        "Burning Blade": {"base_ftp": [1.0, 2.09765625, 3.3984375], "ftp_rep": False, "wsc": 0.4*(player.stats["STR"] + player.stats["INT"]), "nhits": 1, "magical": True, "element": "Fire", "dSTAT": min(32, (player.stats["INT"] - enemy.stats["INT"])/2 + 8), "sc": ["Liquefaction"]},
        "Red Lotus Blade": {"base_ftp": [1.0, 2.3828125, 3.75], "ftp_rep": False, "wsc": 0.4*(player.stats["STR"] + player.stats["INT"]), "nhits": 1, "magical": True, "element": "Fire", "dSTAT": min(32, (player.stats["INT"] - enemy.stats["INT"])/2 + 8), "sc": ["Liquefaction","Detonation"]},
        "Shining Blade": {"base_ftp": [1.125, 2.22265625, 3.5234375], "ftp_rep": False, "wsc": 0.4*(player.stats["STR"] + player.stats["MND"]), "nhits": 1, "magical": True, "element": "Light", "dSTAT": 0, "sc": ["Scission"]},
        "Seraph Blade": {"base_ftp": [1.125, 2.625, 4.125], "ftp_rep": False, "wsc": 0.4*(player.stats["STR"] + player.stats["MND"]), "nhits": 1, "magical": True, "element": "Light", "dSTAT": 0, "sc": ["Scission"]},
        "Circle Blade": {"ftp": 1.0, "ftp_rep": False, "wsc": 1.0*player.stats["STR"], "nhits": 1, "sc": ["Reverberation","Impaction"]},
        "Swift Blade": {"ftp": 1.5, "ftp_rep": True, "wsc": 0.5*(player.stats["STR"] + player.stats["MND"]), "nhits": 3, "sc": ["Gravitation"]},
        "Savage Blade": {"base_ftp": [4.0, 10.25, 13.75], "ftp_rep": False, "wsc": 0.5*(player.stats["STR"] + player.stats["MND"]), "nhits": 2, "sc": ["Fragmentation","Scission"]},
        "Sanguine Blade": {"ftp": 2.75, "ftp_rep": False, "wsc": 0.5*player.stats["MND"] + 0.3*player.stats["STR"], "nhits": 1, "magical": True, "element": "Dark", "dSTAT": (player.stats["INT"] - enemy.stats["INT"])*2, "sc": ["None"]},
        "Requiescat": {"ftp": 1.0, "ftp_rep": True, "wsc": 0.85*player.stats["MND"], "nhits": 5, "sc": ["Aeonic","Gravitation","Scission"]},
        "Knights of Round": {"ftp": 5.0, "ftp_rep": False, "wsc": 0.4*(player.stats["MND"] + player.stats["STR"]), "nhits": 1, "sc": ["Light","Fusion"]},
        "Chant du Cygne": {"ftp": 1.6328125, "ftp_rep": True, "wsc": 0.8*player.stats["DEX"], "nhits": 3, "sc": ["Light","Distortion"], "crit_ws": True},
        "Death Blossom": {"ftp": 4.0, "ftp_rep": False, "wsc": 0.5*player.stats["MND"] + 0.3*player.stats["STR"], "nhits": 3, "sc": ["Fragmentation","Distortion"]},
        "Expiacion": {"base_ftp": [3.796875,9.390625,12.1875], "ftp_rep": False, "wsc": 0.3*(player.stats["STR"] + player.stats["INT"]) + 0.2*player.stats["DEX"], "nhits": 2, "sc": ["Distortion","Scission"]},
        "Fast Blade II": {"base_ftp": [1.8, 3.5, 5.0], "ftp_rep": True, "wsc": 0.8*player.stats["DEX"], "nhits": 2, "sc": ["Fusion"]},
        "Imperator": {"base_ftp": [3.75, 7.5, 11.75], "ftp_rep": False, "wsc": 0.7*(player.stats["DEX"] + player.stats["MND"]), "nhits": 1, "sc": ["Detonation","Compression","Distortion"]},
        
        # Additional weapon skills go here, following the same structure
    }

    if ws_name not in ws_data:
        raise ValueError(f"Unknown weaponskill: {ws_name}")

    ws_stats = ws_data[ws_name]
    if "base_ftp" in ws_stats:
        ws_stats["ftp"] = np.interp(tp, [1000, 2000, 3000], ws_stats["base_ftp"])

    return ws_stats

def apply_weapon_modifiers(player, enemy, ws_name):
    if player.gearset["main"]["Name"] == "Naegling":
        ws_atk_modifier = 0.13
        player.stats["Attack1"] = adjust_attack(player.stats["Attack1"], player.stats.get("Food Attack", 0), player.stats.get("Attack%", 0), ws_atk_modifier)
        if player.stats["Attack2"] > 0:
            player.stats["Attack2"] = adjust_attack(player.stats["Attack2"], player.stats.get("Food Attack", 0), player.stats.get("Attack%", 0), ws_atk_modifier)
    elif player.gearset["main"]["Name"] == "Nandaka":
        enemy.stats["Defense"] *= (1 - 0.03)

    return player, enemy

def weaponskill_info(ws_name, tp, player, enemy, wsc_bonus, dual_wield):
    player, enemy = apply_weapon_modifiers(player, enemy, ws_name)

    ws_stats = setup_ws_stats(ws_name, tp, player, enemy)
    wsc = ws_stats["wsc"] + sum([player.stats[k[0]] * k[1]/100 for k in wsc_bonus])

    scaling = {
        "hybrid": ws_stats.get("hybrid", False),
        "magical": ws_stats.get("magical", False),
        "dSTAT": ws_stats.get("dSTAT", 0),
        "wsc": wsc,
        "nhits": ws_stats["nhits"],
        "element": ws_stats.get("element", "None"),
        "ftp": ws_stats["ftp"],
        "ftp_rep": ws_stats["ftp_rep"],
        "player_attack1": player.stats["Attack1"],
        "player_attack2": player.stats.get("Attack2", 0),
        "player_accuracy1": player.stats["Accuracy1"],
        "player_accuracy2": player.stats.get("Accuracy2", 0),
        "player_rangedattack": player.stats.get("Ranged Attack", 0),
        "player_rangedaccuracy": player.stats.get("Ranged Accuracy", 0),
        "enemy_def": enemy.stats["Defense"],
        "crit_rate": 0,  # Initialize crit_rate
        "ftp_hybrid": ws_stats.get("ftp_hybrid", 0),
    }

    # Apply critical hit rate and other calculations based on ws_name and player's gear/abilities
    if "crit_ws" in ws_stats and ws_stats["crit_ws"]:
        scaling["crit_rate"] = player.stats["Crit Rate"]/100 + get_dex_crit(player.stats["DEX"], enemy.stats["AGI"])

    return scaling

# Example usage
# scaling_info = weaponskill_info("Fast Blade", 2000, player, enemy, wsc_bonus, dual_wield)
