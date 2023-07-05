from create_player import *
import numpy as np
import numpy as np
from actions import *
import sys

# Use an external gear.py file
# https://stackoverflow.com/questions/47350078/importing-external-module-in-single-file-exe-created-with-pyinstaller
import sys
import os
sys.path.append(os.path.dirname(sys.executable))
from gear import *

def build_set(main_job, sub_job, master_level, buffs, abilities, enemy, ws_name, spell_name, action_type, starting_tp, min_tp, max_tp, check_gear, starting_gearset, pdt_requirement, mdt_requirement, input_metric, print_swaps, next_best_percent, ):
    #
    # Build a valid gear set, test it, and return the best set found.
    #
    # action_type = "ranged attack", "weapon skill", "tp round", "spell cast"
    #
    n_iter = 10
    fitn = 2

    ws_dict = {"Katana": ["Blade: Retsu", "Blade: Teki", "Blade: To", "Blade: Chi", "Blade: Ei", "Blade: Jin", "Blade: Ten", "Blade: Ku", "Blade: Yu", "Blade: Metsu", "Blade: Kamu", "Blade: Hi", "Blade: Shun", "Zesho Meppo",],
        "Great Katana": ["Tachi: Enpi", "Tachi: Goten", "Tachi: Kagero", "Tachi: Jinpu", "Tachi: Koki","Tachi: Yukikaze", "Tachi: Gekko", "Tachi: Kasha", "Tachi: Ageha","Tachi: Kaiten", "Tachi: Rana", "Tachi: Fudo", "Tachi: Shoha", "Tachi: Mumei"],
        "Dagger": [ "Viper Bite", "Dancing Edge", "Shark Bite", "Evisceration", "Aeolian Edge", "Mercy Stroke", "Mandalic Stab", "Mordant Rime", "Pyrrhic Kleos", "Rudra's Storm", "Exenterator", "Merciless Strike"],
        "Sword": ["Fast Blade", "Fast Blade II", "Burning Blade", "Red Lotus Blade", "Seraph Blade", "Circle Blade", "Swift Blade", "Savage Blade", "Sanguine Blade", "Knights of Round", "Death Blossom", "Expiacion", "Chant du Cygne", "Requiescat", "Imperator"],
        "Scythe": ["Slice", "Dark Harvest", "Shadow of Death", "Nightmare Scythe", "Spinning Scythe", "Guillotine", "Cross Reaper", "Spiral Hell", "Infernal Scythe", "Catastrophe", "Quietus", "Insurgency", "Entropy", "Origin", ], 
        "Great Sword":["Hard Slash", "Freezebite", "Shockwave", "Sickle Moon", "Spinning Slash", "Ground Strike", "Herculean Slash", "Resolution", "Scourge", "Dimidiation", "Torcleaver", "Fimbulvetr", ], 
        "Club":["Shining Strike", "Seraph Strike", "Skullbreaker", "True Strike", "Judgment", "Hexa Strike", "Black Halo", "Randgrith", "Exudation", "Mystic Boon", "Realmrazer", "Dagda"], 
        "Polearm":["Double Thrust", "Thunder Thrust", "Raiden Thrust", "Penta Thrust", "Wheeling Thrust", "Impulse Drive", "Sonic Thrust", "Geirskogul", "Drakesbane", "Camlann's Torment", "Stardiver", "Diarmuid", ], 
        "Staff":["Heavy Swing", "Rock Crusher", "Earth Crusher", "Starburst", "Sunburst", "Shell Crusher", "Full Swing", "Cataclysm", "Retribution", "Gate of Tartarus", "Omniscience", "Vidohunir", "Shattersoul", "Oshala"], 
        "Great Axe":["Iron Tempest", "Shield Break", "Armor Break", "Weapon Break", "Raging Rush", "Full Break", "Steel Cyclone", "Fell Cleave", "Metatron Torment", "King's Justice", "Ukko's Fury", "Upheaval", "Disaster"], 
        "Axe":["Raging Axe", "Spinning Axe", "Rampage", "Calamity", "Mistral Axe", "Decimation", "Bora Axe", "Onslaught", "Primal Rend", "Cloudsplitter", "Ruinator", "Blitz", ], 
        "Archery":["Flaming Arrow", "Piercing Arrow", "Dulling Arrow", "Sidewinder", "Blast Arrow", "Empyreal Arrow", "Refulgent Arrow", "Namas Arrow", "Jishnu's Radiance", "Apex Arrow", "Sarv"], 
        "Marksmanship":["Hot Shot", "Split Shot", "Sniper Shot", "Slug Shot", "Blast Shot", "Detonator", "Coronach", "Leaden Salute", "Trueflight", "Wildfire", "Last Stand", "Terminus", ], 
        "Hand-to-Hand":["Combo","One Inch Punch","Raging Fists","Spinning Attack","Howling Fist","Dragon Kick","Asuran Fists","Tornado Kick","Ascetic's Fury","Stringing Pummel","Final Heaven","Victory Smite","Shijin Spiral","Maru Kala",],
        }

    melee_ws = [ws for skill in ws_dict if skill not in ["Archery","Marksmanship"] for ws in ws_dict[skill]]
    ranged_ws = [ws for skill in ws_dict if skill in ["Archery","Marksmanship"] for ws in ws_dict[skill]]
    
    ws_type = "melee" if ws_name in melee_ws else "ranged" if ws_name in ranged_ws else "None"
    
    if " Shot" in spell_name:
        spell_type = "Quick Draw"
    elif spell_name=="Ranged Attack":
        spell_type="Ranged Attack"
    elif (": Ichi" in spell_name) or (": Ni" in spell_name) or (": San" in spell_name):
        spell_type = "Ninjutsu"
    else:
        spell_type = "Elemental Magic"

    # List of weapon skills and their associated weapons.
    restricted_ws = {"Blade: Metsu":"Kikoku",
                    "Final Heaven":"Spharai",
                    "Mercy Stroke":"Mandau",
                    "Knights of Round":"Excalibur",
                    "Scourge":"Ragnarok",
                    "Onslaught":"Guttler",
                    "Metatron Torment":"Bravura",
                    "Catastrophe":"Apocalypse",
                    "Geirskogul":"Gungnir",
                    "Tachi: Kaiten":"Amanomurakumo",
                    "Randgrith":"Mjollnir",
                    "Gates of Tartarus":"Claustrum",
                    "Namas Arrow":"Yoichinoyumi",
                    "Coronach":"Annihilator",
                    "Fast Blade II":"Onion Sword III",
                    "Imperator":"Caliburnus",
                    "Jijin Kaimetsu":"Dokoku",
                    "Terminus":"Earp",
                    "Origin":"Foenaria",
                    "Diarmuid":"Gae Buide",
                    "Fimbulvetr":"Hellheim",
                    "Tachi: Mumei":"Kusanagi-no-Tsurugi",
                    "Disaster":"Laphria",
                    "Dagda":"Lorg Mor",
                    "Merciless Strike":"Mpu Gandring",
                    "Oshala":"Opashoro",
                    "Sarv":"Pinaka",
                    "Blitz":"Spalirisos",
                    "Maru Kala":"Varga Purnikawa",
                    }


    best_set =  starting_gearset.copy()

    tcount = 0 # Total number of valid sets checked.
    for slot in starting_gearset:
        # print(starting_gearset[k])
        
        # Unequip gear you can't wear if it's already equipped.
        if main_job.lower() not in starting_gearset[slot]["Jobs"]:
            best_set[slot] = Empty

        # Unequip gear that is not selected to be tested, unless the player locked the slot by selecting nothing.
        if (starting_gearset[slot]["Name2"] not in check_gear[slot]) and len(check_gear[slot])>0:
            best_set[slot] = Empty
            
        # If testing a melee WS, do not find the best ranged weapon unless it is an instrument. This does not apply to RNG or COR who might want savage blade sets to test gun/bow options
        if ws_type=="melee" and main_job not in ["rng","cor"]:
            check_gear["ranged"] = [k for k in check_gear["ranged"] if k["Type"]=="Instrument"]

    # Define JSE earrings now. We'll use them later to prevent Balder's Earring+1 and a JSE+2 being equipped at the same time since we ignore right_ear requirement for testing.
    jse_ears1 = [k + " Earring +1" for k in ["Hattori", "Heathen's", "Lethargy", "Ebers", "Wicce", "Peltast's", "Boii", "Bhikku", "Skulkers", "Chevalier's", "Nukumi", "Fili", "Amini", "Kasuga", "Beckoner's", "Hashishin", "Chasseur's", "Karagoz", "Maculele", "Arbatel", "Azimuth", "Erilaz"]]
    jse_ears2 = [k + " Earring +2" for k in ["Hattori", "Heathen's", "Lethargy", "Ebers", "Wicce", "Peltast's", "Boii", "Bhikku", "Skulkers", "Chevalier's", "Nukumi", "Fili", "Amini", "Kasuga", "Beckoner's", "Hashishin", "Chasseur's", "Karagoz", "Maculele", "Arbatel", "Azimuth", "Erilaz"]]
    jse_ears = jse_ears1+jse_ears2

    Best_Gearset = starting_gearset.copy()

    pdt = 200 # How much PDT the set has
    mdt = 200

    conditional_converge_count = 0 # Break out of the loop if converged.
    pdt_old = 200 # Used to check if the automatic set finder gets stuck trying to find a set that doesn't exist. Compare this value to the old value. If no change in 3 consecutive iterations, then break out.
    mdt_old = 200

    pdt_thresh = pdt_requirement # How much PDT the final set is aiming for, taken from the user input.
    mdt_thresh = mdt_requirement

    pdt_thresh_temp = 200 # How much PDT the current new set must have to be accepted. The starting values are high to ensure that the code enters the loop to begin with.
    mdt_thresh_temp = 200


    while pdt > pdt_thresh or mdt > mdt_thresh:
        # print(f"\nChecking conditions: PDT:{pdt_thresh_temp},  MDT:{mdt_thresh_temp}")

        # Reset some variables between PDT/MDT iterations.

        best_metric = 0.01 # Metric used to find the best set. This part of the code exclusively looks for "highest number".

        for z in range(n_iter):
            print(f"Current iteration: {z+1}")
            
            converged_set = best_set.copy() # The loop is considered converged if the set after a full iteration is the same as this set (no improvements were found).

            # A list of items in each slot that are within some % of the best item in that slot.
            swaps = {"ammo":[],"head":[],"neck":[],"ear1":[],"ear2":[],"body":[],"hands":[],"ring1":[],"ring2":[],"waist":[],"legs":[],"feet":[]}

            # Randomize the order that we check gear slots in
            check_slots = np.array([k for k in check_gear])
            np.random.shuffle(check_slots)

            # For now, the code will only support two simultaneous swaps. Adding a third requires only adding a new for loop, but it adds a significant amount of computation time.
            for i1, slot1 in enumerate(check_slots): 
                for i2, slot2 in enumerate(check_slots):

                    # Do not check duplicate sets.
                    if i2 < i1:
                        continue
                    
                    # Only check single item swaps if fitn==1
                    if fitn==1:
                        if i2 != i1:
                            continue

                    test_set = best_set.copy()
                    
                    # Randomize the order that the gear in each slot is checked.
                    np.random.shuffle(check_gear[slot1])
                    np.random.shuffle(check_gear[slot2])

                    for j1,item1 in enumerate(check_gear[slot1]):
                        for j2,item2 in enumerate(check_gear[slot2]):

                            if (slot1==slot2) and (item1!=item2): # Do not try to equip two different items in the same slot.
                                continue

                            if (main_job not in item1["Jobs"]) or (main_job not in item2["Jobs"]): # Do not equip items your main job can not use.
                                continue

                            if (item1==best_set[slot1]) or (item2==best_set[slot2]): # If an item is already equipped in one of the slots, then skip the iteration. I let the "item1==item2" cases handle single-item swaps.
                                continue

                            # Equip the items and check that the test_set is valid.
                            test_set[slot1] = item1
                            test_set[slot2] = item2


                            if (test_set["ring1"]==test_set["ring2"]) and (test_set["ring1"]["Name"]!="Empty"): # Do not try to equip a second unique ring (unless the item is "Empty").
                                continue
                            if (test_set["ear1"]==test_set["ear2"]) and (test_set["ear1"]["Name"]!="Empty"): # Do not try to equip a second unique earring (unless the item is "Empty").
                                continue
                            if (test_set["main"]==test_set["sub"]) and (test_set["main"]["Name"]!="Empty"): # Do not try to equip a unique weapon (unless the item is "Empty").
                                continue
                            #print("test1")

                            # Do not test 1-handed weapons with grips.
                            one_handed = ["Axe", "Club", "Dagger", "Sword", "Katana"]
                            if (test_set["main"]["Skill Type"] in one_handed) and (test_set["sub"]["Type"] == "Grip"):
                                continue
                            #print("test2")

                            # Do not allow 2-handed weapons with shields or 1-handed weapons.
                            two_handed = ["Great Sword", "Great Katana", "Great Axe", "Polearm", "Scythe", "Staff"]
                            if (test_set["main"]["Skill Type"] in two_handed) and (test_set["sub"]["Type"]=="Weapon" or test_set["sub"]["Type"]=="Shield"):
                                continue
                            #print("test3")

                            # Do not allow a hand-to-hand weapon with an off-hand item.
                            if (test_set["main"]["Skill Type"] == "Hand-to-Hand") and (test_set["sub"]["Name"] != "Empty"):
                                continue

                            #print("test4")

                            archery = ["Empyreal Arrow", "Flaming Arrow", "Namas Arrow","Jishnu's Radiance","Apex Arrow","Refulgent Arrow","Sidewinder","Blast Arrow","Piercing Arrow"]
                            marksmanship = ["Last Stand","Hot Shot","Leaden Salute","Wildfire","Coronach","Trueflight", "Detonator","Blast Shot","Slug Shot","Split Shot"]
                            if (action_type=="weapon skill") and (ws_name in archery+marksmanship):
                                # If using a ranged weapon skill, ensure that the weapon and ammo type match the weapon skill.

                                if (ws_name in archery) and (test_set["ranged"]["Skill Type"]!="Archery" or test_set["ammo"]["Type"]!="Arrow"):
                                    continue
                                
                                if (ws_name in marksmanship) and (test_set["ranged"]["Skill Type"]!="Marksmanship" or test_set["ammo"]["Type"] not in ["Bolt", "Bullet"]):
                                    continue

                                if (test_set["ranged"]["Type"]=="Crossbow") and (test_set["ammo"]["Type"]!="Bolt"):
                                    continue
                                if (test_set["ranged"]["Type"]=="Gun") and (test_set["ammo"]["Type"]!="Bullet"):
                                    continue
                            #print("test5")

                            # Ranged TP attacks require a ranged weapon and ammo to be equipped. We check that the ammo matches the weapon later.
                            if (action_type=="spell cast") and (spell_name=="Ranged Attack"):
                                if (test_set["ranged"]["Type"] not in ["Gun","Bow","Crossbow"]) or (test_set["ammo"]["Type"] not in ["Bullet","Arrow","Bolt"]):
                                    continue
                            #print("test6")

                            # Do not equip an ammo incompatible with your ranged weapon
                            if (test_set["ranged"]["Type"]=="Gun") and (test_set["ammo"].get("Type","None") not in ["Bullet","None"]):
                                continue
                            if (test_set["ranged"]["Type"]=="Bow") and (test_set["ammo"].get("Type","None") not in ["Arrow","None"]):
                                continue
                            if (test_set["ranged"]["Type"]=="Crossbow") and (test_set["ammo"].get("Type","None") not in ["Bolt","None"]):
                                continue
                            #print("test7")

                            # Do not equip a ranged weapon incompatible with your ammo
                            if (test_set["ammo"].get("Type","None")=="Bullet") and (test_set["ranged"].get("Type","None")!="Gun"):
                                continue
                            if (test_set["ammo"].get("Type","None")=="Arrow") and (test_set["ranged"].get("Type","None")!="Bow"):
                                continue
                            if (test_set["ammo"].get("Type","None")=="Bolt") and (test_set["ranged"].get("Type","None")!="Crossbow"):
                                continue
                            #print("test8")

                            if (test_set["ranged"].get("Type","None")=="Instrument") and (test_set["ammo"].get("Type","None")!="None"):
                                continue
                            #print("test9")

                            # Do not allow dual wielding unless the selected main job has native dual wield.
                            if (main_job not in ["nin", "dnc", "thf", "blu"] and sub_job not in ["nin", "dnc"]) and (test_set["sub"]["Type"] == "Weapon"):
                                    continue
                            #print("test10")

                            # Do not equip Balder Earring +1 and the JSE +2 ears at the same time. They both only work if in the right ear.
                            if (test_set["ear1"]["Name"] in jse_ears) and (test_set["ear2"]["Name"]=="Balder Earring +1"):
                                continue
                            if (test_set["ear2"]["Name"] in jse_ears) and (test_set["ear1"]["Name"]=="Balder Earring +1"):
                                continue
                            #print("test11")

                            # "Cannot equip headgear" armor is checked here.
                            if (test_set["body"]["Name"] in ["Cohort Cloak","Cohort Cloak +1","Crepuscular Cloak","Twilight Cloak"]) and (test_set["head"]["Name"]!="Empty"):
                                continue
                            #print("test12")

                            # Impact can only be casted with Twilight Cloak or Crepuscular Cloak
                            if action_type == "spell cast":
                                if (spell_name=="Impact") and (test_set["body"]["Name"] not in ["Crepuscular Cloak","Twilight Cloak"]):
                                    continue
                            #print("test13")

                            if action_type == "weapon skill":
                                # Some weapon skills can only be used with certain weapons.
                                if ws_name in restricted_ws:
                                    if (restricted_ws[ws_name]!=test_set["main"]["Name"]) and (restricted_ws[ws_name]!=test_set["ranged"]["Name"]):
                                        continue
                                #print("test14")

                                # Reject sets if their main-hand weapon or ranged weapon can't use the selected weapon skill.
                                if (ws_name not in ws_dict.get(test_set["main"]["Skill Type"],[])) and (ws_name not in ws_dict.get(test_set["ranged"]["Skill Type"],[])):
                                    continue
                                #print("test15")
                            
                            # At this point, the code should have a valid gear set to play with.



                            # Sets thats survive this long are valid and satisfy the temporary PDT/MDT requirements. We can now test the set.
                            player = create_player(main_job, sub_job, master_level, test_set, buffs, abilities)

                            # Don't even test the set if the DT requirement is not met in both PDT and MDT
                            pdt = player.stats.get("PDT",0) + player.stats.get("DT",0)
                            mdt = player.stats.get("MDT",0) + player.stats.get("DT",0)
                            pdt = -50 if pdt < -50 else pdt # Apply the 50% cap.
                            mdt = -50 if mdt < -50 else mdt
                            pdt += player.stats.get("PDT2",0) + player.stats.get("DT2",0)
                            mdt += player.stats.get("MDT2",0) + player.stats.get("DT2",0)
                            # for slot in test_set:   # TODO: Loop through gear and add MDT/PDT instead of creating a player class
                            #     pdt += test_set[slot].get("PDT2",0) # PDT2 breaks the cap.
                            #     mdt += test_set[slot].get("MDT2",0)
                            if pdt > pdt_thresh_temp or mdt > mdt_thresh_temp:
                                continue


                            # Prepare to test the set.
                            effective_tp = (max_tp + min_tp)/2 + player.stats.get("TP Bonus",0)
                            effective_tp = 1000 if effective_tp < 1000 else 3000 if effective_tp > 3000 else effective_tp

                            if action_type=="weapon skill":
                                decimals = 1
                                nondecimals = 8
                                metric_base, output = average_ws(player, enemy, ws_name, effective_tp, ws_type, input_metric)
                                invert = output[-1]
                                metric = metric_base**invert
                            elif action_type=="spell cast":
                                decimals = 1
                                nondecimals = 8
                                metric_base, output = cast_spell(player, enemy, spell_name, spell_type, input_metric)
                                invert = output[-1]
                                metric = metric_base**invert
                            elif action_type=="attack round":
                                decimals = 3 # How many decimals to show in the output.
                                nondecimals = 8
                                metric_base, output = average_attack_round(player, enemy, starting_tp, min_tp, input_metric)
                                invert = output[-1]
                                metric = metric_base**invert

                            else:
                                print(f"Unknown action_type  ({action_type})")
                                import sys; sys.exit()

                            metric = 0.01 if metric <= 0 else metric # Prevent divide-by-zero errors
                            if (metric > best_metric):
                                if item1==item2:
                                    print(f"[{slot1:<15s}]: [{best_set[slot1]['Name2']} ->  {item1['Name2']}   [{best_metric**invert:>{nondecimals}.{decimals}f} -> {metric**invert:>{nondecimals}.{decimals}f}]")
                                    best_set[slot1] = item1
                                else:
                                    print(f"[{slot1:<6s} & {slot2:<6s}]: [{best_set[slot1]['Name2']} & {best_set[slot2]['Name2']}] -> [{item1['Name2']} & {item2['Name2']}] [{best_metric**invert:>{nondecimals}.{decimals}f} -> {metric**invert:>{nondecimals}.{decimals}f}]")
                                    best_metric = metric
                                    best_set[slot1] = item1
                                    best_set[slot2] = item2
                                best_metric = metric
                                best_output = output
    
                            elif (item1==item2):
                                try:
                                    if (best_metric%metric / best_metric < (float(next_best_percent)/100)) and (slot1 not in ["main","sub","ranged","back"]):
                                        swaps[slot1].append([item1["Name2"],metric**invert])
                                except:
                                    # print(f"Error on \"{item1['Name2']}\" - Metric = {metric}  - Best Metric = {best_metric}")
                                    pass

            if best_set==converged_set: # If no improvement is found after one full iteration.
                # best_player = create_player(main_job, sub_job, master_level, best_set, buffs, abilities)
                # for k in best_player.gearset:
                #     print(k,best_player.gearset[k]["Name2"])
                # print(best_output)
                break # Break out of the main loop and check PDT/MDT conditions.

        best_player0 = create_player(main_job, sub_job, master_level, best_set, buffs, abilities) # TODO: Loop through gear and add MDT/PDT instead of creating a player class

        pdt = best_player0.stats.get("PDT",0) + best_player0.stats.get("DT",0)
        mdt = best_player0.stats.get("MDT",0) + best_player0.stats.get("DT",0)
        pdt = -50 if pdt < -50 else pdt
        mdt = -50 if mdt < -50 else mdt
        pdt += best_player0.stats.get("PDT2",0) + best_player0.stats.get("DT2",0)
        mdt += best_player0.stats.get("MDT2",0) + best_player0.stats.get("DT2",0)

        # for slot in best_set:
        #     pdt += best_set[slot].get("PDT2",0)
        #     mdt += best_set[slot].get("MDT2",0)


        # Compare the pdt and mdt values from this iteration with the previous iteration.
        if pdt == pdt_old and mdt == mdt_old:
            conditional_converge_count += 1
            if conditional_converge_count >= 3:
                print("Unable to find a set which satisfies the conditions better than the current set. Exiting.")
                break
        else:
            conditional_converge_count = 0

        # Save the PDT and MDT values from this iteration to compare with the next iteration.
        pdt_old = pdt
        mdt_old = mdt

        # Update the temporary PDT and MDT requirements so that the next set is slightly closer to the true requirements.
        pdt_thresh_temp = pdt - 1 if pdt-1 > pdt_thresh else pdt_thresh
        mdt_thresh_temp = mdt - 1 if mdt-1 > mdt_thresh else mdt_thresh
        
        print(f"Current best set: PDT:{pdt},  MDT:{mdt}")


    # At this point, we've found the best conditional set.

    # Swap the earrings to make sure the "Right Ear:" effect earrings show up in the ear2 slot.
    if best_set["ear1"]["Name"] in jse_ears+["Balder Earring +1"]:
        best_set["ear1"],best_set["ear2"] = best_set["ear2"],best_set["ear1"]

    # Record the stats for the best gear set.
    best_player = create_player(main_job, sub_job, master_level, best_set, buffs, abilities)


    header = {"weapon skill":ws_name,"spell cast":spell_name,"attack round":"Melee TP set"}[action_type]
    # Print a fancy output.
    print("==============================================================")
    print(f"Best   \"{input_metric}\"   \"{header}\"   set")
    print("==============================================================")
    for k in best_player.gearset:
        print(f"{k:>10s}  {best_player.gearset[k]['Name2']:<50s}")
    print()
    if action_type=="attack round":
        if input_metric=="Time to WS":
            print(f"Avg WS Time = {best_metric**invert:<{nondecimals}.{decimals}f} s")
            print(f"Avg TP per round = {best_output[1]:<5.1f} TP")
        else:
            print(f"Avg Damage per round = {best_output[0]:<{nondecimals}.{decimals}f} damage")
            print(f"Avg time per round = {best_output[2]:<5.1f} TP")
            print(f"Avg TP per round = {best_output[1]:<5.1f} TP")
    else:
        print(f"Avg Damage = {best_output[0]:<{nondecimals}.{decimals}f} damage")
        print(f"Avg TP return = {best_output[1]:<5.1f} TP")
    print("==============================================================")
    print("==============================================================")

    if print_swaps:
        print(f"\nList of potential swaps within {next_best_percent}% of the best set ({float(best_metric)**invert:<{nondecimals}.{decimals}f}):")
        for slot in swaps:
            for swap in swaps[slot]:
                line = f"{slot:<6s} {swap[0]:<50s} {float(swap[1]):<{nondecimals}.{decimals}f} {best_metric%swap[1]**invert/best_metric*100:>5.1f}%"
                print(line)

    return(best_player, best_output)

if __name__ == "__main__":

    main_job = sys.argv[1]
    sub_job = sys.argv[2]
    master_level = int(sys.argv[3])
    buffs = {}
    abilities = {}
    enemy = create_enemy(apex_toad)
    ws_name = "Blade: Metsu"
    spell_name = "Waterja"
    action_type = "weapon skill"
    starting_tp = 0
    min_tp = 1000
    max_tp = 1300
    check_gear = gear_dict
    starting_gearset = { "main" : Heishi,
                        'sub' : Crepuscular_Knife,
                        'ranged' : Empty,
                        'ammo' : Seki,
                        'head' : Malignance_Chapeau,
                        'body' : Tatenashi_Haramaki,
                        'hands' : Malignance_Gloves,
                        'legs' : Samnuha_Tights,
                        'feet' : Malignance_Boots,
                        'neck' : Ninja_Nodowa,
                        'waist' : Sailfi_Belt,
                        'ear1' : Dedition_Earring,
                        'ear2' : Telos_Earring,
                        'ring1' : Gere_Ring,
                        'ring2' : Epona_Ring,
                        'back' : np.random.choice([k for k in capes if "nin" in k["Jobs"] and "DEX Store TP" in k["Name2"] and "Ranged" not in k])}
    pdt_requirement = -50
    mdt_requirement = -21
    print_swaps = True
    next_best_percent = 1

    metric = "Damage Dealt"

    player, output = build_set(main_job, sub_job, master_level, buffs, abilities, enemy, ws_name, spell_name, action_type, starting_tp, min_tp, max_tp, check_gear, starting_gearset, pdt_requirement, mdt_requirement, metric, print_swaps, next_best_percent)
    print(player.stats)


    # TODO: If hit rate is < 20% in initial set, then begin by finding and equipping the max accuracy piece in each slot before finding the best set.
