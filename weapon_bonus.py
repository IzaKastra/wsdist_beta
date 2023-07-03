#
# Created by Kastra on Asura.
# Feel free to /tell in game or send a PM on FFXIAH you have questions, comments, or suggestions.
#
# Version date: 2023 May 10
#
from get_dex_crit import *
import numpy as np

def get_weapon_bonus(main_wpn_name, rng_wpn_name, ws_name,):
    #
    # Check the player's main and ranged weapons for "WS Damage +x%".
    # R15 Relics get +68% for Relic WSs
    # R15 Mythics get +49.5% for Mythic WSs
    # R15 Empyrean/Aeonic get +10% for Empyrean/Aeonic WSs
    # Ambuscade weapons vary by weapon.
    #

    ws_bonus = 0

    if main_wpn_name == 'Naegling':
        if ws_name == 'Savage Blade':
            ws_bonus += 0.15
    elif main_wpn_name == 'Murgleis':
        if ws_name == 'Death Blossom':
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif main_wpn_name == 'Burtgang':
        if ws_name == 'Atonement':
            ws_bonus += 0.3 # Hidden +30% Mythic WS damage
    elif main_wpn_name == "Tizona":
        if ws_name == "Expiacion":
            ws_bonus += 0.495
    elif main_wpn_name == 'Almace':
        if ws_name == "Chant du Cygne":
            ws_bonus += 0.1
    elif main_wpn_name == 'Excalibur':
        if ws_name == 'Knights of Round':
            ws_bonus += 0.68 # Hidden 40% Relic WS damage * R15 +20% WS damage (1.4)*(1.2)
    elif main_wpn_name == "Sequence":
        if ws_name == 'Requiescat':
            ws_bonus += 0.1
    elif main_wpn_name == 'Maxentius':
        if ws_name == 'Black Halo':
            ws_bonus += 0.5
    elif main_wpn_name == 'Tishtrya':
        if ws_name == 'Realmrazer':
            ws_bonus += 0.1
    elif main_wpn_name == 'Mjollnir':
        if ws_name == 'Randgrith':
            ws_bonus += 0.68 # Hidden 40% Relic WS damage * R15 +20% WS damage (1.4)*(1.2)
    elif 'Yagrush' in main_wpn_name:
        if ws_name == 'Mystic Boon':
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif 'Idris' in main_wpn_name:
        if ws_name == 'Exudation':
            ws_bonus += 0.15 # BG Wiki has no mention of a hidden +30% for this weapon+WS combo
    elif main_wpn_name == 'Epeolatry':
        if ws_name == 'Dimidiation':
            ws_bonus += 0.15 # BG Wiki has no mention of a hidden +30% for this weapon+WS combo
    elif 'Kikoku' in main_wpn_name:
        if ws_name == 'Blade: Metsu':
            ws_bonus += 0.68 # Hidden +40% Relic WS damage * R15 +20% WS damage (1.4)*(1.2)
    elif 'Kannagi' in main_wpn_name:
        if ws_name == 'Blade: Hi':
            ws_bonus += 0.1
    elif 'Nagi' in main_wpn_name:
        if ws_name == 'Blade: Kamu':
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif 'Kenkonken' in main_wpn_name:
        if ws_name == 'Stringing Pummel':
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif 'Heishi' in main_wpn_name:
        if ws_name == 'Blade: Shun':
            ws_bonus += 0.1
    elif main_wpn_name == 'Gokotai':
        if ws_name == 'Blade: Ku':
            ws_bonus += 0.6
    elif main_wpn_name == 'Tauret':
        if ws_name == 'Evisceration':
            ws_bonus += 0.5
    elif main_wpn_name == 'Aeneas':
        if ws_name == 'Exenterator':
            ws_bonus += 0.1
    elif main_wpn_name == 'Mandau':
        if ws_name == 'Mercy Stroke':
            ws_bonus += 0.68 # Hidden 40% Relic WS damage * R15 +20% WS damage (1.4)*(1.2)
    elif main_wpn_name == 'Karambit':
        if ws_name == "Asuran Fists":
            ws_bonus += 0.5
    elif main_wpn_name == 'Dojikiri Yasutsuna':
        if ws_name == 'Tachi: Shoha':
            ws_bonus += 0.1
    elif main_wpn_name == 'Kogarasumaru':
        if ws_name == 'Tachi: Rana':
            ws_bonus += 0.495
    elif main_wpn_name == 'Masamune':
        if ws_name == 'Tachi: Fudo':
            ws_bonus += 0.1
    elif main_wpn_name == 'Amanomurakumo':
        if ws_name == 'Tachi: Kaiten':
            ws_bonus += 0.68
    elif main_wpn_name == 'Shining One':
        # # Shining One allows all weapon skills to crit. We deal with this in the weaponskill_info.py file since it modifies the weapon skills themselves
        # # https://www.bg-wiki.com/ffxi/Shining_One
        if ws_name == 'Impulse Drive':
            ws_bonus += 0.4
    elif main_wpn_name == 'Gungnir':
        if ws_name == 'Geirskogul':
            ws_bonus += 0.68 # Hidden 40% Relic WS damage * R15 +20% WS damage (1.4)*(1.2)
    elif main_wpn_name == "Rhongomiant":
        if ws_name == "Camlann's Torment":
            ws_bonus += 0.1
    elif main_wpn_name == "Ryunohige":
        if ws_name == "Drakesbane":
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif main_wpn_name == "Terpsichore":
        if ws_name == "Pyrrhic Kleos":
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif main_wpn_name == "Trishula":
        if ws_name == "Stardiver":
            ws_bonus += 0.1 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif main_wpn_name == 'Hachimonji':
        # Hachimonji does some weird stuff with store TP and multi-hits. I ignore that here.
        # https://www.bg-wiki.com/ffxi/Hachimonji
        if ws_name == 'Tachi: Kasha':
            ws_bonus += 0.25
    elif main_wpn_name == "Apocalypse":
        if ws_name == "Catastrophe":
            ws_bonus += 0.68
    elif main_wpn_name == "Liberator":
        if ws_name == "Insurgency":
            ws_bonus += 0.495
    elif main_wpn_name == "Redemption":
        if ws_name == "Quietus":
            ws_bonus += 0.1
    elif main_wpn_name == "Anguta":
        if ws_name == "Entropy":
            ws_bonus += 0.1
    elif main_wpn_name == "Caladbolg":
        if ws_name == "Torcleaver":
            ws_bonus += 0.1
    elif main_wpn_name == "Ragnarok":
        if ws_name == "Scourge":
            ws_bonus += 0.68
    elif main_wpn_name == "Nandaka":
        if ws_name == "Ground Strike":
            ws_bonus += 0.15
    elif main_wpn_name == "Lycurgos":
        if ws_name == "Steel Cyclone":
            ws_bonus += 0.30
    elif main_wpn_name == "Conqueror":
        if ws_name == "King's Justice":
            ws_bonus += 0.495
    elif main_wpn_name == "Ukonvasara":
        if ws_name == "Ukko's Fury":
            ws_bonus += 0.1
    elif main_wpn_name == "Chango":
        if ws_name == "Upheaval":
            ws_bonus += 0.1
    elif main_wpn_name == "Bravura":
        if ws_name == "Metatron Torment":
            ws_bonus += 0.68
    elif main_wpn_name == "Dolichenus":
        if ws_name == "Decimation":
            ws_bonus += 1.20
    elif main_wpn_name == "Guttler":
        if ws_name == "Onslaught":
            ws_bonus += 0.68
    elif main_wpn_name == 'Aymur':
        if ws_name == 'Primal Rend':
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif main_wpn_name == 'Farsha':
        if ws_name == "Cloudsplitter":
            ws_bonus += 0.1
    elif main_wpn_name == "Tri-edge":
        if ws_name == "Ruinator":
            ws_bonus += 0.1
    elif main_wpn_name == "Lionheart":
        if ws_name == "Resolution":
            ws_bonus += 0.1
    elif main_wpn_name == 'Twashtar':
        if ws_name == "Rudra's Storm":
            ws_bonus += 0.1
    elif main_wpn_name == 'Carnwenhan':
        if ws_name == 'Mordant Rime':
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif main_wpn_name == 'Drepanum':
        if ws_name == 'Spiral Hell':
            ws_bonus += 1.0
    elif main_wpn_name == 'Xoanon':
        if ws_name == 'Retribution':
            ws_bonus += 0.2
    elif main_wpn_name == 'Khatvanga':
        if ws_name == 'Shattersoul':
            ws_bonus += 0.1
    elif main_wpn_name == 'Vajra':
        if ws_name == 'Mandalic Stab':
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif main_wpn_name == 'Vajra':
        if ws_name == 'Pyrrhic Kleos':
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif main_wpn_name == "Glanzfaust":
        if ws_name == "Ascetic's Fury":
            ws_bonus += 0.495
    elif main_wpn_name == "Verethragna":
        if ws_name == "Victory Smite":
            ws_bonus += 0.1
    elif main_wpn_name == "Godhands":
        if ws_name == "Shijin Spiral":
            ws_bonus += 0.1
    elif main_wpn_name == "Spharai":
        if ws_name == "Final Heaven":
            ws_bonus += 0.68
    elif main_wpn_name == 'Tupsimati':
        if ws_name == 'Omniscience':
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif main_wpn_name == 'Laevateinn':
        if ws_name == 'Vidohunir':
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)


    # Do the same with ranged WSs now.
    if rng_wpn_name == "Yoichinoyumi":
        if ws_name == "Namas Arrow":
            ws_bonus += 0.68
    elif rng_wpn_name == "Annihilator":
        if ws_name == "Coronach":
            ws_bonus += 0.68
    elif rng_wpn_name == 'Gandiva':
        if ws_name == "Jishnu's Radiance":
            ws_bonus += 0.1
    elif rng_wpn_name == 'Death Penalty':
        if ws_name == 'Leaden Salute':
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif rng_wpn_name == 'Armageddon':
        if ws_name == "Wildfire":
            ws_bonus += 0.1
    elif rng_wpn_name == 'Gastraphetes':
        if ws_name == 'Trueflight':
            ws_bonus += 0.495 # Hidden +30% Mythic WS damage * R15 +15% WS damage (1.3)*(1.15)
    elif rng_wpn_name == "Ullr":
        if ws_name == "Empyreal Arrow":
            ws_bonus += 0.5
    elif rng_wpn_name == "Fomalhaut":
        if ws_name == "Last Stand":
            ws_bonus += 0.1
    elif rng_wpn_name == "Fail-not":
        if ws_name == "Apex Arrow":
            ws_bonus += 0.1

    return(ws_bonus)
