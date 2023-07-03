#
# Created by Kastra on Asura.
# Feel free to /tell in game or send a PM on FFXIAH you have questions, comments, or suggestions.
#
# Version date: 2023 April 17
#
# Enemy information taken from https://w.atwiki.jp/bartlett3/pages/327.html
#
# Dho Gates triple-bats
apex_bats = {'Name': 'Apex Bats',
             'Level': 129,
             'Defense': 1142,
             'Evasion': 1043,
             'VIT': 254,
             'AGI': 356, # AGI unknown. Using value from apex_toad
             'MND': 233,
             'INT': 233,
             'CHR': 277, # CHR unknown. Using value from apex_toad
             'Magic Defense': 0,
             'Magic Evasion': 0,
             'Location':"Dho Gates"}

# Woh Gates toads
apex_toad = {'Name': "Apex Toad",
             'Level': 132,
             'Defense': 1239,
             'Evasion': 1133,
             'VIT': 270,
             'AGI': 356, # AGI roughly measured using Scoreboard on two different toads.
             'MND': 224,
             'INT': 293,
             'CHR': 277,
             'Magic Defense': 0,
             'Magic Evasion': 0,
             'Location':"Woh Gates"}

# Outer Ra'Kaznar single bats
apex_bat  = {'Name': "Apex Bat",
             'Level': 135,
             'Defense': 1338,
             'Evasion': 1224,
             'VIT': 289,
             'AGI': 356, # AGI unknown. Using value from apex_toad
             'MND': 267,
             'INT': 267,
             'CHR': 267, # CHR unknown. Copied MND/INT
             'Magic Defense': 0,
             'Magic Evasion': 0,
             'Location':"Outer Ra'Kaznar"}

# Crawler's Nest [S] 
apex_lugcrawler_hunter  = {'Name': "Apex Lugcrawler Hunter",
             'Level': 138,
             'Defense': 1446,
             'Evasion': 1314,
             'VIT': 325,
             'AGI': 346,
             'MND': 284,
             'INT': 284,
             'CHR': 284, # CHR unknown. Copied MND/INT
             'Magic Defense': 0,
             'Magic Evasion': 0,
             'Location':"Crawler's Nest [S]"}

apex_knight_lugcrawler  = {'Name': "Apex Knight Lugcrawler",
             'Level': 140,
             'Defense': 1530,
             'Evasion': 1383,
             'VIT': 356,
             'AGI': 343,
             'MND': 297,
             'INT': 297,
             'CHR': 297, # CHR unknown. Copied MND/INT
             'Magic Defense': 0,
             'Magic Evasion': 0,
             'Location':"Crawler's Nest [S]"}

apex_idle_drifter  = {'Name': "Apex Idle Drifter",
             'Level': 142,
             'Defense': 1448,
             'Evasion': 1502,
             'VIT': 348,
             'AGI': 366,
             'MND': 327,
             'INT': 327,
             'CHR': 327, # CHR unknown. Copied MND/INT
             'Magic Defense': 0,
             'Magic Evasion': 0,
             'Location':"Promyvion"}

apex_archaic_cog  = {'Name': "Apex Archaic Cog",
             'Level': 145,
             'Defense': 1704,
             'Evasion': 1551,
             'VIT': 381,
             'AGI': 381, # Unknown. Copied MND
             'MND': 353,
             'INT': 365,
             'CHR': 353, # CHR unknown. Copied MND
             'Magic Defense': 0,
             'Magic Evasion': 0,
             'Location':"Alzadaal Undersea Ruins"}


apex_archaic_cogs  = {'Name': "Apex Archaic Cogs",
             'Level': 147,
             'Defense': 1791,
             'Evasion': 1628,
             'VIT': 399,
             'AGI': 399, # Unknown. Copied VIT
             'MND': 377,
             'INT': 390,
             'CHR': 377, # CHR unknown. Copied MND
             'Magic Defense': 0,
             'Magic Evasion': 0,
             'Location':"Alzadaal Undersea Ruins"}


ozma = {"Name": "Ozma",
             'Level': 999,
             'Defense': 9999,
             'Evasion': 9999,
             'VIT': 999,
             'AGI': 999, # AGI unknown. Using value from apex_toad
             'MND': 999,
             'INT': 999,
             'CHR': 999, # CHR unknown. Using value from apex_toad
             'Magic Defense': 0,
             'Magic Evasion': 0,
             'Location':"Chocobo's Air Garden"}

octorok = {"Name": "Octorok",
             'Level': 1,
             'Defense': 1,
             'Evasion': 1,
             'VIT': 1,
             'AGI': 1,
             'MND': 1,
             'INT': 1,
             'CHR': 1,
             'Magic Defense': 0,
             'Magic Evasion': 0,
             'Location':"Hyrule"}

# preset_enemies = {"147 Archaic Cogs":apex_archaic_cogs,"145 Archaic Cog":apex_archaic_cog,"142 Idle Drifter":apex_idle_drifter, "140 Knight Lugcrawler":apex_knight_lugcrawler, "138 Lugcrawler Hunter":apex_lugcrawler_hunter, "135 Apex Bat":apex_bat,"132 Apex Toad":apex_toad,"129 Apex Bats":apex_bats, "Octorok":octorok, "Ozma":ozma, }
preset_enemies = {"Archaic Cogs":apex_archaic_cogs,"Archaic Cog":apex_archaic_cog,"Idle Drifter":apex_idle_drifter, "Knight Lugcrawler":apex_knight_lugcrawler, "Lugcrawler Hunter":apex_lugcrawler_hunter, "Apex Bat":apex_bat,"Apex Toad":apex_toad,"Apex Bats":apex_bats, "Octorok":octorok, "Ozma":ozma, }
