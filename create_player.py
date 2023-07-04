# TODO thoughts:
#  Auspice checkbox
#  Enlight checkbox (Accuracy+20 on PLD) to go with the Endark checkbox
#
#
#
from enemies import *
class create_enemy:
    #
    # Create an enemy class so that we may modify its stats more easily.
    #
    def __init__(self,enemy):
        #
        #
        #
        self.name = enemy["Name"]
        self.location = enemy["Location"]
        self.stats = {}
        ignore_stats = ["Name","Location"] # Ignore the strings to create a dictionary of numeric values
        for stat in enemy:
            if stat not in ignore_stats:
                self.stats[stat] = enemy[stat]


class create_player:
    #
    # Python class used to build a dictionary of player stats.
    #
    # Attributes:
    #    main_job
    #    sub_job
    #    main_job_level
    #    sub_job_level
    #    gearset
    #    buffs
    #    abilities
    #    stats
    #
    def __init__(self, main_job, sub_job, master_level=20, gearset={}, buffs={}, abilities={},):
        #
        #
        #
        self.main_job = main_job
        self.sub_job = sub_job
        self.gearset = gearset
        self.buffs = buffs
        self.abilities = abilities
        self.master_level = 50 if master_level > 50 else 0 if master_level < 0 else master_level

        self.main_job_level = 99 # Assume Lv99 main job for now, but leave room to expand to arbitrary main jobs level later.
        self.sub_job_level = int(int(self.main_job_level/2) + self.master_level/5)

        # Create a dictionary to contain all of the stats provided to the character from their selected <main_job>, <sub_job>, traits, job points, and merits.
        self.stats = {}

        # Add base stats (ignoring gear or buffs).
        self.add_base_stats()

        # Add stats from gear
        self.add_gear_stats()

        # Add stats from buffs.
        self.add_buffs()

        # Finalize stats by using the BG Wiki equations to calculate stats such as attack and accuracy per weapon, evasion from skill, etc
        self.finalize_stats()

        # Sort the player stats alphabetically.
        self.stats = dict(sorted(self.stats.items()))

    def get_skill_accuracy(self, skill_level):
        #
        # Calculate accuracy from weapon-type skill.
        # The contribution from skill changes with different skill levels. We need to add the contributions separately
        #
        skill_accuracy = 0
        if skill_level > 200:
            skill_accuracy += int((min(skill_level,400)-200)*0.9) + 200
        else:
            skill_accuracy += skill_level
        if skill_level > 400:
            skill_accuracy += int((min(skill_level,600)-400)*0.8)
        if skill_level > 600:
            skill_accuracy += int((skill_level-600)*0.9)

        return(skill_accuracy)



    def finalize_stats(self,):
        #
        # Finalize the player stats. Create main/off-hand attacks/accuracies, increase Evasion based on skill/AGI, etc.
        # We ignore weapon skill bonuses (such as Blade: Shun's attack bonus) here.
        #

        # Define Dual Wield to simplify some code.
        dual_wield = self.gearset["sub"]["Type"] == "Weapon" or self.gearset["main"]["Skill Type"] == "Hand-to-Hand"

        # Increase the Evasion stat based on contribution from Evasion Skill and AGI. 
        # Evasion Skill is worth 0.8 Evasion after Evasion Skill > 300.
        # AGI is worth 0.5 Evasion.
        self.stats["Evasion"] = self.stats.get("Evasion",0) + int(0.5*self.stats.get("AGI",0)) + (300 + 0.8*(self.stats.get("Evasion Skill",0)-300) if self.stats.get("Evasion Skill",0) > 300 else self.stats.get("Evasion Skill",0))


        # Create "Attack1" for main-hand and "Attack2" for off-hand.
        # Off-hand attack uses STR/2
        main_skill = self.gearset["main"].get("Skill Type","None") + " Skill"
        sub_skill = self.gearset["sub"].get("Skill Type","None") + " Skill"
        self.stats["Attack1"] = 8 + self.stats.get(main_skill, 0) + self.stats["STR"] + self.stats.get("Attack",0) + self.stats.get(f"main {main_skill}", 0)
        self.stats["Attack2"] = 8 + self.stats.get(sub_skill, 0) + int(0.5*self.stats["STR"]) + self.stats.get("Attack",0) + self.stats.get(f"sub {sub_skill}",0)

        # Update Ranged Attack
        ranged_skill = self.gearset["ranged"].get("Skill Type","None") + " Skill"
        ammo_skill = self.gearset["ammo"].get("Skill Type","None") + " Skill"
        if ammo_skill=="Throwing Skill": # For Shuriken
            self.stats["Ranged Attack"] += 8 + self.stats.get(ammo_skill,0) + self.stats.get("STR",0)
        elif ranged_skill in ["Marksmanship Skill","Archery Skill"]:
            self.stats["Ranged Attack"] += 8 + self.stats.get(ranged_skill,0) + self.stats.get("STR",0)

        # Additive buffs to Attack and Accuracy from things like BRD have already been added.
        # We still need to add percent-based buffs such as Chaos Roll and Berserk. These have already been conveniently summed into the "Attack%" stat.
        self.stats["Attack1"] *= (1 + self.stats.get("Attack%",0))
        self.stats["Attack2"] *= (1 + self.stats.get("Attack%",0))
        self.stats["Ranged Attack"] *= (1 + self.stats.get("Ranged Attack%",0))

        # Attack from food applies after percent-based buffs, but the STR+ on food applies normally. We use the "Food Attack" stat to separate things.
        self.stats["Attack1"] += self.stats.get("Food Attack",0)
        self.stats["Attack2"] += self.stats.get("Food Attack",0)
        self.stats["Ranged Attack"] += self.stats.get("Food Ranged Attack",0)
        

        # Create "Accuracy1" for main-hand and "Accuracy2" for off-hand.
        main_skill_level = self.stats.get(main_skill,0) + self.stats.get(f"main {main_skill}",0)
        sub_skill_level = self.stats.get(sub_skill,0) + self.stats.get(f"sub {sub_skill}",0)
        ranged_skill_level = self.stats.get(ranged_skill,0)
        ammo_skill_level = self.stats.get(ammo_skill,0)

        self.stats["Accuracy1"] = int(0.75*(self.stats.get("DEX",0))) + self.stats.get("Accuracy",0) + self.get_skill_accuracy(main_skill_level)
        self.stats["Accuracy2"] = int(0.75*(self.stats.get("DEX",0))) + self.stats.get("Accuracy",0) + self.get_skill_accuracy(sub_skill_level)
        if ammo_skill=="Throwing Skill": # For Shuriken
            self.stats["Ranged Accuracy"] += int(0.75*(self.stats.get("AGI",0))) + self.get_skill_accuracy(ammo_skill_level)
        elif ranged_skill in ["Marksmanship Skill","Archery Skill"]:
            self.stats["Ranged Accuracy"] += int(0.75*(self.stats.get("AGI",0))) + self.get_skill_accuracy(ranged_skill_level)


        self.stats["Delay1"] = self.gearset["main"].get("Delay",480-self.stats.get("Martial Arts",0)) # Use base hand-to-hand delay if main-hand item does not have a Delay stat 
        self.stats["Delay2"] = self.gearset["sub"].get("Delay",self.stats["Delay1"]) # Copy main-hand delay if off-hand item does not have delay stat
        self.stats["Ranged Delay"] = self.gearset["ranged"].get("Delay",0)
        self.stats["Ammo Delay"] = self.gearset["ammo"].get("Delay",0)

        self.stats["DMG1"] = self.gearset["main"].get("DMG",0)
        self.stats["DMG2"] = self.gearset["sub"].get("DMG",0)
        self.stats["Ranged DMG"] = self.gearset["ranged"].get("DMG",0)
        self.stats["Ammo DMG"] = self.gearset["ammo"].get("DMG",0)

        # Zero-out stats that don't apply for the given gearset. We have already dealt with Smite/LastResort/Hasso requiring 2-handed weapons too.
        two_handed = ["Great Sword", "Great Katana", "Great Axe", "Polearm", "Scythe", "Staff"]
        if self.gearset["ammo"].get("Type","None")!="Shuriken":
            self.stats["Daken"] = 0
        if self.gearset["main"].get("Skill Type","None")!="Hand-to-Hand":
            self.stats["Kick Attacks"] = 0
            self.stats["Martial Arts"] = 0 # Technically we can fight with H2H while empty-handed, but my "Empty" gear uses "None" skill-type, which means no attack/accuracy from "Hand-to-Hand Skill" TODO-
        if self.gearset["main"]["Skill Type"] not in two_handed:
            self.stats["Zanshin"] = 0
        if (self.gearset["ranged"].get("Type") not in ["Gun","Bow","Crossbow"]) and (self.gearset["ammo"].get("Type","None") not in ["Bullet","Arrow","Bolt","Shuriken"]):
            self.stats["Ranged Attack"] = 0
            self.stats["Ranged Accuracy"] = 0
        if not self.abilities.get("True Shot",False): # Disable True Shot bonuses if True Shot is not enabled.
            self.stats["True Shot"] = 0

        # Treat off-hand stats when not dual wielding.
        if not dual_wield:
            self.stats["Attack2"] = 0
            self.stats["Accuracy2"] = 0
            self.stats["Delay2"] = self.stats["Delay1"]
            self.stats["Dual Wield"] = 0

        # Calculate total haste.
        self.stats["Gear Haste"] = self.stats.get("Gear Haste",0)/102.4
        self.stats["JA Haste"] = self.stats.get("JA Haste",0)/102.4
        self.stats["Magic Haste"] = self.stats.get("Magic Haste",0)
        total_haste = (self.stats["Gear Haste"] if self.stats["Gear Haste"] < 0.25 else 0.25) + (self.stats["JA Haste"] if self.stats["JA Haste"] < 0.25 else 0.25) + (self.stats["Magic Haste"] if self.stats["Magic Haste"] < 448./1024 else 448./1024)

        # Deal with the special case of Hand-to-Hand values.
        if self.gearset["main"]["Skill Type"] == "Hand-to-Hand":
            self.stats["Attack2"] = self.stats["Attack1"] - 0.5*self.stats["STR"]*(1+self.stats.get("Attack%",0))*0 # The off-hand H2H Attack might use STR/2 like normal weapons. This is ignored in the main code where I simply set attack1 = attack2 before calculating H2H damage.
            self.stats["Accuracy2"] = self.stats["Accuracy1"]
            self.gearset["sub"]["Skill Type"] = self.gearset["main"]["Skill Type"]
            base_dmg = 3 + int((self.stats.get("Hand-to-Hand Skill",0) + self.stats.get("main Hand-to-Hand Skill",0))*0.11)
            self.stats["DMG1"] = base_dmg + self.stats["DMG1"]
            self.stats["DMG2"] = self.stats["DMG1"]
            if self.abilities.get("Footwork",False):
                self.stats["Kick DMG"] = self.stats["DMG1"] + self.stats.get("Kick Attacks DMG",0) # Main-hand DMG adds to Kick DMG during Footwork. See [https://www.ffxiah.com/forum/topic/55864/new-monk-questions/#3600604] [https://www.ffxiah.com/forum/topic/36705/iipunch-monk-guide/213/#3368961] and [https://forum.square-enix.com/ffxi/threads/52969-August.-3-2017-%28JST%29-Version-Update]
            else:
                self.stats["Kick DMG"] = base_dmg + self.stats.get("Kick Attacks DMG",0) # Without Footwork, Kick DMG is your base damage (from Skill) and any gear with "Kick Attacks Attack" on it.
            base_delay0 = 480
            self.stats["Delay1"] += base_delay0
            self.stats["Delay2"] = self.stats["Delay1"]
            base_delay = self.stats["Delay1"]
            reduced_delay = (base_delay - self.stats.get("Martial Arts",0)) * (1 - total_haste)
            self.stats["Dual Wield"] = 0 # We set a "dual_wield" variable to True in the main code to trigger off-hand hits, but we need to make sure that the "Dual Wield" stat is zero, otherwise it will stack with Martial Arts for H2H weapons.
        else:
            base_delay = (self.stats["Delay1"] + self.stats["Delay2"])/2 
            reduced_delay = base_delay * ((1 - self.stats.get("Dual Wield",0)/100)) * (1 - total_haste)
            self.stats["Kick DMG"] = 0

        self.stats["Delay Reduction"] = (1 - reduced_delay/base_delay) if (1 - reduced_delay/base_delay) < 0.8 else 0.8

        # We'll apply caps to certain stats in the main code.

    # def add_buffs(self, main_job, sub_job, master_level, stats, gearset, buffs, abilities): # We don't need to pass any of this in because they are all already part of self. TODO: remove these arguments
    def add_buffs(self,):
        #
        # Add stats from buffs and job abilities.
        #
        # Add buffs from Food, COR, BRD, GEO, and WHM first.
        ignore_stats = ["Name","Name2","Type","DMG","Delay","Jobs","Skill Type","Rank"]
        for source in self.buffs:
            for stat in self.buffs[source]:
                if stat not in ignore_stats:
                    self.stats[stat] = self.stats.get(stat,0) + self.buffs[source][stat]

        jobs  = [self.main_job, self.sub_job]
        sub_job_level = int(99/2) + self.master_level/5
        two_handed = ["Great Sword", "Great Katana", "Great Axe", "Polearm", "Scythe", "Staff"]

        # Add buffs from individual job abilities.
        # ===========================================================================
        # ===========================================================================
        # Warrior abilities
        if "war" in jobs:
            if self.abilities.get("Warcry",False):
                if self.main_job=="war":
                    self.stats["Attack%"] = self.stats.get("Attack%",0) + 118./1024
                    self.stats["Attack"] = self.stats.get("Attack",0) + 60
                    self.stats["TP Bonus"] = self.stats.get("TP Bonus",0) + 500+200 # (5/5 Savagery Merits with Relic head)
                elif self.sub_job=="war":
                    self.stats["Attack%"] = self.stats.get("Attack%",0) + int(((self.sub_job_level)/4+4.75))/256.
            if self.abilities.get("Berserk",False):
                self.stats["Attack%"] = self.stats.get("Attack%",0) + 0.25 + 0.085*(self.gearset["main"]["Name"]=="Conqueror") + (100./1024)*(self.main_job=="war") # Warrior main gets +10% more attack with berserk.
                self.stats["Attack"] = self.stats.get("Attack",0) + 40*(self.main_job=="war")
                self.stats["Crit Rate"] = self.stats.get("Crit Rate",0) + 14*(self.gearset["main"]["Name"]=="Conqueror")
            if self.abilities.get("Aggressor",False):
                self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 25 + 20*(self.main_job=="war")
            if self.main_job=="war":
                if self.abilities.get("Mighty Strikes",False):
                    self.stats["Crit Rate"] = 100
                    self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 40
                if self.abilities.get("Blood Rage",False):
                    self.stats["Crit Rate"] = self.stats.get("Crit Rate",0) + 20 + 20
        # ===========================================================================
        # ===========================================================================
        # Monk abilities
        if "mnk" in jobs:
            if self.main_job=="mnk":
                if self.abilities.get("Focus",False):
                    self.stats["Crit Rate"] = self.stats.get("Crit Rate",0) + 20 
                    self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 100 + 20
                if self.abilities.get("Footwork",False):
                    self.stats["Kick Attacks"] = self.stats.get("Kick Attacks",0) + 20
                    self.stats["Kick Attacks Attack%"] = self.stats.get("Kick Attacks Attack%",0) + 100./1024 + 160./1024
                    self.stats["Kick Attack DMG"] = self.stats.get("Kick Attacks DMG",0) + 20 + 20 # Activating footwork increases Kick DMG by 20, with an additional 20 from job points
                if self.abilities.get("Impetus",False):
                    impetus_potency = 0.9
                    self.stats["Crit Rate"] = self.stats.get("Crit Rate",0) + 50*impetus_potency
                    self.stats["Attack"] = self.stats.get("Attack",0) + (100+40)*impetus_potency
                    self.stats["Crit Damage"] = self.stats.get("Crit Damage",0) + 50*impetus_potency*(self.gearset["body"]["Name"]=="Bhikku Cyclas +3")
                    self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 100*impetus_potency
        # ===========================================================================
        # ===========================================================================
        # Black Mage abilities
        if "blm" in jobs:
            if self.main_job=="blm":
                if self.abilities.get("Manafont",False):
                    self.stats["Magic Damage"] = self.stats.get("Magic Damage",0) + 60
                if self.abilities.get("Manawell",False):
                    self.stats["Magic Damage"] = self.stats.get("Magic Damage",0) + 20
        # ===========================================================================
        # ===========================================================================
        # Red Mage abilities
        if "rdm" in jobs:
            if self.main_job=="rdm":
                if self.abilities.get("Chainspell",False):
                    self.stats["Magic Damage"] = self.stats.get("Magic Damage",0) + 40
                if self.abilities.get("Composure",False):
                    self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 20
        # ===========================================================================
        # ===========================================================================
        # Thief abilities
        if "thf" in jobs:
            if self.main_job=="thf":
                if self.abilities.get("Conspirator",False): # Assuming 6 players on the enmity list.
                    self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 25 + 20
                    self.stats["Subtle Blow"] = self.stats.get("Subtle Blow",0) + 50
                    self.stats["Attack"] = self.stats.get("Attack",0) + 25*("Skulker's Vest" in self.gearset["body"]["Name"]) # Must be equipped for the extra Attack
        # ===========================================================================
        # ===========================================================================
        # Paladin abilities
        if "pld" in jobs:
            if self.main_job=="pld":
                if self.abilities.get("Divine Emblem",False):
                    self.stats["Magic Damage"] = self.stats.get("Magic Damage",0) + 40
                if self.abilities.get("Enlight II",False): # Assuming 600 Divine Magic Skill
                    enlight_potency = 0.80
                    self.stats["Accuracy"] = self.stats.get("Accuracy",0) + (120+20)*enlight_potency
        # ===========================================================================
        # ===========================================================================
        # Dark Knight abilities
        if "drk" in jobs:
            if self.abilities.get("Last Resort",False):
                self.stats["Attack%"] = self.stats.get("Attack%",0) + 256./1024 + 100./1024*(self.main_job=="drk")
                self.stats["Attack"] = self.stats.get("Attack",0) + 40*(self.main_job=="drk")
                self.stats["JA Haste"] = self.stats.get("JA Haste",0) + 15 + 10*(self.main_job=="drk") if self.gearset["main"]["Skill Type"] in two_handed else self.stats.get("JA Haste",0)
            if self.main_job=="drk":
                if self.abilities.get("Endark II",False): # Assuming 600 Dark Magic Skill
                    endark_potency = 0.80
                    self.stats["Accuracy"] = self.stats.get("Accuracy",0) + (20)*endark_potency
                    self.stats["Attack"] = self.stats.get("Attack",0) + (131+20)*endark_potency
        # ===========================================================================
        # ===========================================================================
        # Bard abilities
        if self.main_job=="brd":
            if self.buffs["brd"].get("Attack",0)>0:
                self.stats["Attack"] = self.stats.get("Attack",0) + 20 # Job Points give +20 extra attack if you have a Minuet up.
        # ===========================================================================
        # ===========================================================================
        # Ranger abilities
        if "rng" in jobs:
            if self.abilities.get("Sharpshot",False):
                self.stats["Ranged Accuracy"] = self.stats.get("Ranged Accuracy",0) + 40
                self.stats["Ranged Attack"] = self.stats.get("Ranged Attack",0) + 40*(self.main_job=="rng")
            if self.main_job == "rng":
                if self.abilities.get("Barrage",False):
                    self.stats["Ranged Attack"] = self.stats.get("Ranged Attack",0) + 60
                if self.abilities.get("Velocity Shot",False):
                    self.stats["Ranged Attack"] = self.stats.get("Ranged Attack",0) + 40
                    self.stats["JA Haste"] = self.stats.get("JA Haste",0) - 15
                    self.stats["Ranged Attack%"] = self.stats.get("Ranged Attack%",0) + 152./1024 + 112./1024*("Amini Caban" in self.gearset["body"]["Name"]) + 20./1024*("Belenus" in self.gearset["back"]["Name"])
                if self.abilities.get("Double Shot",False):
                    self.stats["Double Shot"] = self.stats.get("Double Shot",0) + 40 + 5*("Arcadian Jerkin" in self.gearset["body"]["Name"])
                    if "Arcadian Jerkin" in self.gearset["body"]["Name"]: # Half of your Double Shot becomes Triple Shot with the relic body equipped. This ratio is assumed from the Triple>Quad ratio for COR linked below.
                        self.stats["Triple Shot"] = self.stats.get("Double Shot",0)/2 # The way this is written will overwrite "Triple Shot" from Oshosi. This is intentional since I believe that RNG can't proc Triple Shot on Oshosi and COR can't proc Double Shot on Oshosi
                        self.stats["Double Shot"] = self.stats.get("Double Shot",0)/2
                else:
                    self.stats["Double Shot"] = 0 + 5*("Arcadian Jerkin" in self.gearset["body"]["Name"])
                    self.stats["Triple Shot"] = 0
                if self.abilities.get("Hover Shot",False): # We double damage dealt with Hover Shot enabled in the main code.
                    self.stats["Ranged Accuracy"] = self.stats.get("Ranged Accuracy",0) + 100
                    self.stats["Magic Accuracy"] = self.stats.get("Magic Accuracy",0) + 100
        # ===========================================================================
        # ===========================================================================
        # Samurai abilities
        if "sam" in jobs:
            if self.abilities.get("Hasso",False) and (self.gearset["main"]["Skill Type"] in two_handed):
                if self.main_job=="sam":
                    self.stats["STR"] = self.stats.get("STR",0) + 14 + 20 
                    self.stats["Zanshin"] = 100 if self.stats.get("Zanshin",0) > 100 else self.stats.get("Zanshin",0)
                    self.stats["Zanhasso"] = self.stats.get("Zanshin",0)*0.35
                else:
                    self.stats["STR"] = self.stats.get("STR",0) + int(self.sub_job_level/7)

                self.stats["JA Haste"] = self.stats.get("JA Haste",0) + 10 + self.stats.get("Hasso+ JA Haste",0)
                self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 10
        # ===========================================================================
        # ===========================================================================
        # Ninja abilities
        if self.main_job=="nin":
            if self.abilities.get("Sange",False) and self.gearset["ammo"]["Type"]=="Shuriken":
                self.stats["Ranged Accuracy"] = self.stats.get("Ranged Accuracy",0) + 100 # Assume 5/5 Sange Merits
                self.stats["Daken"] = 100
            if self.abilities.get("Innin",False):
                innin_potency = 0.7
                self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 20 
                self.stats["Skillchain Bonus"] = self.stats.get("Skillchain Bonus",0) + 5
                self.stats["Magic Burst Damage Trait"] = self.stats.get("Magic Burst Damage Trait",0) + 5
                self.stats["Crit Rate"] = self.stats.get("Crit Rate",0) + (innin_potency*(30-10) + 10)
                self.stats["Ninjutsu Damage%"] = self.stats.get("Ninjutsu Damage%",0) + (innin_potency*(30-10) + 10)
                self.stats["Evasion"] = self.stats.get("Evasion",0) + (innin_potency*(-30 - -10) + -10)
            if self.abilities.get("Futae",False):
                self.stats["Ninjutsu Magic Damage"] = self.stats.get("Ninjutsu Magic Damage",0) + 100
        # ===========================================================================
        # ===========================================================================
        # Blue Mage abilities
        if self.main_job=="blu":
            if self.abilities.get("Nature's Meditation",False):
                self.stats["Attack%"] = self.stats.get("Attack%",0) + 0.20
        # ===========================================================================
        # ===========================================================================
        # Corsair abilities
        if self.main_job == "cor":
            if self.abilities.get("Triple Shot",False):
                self.stats["Triple Shot"] = self.stats.get("Triple Shot",0) + 40
                if "Lanun Gants" in self.gearset["hands"]["Name"]: # Half of your Triple Shot becomes Quad Shot with Relic Hands. See: (https://www.ffxiah.com/forum/topic/31312/the-pirates-lair-a-guide-to-corsair/154/#3323623) and (http://wiki.ffo.jp/html/30818.html)
                    self.stats["Quad Shot"] = self.stats.get("Triple Shot",0)/2 
                    self.stats["Triple Shot"] = self.stats.get("Triple Shot",0)/2
            else:
                self.stats["Triple Shot"] = 0
                self.stats["Quad Shot"] = 0

        # ===========================================================================
        # ===========================================================================
        # Dancer abilities. We already assumed Haste Samba is always active in the "job-specific stats from spells and abilities" section above.
        if self.main_job=="dnc":
            if self.abilities.get("Building Flourish",False):
                self.stats["Crit Rate"] = self.stats.get("Crit Rate",0) + 10
                self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 40
                self.stats["Attack%"] = self.stats.get("Attack%",0) + 0.25
                self.stats["Weapon Skill Damage"] = self.stats.get("Weapon Skill Damage",0) + self.stats.get("Building Flourish WSD",0)
            if self.abilities.get("Climactic Flourish",False):
                self.stats["Crit Rate"] = self.stats.get("Crit Rate",0) + 10
                self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 40
                self.stats["Attack%"] = self.stats.get("Attack%",0) + 0.25
                self.stats["Weapon Skill Damage"] = self.stats.get("Weapon Skill Damage",0) + 20
            # We deal with Climactic, Striking, and Ternary Flourish in the main code since they are special cases that apply some stuff only to the first hit.
            if self.abilities.get("Saber Dance",False):
                self.stats["DA"] = self.stats.get("DA",0) + 25 # Assume minimum potency Saber Dance since it decays quickly.
        # ===========================================================================
        # ===========================================================================
        # Scholar abilities.
        if self.main_job=="sch":
            if self.abilities.get("Ebullience",False):
                self.stats["Magic damage"] = self.stats.get("Magic Damage",0) + 40 # We deal with the damage bonus from Ebullience in the main code.
            if self.abilities.get("Enlightenment",False):
                self.stats["INT"] = self.stats.get("INT",0) + 20
                self.stats["MND"] = self.stats.get("MND",0) + 20
        if "sch" in [self.main_job, self.sub_job]:
            if self.abilities.get("Klimaform",False): 
                self.stats["Magic Accuracy"] = self.stats.get("Magic Accuracy",0) + 15 # SCH Empy+3 feet provide damage+ with klimaform active. We deal with that in the main code.

        # ===========================================================================
        # ===========================================================================
        # Geomancer abilities.
        if self.main_job=="geo":
            if self.abilities.get("Theurgic Focus",False):
                self.stats["-ra Magic Attack"] = self.stats.get("-ra Magic Attack",0) + 50
                self.stats["-ra Magic damage"] = self.stats.get("-ra Magic Damage",0) + 60
        # ===========================================================================
        # ===========================================================================
        # Rune Fencer abilities.
        if "run" in jobs:
            if self.abilities.get("Swordplay",False):
                swordplay_potency = 0.9 # Assume 90% potency
                self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 60*swordplay_potency
                self.stats["Evasion"] = self.stats.get("Evasion",0) + 60*swordplay_potency
        # ===========================================================================
        # ===========================================================================


        # Add Smite and Fencer now.
        if self.gearset["main"]["Skill Type"] in (two_handed+["Hand-to-Hand"]):
            smite_level = self.stats.get("Smite",0)
            self.stats["Attack%"] = self.stats.get("Attack%",0) + {5:304./1024, 4:256./1024, 3:204./1024, 2:152./1024, 1:100./1024, 0:0.}[smite_level]
        if (self.gearset["sub"]["Type"] in ["Shield","None"]) and (self.gearset["main"]["Skill Type"]!="Hand-to-Hand") and (self.gearset["main"]["Skill Type"] not in two_handed):
            fencer_level = 8 if self.stats.get("Fencer",0) > 8 else self.stats.get("Fencer",0)
            fencer_bonuses = {0:[0,0], 1:[200,3], 2:[300,5], 3:[400,7], 4:[450,9], 5:[500,10], 6:[550,11], 7:[600,12], 8:[630,13]}[fencer_level]
            self.stats["TP Bonus"] = self.stats.get("TP Bonus",0) + fencer_bonuses[0]
            self.stats["Crit Rate"] = self.stats.get("Crit Rate",0) + fencer_bonuses[1]

        aftermath_level = self.abilities.get("Aftermath",0)
        main_wpn_name = self.gearset["main"]["Name"]
        ranged_wpn_name = self.gearset["ranged"]["Name"]

        # Add Relic aftermath stats.
        if aftermath_level > 0:
            if main_wpn_name=="Mandau":
                self.stats["Crit Rate"] = self.stats.get("Crit Rate",0) + 5
                self.stats["Crit Damage"] = self.stats.get("Crit Damage",0) + 5
            elif main_wpn_name=="Ragnarok":
                self.stats["Crit Rate"] = self.stats.get("Crit Rate",0) + 10
                self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 15
            elif main_wpn_name=="Guttler":
                self.stats["Attack%"] = self.stats.get("Attack%",0) + 100./1024
            elif main_wpn_name=="Bravura":
                self.stats["DT"] = self.stats.get("DT",0) - 20
            elif main_wpn_name=="Apocalypse":
                self.stats["JA Haste"] = self.stats.get("JA Haste",0) + 10
                self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 15
            elif main_wpn_name=="Gungnir":
                self.stats["Attack%"] = self.stats.get("Attack%",0) + 50./1024
                self.stats["DA"] = self.stats.get("DA",0) + 5
            elif main_wpn_name=="Kikoku":
                self.stats["Attack%"] = self.stats.get("Attack%",0) + 100./1024
                self.stats["Subtle Blow"] = self.stats.get("Subtle Blow",0) + 10
            elif main_wpn_name=="Amanomurakumo":
                self.stats["Zanshin"] = self.stats.get("Zanshin",0) + 10
                self.stats["Store TP"] = self.stats.get("Store TP",0) + 10
            elif main_wpn_name=="Mjollnir":
                self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 20
                self.stats["Magic Accuracy"] = self.stats.get("Magic Accuracy",0) + 20
            elif main_wpn_name=="Claustrum":
                self.stats["DT"] = self.stats.get("DT",0) - 20
            elif ranged_wpn_name=="Yoichinoyumi":
                self.stats["Ranged Accuracy"] = self.stats.get("Ranged Accuracy",0) + 30
            elif ranged_wpn_name=="Annihilator":
                self.stats["Ranged Attack%"] = self.stats.get("Ranged Attack%",0) + 100./1024
            elif main_wpn_name=="Spharai":
                self.stats["Kick Attacks"] = self.stats.get("Kick Attacks",0) + 15
                self.stats["Subtle Blow"] = self.stats.get("Subtle Blow",0) + 10

            # Add Mythic Aftermath to stats, assuming 85% potency for Lv1 and Lv2
            mythic_am_scaling = 0.85
            myth99max = (99-40)*mythic_am_scaling + 40 
            myth49max = (49-30)*mythic_am_scaling + 30
            mythic_am_dict = {"Conqueror":[  ["Accuracy",myth49max], ["Attack",myth99max]   ],
                            "Glanzfaust":[  ["Accuracy",myth49max], ["Attack",myth99max]   ],
                            "Vajra":[  ["Accuracy",myth49max], ["Attack",myth99max]   ],
                            "Gastraphetes":[  ["Ranged Accuracy",myth49max], ["Ranged Attack",myth99max]   ],
                            "Death Penalty":[  ["Ranged Accuracy",myth49max], ["Ranged Attack",myth99max]   ],
                            "Vajra":[  ["Accuracy",myth49max], ["Attack",myth99max]   ],
                            "Burtgang":[  ["Accuracy",myth49max], ["Attack",myth99max]   ],
                            "Liberator":[  ["Accuracy",myth49max], ["Attack",myth99max]   ],
                            "Aymur":[  ["Accuracy",myth49max], ["Attack",myth99max]   ],
                            "Kogarasumaru":[  ["Accuracy",myth49max], ["Attack",myth99max]   ],
                            "Nagi":[  ["Accuracy",myth49max], ["Attack",myth99max]   ],
                            "Nirvana":[  ["Accuracy",myth49max], ["Attack",myth99max]   ],
                            "Ryunohige":[  ["Accuracy",myth49max], ["Attack",myth99max]   ],
                            "Tizona":[  ["Accuracy",myth49max], ["Magic Accuracy",myth49max]   ],
                            "Carnwenhan":[  ["Magic Accuracy",myth49max],["Accuracy",myth49max],    ],
                            "Yagrush":[  ["Magic Accuracy",myth49max],["Accuracy",myth49max],    ],
                            "Laevateinn":[  ["Magic Accuracy",myth49max],["Magic Attack",myth49max],    ],
                            "Tupsimati":[  ["Magic Accuracy",myth49max],["Magic Attack",myth49max],    ],
                            "Idris":[  ["Magic Accuracy",myth49max],["Magic Attack",myth49max],    ],
                            "Murgleis":[  ["Magic Accuracy",myth49max],["Magic Attack",myth49max],    ],
                            "Kenkonken":[  ["Accuracy",myth49max], ["Attack",myth99max]   ],
                            "Terpsichore":[  ["Accuracy",myth49max], ["Attack",myth99max]   ],
                            "Epeolatry":[  ["Accuracy",myth49max], ["Attack",myth99max]   ]
            }
            if main_wpn_name in mythic_am_dict and aftermath_level>0: # Melee Mythic aftermath check. We add other forms of OAX later with similar formats.
                if aftermath_level==3:
                    self.stats["OA2 main"] = self.stats.get("OA2 main",0) + 40
                    self.stats["OA3 main"] = self.stats.get("OA3 main",0) + 20
                else:
                    self.stats[mythic_am_dict[main_wpn_name][aftermath_level-1][0]] = self.stats.get(mythic_am_dict[main_wpn_name][aftermath_level-1][0],0) + mythic_am_dict[main_wpn_name][aftermath_level-1][1]
            if ranged_wpn_name in mythic_am_dict and aftermath_level in [1,2]: # Ranged Mythic aftermath check. We deal with Lv2 later in the main code when calculating damage.
                    self.stats[mythic_am_dict[ranged_wpn_name][aftermath_level-1][0]] = self.stats.get(mythic_am_dict[ranged_wpn_name][aftermath_level-1][0],0) + mythic_am_dict[ranged_wpn_name][aftermath_level-1][1]

            # Prime weapon aftermath effects.  
            prime_aftermath_pdl = [0.02, 0.05, 0.08] # PDL gained from aftermath on prime weapons. https://www.ffxiah.com/forum/topic/57318/prime-ws-information-testing-discussion/12/#3668875
            prime_aftermath_mdmg = [20, 20, 20] # Magic Damage gained from aftermath on prime weapons. Needs testing
            prime_aftermath_matk = [20, 20, 20] # Magic Attack Bonus gained from aftermath on prime weapons. Needs testing
            prime_aftermath_potency = 0.6 # Assume 60% potency for Lv1 and Lv2 aftermath (WSing at 1600 TP and 2600 TP)

            if aftermath_level==1:
                prime_pdl = (prime_aftermath_pdl[1] - prime_aftermath_pdl[0])*prime_aftermath_potency + prime_aftermath_pdl[0]
                prime_mdmg = (prime_aftermath_mdmg[1] - prime_aftermath_mdmg[0])*prime_aftermath_potency + prime_aftermath_mdmg[0]
                prime_matk = (prime_aftermath_matk[1] - prime_aftermath_matk[0])*prime_aftermath_potency + prime_aftermath_matk[0]
            elif aftermath_level==2:
                prime_pdl = (prime_aftermath_pdl[2] - prime_aftermath_pdl[1])*prime_aftermath_potency + prime_aftermath_pdl[1]
                prime_mdmg = (prime_aftermath_mdmg[2] - prime_aftermath_mdmg[1])*prime_aftermath_potency + prime_aftermath_mdmg[1]
                prime_matk = (prime_aftermath_matk[2] - prime_aftermath_matk[1])*prime_aftermath_potency + prime_aftermath_matk[1]
            elif aftermath_level==3:
                prime_pdl = prime_aftermath_pdl[2]
                prime_mdmg = prime_aftermath_mdmg[2]
                prime_matk = prime_aftermath_matk[2]

            prime_am_dict = {"Caliburnus":[["PDL",prime_pdl]],
                            "Dokoku":[["PDL",prime_pdl]],
                            "Earp":[["PDL",prime_pdl]],
                            "Foenaria":[["PDL",prime_pdl]],
                            "Gae Buide":[["PDL",prime_pdl]],
                            "Helheim":[["PDL",prime_pdl]],
                            "Kusanagi-no-Tsurugi":[["PDL",prime_pdl]],
                            "Laphria":[["PDL",prime_pdl]],
                            "Lorg Mor":[["Magic Damage",prime_mdmg]],
                            "Mpu Gandring":[["PDL",prime_pdl]],
                            "Opashoro":[["Magic Damage",prime_mdmg],["Magic Attack",prime_matk]],
                            "Pinaka":[["PDL",prime_pdl]],
                            "Spalirisos":[["PDL",prime_pdl]],
                            "Varga Purnikawa":[["PDL",prime_pdl]],
            }
            if main_wpn_name in prime_am_dict and aftermath_level>0:
                for stat in prime_am_dict[main_wpn_name]:
                    self.stats[stat[0]] = self.stats.get(stat[0],0) + stat[1]

            # Empyrean Aftermath is entirely handled in the main code when calculating damage.

        # Add WHM Auspice checkbox here. TODO
        if self.abilities.get("Auspice",False):
            self.stats["Subtle Blow"] = self.stats.get("Subtle Blow",0) + 29

        if self.abilities.get("Shell V",False):
            self.stats["MDT"] = self.stats.get("MDT",0) - 29


    # def add_gear_stats(self, stats, gearset):
    def add_gear_stats(self,):
        #
        # Add stats from the equipped gear, including set bonuses at the end.
        #
        # A list of stats to not include in <stats>. These do not affect player stats. We will use DMG and Delay in the main code later to calculate damage, though.
        ignore_stats = ["Name","Name2","Type","DMG","Delay","Jobs","Skill Type","Rank"]
        for slot in self.gearset:
            for stat in self.gearset[slot]:
                if stat=="Triple Shot" and self.main_job=="rng": # Skip Triple Shot bonuses on Oshosi for RNG
                    continue
                if stat=="Double Shot" and self.main_job=="cor": # Skip Double Shot bonuses on Oshosi for COR
                    continue
                if stat not in ignore_stats:
                    # A list of combat skills to ignore when seen in the main or sub slots. These skills apply only to their respective slots on weapons so we create a new stat for them.
                    ignore_main_sub_skills = ["Hand-to-Hand Skill","Dagger Skill","Sword Skill","Great Sword Skill","Axe Skill","Great Axe Skill","Scythe Skill","Polearm Skill","Katana Skill","Great Katana Skill","Club Skill","Staff Skill","Evasion Skill","Divine Magic Skill","Elemental Magic Skill","Dark Magic Skill","Ninjutsu Skill","Summoning Magic Skill","Blue Magic Skill","Magic Accuracy Skill"]
                    if not (slot in ["main","sub"] and stat in ignore_main_sub_skills):
                        if stat in ["OA8","OA7","OA6","OA5","OA4","OA3","OA2"]: # OAX stats apply only to the weapon they are attached to.
                            self.stats[f"{stat} {slot}"] = self.stats.get(f"{stat} {slot}",0) + self.gearset[slot][stat]
                        elif stat=="WSC":
                            self.stats[stat] = self.stats.get(stat,[]) + [self.gearset[slot][stat]]
                        else:
                            self.stats[stat] = self.stats.get(stat,0) + self.gearset[slot][stat]
                    else:
                        self.stats[f"{slot} {stat}"] = self.stats.get(f"{slot} {stat}",0) + self.gearset[slot][stat]

        # Count the number of set-bonus gear equipped.
        mummu_count = 0 # Mummu +2 gives DEX/AGI/VIT/CHR
        flamma_count = 0 # Flamma +2 gives STR/DEX/VIT
        mallquis_count = 0 # Mallquis +2 gives VIT/INT/MND
        ayanmo_count = 0 # Ayanmo +2 gives STR/VIT/MND
        regal_ring_count = 0 # Regal Ring with AF+3 gear gives Accuracy/Ranged Accuracy/Magic Accuracy.
        regal_earring_count = 0 # Regal Earring with AF+3 gear gives Accuracy/Ranged Accuracy/Magic Accuracy.
        adhemar_count = 0 # Adhemar +1 gives Crit Rate
        amalric_count = 0 # +10 Magic Attack for every piece of Amalric equipped after the first
        lustratio_count = 0 # +2 WSD for every piece of Amalric equipped after the first
        ryuo_count = 0 # +10 attack for every piece of Ryuo equipped after the first
        af_armor = {"war":"Pummeler","mnk":"anchorite","whm":"theophany","blm":"spaekona","rdm":"atrophy","thf":"pillager","pld":"reverence","drk":"ignominy","bst":"totomic","brd":"brioso","rng":"orion","sam":"wakido","nin":"hachiya","drg":"vishap","smn":"convoker","blu":"assimilator","cor":"laksamana","pup":"foire","dnc":"maxixi","sch":"academic","geo":"geomancy","run":"runeist"}
        for slot in self.gearset:
            if "Adhemar" in self.gearset[slot]["Name"] and "+1" in self.gearset[slot]["Name"]:
                adhemar_count += 1
            if "Amalric" in self.gearset[slot]["Name"] and "+1" in self.gearset[slot]["Name"]:
                amalric_count += 1
            if "Lustratio" in self.gearset[slot]["Name"] and "+1" in self.gearset[slot]["Name"]:
                lustratio_count += 1
            if "Ryuo" in self.gearset[slot]["Name"] and "+1" in self.gearset[slot]["Name"]:
                ryuo_count += 1

            if "Regal Ring" in [self.gearset["ring1"]["Name"], self.gearset["ring2"]["Name"]] and slot in ["head","body","hands","legs","feet"]:
                if af_armor[self.main_job] in self.gearset[slot]["Name"].lower():
                    regal_ring_count += 1
            if "regal earring" in [self.gearset["ear1"]["Name"], self.gearset["ear2"]["Name"]] and slot in ["head","body","hands","legs","feet"]:
                if af_armor[self.main_job] in self.gearset[slot]["Name"].lower():
                    regal_earring_count += 1

            if "Flamma" in self.gearset[slot]["Name"] and slot in ["head","body","hands","legs","feet","ring1","ring2"]:
                flamma_count += 1
            if "Mallquis" in self.gearset[slot]["Name"] and slot in ["head","body","hands","legs","feet","ring1","ring2"]:
                mallquis_count += 1
            if "Ayanmo" in self.gearset[slot]["Name"] and slot in ["head","body","hands","legs","feet","ring1","ring2"]:
                ayanmo_count += 1
            if "Mummu" in self.gearset[slot]["Name"] and slot in ["head","body","hands","legs","feet","ring1","ring2"]:
                mummu_count += 1
    
        # Each set bonus is limited to 5 items, even the Ambuscade sets which have 6 options.
        mallquis_count = 5 if mallquis_count > 5 else mallquis_count
        ayanmo_count = 5 if ayanmo_count > 5 else ayanmo_count
        flamma_count = 5 if flamma_count > 5 else flamma_count
        mummu_count = 5 if mummu_count > 5 else mummu_count
        regal_ring_count = 5 if regal_ring_count > 5 else regal_ring_count
        regal_earring_count = 5 if regal_earring_count > 5 else regal_earring_count

        self.stats["STR"] = self.stats.get("STR",0) + ((ayanmo_count)*8 if ayanmo_count >= 2 else 0) + ((flamma_count)*8 if flamma_count >= 2 else 0) 
        self.stats["DEX"] = self.stats.get("DEX",0) + ((mummu_count)*8 if mummu_count >= 2 else 0) + ((flamma_count)*8 if flamma_count >= 2 else 0) 
        self.stats["VIT"] = self.stats.get("VIT",0) + ((mummu_count)*8 if mummu_count >= 2 else 0) + ((flamma_count)*8 if flamma_count >= 2 else 0) + ((ayanmo_count)*8 if ayanmo_count >= 2 else 0) + ((mallquis_count)*8 if mallquis_count >= 2 else 0)
        self.stats["AGI"] = self.stats.get("AGI",0) + ((mummu_count)*8 if mummu_count >= 2 else 0)
        self.stats["INT"] = self.stats.get("INT",0) + ((mallquis_count)*8 if mallquis_count >= 2 else 0)
        self.stats["MND"] = self.stats.get("MND",0) + ((mallquis_count)*8 if mallquis_count >= 2 else 0) + ((ayanmo_count)*8 if ayanmo_count >= 2 else 0)
        self.stats["CHR"] = self.stats.get("CHR",0) + ((mummu_count)*8 if mummu_count >= 2 else 0)
        self.stats["Crit Rate"] = self.stats.get("Crit Rate",0) + (adhemar_count*2 if adhemar_count > 1 else 0)
        self.stats["Magic Attack"] = self.stats.get("Magic Attack",0) + ((amalric_count)*10 if amalric_count >= 2 else 0)
        self.stats["Weapon Skill Damage"] = self.stats.get("Weapon Skill Damage",0) + ((lustratio_count)*2 if lustratio_count >= 2 else 0)
        self.stats["Attack"] = self.stats.get("Attack",0) + ((ryuo_count)*10 if ryuo_count >= 2 else 0)
        self.stats["Accuracy"] = self.stats.get("Accuracy",0) + (regal_ring_count + regal_earring_count)*15
        self.stats["Ranged Accuracy"] = self.stats.get("Ranged Accuracy",0) + (regal_ring_count + regal_earring_count)*15
        self.stats["Magic Accuracy"] = self.stats.get("Magic Accuracy",0) + (regal_ring_count + regal_earring_count)*15


    # def add_base_stats(self, stats, main_job, sub_job, master_level=20):
    def add_base_stats(self,):
        #
        # Include base stats (without any gear or buffs) to the <stats> dictionary.
        #
        # ===========================================================================
        # ===========================================================================
        # Add base parameters for Lv99 <main_job> and <sub_job> with <master_level> master levels.
        job_parameters = {
            "war":{"STR":97, "DEX":93, "VIT":90, "AGI":93, "INT":84, "MND":84, "CHR":87,},
            "mnk":{"STR":93, "DEX":95, "VIT":97, "AGI":84, "INT":81, "MND":90, "CHR":87,},
            "whm":{"STR":90, "DEX":84, "VIT":90, "AGI":87, "INT":87, "MND":97, "CHR":93,},
            "blm":{"STR":84, "DEX":93, "VIT":84, "AGI":93, "INT":97, "MND":87, "CHR":90,},
            "rdm":{"STR":90, "DEX":90, "VIT":87, "AGI":87, "INT":93, "MND":93, "CHR":90,},
            "thf":{"STR":90, "DEX":97, "VIT":90, "AGI":95, "INT":93, "MND":81, "CHR":81,},
            "pld":{"STR":95, "DEX":87, "VIT":97, "AGI":81, "INT":81, "MND":93, "CHR":93,},
            "drk":{"STR":97, "DEX":93, "VIT":93, "AGI":90, "INT":93, "MND":81, "CHR":81,},
            "bst":{"STR":90, "DEX":97, "VIT":90, "AGI":95, "INT":93, "MND":81, "CHR":81,}, # TODO: Do these match THF by coincidence or are these placeholders?
            "brd":{"STR":90, "DEX":90, "VIT":90, "AGI":84, "INT":90, "MND":90, "CHR":95,},
            "rng":{"STR":87, "DEX":90, "VIT":90, "AGI":97, "INT":87, "MND":90, "CHR":87,},
            "smn":{"STR":0, "DEX":0, "VIT":0, "AGI":0, "INT":0, "MND":0, "CHR":0,},
            "sam":{"STR":93, "DEX":93, "VIT":93, "AGI":90, "INT":87, "MND":87, "CHR":90,},
            "nin":{"STR":93, "DEX":95, "VIT":93, "AGI":95, "INT":90, "MND":81, "CHR":84,},
            "drg":{"STR":95, "DEX":90, "VIT":93, "AGI":90, "INT":84, "MND":87, "CHR":93,},
            "blu":{"STR":87, "DEX":87, "VIT":87, "AGI":87, "INT":87, "MND":87, "CHR":87,},
            "cor":{"STR":87, "DEX":93, "VIT":87, "AGI":95, "INT":93, "MND":87, "CHR":87,},
            "pup":{"STR":87, "DEX":95, "VIT":90, "AGI":93, "INT":87, "MND":84, "CHR":93,},
            "dnc":{"STR":90, "DEX":93, "VIT":87, "AGI":95, "INT":84, "MND":84, "CHR":95,},
            "sch":{"STR":84, "DEX":90, "VIT":87, "AGI":90, "INT":95, "MND":90, "CHR":93,},
            "geo":{"STR":84, "DEX":90, "VIT":90, "AGI":87, "INT":95, "MND":95, "CHR":87,},
            "run":{"STR":93, "DEX":90, "VIT":87, "AGI":95, "INT":90, "MND":90, "CHR":84,},
        }
        subjob_parameters = {
            "war":{"STR":15, "DEX":12, "VIT":10, "AGI":12, "INT":7, "MND":7, "CHR":9,},
            "mnk":{"STR":12, "DEX":13, "VIT":15, "AGI":7, "INT":6, "MND":10, "CHR":9,},
            "whm":{"STR":10, "DEX":7, "VIT":10, "AGI":9, "INT":9, "MND":15, "CHR":12,},
            "blm":{"STR":7, "DEX":12, "VIT":7, "AGI":12, "INT":15, "MND":9, "CHR":10,},
            "rdm":{"STR":10, "DEX":10, "VIT":9, "AGI":9, "INT":12, "MND":12, "CHR":10,},
            "thf":{"STR":10, "DEX":15, "VIT":10, "AGI":13, "INT":12, "MND":6, "CHR":6,},
            "pld":{"STR":13, "DEX":9, "VIT":15, "AGI":6, "INT":6, "MND":12, "CHR":12,},
            "drk":{"STR":15, "DEX":12, "VIT":12, "AGI":10, "INT":12, "MND":6, "CHR":6,},
            "bst":{"STR":0, "DEX":0, "VIT":0, "AGI":0, "INT":0, "MND":0, "CHR":0,}, # Unknown parameter bonuses from BST
            "brd":{"STR":0, "DEX":0, "VIT":0, "AGI":0, "INT":0, "MND":0, "CHR":0,}, # Unknown parameter bonuses from BRD
            "rng":{"STR":9, "DEX":10, "VIT":10, "AGI":15, "INT":9, "MND":10, "CHR":9,},
            "smn":{"STR":7, "DEX":9, "VIT":7, "AGI":10, "INT":13, "MND":13, "CHR":13,},
            "sam":{"STR":12, "DEX":12, "VIT":12, "AGI":10, "INT":9, "MND":9, "CHR":10,},
            "nin":{"STR":12, "DEX":13, "VIT":12, "AGI":13, "INT":10, "MND":6, "CHR":7,},
            "drg":{"STR":13, "DEX":10, "VIT":12, "AGI":10, "INT":7, "MND":9, "CHR":12,},
            "blu":{"STR":9, "DEX":9, "VIT":9, "AGI":9, "INT":9, "MND":9, "CHR":9,},
            "cor":{"STR":9, "DEX":12, "VIT":9, "AGI":13, "INT":12, "MND":9, "CHR":9,},
            "pup":{"STR":9, "DEX":13, "VIT":10, "AGI":12, "INT":9, "MND":7, "CHR":12,},
            "dnc":{"STR":10, "DEX":12, "VIT":9, "AGI":13, "INT":7, "MND":7, "CHR":13,},
            "sch":{"STR":7, "DEX":9, "VIT":8, "AGI":9, "INT":13, "MND":9, "CHR":11,}, # TODO: These are apparently ML0 parameters (Lv49). Needs updated to ML20 (Lv53)
            "geo":{"STR":7, "DEX":10, "VIT":10, "AGI":8, "INT":13, "MND":13, "CHR":9,},
            "run":{"STR":12, "DEX":10, "VIT":9, "AGI":13, "INT":10, "MND":10, "CHR":7,},
            "none":{"STR":0, "DEX":0, "VIT":0, "AGI":0, "INT":0, "MND":0, "CHR":0,},    
        }
        for stat in job_parameters[self.main_job]:
            self.stats[stat] = self.stats.get(stat,0) + job_parameters[self.main_job][stat] + subjob_parameters[self.sub_job][stat] + self.master_level 

        # Traits are setup with the following format:  "job1": [[level1, tier1],[level2,tier2],[etc], "job2":[[level1,tier1],[level2,tier2],[etc]],"job3":etc.. With traits in decending order.
        traits = {"Accuracy":{"rng":[[96,73],[86,60],[70,48],[50,35],[30,22],[10,10]],"drg":[[76,35],[60,22],[30,10]],"dnc":[[76,35],[60,22],[30,10]],"run":[[90,35],[70,22],[50,10]]},
                  "Ranged Accuracy":{"rng":[[96,73],[86,60],[70,48],[50,35],[30,22],[10,10]],"drg":[[76,35],[60,22],[30,10]],"dnc":[[76,35],[60,22],[30,10]],"run":[[90,35],[70,22],[50,10]]},
                  "Attack":{"drk":[[99,96],[91,84],[83,72],[76,60],[70,48],[50,35],[30,22],[10,10]],"war":[[91,35],[65,22],[30,10]],"drg":[[91,22],[10,10]]},
                  "Ranged Attack":{"drk":[[99,96],[91,84],[83,72],[76,60],[70,48],[50,35],[30,22],[10,10]],"war":[[91,35],[65,22],[30,10]],"drg":[[91,22],[10,10]]},
                  "Barrage":{"rng":[[90,6],[70,5],[50,4],[30,3]]}, # Treat Barrage as a trait so we can adjust the number of extra shots based on level. 
                  "Conserve TP":{"drg":[[97,26],[84,24],[71,21],[58,18],[45,15]],"dnc":[[97,21],[87,17],[77,15]],"rng":[[91,18],[80,15]]},
                  "Crit Damage":{"thf":[[97,14],[91,11],[84,8],[78,5]],"dnc":[[99,11],[88,8],[80,5]],"drk":[[95,8],[85,5]]},
                  "Daken":{"nin":[[95,40],[70,35],[55,30],[40,25],[25,20]]},
                  "PDL Trait":{"drk":[[80,50],[70,40],[55,30],[40,20],[20,10]],"mnk":[[90,30],[60,20],[30,10]],"rng":[[90,30],[60,20],[30,10]],"drg":[[90,30],[60,20],[30,10]],"war":[[80,20],[40,10]],"sam":[[80,20],[40,10]],"bst":[[90,20],[45,10]],"pup":[[90,20],[45,10]],"dnc":[[90,20],[45,10]],"thf":[[50,10]],"nin":[[50,10]],"rdm":[[60,10]]},
                  "Ranged Crit Damage":{"rng":[[99,45],[90,40],[80,35],[70,30],[60,20],[50,10]]}, # Does not apply to weapon skills
                  "DA":{"war":[[99,18],[85,16],[75,14],[50,12],[25,10]]},
                  "Dual Wield":{"nin":[[85,35],[65,30],[45,25],[25,15],[10,10]],"dnc":[[80,30],[60,25],[40,15],[20,10]],"thf":[[98,25],[90,15],[83,10]]},
                  "Evasion":{"thf":[[88,72],[76,60],[70,48],[50,35],[30,22],[10,10]],"dnc":[[86,48],[75,35],[45,22],[15,10]],"pup":[[76,48],[60,35],[40,22],[20,10]]},
                  "Fencer":{"war":[[97,5],[84,4],[71,3],[58,2],[45,1]],"bst":[[94,3],[87,2],[80,1]],"brd":[[95,2],[85,1]]}, # Listed as tiers for now.
                  "Kick Attacks":{"mnk":[[76,14],[71,12],[51,10]]},
                  "Magic Burst Damage Trait":{"blm":[[97,13],[84,11],[71,9],[58,7],[45,5]],"sch":[[99,7],[89,7],[79,5]],"nin":[[90,7],[80,5]],"rdm":[[95,7],[85,5]]},
                  "Magic Attack":{"blm":[[91,40],[81,36],[70,32],[50,28],[30,24],[10,20]],"rdm":[[86,28],[40,24],[20,20]]},
                  "Magic Defense":{"run":[[99,22],[91,20],[76,18],[70,16],[50,14],[30,12],[10,10]],"whm":[[91,20],[81,18],[70,16],[50,14],[30,12],[10,10]],"rdm":[[96,14],[45,12],[25,10]]},
                  "Martial Arts":{"mnk":[[82,200],[75,180],[61,160],[46,140],[31,120],[16,100],[1,80]],"pup":[[97,160],[87,140],[75,120],[50,100],[25,80]]},
                  "Occult Acumen":{"drk":[[97,125],[84,100],[71,75],[58,50],[45,25]],"sch":[[98,75],[88,50],[78,25]],"blm":[[95,50],[85,25]]}, # Units: (TP / MP)
                  "Recycle":{"rng":[[50,30],[35,20],[20,10]],"cor":[[90,30],[65,20],[35,10]]},
                  "Skillchain Bonus":{"dnc":[[97,23],[84,20],[71,16],[58,12],[45,8]],"sam":[[98,16],[88,12],[78,8]],"nin":[[95,12],[85,8]],"mnk":[[95,12],[85,8]]},
                  "Smite":{"drk":[[95,5],[75,4],[55,3],[35,2],[15,1],],"war":[[95,3],[65,2],[35,1],],"mnk":[[80,2],[40,1],],"drg":[[80,2],[40,1],],"pup":[[40,1],]}, # Listed as tiers for now.
                  "Store TP":{"sam":[[90,30],[70,25],[50,20],[30,15],[10,10]]},
                  "Subtle Blow":{"mnk":[[91,25],[65,20],[40,15],[25,10],[5,5]],"nin":[[75,25],[60,20],[45,15],[30,10],[15,5]],"dnc":[[86,20],[65,15],[45,10],[25,5]]},
                  "TA":{"thf":[[95,6],[55,5]]},
                  "True Shot":{"rng":[[98,7],[88,5],[78,3]],"cor":[[95,5],[85,3]]},
                  "Weapon Skill Damage Trait":{"drg":[[95,21],[85,19],[75,17],[65,13],[55,10],[45,7]]},
                  "Zanshin":{"sam":[[95,50],[75,45],[50,35],[35,25],[20,15]]},
                  }
        for trait in traits:
            # Add <main_job> traits first so that <sub_job> traits do not overwrite them and they do not stack.
            if self.main_job in traits[trait]:
                for k in traits[trait][self.main_job]: # Loop through the tiers in decending order. Stop on the highest tier below or equal to your main job level.
                    if self.main_job_level >= k[0]:
                        self.stats[trait] = self.stats.get(trait,0) + k[1] # Directly add the <main_job> trait to player stats.
                        break
            # Add <sub_job> traits now.
             # Since we add traits immediately after base parameters, all stats should be 0 except those from <main_job> traits. This ordering ensures that we can cleanly compare <main_job> and <sub_job> trait tiers and keep only the highest without stacking them.
            if self.sub_job in traits[trait]:
                for k in traits[trait][self.sub_job]:
                    if self.sub_job_level >= k[0]:
                        self.stats[trait] = max(self.stats.get(trait,0), k[1]) # Only keep the highest tier trait between your <main_job> and <sub_job>.
                        break

        # BST gets +50 Accuracy from Tandem Strike traits when the pet is attacking the same target.
        if self.main_job=="bst":
            self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 50

        # ===========================================================================
        # ===========================================================================
        # Add combat skills for a level 99 <main_job>. We add merits later.
        job_combat_stats = {
                        "war":{"Hand-to-Hand Skill":334,"Dagger Skill":388,"Sword Skill":398,"Great Sword Skill":404,"Axe Skill":417,"Great Axe Skill":424,"Scythe Skill":404,"Polearm Skill":388,"Club Skill":388,"Staff Skill":398,"Archery Skill":334,"Marksmanship Skill":334,"Throwing Skill":334,"Evasion Skill":373,},
                        "mnk":{"Hand-to-Hand Skill":424,"Staff Skill":398,"Club Skill":378,"Throwing Skill":300,"Evasion Skill":404,},
                        "whm":{"Club Skill":404,"Staff Skill":378,"Throwing Skill":300,"Evasion Skill":300,"Divine Magic Skill":417},
                        "blm":{"Dagger Skill":334,"Scythe Skill":300,"Club Skill":378,"Staff Skill":388,"Throwing Skill":334,"Evasion Skill":300,"Elemental Magic Skill":424,"Dark Magic Skill":417,},
                        "rdm":{"Dagger Skill":398,"Sword Skill":398,"Club Skill":334,"Archery Skill":334,"Throwing Skill":265,"Evasion Skill":334,"Divine Magic Skill":300,"Elemental Magic Skill":378,"Dark Magic Skill":300,},
                        "thf":{"Hand-to-Hand Skill":300,"Dagger Skill":424,"Sword Skill":334,"Club Skill":300,"Archery Skill":368,"Marksmanship Skill":378,"Throwing Skill":334,"Evasion Skill":424,},
                        "pld":{"Sword Skill":424,"Club Skill":417,"Staff Skill":417,"Great Sword Skill":398,"Dagger Skill":368,"Polearm Skill":300,"Evasion Skill":373,"Divine Magic Skill":404,},
                        "drk":{"Dagger Skill":373,"Sword Skill":388,"Great Sword Skill":417,"Axe Skill":388,"Great Axe Skill":388,"Scythe Skill":424,"Club Skill":368,"Marksmanship Skill":300,"Evasion Skill":373,"Elemental Magic Skill":404,"Dark Magic Skill":417},
                        "bst":{"Dagger Skill":378,"Sword Skill":300,"Axe Skill":424,"Scythe Skill":368,"Club Skill":334,"Evasion Skill":373,},
                        "brd":{"Dagger Skill":388,"Sword Skill":368,"Club Skill":334,"Staff Skill":378,"Throwing Skill":300,"Evasion Skill":334,},
                        "rng":{"Dagger Skill":388,"Sword Skill":334,"Axe Skill":388,"Club Skill":300,"Archery Skill":424,"Marksmanship Skill":424,"Throwing Skill":368,"Evasion Skill":300,},
                        "smn":{"Dagger Skill":300,"Club Skill":378,"Staff Skill":398,"Evasion Skill":300,"Summoning Magic Skill":417,},
                        "sam":{"Dagger Skill":300,"Sword Skill":378,"Polearm Skill":388,"Great Katana Skill":424,"Club Skill":300,"Archery Skill":378,"Throwing Skill":378,"Evasion Skill":404,},
                        "nin":{"Hand-to-Hand Skill":300,"Dagger Skill":378,"Sword Skill":373,"Katana Skill":424,"Great Katana Skill":368,"Club Skill":300,"Archery Skill":300,"Marksmanship Skill":373,"Throwing Skill":424,"Evasion Skill":417,"Ninjutsu Skill":417,},
                        "drg":{"Dagger Skill":300,"Sword Skill":368,"Polearm Skill":424,"Club Skill":300,"Staff Skill":388,"Evasion Skill":388,},
                        "blu":{"Sword Skill":424,"Club Skill":388,"Evasion Skill":368,"Blue Magci Skill":424,},
                        "cor":{"Dagger Skill":404,"Sword Skill":388,"Marksmanship Skill":398,"Throwing Skill":378,"Evasion Skill":334,},
                        "pup":{"Hand-to-Hand Skill":424,"Dagger Skill":368,"Club Skill":334,"Throwing Skill":378,"Evasion Skill":398,},
                        "dnc":{"Dagger Skill":424,"Hand-to-Hand Skill":334,"Sword Skill":334,"Throwing Skill":378,"Evasion Skill":404,},
                        "sch":{"Dagger Skill":334,"Club Skill":378,"Staff Skill":378,"Throwing Skill":334,"Evasion Skill":300,"Divine Magic Skill":404,"Elemental Magic Skill":404,"Dark Magic Skill":404,},
                        "geo":{"Club Skill":404,"Staff Skill":378,"Dagger Skill":368,"Evasion Skill":334,"Elemental Magic Skill":404,"Dark Skill":373,},
                        "run":{"Great Sword Skill":424,"Sword Skill":417,"Great Axe Skill":398,"Axe Skill":388,"Club Skill":368,"Evasion Skill":404,"Divine Magic Skill":398,},
        }
        for stat in job_combat_stats[self.main_job]:
            self.stats[stat] = self.stats.get(stat,0) + job_combat_stats[self.main_job][stat] + self.master_level

        # ===========================================================================
        # ===========================================================================
        # Add stats from job merits.

        # Stats that are obtained through merits.
        job_merit_stats = {
                            "war":{"DA":5,},
                            "mnk":{"Kick Attacks":5,},
                            "whm":{},
                            "blm":{"Magic Attack":10, "Magic Accuracy":25,},
                            "rdm":{"Magic Accuracy":15+25,"Accuracy":25*0,},
                            "thf":{"TA":5,"Accuracy":15,"Ranged Accuracy":15,},
                            "pld":{},
                            "drk":{},
                            "bst":{},
                            "brd":{},
                            "rng":{},
                            "smn":{},
                            "sam":{"Zanshin":5,"Store TP":10,"Weapon Skill Damage":19,},
                            "nin":{"Subtle Blow":5,"Ninjutsu Magic Accuracy":25,"Ninjutsu Magic Attack":20+10,"Ninjutsu Magic Damage":0}, # Including +10 matk from group1 and +20 matk from group 2. 
                            "drg":{},
                            "blu":{},
                            "cor":{},
                            "pup":{},
                            "dnc":{}, # Ignoring Saber Dance, Fan Dance, and Closed Position.
                            "sch":{"Helix Magic Accuracy":15,"Helix Magic Attack":10},
                            "geo":{},
                            "run":{},
        }
        for stat in job_merit_stats[self.main_job]:
            self.stats[stat] = self.stats.get(stat,0) + job_merit_stats[self.main_job].get(stat,0)

        # Add +5% crit rate from merits and +5% and an additional 5% from the base crit chance
        self.stats["Crit Rate"] = self.stats.get("Crit Rate",0) + 5 + 5

        # Add +16 to all combat stats from merits.
        all_combat_skills = ["Hand-to-Hand Skill","Dagger Skill","Sword Skill","Great Sword Skill","Axe Skill","Great Axe Skill","Scythe Skill","Polearm Skill","Katana Skill","Great Katana Skill","Club Skill","Staff Skill","Archery Skill","Marksmanship Skill","Throwing Skill","Evasion Skill","Divine Magic Skill","Elemental Magic Skill","Dark Magic Skill","Ninjutsu Skill","Summoning Magic Skill","Blue Magic Skill",]
        for stat in all_combat_skills:
            self.stats[stat] = self.stats.get(stat,0) + 16

        # ===========================================================================
        # ===========================================================================
        # Add stats from job mastery, including job gifts and job point bonuses.
        # There could easily be typos here. These were all added manually by using ctrl+F on each job page for specific stat names within the Job Points sections.

        job_mastery_stats = {
                            "war":{"Accuracy":26, "Ranged Accuracy":26, "Attack":70, "Ranged Attack":70, "Magic Accuracy":36,"Fencer TP Bonus":230,"Crit Rate":10,"Crit Damage":10,"DA":10,"Evasion":36,"Magic Evasion":36,},
                            "mnk":{"Accuracy":41, "Ranged Accuracy":41, "Attack":40, "Ranged Attack":40, "Magic Accuracy":36,"Evasion":42,"Magic Evasion":36,"Subtle Blow":10,"Martial Arts":10,"Kick Attacks Attack":40,"Kick Attacks Accuracy":20},
                            "whm":{"Accuracy":14, "Ranged Accuracy":14, "Magic Accuracy":20+50, "Magic Attack":22,"Magic Defense":50,"Divine Magic Skill":36,},
                            "blm":{"Magic Burst Damage Trait":20+23, "Magic Accuracy":20, "Magic Damage":20+23, "Magic Defense":14, "Magic Attack":50, "Magic Evasion":42, "Magic Accuracy":32, "Elemental Magic Skill":36, "Dark Magic Skill":36,},
                            "rdm":{"Magic Attack":20+28,"Magic Accuracy":20+70,"Magic Defense":28,"Magic Evasion":56,"Accuracy":22,"Ranged Accuracy":22,}, # Composure Accuracy+20 is added later
                            "thf":{"Sneak Attack Bonus":20,"Trick Attack Bonus":20,"Attack":50,"Ranged Attack":50,"Evasion":70,"Accuracy":36,"Ranged Accuracy":36,"Magic Evasion":36,"Magic Accuracy":36,"TA":8,"Crit Damage":8,"Dual Wield":5,"TA Attack":20},
                            "pld":{"Accuracy":28,"Ranged Accuracy":28,"Attack":28,"Ranged Attack":28,"Evasion":22,"Magic Evasion":42,"Divine Magic Skill":36,"Magic Accuracy":42},
                            "drk":{"Attack":106,"Ranged Attack":106,"Evasion":22,"Magic Evasion":36,"Accuracy":22,"Ranged Accuracy":22,"Magic Accuracy":42,"Dark Magic Skill":36,"Crit Damage":8,"Weapon Skill Damage":8,},
                            "bst":{"Attack":70,"Ranged Attack":70,"Accuracy":36,"Ranged Accuracy":36,"Magic Evasion":36,"Magic Accuracy":36,"Fencer TP Bonus":230,"Evasion":36,},
                            "brd":{"Evasion":22,"Accuracy":21,"Ranged Accuracy":21,"Magic Defense":15,"Magic Evasion":36,"Magic Accuracy":36,},
                            "rng":{"Double Shot":20,"Attack":70,"Ranged Attack":70,"Evasion":14,"Accuracy":70,"Ranged Accuracy":70,"Magic Evasion":36,"Converve TP":15,"True Shot":8,"Ranged Crit Damage":8,"Barrage":1,"Barrage Ranged Attack":60,},
                            "smn":{"Magic Defense":22,"Magic Evasion":22,"Evasion":22,"Summoning Magic Skill":36,},
                            "sam":{"Attack":70,"Ranged Attack":70,"Evasion":36,"Accuracy":36,"Ranged Accuracy":36,"Magic Evasion":36,"Zanshin":10,"Zanshin Attack":40,"Store TP":8,"Skillchain Bonus":8,}, 
                            "nin":{"Ninjutsu Magic Damage":40,"Ninjutsu Magic Accuracy":20, "Attack":70,"Ranged Attack":70,"Evasion":64,"Accuracy":56,"Ranged Accuracy":56,"Magic Attack":28,"Magic Evasion":50,"Magic Accuracy":50,"Ninjutsu Skill":36,"Daken":14,"Weapon Skill Damage":5},
                            "drg":{"Attack":70,"Ranged Attack":70,"Evasion":36,"Accuracy":64,"Ranged Accuracy":64,"Magic Evasion":36,"Magic Evasion":36,"Crit Damage":8,},
                            "blu":{"Attack":70,"Ranged Attack":70,"Evasion":36,"Accuracy":36,"Ranged Accuracy":36,"Magic Defense":36,"Magic Attack":36,"Magic Evasion":36,"Blue Magic Skill":36,},
                            "cor":{"Triple Shot":20,"True Shot":6,"Ranged Accuracy":20+36,"Attack":36,"Ranged Attack":36,"Accuracy":36,"Evasion":22,"Magic Attack":14,"Magic Evasion":36,"Magic Accuracy":36,"Quick Draw Damage":40}, # TODO: What is "Increases Damage from Sweet Spot"? Is this +20% or +20 weapon+ammo DMG?
                            "pup":{"Martial Arts":40,"Attack":42,"Ranged Attack":42,"Evasion":56,"Accuracy":50,"Ranged Accuracy":50,"Magic Evasion":36,"Magic Accuracy":36,},
                            "dnc":{"Flourish CHR%":20,"Building Flourish WSD":20,"Attack":42,"Ranged Attack":42,"Evasion":64,"Accuracy":64,"Ranged Accuracy":64,"Magic Evasion":36,"Magic Accuracy":36,"Subtle Blow":13,"Crit Damage":8,"Skillchain Bonus":8,"Dual Wield":5},
                            "sch":{"Magic Defense":22,"Magic Attack":36,"Magic Evasion":42,"Magic Accuracy":42,"Dark Magic Skill":36,"Elemental Magic Skill":36,"Magic Burst Damage Trait":13},
                            "geo":{"Magic Accuracy":20,"Magic Attack":20+42,"Magic Defense":28,"Magic Evasion":50,"Magic Accuracy":50,"Elemental Magic Skill":36,"Dark Magic Skill":36,"Magic Damage":13},
                            "run":{"Lunge Bonus":20,"Attack":50,"Ranged Attack":50,"Evasion":56,"Accuracy":56,"Ranged Accuracy":56,"Magic Defense":56,"Magic Evasion":70,"Magic Accuracy":36,},
        }
        for stat in job_mastery_stats[self.main_job]:
            self.stats[stat] = self.stats.get(stat,0) + job_mastery_stats[self.main_job].get(stat,0)

        # ===========================================================================
        # ===========================================================================
        # Add job-specific stats from spells and abilities which are assumed to be active full-time.

        if self.main_job == "rdm": 
            self.stats["TA"] = self.stats.get("TA",0) + 35 # Temper2
            self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 50
            # TODO: "Gain-PARAMETER" spells are treated later as a checkbox buff.

        if self.main_job == "run":
            self.stats["DA"] = self.stats.get("DA",0) + 17 # Temper1
        
        if "sch" in [self.main_job, self.sub_job]:
            self.stats["Elemental Magic Skill"] = max(self.stats.get("Elemental Magic Skill",0), 404+16) # Dark Arts enhances elemental magic skill to B+ rank, plus 16 from merits
            self.stats["Dark Magic Skill"] = max(self.stats.get("Dark Magic Skill",0), 404+16) # Dark Arts enhances dark magic skill to B+ rank, plus 16 from merits
            self.stats["Divine Magic Skill"] = max(self.stats.get("Divine Magic Skill",0), 404+16) # Light Arts enhances divine magic skill to B+ rank, plus 16 from merits

        if self.main_job == "blu": # "Zahak Reborn" spell set.
            self.stats["Accuracy"] = self.stats.get("Accuracy",0) + 48
            self.stats["Ranged Accuracy"] = self.stats.get("Ranged Accuracy",0) + 48
            self.stats["Magic Accuracy"] = self.stats.get("Magic Accuracy",0) + 36
            self.stats["Store TP"] = self.stats.get("Store TP",0) + 30
            self.stats["Dual Wield"] = self.stats.get("Dual Wield",0) + 25
            self.stats["TA"] = self.stats.get("TA",0) + 5
            self.stats["Crit Damage"] = self.stats.get("Crit Damage",0) + 11
            self.stats["Skillchain Bonus"] = self.stats.get("Skillchain Bonus",0) + 16
            self.stats["STR"] = self.stats.get("STR",0) + 5+4+3+2-3
            self.stats["DEX"] = self.stats.get("DEX",0) + 8+6+2+4+4+1+8+4
            self.stats["VIT"] = self.stats.get("VIT",0) + 4+7+4
            self.stats["AGI"] = self.stats.get("AGI",0) + 5+2+1
            self.stats["MND"] = self.stats.get("MND",0) + 4+2
            self.stats["INT"] = self.stats.get("INT",0) + 4-1
            self.stats["CHR"] = self.stats.get("CHR",0) + 1+5-2

        if self.main_job == "drg": # Bonus stats for having a fully leveled Wyvern pet:
            self.stats["Wyvern Bonus Attack%"] = True # This represents the +20% attack that will be applied later for having a wyvern out. Additive bonus with smite, berserk, chaos roll, etc.
            self.stats["Weapon Skill Damage Trait"] = self.stats.get("Weapon Skill Damage Trait",0) + 10 
            self.stats["JA Haste"] = self.stats.get("JA Haste",0) + 10
            self.stats["DA"] = self.stats.get("DA",0) + 15
            self.stats["Attack"] = self.stats.get("Attack",0) + 40 # +40 attack for having a fully leveled Wyvern pet with 20/20 Job Points.

        if self.main_job == "nin":
            self.stats["Store TP"] = self.stats.get("Store TP",0) + 10 # Kakka: Ichi
            self.stats["Subtle Blow"] = self.stats.get("Subtle Blow",0) + 10 # Myoshu: Ichi
            
        if "dnc" in [self.main_job, self.sub_job] and self.abilities.get("Haste Samba",False):
            self.stats["JA Haste"] = self.stats.get("JA Haste",0) + 10 if self.main_job == "dnc" else self.stats.get("JA Haste",0) + 5 # Haste Samba





if __name__ == "__main__":
    #
    #
    #
    import sys
    from gear import *
    main_job = sys.argv[1]
    sub_job = sys.argv[2]
    master_level = int(sys.argv[3])
    gearset = { "main" : Heishi,
                "sub" : Kraken_Club,
                "ranged" : Empty,
                "ammo" : Date,
                "head" : Blistering_Sallet,
                "body" : Mpaca_Doublet30,
                "hands" : Hachiya_Tekko,
                "legs" : Jokushu_Haidate,
                "feet" : Mochizuki_Kyahan,
                "neck" : Ninja_Nodowa,
                "waist" : Fotia_Belt,
                "ear1" : Odr_Earring,
                "ear2" : Lugra_Earring_Aug,
                "ring1" : Regal_Ring,
                "ring2" : Gere_Ring,
                "back" : Empty}

    Grape_Daifuku2 = {"Name": "Grape Daifuku +1", "Type":"Food","STR":3, "VIT":4, "Food Attack":55, "Food Ranged Attack":55, "Accuracy":85, "Ranged Accuracy":85, "Magic Attack":4}
    buffs = {"food": Grape_Daifuku2,
             "brd": {"Attack": 0, "Accuracy": 0, "Ranged Accuracy": 0,"STR":0,"DEX":0, "VIT":0, "AGI":0, "INT":0, "MND":0, "CHR":0,},
             "cor": {"Attack%": 0., "Ranged Attack%":0., "Store TP": 0, "Accuracy": 0, "Magic Attack": 0, "DA":0, "Crit Rate": 0},
             "geo": {"Attack%": 0, "Ranged Attack%": 0, "Accuracy": 0, "Ranged Accuracy":0, "STR":0,"DEX":0, "VIT":0, "AGI":0, "INT":0, "MND":0, "CHR":0,},
             "whm": {"MDT":-29,"Magic Haste": 307./1024, "STR":0,"DEX":0, "VIT":0, "AGI":0, "INT":0, "MND":0, "CHR":0}, # WHM buffs like boost-STR.
             }
    abilities = {"Ebullience":False,
                        "Futae":False,
                        "Sneak Attack":False,
                        "Trick Attack":False,
                        "Footwork":False,
                        "Impetus":False,
                        "Building Flourish":False,
                        "Climactic Flourish":False,
                        "Striking Flourish":False,
                        "Ternary Flourish":False,
                        "Velocity Shot":False,
                        "Blood Rage":False,
                        "Last Resort":False}


    player = create_player(main_job, sub_job, master_level, gearset, buffs, abilities)
    

    print(f"\n\nPlayer stats list ({player.main_job_level}{player.main_job.upper()}/{player.sub_job_level}{player.sub_job.upper()})\n\n",player.stats)