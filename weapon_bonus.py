'''
File containing weapon skill bonuses from specific weapons.
    
Author: Kastra (Asura server)
'''
from get_dex_crit import *
import numpy as np

def get_weapon_bonus(main_wpn_name, rng_wpn_name, ws_name):

    weapon_skill_bonuses = {

        # Ambuscade weapons
        "Dolichenus": {"Decimation": 1.2},
        "Drepanum": {"Spiral Hell": 1.0},
        "Gokotai": {"Blade: Ku": 0.6},
        "Hachimonji": {"Tachi: Kasha": 0.25},
        "Karambit": {"Asuran Fists": 0.5},
        "Lycurgos": {"Steel Cyclone": 0.3},
        "Maxentius": {"Black Halo": 0.5},
        "Naegling": {"Savage Blade": 0.15},
        "Nandaka": {"Ground Strike": 0.15},
        "Shining One": {"Impulse Drive": 0.4},
        "Tauret": {"Evisceration": 0.5},
        "Ullr": {"Empyreal Arrow": 0.5},
        "Xoanon": {"Retribution": 0.2},

        # Relic weapons & R15
        "Amanomurakumo": {"Tachi: Kaiten": 0.40},
        "Annihilator": {"Coronach": 0.40},
        "Apocalypse": {"Catastrophe": 0.40},
        "Bravura": {"Metatron Torment": 0.40},
        "Excalibur": {"Knights of Round": 0.40},
        "Gungnir": {"Geirskogul": 0.40},
        "Guttler": {"Onslaught": 0.40},
        "Kikoku": {"Blade: Metsu": 0.40},
        "Mandau": {"Mercy Stroke": 0.40},
        "Mjollnir": {"Randgrith": 0.40},
        "Ragnarok": {"Scourge": 0.40},
        "Spharai": {"Final Heaven": 0.40},
        "Yoichinoyumi": {"Namas Arrow": 0.40},

        "Amanomurakumo R15": {"Tachi: Kaiten": 0.68},
        "Annihilator R15": {"Coronach": 0.68},
        "Apocalypse R15": {"Catastrophe": 0.68},
        "Bravura R15": {"Metatron Torment": 0.68},
        "Excalibur R15": {"Knights of Round": 0.68},
        "Gungnir R15": {"Geirskogul": 0.68},
        "Guttler R15": {"Onslaught": 0.68},
        "Kikoku R15": {"Blade: Metsu": 0.68},
        "Mandau R15": {"Mercy Stroke": 0.68},
        "Mjollnir R15": {"Randgrith": 0.68},
        "Ragnarok R15": {"Scourge": 0.68},
        "Spharai R15": {"Final Heaven": 0.68},
        "Yoichinoyumi R15": {"Namas Arrow": 0.68},

        # Empyrean weapons R15 only
        "Almace R15": {"Chant du Cygne": 0.1},
        "Armageddon R15": {"Wildfire": 0.1},
        "Caladbolg R15": {"Torcleaver": 0.1},
        "Farsha R15": {"Cloudsplitter": 0.1},
        "Gandiva R15": {"Jishnu's Radiance": 0.1},
        "Kannagi R15": {"Blade: Hi": 0.1},
        "Masamune R15": {"Tachi: Fudo": 0.1},
        "Redemption R15": {"Quietus": 0.1},
        "Rhongomiant R15": {"Camlann's Torment": 0.1},
        "Twashtar R15": {"Rudra's Storm": 0.1},
        "Ukonvasara R15": {"Ukko's Fury": 0.1},
        "Verethragna R15": {"Victory Smite": 0.1},

        # Mythic weapons & R15
        "Aymur R15": {"Primal Rend": 0.495},
        "Burtgang R15": {"Atonement": 0.3},
        "Carnwenhan R15": {"Mordant Rime": 0.495},
        "Conqueror R15": {"King's Justice": 0.495},
        "Death Penalty R15": {"Leaden Salute": 0.495},
        "Gastraphetes R15": {"Trueflight": 0.495},
        "Glanzfaust R15": {"Ascetic's Fury": 0.495},
        "Kenkonken R15": {"Stringing Pummel": 0.495},
        "Kogarasumaru R15": {"Tachi: Rana": 0.495},
        "Laevateinn R15": {"Vidohunir": 0.495},
        "Liberator R15": {"Insurgency": 0.495},
        "Murgleis R15": {"Death Blossom": 0.495},
        "Nagi R15": {"Blade: Kamu": 0.495},
        "Ryunohige R15": {"Drakesbane": 0.495},
        "Terpsichore R15": {"Pyrrhic Kleos": 0.495},
        "Tizona R15": {"Expiacion": 0.495},
        "Tupsimati R15": {"Omniscience": 0.495},
        "Nirvana R15": {"Garland of Bliss": 0.495},
        "Vajra R15": {"Mandalic Stab": 0.495},
        "Yagrush R15": {"Mystic Boon": 0.495},

        "Aymur": {"Primal Rend": 0.3},
        "Burtgang": {"Atonement": 0.3},
        "Carnwenhan": {"Mordant Rime": 0.3},
        "Conqueror": {"King's Justice": 0.3},
        "Death Penalty": {"Leaden Salute": 0.3},
        "Gastraphetes": {"Trueflight": 0.3},
        "Glanzfaust": {"Ascetic's Fury": 0.3},
        "Kenkonken": {"Stringing Pummel": 0.3},
        "Kogarasumaru": {"Tachi: Rana": 0.3},
        "Laevateinn": {"Vidohunir": 0.3},
        "Liberator": {"Insurgency": 0.3},
        "Murgleis": {"Death Blossom": 0.3},
        "Nagi": {"Blade: Kamu": 0.3},
        "Ryunohige": {"Drakesbane": 0.3},
        "Terpsichore": {"Pyrrhic Kleos": 0.3},
        "Tizona": {"Expiacion": 0.3},
        "Tupsimati": {"Omniscience": 0.3},
        "Nirvana": {"Garland of Bliss": 0.3},
        "Vajra": {"Mandalic Stab": 0.3},
        "Yagrush": {"Mystic Boon": 0.3},

        # Ergon weapons
        "Epeolatry R15": {"Dimidiation": 0.15},
        "Idris R15": {"Exudation": 0.15},

        # Aeonic Weapons
        "Aeneas R15": {"Exenterator": 0.1},
        "Anguta R15": {"Entropy": 0.1},
        "Chango R15": {"Upheaval": 0.1},
        "Dojikiri Yasutsuna R15": {"Tachi: Shoha": 0.1},
        "Fail-not R15": {"Apex Arrow": 0.1},
        "Fomalhaut R15": {"Last Stand": 0.1},
        "Godhands R15": {"Shijin Spiral": 0.1},
        "Heishi Shorinken R15": {"Blade: Shun": 0.1},
        "Khatvanga R15": {"Shattersoul": 0.1},
        "Lionheart R15": {"Resolution": 0.1},
        "Sequence R15": {"Requiescat": 0.1},
        "Tishtrya R15": {"Realmrazer": 0.1},
        "Tri-edge R15": {"Ruinator": 0.1},
        "Trishula R15": {"Stardiver": 0.1},

    }


    ws_bonus = 0
    if main_wpn_name in weapon_skill_bonuses:
        ws_bonus += weapon_skill_bonuses[main_wpn_name].get(ws_name, 0)
    if rng_wpn_name in weapon_skill_bonuses:
        ws_bonus += weapon_skill_bonuses[rng_wpn_name].get(ws_name, 0)

    return ws_bonus