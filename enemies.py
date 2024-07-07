def create_enemy(name, level, defense, evasion, vit, agi, mnd, int, chr, location, chr_comment=None, agi_comment=None):
    enemy = {
        'Name': name,
        'Level': level,
        'Defense': defense,
        'Evasion': evasion,
        'VIT': vit,
        'AGI': agi,
        'MND': mnd,
        'INT': int,
        'CHR': chr,
        'Magic Defense': 0,
        'Magic Evasion': 0,
        'Location': location
    }
    if chr_comment:
        enemy['CHR'] = f"{chr}  # {chr_comment}"
    if agi_comment:
        enemy['AGI'] = f"{agi}  # {agi_comment}"
    return enemy

enemies = [
    ("Apex Bats", 129, 1142, 1043, 254, 298, 233, 233, 247, "Dho Gates"),
    ("Apex Toad", 132, 1239, 1133, 270, 348, 224, 293, 277, "Woh Gates"),
    ("Apex Bat", 135, 1338, 1224, 289, 340, 267, 267, 282, "Outer Ra'Kaznar"),
    ("Apex Lugcrawler Hunter", 138, 1446, 1314, 325, 346, 284, 284, 284, "Crawler's Nest [S]", "CHR unknown. Copied MND/INT"),
    ("Apex Knight Lugcrawler", 140, 1530, 1383, 356, 343, 297, 297, 297, "Crawler's Nest [S]", "CHR unknown. Copied MND/INT"),
    ("Apex Idle Drifter", 142, 1448, 1502, 348, 366, 327, 327, 327, "Promyvion", "CHR unknown. Copied MND/INT"),
    ("Apex Archaic Cog", 145, 1704, 1551, 381, 440, 353, 365, 353, "Alzadaal Undersea Ruins", "CHR unknown. Copied MND"),
    ("Apex Archaic Cogs", 147, 1791, 1628, 399, 443, 377, 390, 377, "Alzadaal Undersea Ruins", "CHR unknown. Copied MND"),
    ("Ozma", 999, 9999, 9999, 999, 999, 999, 999, 999, "Chocobo's Air Garden", "CHR unknown. Using value from apex_toad", "AGI unknown. Using value from apex_toad"),
    ("Octorok", 1, 1, 1, 1, 1, 1, 1, 1, "Hyrule")
]

preset_enemies = {name: create_enemy(name, level, defense, evasion, vit, agi, mnd, int, chr, location, chr_comment) for name, level, defense, evasion, vit, agi, mnd, int, chr, location, *chr_comment in enemies}
