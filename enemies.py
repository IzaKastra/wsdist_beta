import sys

# Enemy information taken from https://w.atwiki.jp/bartlett3/pages/327.html

# Add new enemies to the default list by copy+pasting a pre-existing entry and adjusting the values.

enemies = [
    {"Name":"Apex Bats", "Level":129, "Defense":1142, "Evasion":1043, "VIT":254, "AGI":298, "MND":233, "INT":233, "CHR":247, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":"Dho Gates"},
    {"Name":"Apex Toad", "Level":132, "Defense":1239, "Evasion":1133, "VIT":270, "AGI":348, "MND":224, "INT":293, "CHR":277, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":-25, "Location":"Woh Gates"}, 
    {"Name":"Apex Bat", "Level":135, "Defense":1338, "Evasion":1224, "VIT":289, "AGI":340, "MND":267, "INT":267, "CHR":282, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":"Outer Ra'Kaznar"},
    {"Name":"Apex Lugcrawler Hunter", "Level":138, "Defense":1446, "Evasion":1314, "VIT":325, "AGI":346, "MND":284, "INT":284, "CHR":284, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":"Crawler's Nest [S]",}, # "CHR unknown. Copied MND,INT
    {"Name":"Apex Knight Lugcrawler", "Level":140, "Defense":1530, "Evasion":1383, "VIT":356, "AGI":343, "MND":297, "INT":297, "CHR":297, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":"Crawler's Nest [S]"}, # CHR unknown. Copied MND,INT
    {"Name":"Apex Idle Drifter", "Level":142, "Defense":1448, "Evasion":1502, "VIT":348, "AGI":366, "MND":327, "INT":327, "CHR":327, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":"Promyvion"}, # CHR unknown. Copied MND, INT
    {"Name":"Apex Archaic Cog", "Level":145, "Defense":1704, "Evasion":1551, "VIT":381, "AGI":440, "MND":353, "INT":365, "CHR":353, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":"Alzadaal Undersea Ruins"},  # CHR unknown. Copied MND
    {"Name":"Apex Archaic Cogs", "Level":147, "Defense":1791, "Evasion":1628, "VIT":399, "AGI":443, "MND":377, "INT":390, "CHR":377, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":"Alzadaal Undersea Ruins"},  # CHR unknown. Copied MND
    {"Name":"Ghatjot", "Level":135, "Defense":1444, "Evasion":1224, "VIT":444, "AGI":444, "MND":444, "INT":444, "CHR":444, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":"Sortie"},  #444 is unknown
    {"Name":"Leshonn", "Level":135, "Defense":1444, "Evasion":1249, "VIT":444, "AGI":444, "MND":444, "INT":444, "CHR":444, "Magic Evasion":0, "Magic Defense":100, "Magic Damage Taken":0, "Location":"Sortie"},  #444 is unknown
    {"Name":"Skomora", "Level":135, "Defense":1444, "Evasion":1224, "VIT":444, "AGI":444, "MND":444, "INT":444, "CHR":444, "Magic Evasion":0, "Magic Defense":100, "Magic Damage Taken":0, "Location":"Sortie"},  #444 is unknown
    {"Name":"Degei", "Level":135, "Defense":1444, "Evasion":1249, "VIT":444, "AGI":444, "MND":444, "INT":444, "CHR":444, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":"Sortie"},  #444 is unknown
    {"Name":"Dhartok", "Level":145, "Defense":1444, "Evasion":1581, "VIT":444, "AGI":444, "MND":338, "INT":363, "CHR":444, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":"Sortie"},  #444 is unknown
    {"Name":"Gartell", "Level":145, "Defense":1444, "Evasion":1613, "VIT":444, "AGI":444, "MND":394, "INT":350, "CHR":444, "Magic Evasion":0, "Magic Defense":100, "Magic Damage Taken":0, "Location":"Sortie"},  #444 is unknown
    {"Name":"Triboulex", "Level":145, "Defense":1444, "Evasion":1581, "VIT":444, "AGI":444, "MND":367, "INT":504, "CHR":444, "Magic Evasion":0, "Magic Defense":100, "Magic Damage Taken":0, "Location":"Sortie"},  #444 is unknown
    {"Name":"Aita", "Level":145, "Defense":1444, "Evasion":1623, "VIT":444, "AGI":444, "MND":427, "INT":494, "CHR":444, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":"Sortie"},  #444 is unknown
    {"Name":"Aminon", "Level":149, "Defense":1444, "Evasion":1774, "VIT":444, "AGI":444, "MND":468, "INT":540, "CHR":444, "Magic Evasion":0, "Magic Defense":152, "Magic Damage Taken":0, "Location":"Sortie"},  #444 is unknown
    {"Name":"Ozma", "Level":999, "Defense":9999, "Evasion":9999, "VIT":999, "AGI":999, "MND":999, "INT":999, "CHR":999, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":"Chocobo's Air Garden"},
    {"Name":"Octorok", "Level":1, "Defense":1, "Evasion":1, "VIT":1, "AGI":1, "MND":1, "INT":1, "CHR":1, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":"Hyrule"},
    {"Name":"BG Wiki sets", "Level":0, "Defense":1500, "Evasion":1350, "VIT":340, "AGI":340, "MND":280, "INT":280, "CHR":280, "Magic Evasion":0, "Magic Defense":0, "Magic Damage Taken":0, "Location":""},
    ]




# Check that all necessary stats are included in all enemies
missing_stat = False
for enemy in enemies:
    for key in ["Name", "Level", "Defense", "Evasion", "VIT", "AGI", "MND", "INT", "CHR", "Magic Evasion", "Magic Defense", "Magic Damage Taken", "Location"]: 
        if enemy.get(key, False) is False:
            print(f"Missing stat \"{key}\" for {enemy['Name']}. Update the enemies.py file to include this stat.")
            missing_stat = True
if missing_stat:
    sys.exit()
preset_enemies = {k["Name"]:k for k in sorted(enemies, key=lambda x:x["Level"])}