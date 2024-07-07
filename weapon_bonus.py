#
# Version date: 2024 July 07
#
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

        # Relic weapons
        "Amanomurakumo": {"Tachi: Kaiten": 0.68},
        "Annihilator": {"Coronach": 0.68},
        "Apocalypse": {"Catastrophe": 0.68},
        "Bravura": {"Metatron Torment": 0.68},
        "Excalibur": {"Knights of Round": 0.68},
        "Gungnir": {"Geirskogul": 0.68},
        "Guttler": {"Onslaught": 0.68},
        "Kikoku": {"Blade: Metsu": 0.68},
        "Mandau": {"Mercy Stroke": 0.68},
        "Mjollnir": {"Randgrith": 0.68},
        "Ragnarok": {"Scourge": 0.68},
        "Spharai": {"Final Heaven": 0.68},
        "Yoichinoyumi": {"Namas Arrow": 0.68},

        # Empyrean weapons
        "Almace": {"Chant du Cygne": 0.1},
        "Armageddon": {"Wildfire": 0.1},
        "Caladbolg": {"Torcleaver": 0.1},
        "Farsha": {"Cloudsplitter": 0.1},
        "Gandiva": {"Jishnu's Radiance": 0.1},
        "Kannagi": {"Blade: Hi": 0.1},
        "Masamune": {"Tachi: Fudo": 0.1},
        "Redemption": {"Quietus": 0.1},
        "Rhongomiant": {"Camlann's Torment": 0.1},
        "Twashtar": {"Rudra's Storm": 0.1},
        "Ukonvasara": {"Ukko's Fury": 0.1},
        "Verethragna": {"Victory Smite": 0.1},

        # Mythic weapons
        "Aymur": {"Primal Rend": 0.495},
        "Burtgang": {"Atonement": 0.3},
        "Carnwenhan": {"Mordant Rime": 0.495},
        "Conqueror": {"King's Justice": 0.495},
        "Death Penalty": {"Leaden Salute": 0.495},
        "Gastraphetes": {"Trueflight": 0.495},
        "Glanzfaust": {"Ascetic's Fury": 0.495},
        "Kenkonken": {"Stringing Pummel": 0.495},
        "Kogarasumaru": {"Tachi: Rana": 0.495},
        "Laevateinn": {"Vidohunir": 0.495},
        "Liberator": {"Insurgency": 0.495},
        "Murgleis": {"Death Blossom": 0.495},
        "Nagi": {"Blade: Kamu": 0.495},
        "Ryunohige": {"Drakesbane": 0.495},
        "Terpsichore": {"Pyrrhic Kleos": 0.495},
        "Tizona": {"Expiacion": 0.495},
        "Tupsimati": {"Omniscience": 0.495},
        "Vajra": {"Mandalic Stab": 0.495},
        "Yagrush": {"Mystic Boon": 0.495},

        # Ergon weapons
        "Epeolatry": {"Dimidiation": 0.15},
        "Idris": {"Exudation": 0.15},

        # Aeonic Weapons
        "Aeneas": {"Exenterator": 0.1},
        "Anguta": {"Entropy": 0.1},
        "Chango": {"Upheaval": 0.1},
        "Dojikiri Yasutsuna": {"Tachi: Shoha": 0.1},
        "Fail-not": {"Apex Arrow": 0.1},
        "Fomalhaut": {"Last Stand": 0.1},
        "Godhands": {"Shijin Spiral": 0.1},
        "Heishi Shorinken": {"Blade: Shun": 0.1},
        "Khatvanga": {"Shattersoul": 0.1},
        "Lionheart": {"Resolution": 0.1},
        "Sequence": {"Requiescat": 0.1},
        "Tishtrya": {"Realmrazer": 0.1},
        "Tri-edge": {"Ruinator": 0.1},
        "Trishula": {"Stardiver": 0.1},

    }


    ws_bonus = 0
    if main_wpn_name in weapon_skill_bonuses:
        ws_bonus += weapon_skill_bonuses[main_wpn_name].get(ws_name, 0)
    if rng_wpn_name in weapon_skill_bonuses:
        ws_bonus += weapon_skill_bonuses[rng_wpn_name].get(ws_name, 0)

    return ws_bonus