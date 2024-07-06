#
# Created by Kastra on Asura.
# Feel free to /tell in game or send a PM on FFXIAH you have questions, comments, or suggestions.
#
# Version date: 2023 May 10
#
from get_dex_crit import *
import numpy as np


def get_weapon_bonus(main_wpn_name, rng_wpn_name, ws_name):
    weapon_skill_bonuses = {
        # Main Weapons
        "Naegling": {"Savage Blade": 0.15},
        "Murgleis": {"Death Blossom": 0.495},
        "Burtgang": {"Atonement": 0.3},
        "Tizona": {"Expiacion": 0.495},
        "Almace": {"Chant du Cygne": 0.1},
        "Excalibur": {"Knights of Round": 0.68},
        "Sequence": {"Requiescat": 0.1},
        "Maxentius": {"Black Halo": 0.5},
        "Tishtrya": {"Realmrazer": 0.1},
        "Mjollnir": {"Randgrith": 0.68},
        "Yagrush": {"Mystic Boon": 0.495},
        "Idris": {"Exudation": 0.15},
        "Epeolatry": {"Dimidiation": 0.15},
        "Kikoku": {"Blade: Metsu": 0.68},
        "Kannagi": {"Blade: Hi": 0.1},
        "Nagi": {"Blade: Kamu": 0.495},
        "Kenkonken": {"Stringing Pummel": 0.495},
        "Heishi": {"Blade: Shun": 0.1},
        "Gokotai": {"Blade: Ku": 0.6},
        "Tauret": {"Evisceration": 0.5},
        "Aeneas": {"Exenterator": 0.1},
        "Mandau": {"Mercy Stroke": 0.68},
        "Karambit": {"Asuran Fists": 0.5},
        "Dojikiri Yasutsuna": {"Tachi: Shoha": 0.1},
        "Kogarasumaru": {"Tachi: Rana": 0.495},
        "Masamune": {"Tachi: Fudo": 0.1},
        "Amanomurakumo": {"Tachi: Kaiten": 0.68},
        "Shining One": {"Impulse Drive": 0.4},
        "Gungnir": {"Geirskogul": 0.68},
        "Rhongomiant": {"Camlann's Torment": 0.1},
        "Ryunohige": {"Drakesbane": 0.495},
        "Terpsichore": {"Pyrrhic Kleos": 0.495},
        "Trishula": {"Stardiver": 0.1},
        "Hachimonji": {"Tachi: Kasha": 0.25},
        "Apocalypse": {"Catastrophe": 0.68},
        "Liberator": {"Insurgency": 0.495},
        "Redemption": {"Quietus": 0.1},
        "Anguta": {"Entropy": 0.1},
        "Caladbolg": {"Torcleaver": 0.1},
        "Ragnarok": {"Scourge": 0.68},
        "Nandaka": {"Ground Strike": 0.15},
        "Lycurgos": {"Steel Cyclone": 0.3},
        "Conqueror": {"King's Justice": 0.495},
        "Ukonvasara": {"Ukko's Fury": 0.1},
        "Chango": {"Upheaval": 0.1},
        "Bravura": {"Metatron Torment": 0.68},
        "Dolichenus": {"Decimation": 1.2},
        "Guttler": {"Onslaught": 0.68},
        "Aymur": {"Primal Rend": 0.495},
        "Farsha": {"Cloudsplitter": 0.1},
        "Tri-edge": {"Ruinator": 0.1},
        "Lionheart": {"Resolution": 0.1},
        "Twashtar": {"Rudra's Storm": 0.1},
        "Carnwenhan": {"Mordant Rime": 0.495},
        "Drepanum": {"Spiral Hell": 1.0},
        "Xoanon": {"Retribution": 0.2},
        "Khatvanga": {"Shattersoul": 0.1},
        "Vajra": {"Mandalic Stab": 0.495},
        "Terpsichore": {"Pyrrhic Kleos": 0.495},
        "Glanzfaust": {"Ascetic's Fury": 0.495},
        "Verethragna": {"Victory Smite": 0.1},
        "Godhands": {"Shijin Spiral": 0.1},
        "Spharai": {"Final Heaven": 0.68},
        "Tupsimati": {"Omniscience": 0.495},
        "Laevateinn": {"Vidohunir": 0.495},
        # Ranged Weapons
        "Yoichinoyumi": {"Namas Arrow": 0.68},
        "Annihilator": {"Coronach": 0.68},
        "Gandiva": {"Jishnu's Radiance": 0.1},
        "Death Penalty": {"Leaden Salute": 0.495},
        "Armageddon": {"Wildfire": 0.1},
        "Gastraphetes": {"Trueflight": 0.495},
        "Ullr": {"Empyreal Arrow": 0.5},
        "Fomalhaut": {"Last Stand": 0.1},
        "Fail-not": {"Apex Arrow": 0.1},
    }

    ws_bonus = 0

    # Get the bonus for the main weapon
    if main_wpn_name in weapon_skill_bonuses:
        ws_bonus += weapon_skill_bonuses[main_wpn_name].get(ws_name, 0)

    # Get the bonus for the ranged weapon
    if rng_wpn_name in weapon_skill_bonuses:
        ws_bonus += weapon_skill_bonuses[rng_wpn_name].get(ws_name, 0)

    return ws_bonus
