'''
File containing buffs and their potencies
    
Author: Kastra (Asura server)
'''

cor = {
    "Chaos":       {"Attack%":[{"I":0.0625,"II":0.0781,"III":0.0937,"IV":0.25,"V":0.1093,"VI":0.1250,"VII":0.1562,"VIII":0.0312,"IX":0.1718,"X":0.1875,"XI":0.3125}, 32./1024, 100./1024],
                    "Ranged Attack%":[{"I":0.0625,"II":0.0781,"III":0.0937,"IV":0.25,"V":0.1093,"VI":0.1250,"VII":0.1562,"VIII":0.0312,"IX":0.1718,"X":0.1875,"XI":0.3125}, 32./1024, 100./1024],},
    "Samurai":     {"Store TP":[{"I":8,"II":32,"III":10,"IV":12,"V":14,"VI":4,"VII":16,"VIII":20,"IX":22,"X":24,"XI":40},4,10]},
    "Rogue's":     {"Crit Rate":[{"I":1,"II":2,"III":3,"IV":4,"V":10,"VI":5,"VII":6,"VIII":7,"IX":1,"X":8,"XI":14},1,5]},
    "Monk's":      {"Subtle Blow":[{"I":8,"II":10,"III":32,"IV":12,"V":14,"VI":16,"VII":4,"VIII":20,"IX":22,"X":24,"XI":40},4,10]},
    "Fighter's":   {"DA":[{"I":1,"II":2,"III":3,"IV":4,"V":10,"VI":5,"VII":6,"VIII":6,"IX":1,"X":7,"XI":15},1,5]},
    "Hunter's":    {"Accuracy":[{"I":10,"II":13,"III":15,"IV":40,"V":18,"VI":20,"VII":25,"VIII":5,"IX":28,"X":30,"XI":50},5,15],
                    "Ranged Accuracy":[{"I":10,"II":13,"III":15,"IV":40,"V":18,"VI":20,"VII":25,"VIII":5,"IX":28,"X":30,"XI":50},5,15]},
    "Wizard's":    {"Magic Attack":[{"I":4,"II":6,"III":8,"IV":10,"V":25,"VI":12,"VII":14,"VIII":17,"IX":2,"X":20,"XI":30},2,10]},
    "Warlock's":   {"Magic Accuracy":[{"I":10,"II":13,"III":15,"IV":40,"V":18,"VI":20,"VII":25,"VIII":5,"IX":28,"X":30,"XI":50},5,15]},
    "Tactician's": {"Regain":[{"I":10,"II":10,"III":10,"IV":10,"V":30,"VI":10,"VII":10,"VIII":0,"IX":20,"X":20,"XI":40},2,10]}
}

brd = {
    "Honor March": {"Magic Haste": [126./1024, 12./1024], "Attack": [168, 16], "Ranged Attack": [168, 16], "Accuracy": [42, 4], "Ranged Accuracy": [42, 4]},
    "Victory March": {"Magic Haste": [163./1024, 16.25/1024]},
    "Advancing March": {"Magic Haste": [108./1024, 11.8/1024]},
    "Minuet V": {"Attack": [124+25, 12.375], "Ranged Attack": [124+25, 12.375]},
    "Minuet IV": {"Attack": [112+25, 11.2], "Ranged Attack": [112+25, 11.2]},
    "Minuet III": {"Attack": [96+25, 9.5], "Ranged Attack": [96+25, 9.5]},
    "Minuet II": {"Attack": [64+25, 6.2], "Ranged Attack": [64+25, 6.2]},
    "Minuet": {"Attack": [32+25, 3.2], "Ranged Attack": [32+25, 3.2]},
    "Blade Madrigal": {"Accuracy": [60, 6]},
    "Sword Madrigal": {"Accuracy": [45, 4.5]},
    "Herculean Etude":{"STR":[15,1]},
    "Sinewy Etude":{"STR":[9,1]},
    "Uncanny Etude":{"DEX":[15,1]},
    "Dextrous Etude":{"DEX":[9,1]},
    "Vital Etude":{"VIT":[15,1]},
    "Vivacious Etude":{"VIT":[9,1]},
    "Swift Etude":{"AGI":[15,1]},
    "Quick Etude":{"AGI":[9,1]},
    "Sage Etude":{"INT":[15,1]},
    "Learned Etude":{"INT":[9,1]},
    "Logical Etude":{"MND":[15,1]},
    "Spirited Etude":{"MND":[9,1]},
    "Bewitching Etude":{"CHR":[15,1]},
    "Enchanting Etude":{"CHR":[9,1]},
    "Hunter's Prelude":{"Ranged Accuracy":[45,4.5]},
    "Archer's Prelude":{"Ranged Accuracy":[60,6]},
    "Aria of Passion":{"PDL":[12,1.333]}
}

brd_song_limits = {
    "Minuet V":8,
    "Minuet IV":8,
    "Minuet III":8,
    "Minuet II":8,
    "Minuet":8,
    "Blade Madrigal":9,
    "Sword Madrigal":9,
    "Victory March":8,
    "Advancing March":8,
    "Honor March":4,
    "Sinewy Etude":9,
    "Herculean Etude":9,
    "Dextrous Etude":9,
    "Uncanny Etude":9,
    "Vivacious Etude":9,
    "Vital Etude":9,
    "Quick Etude":9,
    "Swift Etude":9,
    "Learned Etude":9,
    "Sage Etude":9,
    "Spirited Etude":9,
    "Logical Etude":9,
    "Enchanting Etude":9,
    "Bewitching Etude":9,
    "Hunter's Prelude":8,
    "Archer's Prelude":8,
    "Aria of Passion":7,
}

geo = {"Fury": {"Attack%": [0.347,0.027], "Ranged Attack%": [0.347,0.027]},
       "Acumen": {"Magic Attack": [15,3]},
       "Focus": {"Magic Accuracy":[50,5]},
       "Haste": {"Magic Haste": [29.9/100, 1.1/100]},
       "Precision": {"Accuracy": [50,5], "Ranged Accuracy": [50,5]},
       "STR":{"STR":[25,2]},
       "DEX":{"DEX":[25,2]},
       "VIT":{"VIT":[25,2]},
       "AGI":{"AGI":[25,2]},
       "INT":{"INT":[25,2]},
       "MND":{"MND":[25,2]},
       "CHR":{"CHR":[25,2]}
    }


storm_spells = [spell_name for sublist in [[k + "storm II", k+"storm"] for k in ["Aurora", "Void", "Fire", "Sand", "Rain", "Wind", "Hail", "Thunder"]] for spell_name in sublist]
base_parameters = ["STR", "DEX", "VIT", "AGI", "MND", "INT", "CHR"]
whm = {
        "Haste":{"Magic Haste":150/1024},
        "Haste II":{"Magic Haste":307/1024},
        **{f"{key}storm II": values for key,values in {"Aurora":{"CHR":7}, "Void":{stat:3 for stat in base_parameters}, "Fire":{"STR":7}, "Sand":{"VIT":7}, "Rain":{"MND":7}, "Wind":{"AGI":7}, "Hail":{"INT":7}, "Thunder":{"DEX":7}}.items()},
        **{f"Boost-{stat}":{stat:25} for stat in base_parameters},
        **{f"Gain-{stat}":{stat:55} for stat in base_parameters},
        "Shell V": {"MDT":-29}
    }



cor_debuffs = {
    "Light Shot": {"Defense":28/1024},
}

geo_debuffs = {
    "Frailty": {"Defense":[0.148, 0.027]},
    "Torpor": {"Evasion":[50, 5]},
    "Malaise": {"Magic Defense":[15, 3]},
    "Languor":{"Magic Evasion":[50, 5]},
}

whm_debuffs = {
    "Dia":     {"Defense": 104./1024},
    "Dia II":  {"Defense": 156./1024},
    "Dia III": {"Defense": 208./1024},
}


#  Misc debuffs become "Special Toggles" that can be enabled/disabled individually in the GUI.
# Add your own custom debuffs here using the same format as the others.
all_jobs = ["war", "mnk", "whm", "blm", "rdm", "thf", "pld", "drk", "bst", "brd", "rng", "smn", "sam", "nin", "drg", "blu", "cor", "pup", "dnc", "sch", "geo", "run"]

misc_debuffs = {
    "Angon": {"Defense":0.2, "level requirement":0, "job requirement":all_jobs}, 
    "Armor Break": {"Defense": 0.25, "level requirement":0, "job requirement":all_jobs},
    "Corrosive Ooze": {"Defense": 0.33, "level requirement":0, "job requirement":all_jobs},
    "Box Step (sub)": {"Defense": 0.13, "level requirement":30, "job requirement":["dnc"]},
    "Box Step": {"Defense": 0.23, "level requirement":0, "job requirement":all_jobs},
    "Swooping Frenzy": {"Defense":0.25, "Magic Defense":25, "level requirement":0, "job requirement":all_jobs},
    "Distract III": {"Evasion": 280, "level requirement":0, "job requirement":all_jobs},
    # "Custom Debuff": {"VIT": 280, "level requirement":0, "job requirement":all_jobs},
}


