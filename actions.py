import matplotlib.pyplot as plt
import numpy as np
from get_hit_rate import get_hit_rate
from weaponskill_info import weaponskill_info
from get_ma_rate import get_ma_rate3
from get_fstr import *
from get_pdif import *
from get_phys_damage import *
from weapon_bonus import *
from get_tp import get_tp
from nuking import *
from get_dint_m_v import *
from get_delay_timing import *

def color_text(color, text):
    #
    # Print colored text to windows powershell.
    # Colors taken from https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal, but I should find the main source.
    #
    colors = {"yellow":"\033[93m",
              "red":"\033[91m",
              "cyan":"\033[96m",
              "green":"\033[92m",}
    color_cancel = "\033[0m"

    colored_text = f"{colors[color]}{text}{color_cancel}"
    
    return(colored_text)


def verbose_output(phys_dmg, magic_dmg, tp_return, crit, special="other"):
    #
    # Printed output used for multi-attack procs when printing damage dealt by each hit.
    #
    phys_dmg2 = f"+{phys_dmg:.0f}"
    magic_dmg2 = f"+{magic_dmg:.0f}"
    tp_return2 = f"+{tp_return:.1f}"

    if special == "main":
        print(f"    {'Main-hand:':<10s}  {phys_dmg2:>7s} Phys. {magic_dmg2:>7s} Magic.  {tp_return2:>5s} TP  " + (color_text("yellow", "Critical Hit!") if crit else ""))
    elif special == "sub":
        print(f"    {'Off-hand:':<10s}  {phys_dmg2:>7s} Phys. {magic_dmg2:>7s} Magic.  {tp_return2:>5s} TP  " + (color_text("yellow", "Critical Hit!") if crit else ""))
    elif special == "hybrid":
        print(f"    {'Hybrid:':<10s}  {phys_dmg2:>7s} Phys. {magic_dmg2:>7s} Magic.  {tp_return2:>5s} TP  " + (color_text("yellow", "Critical Hit!") if crit else ""))
    elif special == "magic":
        print(f"    {'Magic:':<10s}  {phys_dmg2:>7s} Phys. {magic_dmg2:>7s} Magic.  {tp_return2:>5s} TP  " + (color_text("yellow", "Critical Hit!") if crit else ""))
    elif special == "zanshin":
        print(f"    {'Zanshin:':<10s}  {phys_dmg2:>7s} Phys. {magic_dmg2:>7s} Magic.  {tp_return2:>5s} TP  " + (color_text("yellow", "Critical Hit!") if crit else ""))
    elif special == "daken":
        print(f"    {'Daken:':<10s}  {phys_dmg2:>7s} Phys. {magic_dmg2:>7s} Magic.  {tp_return2:>5s} TP  " + (color_text("yellow", "Critical Hit!") if crit else ""))
    elif special == "kick":
        print(f"    {'Kick:':<10s}  {phys_dmg2:>7s} Phys. {magic_dmg2:>7s} Magic.  {tp_return2:>5s} TP  " + (color_text("yellow", "Critical Hit!") if crit else ""))
    elif special == "ranged":
        print(f"    {'Ranged:':<10s}  {phys_dmg2:>7s} Phys. {magic_dmg2:>7s} Magic.  {tp_return2:>5s} TP  " + (color_text("yellow", "Critical Hit!") if crit else ""))
    else:
        print(f"                {phys_dmg2:>7s} Phys. {magic_dmg2:>7s} Magic.  {tp_return2:>5s} TP  " + (color_text("yellow", "Critical Hit!") if crit else ""))
        

def run_simulation(player_tp, player_ws, enemy, ws_threshold, ws_name, ws_type, plot_dps=False, verbose=False):
    #
    #
    #
    verbose_dps = player_tp.abilities.get("Verbose DPS", False)
    very_verbose_dps = player_tp.abilities.get("Very Verbose DPS", False)
    dual_wield = ((player_tp.gearset["sub"].get("Type",None) == "Weapon") or (player_tp.gearset["main"]["Skill Type"] == "Hand-to-Hand")) and ((player_ws.gearset["sub"].get("Type",None) == "Weapon") or (player_ws.gearset["main"]["Skill Type"] == "Hand-to-Hand"))

    time_per_attack_round = get_delay_timing(player_tp.stats["Delay1"], player_tp.stats["Delay2"] if dual_wield and (player_ws.gearset["main"]["Skill Type"] != "Hand-to-Hand") else 0, player_tp.stats.get("Dual Wield",0)/100, player_tp.stats.get("Martial Arts",0), player_tp.stats.get("Magic Haste",0), player_tp.stats.get("JA Haste",0), player_tp.stats.get("Gear Haste",0))

    regain_tp = player_tp.stats.get("Dual Wield",0)*(player_tp.gearset["main"]["Name"]=="Gokotai") + player_tp.stats.get("Regain",0) # Total regain in TP set
    regain_ws = player_ws.stats.get("Dual Wield",0)*(player_ws.gearset["main"]["Name"]=="Gokotai") + player_ws.stats.get("Regain",0) # Total regain in WS set

    time = 0 # Time since simulation start in seconds
    n_ws = 10000 # Number of weapon skills to simulate
    tp = 0

    damage = 0  # Total damage dealt
    damage_list = [] # List of damage at each interval, useful for plotting
    time_list = []
    phys_dmg_list = []
    magic_dmg_list = []

    tp_damage = 0 # Total damage dealt from TP phase
    tp_damage_list = []
    tp_time_list = []

    ws_damage = 0 # Total damage dealt from WS phase
    ws_damage_list = []
    ws_time_list = []

    total_time = 2*3600 # seconds
    avg_tp_dmg = []
    avg_ws_dmg = []

    avg_ws_tp = [] # List containing the values of player TP when each WS was used (before TP Bonus)

    while time < total_time:
        tp0 = tp
        while tp < ws_threshold:
            tp0 = tp
            tp_round = average_attack_round(player_tp, enemy, tp, ws_threshold, "Time to WS", simulation=True)
            physical_damage = tp_round[0]
            tp_return = tp_round[1]
            magical_damage = tp_round[2]
            damage += physical_damage + magical_damage

            tp_damage += physical_damage + magical_damage
            tp += tp_return
            regain_tp_return = round((time_per_attack_round/3)*(regain_tp),1) # Extra TP from regain, averaged over time per attack round to simplify things
            tp += regain_tp_return
            print(f"    Regain bonus: +{regain_tp_return:.1f} TP") if (very_verbose_dps or verbose_dps) and regain_tp_return>0 else None
            time += time_per_attack_round
            avg_tp_dmg.append(physical_damage + magical_damage)

            phys_dmg_list.append(physical_damage)
            magic_dmg_list.append(magical_damage)
            damage_list.append(damage)
            time_list.append(time)

            tp_damage_list.append(tp_damage)
            tp_time_list.append(time)

        ws_sim = average_ws(player_ws, enemy, ws_name, tp + player_ws.stats.get("TP Bonus",0), ws_type, "Damage dealt", simulation=True)
        avg_ws_tp.append(tp)

        damage += ws_sim[0]
        ws_damage += ws_sim[0]
        tp = ws_sim[1]
        time += 2.0 # 2.0 seconds of delay after using a WS  (see https://www.bg-wiki.com/ffxi/Forced_Delay)
        regain_ws_return = round((2./3)*(regain_ws),1) # Extra TP gained from Regain during the 2s delay after using a WS.
        tp += regain_ws_return
        print(f"    Regain bonus: +{regain_ws_return:.1f} TP") if (very_verbose_dps or verbose_dps) and regain_ws_return>0 else None
        print() if (verbose_dps or very_verbose_dps) else None
        print() if (verbose_dps or very_verbose_dps) else None

        avg_ws_dmg.append(ws_sim[0])
        damage_list.append(damage)
        time_list.append(time)

        ws_damage_list.append(ws_damage)
        ws_time_list.append(time)


    time_list = np.array(time_list)
    damage_list = np.array(damage_list)
    tp_damage_list = np.array(tp_damage_list)
    ws_damage_list = np.array(ws_damage_list)
    tp_time_list = np.array(tp_time_list)
    ws_time_list = np.array(ws_time_list)
    phys_dmg_list = np.array(phys_dmg_list)
    magic_dmg_list = np.array(magic_dmg_list)

    if plot_dps:
        plt.plot(time_list, damage_list/time_list,label=f"Total={damage/time:7.1f}")
        plt.plot(tp_time_list, tp_damage_list/tp_time_list,label=f"TP={tp_damage/time:7.1f} ({tp_damage/damage*100:5.1f}%)")
        plt.plot(ws_time_list, ws_damage_list/ws_time_list,label=f"WS={ws_damage/time:7.1f} ({ws_damage/damage*100:5.1f}%)")
        plt.xlabel("Time (s)")
        plt.ylabel("DPS")
        plt.legend()
        plt.show()

    print()
    print(f"""
    =========================
    Total time: {(time/3600):5.1f} h
    Time/Attack: {time_per_attack_round:7.3f} s
    Average Dmg/Attack: {np.average(avg_tp_dmg):8.1f}
        Physical: {np.average(phys_dmg_list):8.1f} ({np.average(phys_dmg_list)/np.average(avg_tp_dmg)*100:5.1f}%)
         Magical: {np.average(magic_dmg_list):8.1f} ({np.average(magic_dmg_list)/np.average(avg_tp_dmg)*100:5.1f}%)
    Average Dmg/WS: {np.average(avg_ws_dmg):8.1f}
    Average TP/WS: {np.average(avg_ws_tp):4.0f} TP (+{player_ws.stats.get("TP Bonus",0)} TP Bonus)
    Total Damage: {damage/1e6:5.1f}M damage (Total DPS: {damage/time:7.1f})
    TP Damage: {tp_damage/1e6:5.1f}M damage (TP DPS: {tp_damage/time:7.1f}; {tp_damage/damage*100:5.1f}%)
    WS Damage: {ws_damage/1e6:5.1f}M damage (WS DPS: {ws_damage/time:7.1f}; {ws_damage/damage*100:5.1f}%)
    =========================
    """)

def average_attack_round(player, enemy, starting_tp, ws_threshold, input_metric, simulation=False, verbose=False):
    #
    # Calculate the damage dealt from a typical attack round.
    # Mostly copy/pasted from the melee weapon skill section.
    #
    # starting_tp = starting TP value.
    # ending_tp = TP threshold (use WS after this TP value is reached)
    #
    dual_wield = (player.gearset["sub"].get("Type",None) == "Weapon") or (player.gearset["main"]["Skill Type"] == "Hand-to-Hand")

    verbose_dps = player.abilities.get("Verbose DPS", False)
    very_verbose_dps = player.abilities.get("Very Verbose DPS", False)

    enemy_defense = enemy.stats["Defense"]
    enemy_evasion = enemy.stats["Evasion"]

    nhits = 1

    qa = player.stats.get("QA",0)/100 if player.stats.get("QA",0)/100 < 1.0 else 1.0
    ta = player.stats.get("TA",0)/100 if player.stats.get("TA",0)/100 < 1.0 else 1.0
    da = player.stats.get("DA",0)/100 if player.stats.get("DA",0)/100 < 1.0 else 1.0
    oa8_main = player.stats.get("OA8 main",0)/100
    oa7_main = player.stats.get("OA7 main",0)/100
    oa6_main = player.stats.get("OA6 main",0)/100
    oa5_main = player.stats.get("OA5 main",0)/100
    oa4_main = player.stats.get("OA4 main",0)/100
    oa3_main = player.stats.get("OA3 main",0)/100
    oa2_main = player.stats.get("OA2 main",0)/100

    oa8_sub = player.stats.get("OA8 sub",0)/100
    oa7_sub = player.stats.get("OA7 sub",0)/100
    oa6_sub = player.stats.get("OA6 sub",0)/100
    oa5_sub = player.stats.get("OA5 sub",0)/100
    oa4_sub = player.stats.get("OA4 sub",0)/100
    oa3_sub = player.stats.get("OA3 sub",0)/100
    oa2_sub = player.stats.get("OA2 sub",0)/100
    
    oa_list = np.array([player.stats.get("OA3 main",0), # Notice that there is no support for main-hand Kclub. Only the off-hand values support OA4+
            player.stats.get("OA2 main",0),
            player.stats.get("OA8 sub",0),
            player.stats.get("OA7 sub",0),
            player.stats.get("OA6 sub",0),
            player.stats.get("OA5 sub",0),
            player.stats.get("OA4 sub",0),
            player.stats.get("OA3 sub",0),
            player.stats.get("OA2 sub",0),
            ])/100

    ta_dmg = player.stats.get("TA Damage%",0)/100
    da_dmg = player.stats.get("DA Damage%",0)/100

    pdl_gear = player.stats.get("PDL",0)/100
    pdl_trait = player.stats.get("PDL Trait",0)/100

    crit_rate = player.stats["Crit Rate"]/100 + get_dex_crit(player.stats["DEX"], enemy.stats["AGI"])
    crit_dmg = player.stats.get("Crit Damage",0)/100 # Crit rate was read in earlier directly from the WS attributes.


    crit_rate += 0.5*(1 - starting_tp/3000) * (player.gearset["main"]["Name"]=="Tauret") # Tauret provides +crit_rate to auto attacks with low TP. (https://www.bg-wiki.com/ffxi/Tauret)
    
    crit_rate = 1.0 if crit_rate > 1.0 else crit_rate

    stp = player.stats.get("Store TP",0)/100 + (50./100)*crit_rate*(player.gearset["main"]["Name"]=="Karambit") # Karambit provides +50 STP to critical hit auto attacks. Thus we add crit% of 50 to our STP for average attack rounds, then divide by 100 to keep Store TP as a %. (https://www.bg-wiki.com/ffxi/Karambit)

    # Read in delay values now so we can use them in the magical WS section, which return TP for their one magic hit.
    base_delay = (player.stats["Delay1"] + player.stats["Delay2"])/2 
    mdelay = (base_delay - player.stats.get("Martial Arts",0)) * ((1 - player.stats.get("Dual Wield",0)/100))

    main_dmg = player.stats["DMG1"]
    sub_dmg = player.stats["DMG2"]
    fstr_main = get_fstr(main_dmg, player.stats["STR"], enemy.stats["VIT"])
    fstr_sub = get_fstr(sub_dmg, player.stats["STR"], enemy.stats["VIT"])

    attack1 = player.stats["Attack1"]
    attack2 = player.stats["Attack2"]

    accuracy1 = player.stats["Accuracy1"]
    accuracy2 = player.stats["Accuracy2"]

    one_handed_skills = ["Axe", "Club", "Dagger", "Sword", "Katana",]
    two_handed_skills = ["Great Sword", "Great Katana", "Great Axe", "Polearm", "Scythe", "Staff",] # I treat Hand-to-Hand separately where needed. Search for "Hand-to-Hand" to find these locations.

    main_skill_type = player.gearset["main"]["Skill Type"]
    sub_skill_type = player.gearset["sub"].get("Skill Type",None) if not main_skill_type=="Hand-to-Hand" else "Hand-to-Hand"
    attack2 = attack1 if main_skill_type == "Hand-to-Hand" else attack2

    hit_rate_cap_main = 0.99 if main_skill_type in one_handed_skills or main_skill_type == "Hand-to-Hand" else 0.95
    hit_rate_cap_sub = 0.99 if sub_skill_type == "Hand-to-Hand" else 0.95

    hit_rate11 = get_hit_rate(accuracy1, enemy_evasion, hit_rate_cap_main) # hit_rate of the first main-hand hit.
    hit_rate12 = get_hit_rate(accuracy1, enemy_evasion, hit_rate_cap_main) # hit_rate of all other main-hand hits.
    hit_rate21 = get_hit_rate(accuracy2, enemy_evasion, hit_rate_cap_sub)
    hit_rate22 = get_hit_rate(accuracy2, enemy_evasion, hit_rate_cap_sub)

    if not dual_wield:
        hit_rate21 = 0
        hit_rate22 = 0

    hit_rate_matrix = np.array([[hit_rate11, hit_rate21],[hit_rate12, hit_rate22]])

    # Ranged stuff is entirely for Daken shuriken throws in this TP function.
    daken = player.stats.get("Daken",0)/100 if player.stats.get("Daken",0)/100 < 1.0 else 1.0
    ammo_dmg = player.stats.get("Ammo DMG",0)
    fstr_ammo = get_fstr2(ammo_dmg, player.stats["STR"], enemy.stats["VIT"])
    ammo_delay = player.stats.get("Ammo Delay",0)
    ranged_accuracy = player.stats["Ranged Accuracy"] + 100*(player.stats.get("Daken",0)>0) # Daken gets +100 ranged accuracy by default.
    ranged_attack = player.stats.get("Ranged Attack",0)
    ammo_skill_type = player.gearset["ammo"].get("Skill Type","None")
    hit_rate_cap_ranged = 0.99 if player.abilities.get("Sharpshot",False) else 0.95 # Maybe NIN/RNG uses Sharpshot? May as well leave this in.
    hit_rate_ranged = get_hit_rate(ranged_accuracy, enemy_evasion, hit_rate_cap_ranged)

    # Kick attacks also contribute. We've already assigned Kick DMG based on stats and Footwork in the class file.
    kick_dmg = player.stats["Kick DMG"]
    fstr_kick = get_fstr(kick_dmg, player.stats["STR"], enemy.stats.get("VIT",0))
    kickattacks = player.stats.get("Kick Attacks",0)/100 if player.stats.get("Kick Attacks",0)/100 < 1.0 else 1.0

    zanshin = player.stats.get("Zanshin",0)/100
    zanshin = 1.0 if zanshin > 1.0 else zanshin
    zanhasso = player.stats.get("Zanhasso",0)/100
    zanshin_hit_rate = get_hit_rate(accuracy1+34, enemy_evasion, 0.95)
    zanshin_oa2 = player.stats.get("Zanshin OA2",0)/100

    enhancing_magic_skill = player.abilities.get("Enh. Skill",0)
    enspell_active = player.abilities.get("EnSpell",False) or player.abilities.get("Endark II", False) or player.abilities.get("Enlight II", False)
    if player.abilities.get("EnSpell",False):
        enspell_damage_percent_main = player.stats.get("EnSpell Damage% main",0) + player.stats.get("EnSpell Damage%",0)
        enspell_damage_percent_sub = player.stats.get("EnSpell Damage% sub",0) + player.stats.get("EnSpell Damage%",0)
        enspell_damage_main = player.stats.get("EnSpell Damage main",0) + player.stats.get("EnSpell Damage",0)
        enspell_damage_sub = player.stats.get("EnSpell Damage sub",0) + player.stats.get("EnSpell Damage",0)
        magic_crit_rate2 = player.stats.get("Magic Crit Rate II",0)/100

        active_storm = player.abilities.get("Storm spell",False)
        if active_storm!="None" and player.gearset["waist"]["Name"]=="Hachirin-no-Obi":
            dayweather = 0.25 if "II" in active_storm else 0.10 # Assume the EnSpell element matches the storm spell selected.
        else:
            dayweather = 0

        # Assume the EnSpell element matches the element corresponding to the gear with the highest elemental damage bonus, ignoring light/dark. Orpheus sash is applies separately.
        elemental_magic_attack_bonus = (max([player.stats.get(f"{element.capitalize()} Elemental Bonus", 0) for element in ["Earth", "Water", "Wind", "Fire", "Ice", "Thunder"]])/100 + player.stats.get("Elemental Bonus",0)/100)

        main_enspell_damage = get_enspell_damage(enhancing_magic_skill, enspell_damage_percent_main, enspell_damage_main) * (1 + dayweather) * (1 + elemental_magic_attack_bonus) * (1.0 + 0.25*(np.random.uniform() < magic_crit_rate2))
        sub_enspell_damage = get_enspell_damage(enhancing_magic_skill, enspell_damage_percent_main, enspell_damage_sub) * (1 + dayweather) * (1 + elemental_magic_attack_bonus) * (1.0 + 0.25*(np.random.uniform() < magic_crit_rate2))

    elif player.abilities.get("Enlight II", False):
        enlight_potency = 0.8
        if enhancing_magic_skill <=500:
            main_enspell_damage = 2*((enhancing_magic_skill + 85)/13) + ((enhancing_magic_skill + 85)/26)
        else:
            main_enspell_damage = 2*((enhancing_magic_skill + 400)/20) + ((enhancing_magic_skill + 400)/40)
        main_enspell_damage = int(main_enspell_damage * enlight_potency) + 20 # +20 from Job points
        sub_enspell_damage = 0

    elif player.abilities.get("Endark II", False): # https://ffxiclopedia.fandom.com/wiki/Endark_II
        endark_potency = 0.8
        main_enspell_damage = int(((enhancing_magic_skill + 20)/13 + 5)*2.5 * endark_potency) + 20 # +20 from Job points
        sub_enspell_damage = 0



    aftermath = player.abilities.get("Aftermath",0)
    # Empyrean Lv1/2/3 aftermath multiplier: 30%/40%/50% chance of dealing triple damage for all attacks by that weapon (main-hand)
    empyrean_am_damage_bonus = 1.0
    empyrean_weapons = ["Verethragna","Twashtar","Almace","Caladbolg","Farsha","Ukonvasara","Redemption","Kannagi","Rhongomiant","Gambanteinn","Masamune","Hvergelmir"]
    empyrean_am = [0.3, 0.4, 0.5]
    if player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0:
        empyrean_am_damage_bonus += 2*empyrean_am[aftermath-1]


    # Hidden triple damage +13% of the time on relics. No Aftermath required.
    relic_hidden_damage_bonus = 1.0
    relic_weapons30 = ["Spharai","Mandau","Excalibur","Kikoku","Mjollnir"] # occasionally 3.0x damage
    relic_weapons25 = ["Ragnarok","Guttler","Gungnir","Amanomurakumo","Claustrum"] # occasionally 2.5x damage
    relic_weapons20 = ["Bravura","Apocalypse"] # occasionally 2.0x damage
    if player.gearset["main"]["Name"] in relic_weapons30:
        relic_hidden_damage_bonus += 2*0.13
    elif player.gearset["main"]["Name"] in relic_weapons25:
        relic_hidden_damage_bonus += 1.5*0.16
    elif player.gearset["main"]["Name"] in relic_weapons20:
        relic_hidden_damage_bonus += 1*0.2
 
    # Hidden double/triple damage +30% of the time on primes. No Aftermath required.
    prime_hidden_damage_bonus = 1.0
    prime_weapons3 = ["Varga Purnikawa V",   "Mpu Gandring V",  "Caliburnus V",  "Helheim V",  "Spalirisos V",  "Laphria V",  "Foenaria V",  "Gae Buide V",  "Dokoku V",  "Kusanagi no Tsurugi V",  "Lorg Mor V",  "Opashoro V"]
    prime_weapons2 = ["Varga Purnikawa IV", "Mpu Gandring IV", "Caliburnus IV", "Helheim IV", "Spalirisos IV", "Laphria IV", "Foenaria IV", "Gae Buide IV", "Dokoku IV", "Kusanagi no Tsurugi IV", "Lorg Mor IV", "Opashoro IV"]
    if player.gearset["main"]["Name2"] in prime_weapons3:
        prime_hidden_damage_bonus += 2*0.3
    elif player.gearset["main"]["Name2"] in prime_weapons2:
        prime_hidden_damage_bonus += 1*0.3
    
    physical_damage = 0 
    magical_damage = 0 # EnSpells for auto-attack rounds
    main_hit_damage = 0 # "DA DMG" and "TA DMG" apply to all hits. We need to record the damage for each hit before rolling QA > TA > DA so we can increase it later
    sub_hit_damage = 0
    zanshin_damage = 0
    kickattacks_damage = 0
    daken_damage = 0
    total_damage = 0
    tp_return = 0
    main_hit_connects = False # Used to make sure Zanshin doesn't proc without ZanHasso if the main-hit connects
    main_ma_proc = False # Used to ensure Zanshin doesn't proc on a multi-attack
    main_da_proc = False # Used to keep track of DA/TA procs for "DA DMG%" and "TA DMG%" stats (see Sakpata's Helm)
    main_ta_proc = False # Used to keep track of DA/TA procs for "DA DMG%" and "TA DMG%" stats (see Sakpata's Helm)
    sub_da_proc = False # Used to keep track of DA/TA procs for "DA DMG%" and "TA DMG%" stats (see Sakpata's Helm)
    sub_ta_proc = False # Used to keep track of DA/TA procs for "DA DMG%" and "TA DMG%" stats (see Sakpata's Helm)

    if simulation:

        print(f"Auto-attack round starting with {starting_tp:.1f} TP:") if (verbose_dps or very_verbose_dps) else None

        striking_flourish = False
        ternary_flourish = False
        climactic_flourish = False
        sneak_attack = False
        trick_attack = False


        # To properly account for "DA Damage+" and "TA Damage+" stats boosting the first main/sub hit, we need to determine if a double or triple attack is proced before the first hit is done.
        qa_proc_main = np.random.uniform() < qa
        ta_proc_main = (np.random.uniform() < ta) * (not qa_proc_main)
        da_proc_main = (np.random.uniform() < da) * (not qa_proc_main) * (not ta_proc_main)

        # Repeat for off-hand
        qa_proc_sub = np.random.uniform() < qa
        ta_proc_sub = (np.random.uniform() < ta) * (not qa_proc_sub)
        da_proc_sub = (np.random.uniform() < da) * (not qa_proc_sub) * (not ta_proc_sub)

        


        attempted_hits = 0

        # Main-hand hit
        attempted_hits += 1
        if np.random.uniform() < hit_rate11:
            main_hit_connects = True
            pdif, crit = get_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
            phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0) * (1.0 + 2.0*(np.random.uniform()<0.13 and player.gearset["main"]["Name"] in relic_weapons30)) \
                                                                                            * (1.0 + 1.5*(np.random.uniform()<0.16 and player.gearset["main"]["Name"] in relic_weapons25)) \
                                                                                            * (1.0 + 1.0*(np.random.uniform()<0.2 and player.gearset["main"]["Name"] in relic_weapons20)) \
                                                                                            * (1.0 + 2.0*(np.random.uniform()<0.3 and player.gearset["main"]["Name2"] in prime_weapons3)) \
                                                                                            * (1.0 + 1.0*(np.random.uniform()<0.3 and player.gearset["main"]["Name2"] in prime_weapons2)) \
                                                                                            * (1.0 + 2.0*(np.random.uniform() < empyrean_am[aftermath-1] and player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0)) \
                                                                                            * (1 + da_dmg*da_proc_main) * (1 + ta_dmg*ta_proc_main) # Boosts first hit damage if DA or TA procs and you have DA/TA Damage+ stat
            main_hit_damage += phys_dmg_ph
            tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp) # Add TP return from the main-hand hit
            tp_return += tp_ph
            magic_dmg_ph = 0
            if enspell_active:
                magic_dmg_ph += main_enspell_damage
                magical_damage += magic_dmg_ph
            verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "main") if very_verbose_dps else None
        else:
                print(f"    {'Main-hand':<10s}        "+color_text("red","Missed.")) if very_verbose_dps else None

    
        # Off-hand hit
        if dual_wield:
            attempted_hits += 1
            if np.random.uniform() < hit_rate21:
                pdif, crit = get_pdif_melee(attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0) * (1 + da_dmg*da_proc_sub) * (1 + ta_dmg*ta_proc_sub) # Boosts first off-hand hit damage if DA or TA procs and you have DA/TA Damage+ stat
                sub_hit_damage += phys_dmg_ph
                tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                tp_return += tp_ph
                magic_dmg_ph = 0
                if enspell_active:
                    magic_dmg_ph += sub_enspell_damage
                    magical_damage += magic_dmg_ph
                verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "sub") if very_verbose_dps else None
            else:
                print(f"    {'Off-hand':<10s}        "+color_text("red","Missed.")) if very_verbose_dps else None

        # Check main-hand multi-attack
        if qa_proc_main:
            print("    Main-hand Quad. Attack:") if (verbose_dps or very_verbose_dps) else None
            main_ma_proc = True
            for i in range(3): # 3 bonus hits on a Quad. Attack
                if attempted_hits < 8:
                    attempted_hits += 1
                    if np.random.uniform() < hit_rate12:
                        pdif, crit = get_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                        phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)*(1.0 + 2.0*(np.random.uniform() < empyrean_am[aftermath-1] and player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0))
                        main_hit_damage += phys_dmg_ph
                        tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                        tp_return += tp_ph

                        magic_dmg_ph = 0
                        if enspell_active:
                            magic_dmg_ph += main_enspell_damage
                            magical_damage += magic_dmg_ph
                        verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                    else:
                        print("                      "+color_text("red","Missed.")) if very_verbose_dps else None


        elif ta_proc_main:
            print("    Main-hand Triple Attack:") if (verbose_dps or very_verbose_dps) else None
            main_ta_proc = True # Used to increase damage of all hits of a TA for "TA Damage%" stats
            main_ma_proc = True
            for i in range(2):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if np.random.uniform() < hit_rate12:
                        pdif, crit = get_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                        phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)*(1.0 + 2.0*(np.random.uniform() < empyrean_am[aftermath-1] and player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0)) * (1 + ta_dmg)
                        main_hit_damage += phys_dmg_ph
                        tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                        tp_return += tp_ph

                        magic_dmg_ph = 0
                        if enspell_active:
                            magic_dmg_ph += main_enspell_damage
                            magical_damage += magic_dmg_ph
                        verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                    else:
                        print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
        elif da_proc_main:
            print("    Main-hand Double Attack:") if (verbose_dps or very_verbose_dps) else None
            main_da_proc = True
            main_ma_proc = True
            for i in range(1):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if np.random.uniform() < hit_rate12:
                        pdif, crit = get_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                        phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)*(1.0 + 2.0*(np.random.uniform() < empyrean_am[aftermath-1] and player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0)) * (1 + da_dmg)
                        main_hit_damage += phys_dmg_ph
                        tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                        tp_return += tp_ph

                        magic_dmg_ph = 0
                        if enspell_active:
                            magic_dmg_ph += main_enspell_damage
                            magical_damage += magic_dmg_ph
                        verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                    else:
                        print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
        elif np.random.uniform() < oa8_main:
            print("    Main-hand OA8:") if (verbose_dps or very_verbose_dps) else None
            main_oa8_proc = True
            main_ma_proc = True
            for i in range(7):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if np.random.uniform() < hit_rate12:
                        pdif, crit = get_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                        phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)*(1.0 + 2.0*(np.random.uniform() < empyrean_am[aftermath-1] and player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0))
                        main_hit_damage += phys_dmg_ph
                        tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                        tp_return += tp_ph

                        magic_dmg_ph = 0
                        if enspell_active:
                            magic_dmg_ph += main_enspell_damage
                            magical_damage += magic_dmg_ph
                        verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                    else:
                        print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
        elif np.random.uniform() < oa7_main:
            print("    Main-hand OA7:") if (verbose_dps or very_verbose_dps) else None
            main_ma_proc = True
            for i in range(6):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if np.random.uniform() < hit_rate12:
                        pdif, crit = get_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                        phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)*(1.0 + 2.0*(np.random.uniform() < empyrean_am[aftermath-1] and player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0))
                        main_hit_damage += phys_dmg_ph
                        tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                        tp_return += tp_ph

                        magic_dmg_ph = 0
                        if enspell_active:
                            magic_dmg_ph += main_enspell_damage
                            magical_damage += magic_dmg_ph
                        verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                    else:
                        print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
        elif np.random.uniform() < oa6_main:
            print("    Main-hand OA6:") if (verbose_dps or very_verbose_dps) else None
            main_ma_proc = True
            for i in range(5):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if np.random.uniform() < hit_rate12:
                        pdif, crit = get_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                        phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)*(1.0 + 2.0*(np.random.uniform() < empyrean_am[aftermath-1] and player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0))
                        main_hit_damage += phys_dmg_ph
                        tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                        tp_return += tp_ph

                        magic_dmg_ph = 0
                        if enspell_active:
                            magic_dmg_ph += main_enspell_damage
                            magical_damage += magic_dmg_ph
                        verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                    else:
                        print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
        elif np.random.uniform() < oa5_main:
            print("    Main-hand OA5:") if (verbose_dps or very_verbose_dps) else None
            main_ma_proc = True
            for i in range(4):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if np.random.uniform() < hit_rate12:
                        pdif, crit = get_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                        phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)*(1.0 + 2.0*(np.random.uniform() < empyrean_am[aftermath-1] and player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0))
                        main_hit_damage += phys_dmg_ph
                        tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                        tp_return += tp_ph

                        magic_dmg_ph = 0
                        if enspell_active:
                            magic_dmg_ph += main_enspell_damage
                            magical_damage += magic_dmg_ph
                        verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                    else:
                        print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
        elif np.random.uniform() < oa4_main:
            print("    Main-hand OA4:") if (verbose_dps or very_verbose_dps) else None
            main_ma_proc = True
            for i in range(3):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if np.random.uniform() < hit_rate12:
                        pdif, crit = get_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                        phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)*(1.0 + 2.0*(np.random.uniform() < empyrean_am[aftermath-1] and player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0))
                        main_hit_damage += phys_dmg_ph
                        tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                        tp_return += tp_ph

                        magic_dmg_ph = 0
                        if enspell_active:
                            magic_dmg_ph += main_enspell_damage
                            magical_damage += magic_dmg_ph
                        verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                    else:
                        print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
        elif np.random.uniform() < oa3_main:
            print("    Main-hand OA3:") if (verbose_dps or very_verbose_dps) else None
            main_ma_proc = True
            for i in range(2):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if np.random.uniform() < hit_rate12:
                        pdif, crit = get_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                        phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)*(1.0 + 2.0*(np.random.uniform() < empyrean_am[aftermath-1] and player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0))
                        main_hit_damage += phys_dmg_ph
                        tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                        tp_return += tp_ph

                        magic_dmg_ph = 0
                        if enspell_active:
                            magic_dmg_ph += main_enspell_damage
                            magical_damage += magic_dmg_ph
                        verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                    else:
                        print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
        elif np.random.uniform() < oa2_main:
            print("    Main-hand OA2:") if (verbose_dps or very_verbose_dps) else None
            main_ma_proc = True
            for i in range(1):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if np.random.uniform() < hit_rate12:
                        pdif, crit = get_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                        phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)*(1.0 + 2.0*(np.random.uniform() < empyrean_am[aftermath-1] and player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0))
                        main_hit_damage += phys_dmg_ph
                        tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                        tp_return += tp_ph

                        magic_dmg_ph = 0
                        if enspell_active:
                            magic_dmg_ph += main_enspell_damage
                            magical_damage += magic_dmg_ph
                        verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                    else:
                        print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
        physical_damage += main_hit_damage

        # Check off-hand multi-attack.
        if dual_wield:
            if attempted_hits < 8:
                if qa_proc_sub:
                    print("    Off-hand Quad. Attack:") if (verbose_dps or very_verbose_dps) else None
                    for i in range(3): # 3 bonus hits on a Quad. Attack
                        if attempted_hits < 8:
                            attempted_hits += 1
                            if np.random.uniform() < hit_rate22:
                                pdif, crit = get_pdif_melee(attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)
                                sub_hit_damage += phys_dmg_ph
                                tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                                tp_return += tp_ph

                                magic_dmg_ph = 0
                                if enspell_active:
                                    magic_dmg_ph += sub_enspell_damage
                                    magical_damage += magic_dmg_ph
                                verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                            else:
                                print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                elif ta_proc_sub:
                    print("    Off-hand Triple Attack:") if (verbose_dps or very_verbose_dps) else None
                    sub_ta_proc = True
                    for i in range(2):
                        if attempted_hits < 8:
                            attempted_hits += 1
                            if np.random.uniform() < hit_rate22:
                                pdif, crit = get_pdif_melee(attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0) * (1 + ta_dmg)
                                sub_hit_damage += phys_dmg_ph
                                tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                                tp_return += tp_ph

                                magic_dmg_ph = 0
                                if enspell_active:
                                    magic_dmg_ph += sub_enspell_damage
                                    magical_damage += magic_dmg_ph
                                verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                            else:
                                print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                elif da_proc_sub:
                    print("    Off-hand Double Attack:") if (verbose_dps or very_verbose_dps) else None
                    sub_da_proc = True
                    for i in range(1):
                        if attempted_hits < 8:
                            attempted_hits += 1
                            if np.random.uniform() < hit_rate22:
                                pdif, crit = get_pdif_melee(attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0) * (1 + da_dmg)
                                sub_hit_damage += phys_dmg_ph
                                tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                                tp_return += tp_ph

                                magic_dmg_ph = 0
                                if enspell_active:
                                    magic_dmg_ph += sub_enspell_damage
                                    magical_damage += magic_dmg_ph
                                verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                            else:
                                print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                elif np.random.uniform() < oa8_sub:
                    print("    Off-hand OA8:") if (verbose_dps or very_verbose_dps) else None
                    for i in range(7):
                        if attempted_hits < 8:
                            attempted_hits += 1
                            if np.random.uniform() < hit_rate22:
                                pdif, crit = get_pdif_melee(attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)
                                sub_hit_damage += phys_dmg_ph
                                tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                                tp_return += tp_ph

                                magic_dmg_ph = 0
                                if enspell_active:
                                    magic_dmg_ph += sub_enspell_damage
                                    magical_damage += magic_dmg_ph
                                verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                            else:
                                print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                elif np.random.uniform() < oa7_sub:
                    print("    Off-hand OA7:") if (verbose_dps or very_verbose_dps) else None
                    for i in range(6):
                        if attempted_hits < 8:
                            attempted_hits += 1
                            if np.random.uniform() < hit_rate22:
                                pdif, crit = get_pdif_melee(attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)
                                sub_hit_damage += phys_dmg_ph
                                tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                                tp_return += tp_ph

                                magic_dmg_ph = 0
                                if enspell_active:
                                    magic_dmg_ph += sub_enspell_damage
                                    magical_damage += magic_dmg_ph
                                verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                            else:
                                print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                elif np.random.uniform() < oa6_sub:
                    print("    Off-hand OA6:") if (verbose_dps or very_verbose_dps) else None
                    for i in range(5):
                        if attempted_hits < 8:
                            attempted_hits += 1
                            if np.random.uniform() < hit_rate22:
                                pdif, crit = get_pdif_melee(attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)
                                sub_hit_damage += phys_dmg_ph
                                tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                                tp_return += tp_ph

                                magic_dmg_ph = 0
                                if enspell_active:
                                    magic_dmg_ph += sub_enspell_damage
                                    magical_damage += magic_dmg_ph
                                verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                            else:
                                print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                elif np.random.uniform() < oa5_sub:
                    print("    Off-hand OA5:") if (verbose_dps or very_verbose_dps) else None
                    for i in range(4):
                        if attempted_hits < 8:
                            attempted_hits += 1
                            if np.random.uniform() < hit_rate22:
                                pdif, crit = get_pdif_melee(attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)
                                sub_hit_damage += phys_dmg_ph
                                tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                                tp_return += tp_ph

                                magic_dmg_ph = 0
                                if enspell_active:
                                    magic_dmg_ph += sub_enspell_damage
                                    magical_damage += magic_dmg_ph
                                verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                            else:
                                print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                elif np.random.uniform() < oa4_sub:
                    print("    Off-hand OA4:") if (verbose_dps or very_verbose_dps) else None
                    for i in range(3):
                        if attempted_hits < 8:
                            attempted_hits += 1
                            if np.random.uniform() < hit_rate22:
                                pdif, crit = get_pdif_melee(attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)
                                sub_hit_damage += phys_dmg_ph
                                tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                                tp_return += tp_ph

                                magic_dmg_ph = 0
                                if enspell_active:
                                    magic_dmg_ph += sub_enspell_damage
                                    magical_damage += magic_dmg_ph
                                verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                            else:
                                print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                elif np.random.uniform() < oa3_sub:
                    print("    Off-hand OA3:") if (verbose_dps or very_verbose_dps) else None
                    for i in range(2):
                        if attempted_hits < 8:
                            attempted_hits += 1
                            if np.random.uniform() < hit_rate22:
                                pdif, crit = get_pdif_melee(attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)
                                sub_hit_damage += phys_dmg_ph
                                tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                                tp_return += tp_ph

                                magic_dmg_ph = 0
                                if enspell_active:
                                    magic_dmg_ph += sub_enspell_damage
                                    magical_damage += magic_dmg_ph
                                verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                            else:
                                print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                elif np.random.uniform() < oa2_sub:
                    print("    Off-hand OA2:") if (verbose_dps or very_verbose_dps) else None
                    for i in range(1):
                        if attempted_hits < 8:
                            attempted_hits += 1
                            if np.random.uniform() < hit_rate22:
                                pdif, crit = get_pdif_melee(attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)
                                sub_hit_damage += phys_dmg_ph
                                tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                                tp_return += tp_ph

                                magic_dmg_ph = 0
                                if enspell_active:
                                    magic_dmg_ph += sub_enspell_damage
                                    magical_damage += magic_dmg_ph
                                verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                            else:
                                print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
            physical_damage += sub_hit_damage


        # Zanshin only procs if main_hit_connects=False or if ZanHasso procs.
        if attempted_hits < 8:
            if ((not main_hit_connects) or (np.random.uniform() < zanhasso)) and (not dual_wield) and (main_skill_type in two_handed_skills):
                if not main_ma_proc: # Even with ZanHasso, Zanshin will not proc if you get a multi-attack proc
                    if np.random.uniform() < zanshin_oa2:
                        print("    Zanshin OA2:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(2):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < zanshin_hit_rate:
                                    pdif, crit = get_pdif_melee(attack1 + player.stats.get("Zanshin Attack",0), main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)*(1.0 + 2.0*(np.random.uniform() < empyrean_am[aftermath-1] and player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0))
                                    zanshin_damage += phys_dmg_ph
                                    tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                                    tp_return += tp_ph

                                    magic_dmg_ph = 0
                                    if enspell_active:
                                        magic_dmg_ph += main_enspell_damage
                                        magical_damage += magic_dmg_ph
                                    verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None

                    elif np.random.uniform() < zanshin:
                        for i in range(1):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < zanshin_hit_rate:
                                    pdif, crit = get_pdif_melee(attack1 + player.stats.get("Zanshin Attack",0), main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, 0, pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)*(1.0 + 2.0*(np.random.uniform() < empyrean_am[aftermath-1] and player.gearset["main"]["Name"] in empyrean_weapons and aftermath>0))
                                    zanshin_damage += phys_dmg_ph
                                    tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                                    tp_return += tp_ph

                                    magic_dmg_ph = 0
                                    if enspell_active:
                                        magic_dmg_ph += main_enspell_damage
                                        magical_damage += magic_dmg_ph
                                    verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "zanshin") if very_verbose_dps else None
                                else:
                                    print(f"     {'Zanshin:':<10s}        "+color_text("red","Missed.")) if very_verbose_dps else None
        physical_damage += zanshin_damage


        # Kick Attack proc
        if attempted_hits < 8:
            if np.random.uniform() < kickattacks and (main_skill_type=="Hand-to-Hand"):
                attempted_hits += 1
                if np.random.uniform() < hit_rate11:
                    kickattacks_pdif, crit = get_pdif_melee(attack1 + player.stats.get("Kick Attacks Attack",0), main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                    phys_dmg_ph = get_phys_damage(kick_dmg, fstr_kick, 0, kickattacks_pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)
                    kickattacks_damage = phys_dmg_ph
                    tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                    tp_return += tp_ph

                    magic_dmg_ph = 0
                    if enspell_active:
                        magic_dmg_ph += main_enspell_damage
                        magical_damage += magic_dmg_ph
                        verbose_output(phys_dmg_ph, magic_dmg_ph, tp_ph, crit, "kick") if very_verbose_dps else None
                    else:
                        print(f"     {'Kick:':<10s}        "+color_text("red","Missed.")) if very_verbose_dps else None

                    # Kick attacks are probably not affected by Verethragna aftermath
        physical_damage += kickattacks_damage


        # Daken proc
        if attempted_hits < 8:
            if np.random.uniform() < daken and (ammo_skill_type=="Throwing"):
                attempted_hits += 1
                if np.random.uniform() < hit_rate_ranged:
                    daken_pdif, crit = get_pdif_ranged(ranged_attack, ammo_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                    phys_dmg_ph = get_phys_damage(ammo_dmg, fstr_ammo, 0, daken_pdif, 1.0, crit, crit_dmg, 0, 0, 0, 0)
                    daken_damage = phys_dmg_ph
                    tp_ph = get_tp(1, ammo_delay, stp)
                    tp_return += tp_ph
                    # Daken is not affected by Kannagi aftermath
                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "daken") if very_verbose_dps else None
                else:
                    print(f"     {'Daken:':<10s}        "+color_text("red","Missed.")) if very_verbose_dps else None

        physical_damage += daken_damage

        if verbose_dps or very_verbose_dps:
            print(f"    =       Phys. Damage: {physical_damage:>6.0f}")
            print(f"    =       Magic Damage: {magical_damage:>6.0f}")
            print(f"    =       TP Returned:  {tp_return:>6.1f}")

        return(physical_damage, tp_return, magical_damage)


    else: # Not running simulations, just checking averages

        striking_flourish = player.abilities.get("Striking Flourish",False)
        ternary_flourish = player.abilities.get("Ternary Flourish",False)
        climactic_flourish = player.abilities.get("Climactic Flourish",False)
        sneak_attack = player.abilities.get("Sneak Attack",False)
        trick_attack = player.abilities.get("Trick Attack",False)

        if sneak_attack or trick_attack:
            hit_rate11 = 1.0
            hit_rate21 = 1.0

        # Use multi-attack values to estimate the number of hits per weapon. This must include Flourishes, which can force multi-attacks.
        main_hits, sub_hits, daken_hits, kickattack_hits, zanshin_hits = get_ma_rate3(player.main_job, nhits, qa, ta, da, oa_list, dual_wield, hit_rate_matrix, hit_rate_ranged, daken, kickattacks, zanshin, zanhasso, zanshin_hit_rate, zanshin_oa2, striking_flourish, ternary_flourish, True)

        if player.abilities.get("EnSpell",False):
            magical_damage += main_hits * get_enspell_damage(enhancing_magic_skill, enspell_damage_percent_main, enspell_damage_main)
            magical_damage += sub_hits * get_enspell_damage(enhancing_magic_skill, enspell_damage_percent_sub, enspell_damage_sub)
            magical_damage += kickattack_hits * get_enspell_damage(enhancing_magic_skill, enspell_damage_percent_main, enspell_damage_main)
            magical_damage += zanshin_hits * get_enspell_damage(enhancing_magic_skill, enspell_damage_percent_main, enspell_damage_main)
            magical_damage *= (1 + dayweather)
            magical_damage *= (1 + elemental_magic_attack_bonus)
            magical_damage *= (1 + 0.25*magic_crit_rate2)

        tp_per_attack_round = 0
        tp_per_attack_round += get_tp(main_hits + sub_hits + kickattack_hits, (mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay), stp)  # Non-zanshin hits get normal TP. Note that H2H use half of today mdelay for each hand
        tp_per_attack_round += get_tp(zanshin_hits, (mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay), stp, player.main_job=="sam") # Zanshin hits get bonus TP if SAM is your main job and you have Ikishoten merits, which I assume you do.
        tp_per_attack_round += get_tp(daken_hits, ammo_delay, stp)

        # This next line's function call can probably be brought into this main code instead of being its own function/file. TODO
        time_per_attack_round = get_delay_timing(player.stats["Delay1"], player.stats["Delay2"] if dual_wield and (player.gearset["main"]["Skill Type"] != "Hand-to-Hand") else 0, player.stats.get("Dual Wield",0)/100, player.stats.get("Martial Arts",0), player.stats.get("Magic Haste",0), player.stats.get("JA Haste",0), player.stats.get("Gear Haste",0))

        # Add the passive TP generation from Regain, occuring once every 3 seconds.
        regain_tp = player.stats.get("Dual Wield",0)*(player.gearset["main"]["Name"]=="Gokotai") + player.stats.get("Regain",0)
        tp_per_attack_round += (time_per_attack_round/3)*(regain_tp) 

        attacks_per_ws = (ws_threshold - starting_tp) / tp_per_attack_round

        time_per_ws = time_per_attack_round * attacks_per_ws # Real time (seconds) to reach your desired TP value from your starting TP value using the defined gearset and buffs.


        # Damage from first main-hand hit with no bonuses (also known as the damage dealt by multi-attacks from the main-hand)
        main_hit_pdif = get_avg_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
        main_hit_damage = get_avg_phys_damage(main_dmg, fstr_main, 0, main_hit_pdif, 1.0, crit_rate, crit_dmg, 0, 0, 0) #Using FTP2, WSD=0, etc
        main_hit_damage *= (empyrean_am_damage_bonus if player.gearset["main"]["Name"]!="Verethragna" else 1.0) # Verethragna Empyrean Aftermath apparently only applies to the first main-hit?
        physical_damage += main_hits*main_hit_damage

        # Calculate the correction to the first hit based on the full set of buffs and bonuses.
        sneak_attack_bonus = (player.stats["DEX"] * (1+player.stats.get("Sneak Attack Bonus",0)/100))*sneak_attack*(player.main_job=="thf") # THF subjob does not gain the extra base damage
        trick_attack_bonus = (player.stats["AGI"] * (1+player.stats.get("Trick Attack Bonus",0)/100))*trick_attack*(player.main_job=="thf") # THF subjob does not gain the extra base damage
        climactic_flourish_bonus = (0.5*player.stats["CHR"] * (1+player.stats.get("Flourish CHR%",0)/100))*climactic_flourish
        striking_flourish_bonus = (1.0*player.stats["CHR"] * (1+player.stats.get("Flourish CHR%",0)/100))*striking_flourish
        ternary_flourish_bonus = (1.0*player.stats["CHR"] * (1+player.stats.get("Flourish CHR%",0)/100))*ternary_flourish

        climactic_crit_dmg = player.stats.get("Climactic Crit Damage",0)/100*climactic_flourish # Crit damage +31% for the first hit when using the DNC Empy+3 head
        striking_crit_rate = player.stats.get("Striking Crit Rate",0)/100*striking_flourish # Crit rate +70% for the first hit when using the DNC Empy+3 body
        vajra_bonus_crit_dmg = 0.3*(player.gearset["main"]["Name"]=="Vajra" and (sneak_attack or trick_attack)) # Crit damage +30% for the first hit.

        first_main_hit_crit_rate = (1.0 if sneak_attack or trick_attack or climactic_flourish else (crit_rate+striking_crit_rate*(crit_rate>0))) # Special crit rate for SA/TA/Flourishes.
        adjusted_crit_dmg = (crit_dmg + vajra_bonus_crit_dmg)*(1+climactic_crit_dmg) # Special crit damage that applies to first hit of SA/TA/ClimacticFlourish. Climactic with DNC Empy head provides a unique Crit Damage that applies separately.
        first_main_hit_pdif = get_avg_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, first_main_hit_crit_rate)
        first_main_hit_damage = get_avg_phys_damage(main_dmg, fstr_main, 0, first_main_hit_pdif, 1.0, first_main_hit_crit_rate, adjusted_crit_dmg, 0, 0, 0, sneak_attack_bonus, trick_attack_bonus, climactic_flourish_bonus, striking_flourish_bonus, ternary_flourish_bonus)

        first_main_hit_damage *= relic_hidden_damage_bonus # Hidden relic damage only applies to the first main-hand hit.
        first_main_hit_damage *= empyrean_am_damage_bonus
        first_main_hit_damage *= prime_hidden_damage_bonus

        # Adds the extra damage gained by those bonuses to the first hit's damage.
        physical_damage += (first_main_hit_damage*hit_rate11 - main_hit_damage*hit_rate11)

        # Striking Flourish also boosts the crit rate for its double attack hit, but doesn't provide the +100% CHR bonus (probably)
        if striking_flourish:
            # Define a new crit rate that adds 70% only if crit_rate>0 already (only for critical hit WSs)
            striking_flourish_crit_rate = crit_rate + striking_crit_rate*(crit_rate>0) # This crit_rate>0 ensures I am not letting non-crit WSs crit.
            striking_flourish_pdif1 = get_avg_pdif_melee(attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, striking_flourish_crit_rate)
            striking_flourish_DA_damage = get_avg_phys_damage(main_dmg, fstr_main, wsc, striking_flourish_pdif1, ftp2, striking_flourish_crit_rate, crit_dmg, 0, ws_bonus, ws_trait)
            physical_damage += (striking_flourish_DA_damage - main_hit_damage)*hit_rate11 # Add on the difference in damage from a 2nd hit with higher crit.

        # Calculate the damage for off-hand hits, which receive no bonuses. No fancy correction terms are required here.
        offhand_pdif = get_avg_pdif_melee(attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
        offhand_damage = get_avg_phys_damage(sub_dmg, fstr_sub, 0, offhand_pdif, 1.0, crit_rate, crit_dmg, 0, 0, 0)
        physical_damage += offhand_damage*sub_hits

        physical_damage *= (1 + da_dmg*da)*(1 + ta_dmg*ta) # Main-hand and off-hand hits from a multi-attack are fully boosted by "DA Damage" and "TA Damage" stats.

        # Now add Kick Attacks damage. Again, nothing fancy here except we use the MNK-specific "Kick Attacks Attack" stat.
        kickattacks_pdif = get_avg_pdif_melee(attack1 + player.stats.get("Kick Attacks Attack",0), main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
        kickattacks_damage = get_avg_phys_damage(kick_dmg, fstr_kick, 0, kickattacks_pdif, 1.0, crit_rate, crit_dmg, 0, 0, 0)
        physical_damage += kickattacks_damage*kickattack_hits
        # Kick attacks probably aren't affected by Verethragna aftermath

        # Now Daken shuriken throws.
        daken_pdif = get_avg_pdif_ranged(ranged_attack, ammo_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
        daken_damage = get_avg_phys_damage(ammo_dmg, fstr_ammo, 0, daken_pdif, 1.0, crit_rate, crit_dmg, 0, 0, 0)
        physical_damage += daken_hits*daken_damage / empyrean_am_damage_bonus
        # Daken is not affected by Kannagi aftermath

        # Now Zanshin hits, which also have a SAM-specific "Zanshin Attack" stat.
        zanshin_pdif = get_avg_pdif_melee(attack1 + player.stats.get("Zanshin Attack",0), main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
        zanshin_damage = get_avg_phys_damage(main_dmg, fstr_main, 0, zanshin_pdif, 1.0, crit_rate, crit_dmg, 0, 0, 0) # Using FTP2, WSD=0, etc
        zanshin_damage *= empyrean_am_damage_bonus # Zanshin damage is affected by empyrean aftermath since it is just another main-hand hit.
        physical_damage += zanshin_hits*zanshin_damage


    damage = physical_damage + magical_damage

    if input_metric=="Damage dealt":
        metric = damage
        invert = 1
    elif input_metric=="TP return":
        metric = tp_per_attack_round
        invert = 1
    elif input_metric=="DPS":
        metric = damage / time_per_attack_round # DPS for TP phase only seems like a useless metric. You really need to include TP and WS phases together for DPS to mean anything.
        invert = 1
    elif input_metric=="TP > Damage":
        metric = damage*tp_per_attack_round*tp_per_attack_round/1e4
        invert = 1
    elif input_metric=="Damage > TP":
        metric = damage*damage*tp_per_attack_round/1e6
        invert = 1
    elif input_metric=="Time to WS":
        metric = time_per_ws
        invert = -1
    else:
        metric = time_per_ws
        invert = -1

    return(metric, [damage, tp_per_attack_round, time_per_attack_round, invert], magical_damage) 


def cast_spell(player, enemy, spell_name, spell_type, input_metric):
    #
    # Calculate average spell damage. Includes "Ranged Attack" and "Quick Draw"
    # A lot of the magic damage code is repeated and I'd like to reduce this later.
    #

    if spell_name == "EnSpell":

        main_skill_type = player.gearset["main"]["Skill Type"]
        # two_handed_skills = ["Great Sword", "Great Katana", "Great Axe", "Polearm", "Scythe", "Staff",]
        # one_handed_skills = ["Axe", "Club", "Dagger", "Sword", "Katana",]
        # hit_rate_cap_main = 0.99 if main_skill_type in one_handed_skills or main_skill_type == "Hand-to-Hand" else 0.95
        # enemy_evasion = enemy.stats["Evasion"]
        # accuracy1 = player.stats["Accuracy1"]
        # hit_rate11 = get_hit_rate(accuracy1, enemy_evasion, hit_rate_cap_main)

        base_delay = (player.stats["Delay1"] + player.stats["Delay2"])/2 
        mdelay = (base_delay - player.stats.get("Martial Arts",0)) * ((1 - player.stats.get("Dual Wield",0)/100))
        stp = player.stats.get("Store TP",0)/100
        tp_return = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)

        enhancing_magic_skill = player.abilities.get("Enh. Skill",0)
        enspell_damage_percent_main = player.stats.get("EnSpell Damage% main",0) + player.stats.get("EnSpell Damage%",0)
        enspell_damage_main = player.stats.get("EnSpell Damage main",0) + player.stats.get("EnSpell Damage",0)
        magic_crit_rate2 = player.stats.get("Magic Crit Rate II",0)/100

        active_storm = player.abilities.get("Storm spell", False)
        if active_storm!="None" and player.gearset["waist"]["Name"]=="Hachirin-no-Obi":
            dayweather = 0.25 if "II" in active_storm else 0.10 # Assume the EnSpell element matches the storm spell selected.
        else:
            dayweather = 0

        # Assume the EnSpell element matches the element corresponding to the gear with the highest elemental damage bonus, ignoring light/dark. Orpheus sash is applies separately.
        elemental_magic_attack_bonus = (max([player.stats.get(f"{element.capitalize()} Elemental Bonus", 0) for element in ["Earth", "Water", "Wind", "Fire", "Ice", "Thunder"]])/100 + player.stats.get("Elemental Bonus",0)/100)
        magical_damage = get_enspell_damage(enhancing_magic_skill, enspell_damage_percent_main, enspell_damage_main) * (1 + dayweather) * (1 + elemental_magic_attack_bonus) * (1.0 + 0.25*magic_crit_rate2)

        # magical_damage *= hit_rate11
        # tp_return *= hit_rate11

        return(magical_damage, [magical_damage, tp_return, 1])

    dINT = player.stats["INT"] - enemy.stats["INT"]
    dMND = player.stats["MND"] - enemy.stats["MND"]
    
    dINT = 0 if dINT < 0 else dINT # dINT can be negative, but its relation with base damage is different and untested in this range.
    
    magic_damage_stat = player.stats.get("Magic Damage",0) # Some jobs have special/specific magic damage, such as NIN, which has +40 Magic Damage from Job Points which only apply to Ninjutsu spells.
    magic_attack = player.stats.get("Magic Attack",0) # Some equipment has special magic attack, which applies in separate multiplicative terms on a per-element basis. Normally we see (1+matk)/(1+mdef), but Archon Ring uses something like (1+matk)/(1+mdef) * (1+dark_matk)/(1+dark_mdef)
    magic_accuracy = player.stats.get("Magic Accuracy",0) + player.stats.get("main Magic Accuracy Skill",0) # We add Magic Accuracy from dSTAT later and magic skill
    magic_crit_rate2 = 1 + 0.25*(player.stats.get("Magic Crit Rate II",0)/100) # Magic Crit Rate II is +25% damage x% of the time.

    if spell_name.split()[0][-2:]=="ra" and player.main_job=="geo": # Theurgic Focus boosts Magic Damage and Magic Attack for -ra spells.
        magic_damage_stat += player.stats.get("-ra Magic Damage",0)
        magic_attack += player.stats.get("-ra Magic Attack",0)

    enemy_magic_defense = enemy.stats.get("Magic Defense",0)
    enemy_magic_evasion = enemy.stats.get("Magic Evasion",0)
    enemy_mdt = enemy.stats.get("MDT",1.0) # Enemy MDT is usually 1.0 (-0%) unless the enemy casts shell or a similar spell/ability.

    dayweather = 1.0 # We increase this later
    storm_elements = {"Sandstorm II":"earth","Rainstorm II":"water","Windstorm II":"wind","Firestorm II":"fire","Hailstorm II":"ice","Thunderstorm II":"thunder","Aurorastorm II":"light","Voidstorm II":"dark",
                      "Sandstorm":"earth","Rainstorm":"water","Windstorm":"wind","Firestorm":"fire","Hailstorm":"ice","Thunderstorm":"thunder","Aurorastorm":"light","Voidstorm":"dark"}
    active_storm =  player.abilities.get("Storm spell",False)

    skillchain_step = 2
    magic_burst_multiplier = 1.0 # Standard +35% damage for magic bursting
    burst_bonus_multiplier = 1.0 # Magic Burst damage bonus from gear. BG lists this as separate from the standard MB multiplier
    if player.abilities.get("Magic Burst",False):
        magic_accuracy += 100 + player.stats.get("Magic Burst Accuracy",0)
        magic_burst_multiplier += 0.35
        skillchain_steps_bonus = (skillchain_step-2)*0.10 # +10% magic damage for each step in the skillchain after the 2nd (for each extra skillchain formed)
        magic_burst_multiplier += skillchain_steps_bonus


        burst_bonus1 = 40 if player.stats.get("Magic Burst Damage",0) > 40 else player.stats.get("Magic Burst Damage",0)
        burst_bonus2 = player.stats.get("Magic Burst Damage II",0)
        burst_bonus3 = player.stats.get("Magic Burst Damage Trait",0)
        burst_bonus_multiplier += burst_bonus1/100 + burst_bonus2/100 + burst_bonus3/100 # Magic Burst damage bonus from gear. BG lists this as separate from the standard MB multiplier


    # Calculate Quick Draw damage and TP return.
    if spell_type=="Quick Draw":
        element = spell_name.split()[0]

        magic_accuracy += player.stats.get("Quick Draw Magic Accuracy",0)
        magic_accuracy += player.stats["AGI"]/2 # Quick Draw magic accuracy benefits from AGI.
        quick_draw_damage = player.stats.get("Quick Draw Damage",0) # +40 from JP, +20 from AF+3 head, +20 from AF+3 feet

        ranged_dmg = player.stats.get("Ranged DMG",0)
        ammo_dmg = player.stats.get("Ammo DMG",0)
        ranged_delay = player.stats.get("Ranged Delay",0)
        ammo_delay = player.stats.get("Ammo Delay",0)

        magic_hit_rate = get_magic_hit_rate(magic_accuracy, enemy_magic_evasion) if enemy_magic_evasion > 0 else 1.0
        resist_state = get_resist_state_average(magic_hit_rate) # TODO: When creating a distribution, use a proper sampling of resist states, rather than the average.
        magic_attack_ratio = (100 + magic_attack) / (100 + enemy_magic_defense)

        if player.gearset["waist"]["Name"]=="Hachirin-no-Obi" and active_storm:
            if element.lower() == storm_elements.get(active_storm,False):
                dayweather = 1.25 if "II" in active_storm else 1.1

        affinity = 1 + 0.05*player.stats.get(f"{element} Affinity",0) + 0.05*(player.stats.get(f"{element} Affinity",0)>0) # Elemental Affinity Bonus. Only really applies to Magian Trial staves. Archon Ring is different.
        element_magic_attack_bonus = 1 + (player.stats.get(f"{element.capitalize()} Elemental Bonus", 0)/100 + player.stats.get("Elemental Bonus",0)/100) # Archon Ring, Pixie Hairpin +1, Orpheus, and more get their own (1+matk)/(1+mdef) terms.

        magic_multiplier = resist_state*magic_attack_ratio*element_magic_attack_bonus*dayweather*enemy_mdt*affinity*magic_crit_rate2

        base_damage = int(((ranged_dmg+ammo_dmg)*2 + quick_draw_damage) * (1 + player.stats.get("Quick Draw Damage%",0)/100) + magic_damage_stat)
        damage = base_damage * magic_multiplier

        tp_return = get_tp(1.0, ranged_delay+ammo_delay, player.stats.get("Store TP",0)) # Assume 100% hit rate on Quick Draw

        if input_metric=="Damage dealt":
            metric = damage
            invert = 1
        elif input_metric=="TP return":
            metric = tp_return
            invert = 1
        else:
            metric = damage
            invert = 1

        return(metric, [damage, tp_return, invert]) 



    # Now deal with Ninjutsu damage.
    elif spell_type=="Ninjutsu":
        spells = {
                "Katon": "Fire",
                "Suiton": "Water",
                "Raiton": "Thunder",
                "Doton": "Earth",
                "Huton": "Wind",
                "Hyoton": "Ice"
                }
        element = spells[spell_name.split(":")[0]].lower()
        tier = spell_name.split()[-1]

        magic_attack += player.stats.get("Ninjutsu Magic Attack",0)
        magic_damage_stat += player.stats.get("Ninjutsu Magic Damage",0)
        magic_accuracy += player.stats.get("Ninjutsu Magic Accuracy",0) + player.stats.get("Ninjutsu Skill",0)

        magic_hit_rate = get_magic_hit_rate(magic_accuracy, enemy_magic_evasion) if enemy_magic_evasion > 0 else 1.0
        resist_state = get_resist_state_average(magic_hit_rate) # TODO: When creating a distribution, use a proper sampling of resist states, rather than the average.
        magic_attack_ratio = (100 + magic_attack) / (100 + enemy_magic_defense)

        if player.gearset["waist"]["Name"]=="Hachirin-no-Obi" and active_storm:
            if element.lower() == storm_elements.get(active_storm,False):
                dayweather = 1.25 if "II" in active_storm else 1.1

        affinity = 1 + 0.05*player.stats.get(f"{element} Affinity",0) + 0.05*(player.stats.get(f"{element} Affinity",0)>0) # Elemental Affinity Bonus. Only really applies to Magian Trial staves. Archon Ring is different.
        element_magic_attack_bonus = 1 + (player.stats.get(f"{element.capitalize()} Elemental Bonus", 0)/100 + player.stats.get("Elemental Bonus",0)/100) # Archon Ring, Pixie Hairpin +1, Orpheus, and more get their own (1+matk)/(1+mdef) terms.

        ninjutsu_damage_multiplier = 1 + player.stats.get("Ninjutsu Damage%",0)/100
        
        futae_multiplier = 1.0
        if player.abilities.get("Futae",False):
            futae_multiplier += 0.5 + player.stats.get("Futae Bonus",0)/100

        # Now get the Ninjutsu Skill potency multiplier.
        ninjutsu_skill = player.stats.get("Ninjutsu Skill",0)
        if tier == "Ichi":
            ninjutsu_skill_potency = ((100 + (ninjutsu_skill-50)/2)/100 if ninjutsu_skill <= 250 else 2.0) if ninjutsu_skill > 50 else 1.0
        elif tier == "Ni":
            ninjutsu_skill_potency = ((100 + (ninjutsu_skill-126)/2)/100 if ninjutsu_skill <= 350 else 2.12) if ninjutsu_skill > 126 else 1.0
        elif tier == "San":
            ninjutsu_skill_potency = ((100 + (ninjutsu_skill-276)/2)/100 if ninjutsu_skill <= 500 else 2.12) if ninjutsu_skill > 276 else 1.0
        else:
            ninjutsu_skill_potency = 0 # If something breaks and tier wasn't given, then just give 0 potency (results in zero damage always).

        # Each elemental damage spell has an M and V associated with it to determine its base damage, based on dINT or dMND. TODO: Integerize at each step of magic_multiplier
        m,v = get_mv_ninjutsu(tier, dINT)
        base_damage = int(v+magic_damage_stat+dINT*m)
        magic_multiplier = resist_state*magic_attack_ratio*element_magic_attack_bonus*dayweather*enemy_mdt*affinity*magic_crit_rate2*ninjutsu_damage_multiplier*futae_multiplier*ninjutsu_skill_potency*magic_burst_multiplier*burst_bonus_multiplier
        damage = base_damage * magic_multiplier

        tp_return = 0 # Note that Ninjutsu never returns TP since Occult Acumen is based on MP consumed.

        if input_metric=="Damage dealt": 
            metric = damage
            invert = 1
        else:
            metric = damage
            invert = 1

        return(metric, [damage, tp_return, invert]) 

    elif spell_type=="Elemental Magic":
        spells = {
                "Stone":[4,"Earth"],"Stone II":[16,"Earth"],"Stone III":[40,"Earth"],"Stone IV":[88,"Earth"],"Stone V":[156,"Earth"],"Stone VI":[237,"Earth"],
                "Water":[5,"Water"],"Water II":[19,"Water"],"Water III":[46,"Water"],"Water IV":[99,"Water"],"Water V":[175,"Water"],"Water VI":[266,"Water"],
                "Aero":[6,"Wind"],"Aero II":[22,"Wind"],"Aero III":[54,"Wind"],"Aero IV":[115,"Wind"],"Aero V":[198,"Wind"],"Aero VI":[299,"Wind"],
                "Fire":[7,"Fire"],"Fire II":[26,"Fire"],"Fire III":[63,"Fire"],"Fire IV":[135,"Fire"],"Fire V":[288,"Fire"],"Fire VI":[339,"Fire"],
                "Blizzard":[8,"Ice"],"Blizzard II":[31,"Ice"],"Blizzard III":[75,"Ice"],"Blizzard IV":[162,"Ice"],"Blizzard V":[267,"Ice"],"Blizzard VI":[386,"Ice"],
                "Thunder":[9,"Thunder"],"Thunder II":[37,"Thunder"],"Thunder III":[91,"Thunder"],"Thunder IV":[195,"Thunder"],"Thunder V":[306,"Thunder"],"Thunder VI":[437,"Thunder"],
                "Stoneja":[298,"Earth"],
                "Waterja":[318,"Water"],
                "Aeroja":[338,"Wind"],
                "Firaja":[358,"Fire"],
                "Blizzaja":[378,"Ice"],
                "Thundaja":[398,"Thunder"],
                "Geohelix II":[78,"Earth"],
                "Hydrohelix II":[78,"Water"],
                "Anemohelix II":[78,"Wind"],
                "Pyrohelix II":[78,"Fire"],
                "Cryohelix II":[78,"Ice"],
                "Ionohelix II":[78,"Thunder"],
                "Luminohelix II":[78,"Light"],
                "Noctohelix II":[78,"Dark"],
                "Kaustra":[0,"Dark"],
                "Impact":[666,"Dark"]
        }


        if spell_name in spells:
            element = spells[spell_name][1].lower()
            if spell_name[-2:]=="ja":
                tier = "ja"
                mp_cost = spells[spell_name][0]
            elif "helix" in spell_name:
                tier="helix"
                mp_cost = spells[spell_name][0]
                magic_attack += player.stats.get("Helix Magic Attack",0)
                magic_accuracy += player.stats.get("Helix Magic Accuracy",0)
            elif spell_name=="Kaustra":
                tier=None
                mp_cost = spells[spell_name][0]
            elif spell_name=="Impact":
                mp_cost = spells[spell_name][0]
                tier=None
            elif spell_name.split()[-1] in ["II","III","IV","V","VI"]:
                tier = spell_name.split()[-1]
                mp_cost = spells[spell_name][0]
            else:
                tier = "I"
                mp_cost = spells[spell_name][0]

        ebullience_multiplier = 1.0
        ebullience = player.abilities.get("Ebullience",False)
        if ebullience:
            ebullience_multiplier += 0.2 + player.stats.get("Ebullience Bonus",0)/100
            # We've already added +40 magic damage from Ebullience in the setup code. We do add +40 magic damage to Kaustra manually below, though.

        klimaform_multiplier = 1.0 + player.abilities.get("Klimaform",False)*player.stats.get("Klimaform Damage%",0)/100

        if spell_name == "Kaustra":
            player_level = 99
            dINT = 0 if dINT < 0 else 300 if dINT > 300 else dINT # Assuming lower dINT cap of 0. This is probably not exactly true.
            base_damage = np.round(0.067*player_level,1)*(37 + 40*ebullience + int(0.67*dINT)) # Ebullience applies +40 magic damage inside the Kaustra base damage formula too.
        elif spell_name == "Impact":
            m, v, window = 0, 0, 0
            base_damage = 1
        else:
            m, v, window = get_mv_blm(element, tier, dINT)
            base_damage = int(v + magic_damage_stat + (dINT-window)*m) # Black Magic uses (dINT-window)*m. This was simply a choice of the person who collected and fit the data.



        magic_accuracy += player.stats.get("Elemental Magic Skill",0) + get_dstat_macc(player.stats["INT"], enemy.stats["INT"]) # Calculate the magic accuracy bonus/penalty from dINT.


        magic_hit_rate = get_magic_hit_rate(magic_accuracy, enemy_magic_evasion) if enemy_magic_evasion > 0 else 1.0
        resist_state = get_resist_state_average(magic_hit_rate) # TODO: When creating a distribution, use a proper sampling of resist states, rather than the average.
        magic_attack_ratio = (100 + magic_attack) / (100 + enemy_magic_defense)

        if player.gearset["waist"]["Name"]=="Hachirin-no-Obi" and active_storm:
            if element.lower() == storm_elements.get(active_storm,False):
                dayweather = 1.25 if "II" in active_storm else 1.1

        affinity = 1 + 0.05*player.stats.get(f"{element} Affinity",0) + 0.05*(player.stats.get(f"{element} Affinity",0)>0) # Elemental Affinity Bonus. Only really applies to Magian Trial staves. Archon Ring is different.
        element_magic_attack_bonus = 1 + (player.stats.get(f"{element.capitalize()} Elemental Bonus", 0)/100 + player.stats.get("Elemental Bonus",0)/100) # Archon Ring, Pixie Hairpin +1, Orpheus, and more get their own (1+matk)/(1+mdef) terms.


        magic_multiplier = resist_state*magic_attack_ratio*element_magic_attack_bonus*dayweather*enemy_mdt*affinity*magic_crit_rate2*ebullience_multiplier*klimaform_multiplier*magic_burst_multiplier*burst_bonus_multiplier

        damage = base_damage * magic_multiplier

        # Occult Acumen allows spellcasting to return TP based on the amount of MP the spell costs before reductions.
        stp = player.stats.get("Store TP",0)/100
        occult_acumen = player.stats.get("Occult Acumen",0)/100

        tp_return = int(mp_cost * occult_acumen) * (1 + stp)

        if input_metric=="Damage dealt":
            metric = damage
            invert = 1
        elif input_metric=="TP return":
            metric = tp_return
            invert = 1
        else:
            metric = damage
            invert = 1

        return(metric, [damage, tp_return, invert]) 
    
    elif spell_type=="Ranged Attack": # I treat Ranged Attacks as spells to keep everything together.
        #
        # Estimate the average white damage from a single /ra ranged attack.
        #

        aftermath = player.abilities.get("Aftermath",0)
        # Empyrean Aftermath: 30%/40%/50% chance of dealing triple damage.
        empyrean_am_damage_bonus = 1.0
        if player.gearset["ranged"]["Name"] in ["Gandiva","Armageddon"] and aftermath>0:
            empyrean_am = [0.3, 0.4, 0.5]
            empyrean_am_damage_bonus += 2*empyrean_am[aftermath-1]

        # Hidden triple damage +13% of the time on relics. No Aftermath required.
        relic_hidden_damage_bonus = 1.0
        if player.gearset["ranged"]["Name"] in ["Annihilator","Yoichinoyumi"]:
            relic_hidden_damage_bonus += 2*0.13

        # Mythic Aftermath Lv3: 40% chance to double damage, 20% chance to triple damage.
        mythic_am_damage_bonus = 1.0
        if player.gearset["ranged"]["Name"] in ["Gastraphetes","Death Penalty"] and aftermath==3:
            mythic_am_damage_bonus += 1*0.4 + 2*0.2


        player_str = player.stats["STR"]
        player_agi = player.stats["AGI"]

        stp = player.stats.get("Store TP",0)/100
        
        enemy_agi = enemy.stats.get("AGI",0)
        enemy_evasion = enemy.stats.get("Evasion",0)
        enemy_defense = enemy.stats.get("Defense",0)
        
        sharpshot = player.abilities.get("Sharpshot",False)
        hover_shot = player.abilities.get("Hover Shot",False)

        true_shot = player.stats.get("True Shot",0)/100

        double_shot = player.stats.get("Double Shot",0)/100
        double_shot = 1.0 if double_shot > 1.0 else double_shot
        double_shot_damage = player.stats.get("Double Shot Damage%",0)/100

        triple_shot = player.stats.get("Triple Shot",0)/100
        triple_shot = 1.0 if triple_shot > 1.0 else triple_shot
        triple_shot_damage = player.stats.get("Triple Shot Damage%",0)/100

        quad_shot = player.stats.get("Quad Shot",0)/100

        crit_dagi = ((player_agi - enemy_agi)/10)/100 if (player_agi > enemy_agi) else 0
        crit_rate = player.stats.get("Crit Rate",0)/100 + + player.stats.get("Ranged Crit Rate", 0)/100 + crit_dagi # Ranged attacks gain crit rate from AGI, not DEX
        crit_dmg = player.stats.get("Crit Damage",0)/100 + player.stats.get("Ranged Crit Damage",0)/100 # "Crit damage" plus "Dead Aim trait" bonuses

        pdl_gear = player.stats.get("PDL",0)/100
        pdl_trait = player.stats.get("PDL Trait",0)/100
        
        ranged_delay = player.gearset["ranged"].get("Delay",0)
        ammo_delay = player.gearset["ammo"].get("Delay",0)

        ranged_dmg = player.stats.get("Ranged DMG",0)
        ammo_dmg = player.stats.get("Ammo DMG",0)
        fstr_rng = get_fstr2(ranged_dmg, player.stats["STR"], enemy.stats["VIT"])

        player_rangedattack = player.stats.get("Ranged Attack",0)
        player_rangedaccuracy = player.stats.get("Ranged Accuracy",0) + 100*hover_shot

        barrage_hits = 0
        if player.abilities.get("Barrage",False) and player.gearset["ammo"].get("Type","None") in ["Bolt","Bullet","Arrow"]:
            # Barrage bonuses (do not apply to throwing)
            player_rangedattack += player.stats.get("Barrage Ranged Attack",0)
            player_rangedaccuracy += player.stats.get("Barrage Ranged Accuracy",0)
            barrage_hits += player.stats.get("Barrage",0)

        ranged_skills = ["Marksmanship","Archery","Throwing"]
        ranged_skill_type = player.gearset["ranged"].get("Skill Type",False)
        ranged_skill_type = player.gearset["ammo"].get("Skill Type",None) if not ranged_skill_type else ranged_skill_type


        # Calculate ranged hit rates.
        ranged_accuracy = player_rangedaccuracy
        hit_rate_cap_ranged = 0.99 if sharpshot else 0.95

        hit_rate_ranged = get_hit_rate(ranged_accuracy, enemy_evasion, hit_rate_cap_ranged)

        # Now calculate damage dealt and TP returned by the /ra, considering one shot at a time for multi-shot hits.
        phys = 0
        tp_return = 0

        nhits = 1 + barrage_hits

        main_hits = 0
        for i in np.arange(nhits):
            # Add the average number of barrage hits gained.
            # Note that if one hit fails, then the remaining hits are skipped.
            main_hits += 1*(hit_rate_ranged**(i+1))

        tp_return += get_tp(main_hits, ranged_delay+ammo_delay, stp)
        avg_pdif_rng = get_avg_pdif_ranged(player_rangedattack, ranged_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
        ranged_hit_damage = get_avg_phys_damage(ranged_dmg+ammo_dmg, fstr_rng, 0, avg_pdif_rng, 1.0, crit_rate, crit_dmg, 0, 0, 0)
        phys += ranged_hit_damage*main_hits * relic_hidden_damage_bonus

        # Add the bonus damage from a double shot proc. For 0% Double shot, this will add 0 damage.
        double_shot_hits = 1*hit_rate_ranged*double_shot
        tp_return += get_tp(double_shot_hits, ranged_delay+ammo_delay, stp)
        ranged_hit_damage = get_avg_phys_damage(ranged_dmg+ammo_dmg, fstr_rng, 0, avg_pdif_rng, 1.0, crit_rate, crit_dmg, 0, 0, 0)
        phys += ranged_hit_damage*double_shot_hits*(1+double_shot_damage)

        # Add the bonus damage from a triple shot proc. For 0% Triple shot, this will add 0 damage.
        triple_shot_hits = 2*hit_rate_ranged*triple_shot
        tp_return += get_tp(triple_shot_hits, ranged_delay+ammo_delay, stp)
        ranged_hit_damage = get_avg_phys_damage(ranged_dmg+ammo_dmg, fstr_rng, 0, avg_pdif_rng, 1.0, crit_rate, crit_dmg, 0, 0, 0)
        phys += ranged_hit_damage*triple_shot_hits*(1+triple_shot_damage)

        # Add the bonus damage from a quad shot proc. For 0% Quad shot, this will add 0 damage.
        quad_shot_hits = 3*hit_rate_ranged*quad_shot
        tp_return += get_tp(quad_shot_hits, ranged_delay+ammo_delay, stp)
        phys += ranged_hit_damage*quad_shot_hits

        # Recycle procs will increase TP gained by +50 for 5/5 Recycle merits on Ranger
        # This applies to all double/triple/quad shot bonuses too. Recycle simply has to proc.
        if "Arcadian Beret" in player.gearset["head"]["Name"]:
            recycle = player.stats.get("Recycle",0)
            recycle = 90 if recycle > 90 else recycle
            tp_return += 50*recycle/100 # Chance to proc on first hit.
            tp_return += 1*50*recycle/100*double_shot # Chance to proc on the Double Shot
            tp_return += 2*50*recycle/100*triple_shot # Chance to proc on two Triple Shots
            tp_return += 3*50*recycle/100*quad_shot # Chance to proc on three Quad shots (should be zero for Ranger anyway)

    # Apply damage multipliers which affect all hits. 
    damage = phys * (1 + true_shot) * (1 + hover_shot) * empyrean_am_damage_bonus * mythic_am_damage_bonus

    if input_metric=="Damage dealt":
        metric = damage
        invert = 1
    elif input_metric=="TP return":
        metric = tp_return
        invert = 1
    elif input_metric=="TP > Damage":
        metric = damage*tp_return*tp_return/1e4
        invert = 1
    elif input_metric=="Damage > TP":
        metric = damage*damage*tp/1e6
        invert = 1
    else:
        metric = damage
        invert = 1

    return(metric, [damage, tp_return, invert]) 


def real_tp_round(player, enemy, starting_tp, ws_threshold, input_metric):
    pass


def real_ws(player, enemy, ws_name, tp, ws_type, input_metric):
    #
    #
    #
    pass


def average_ws(player, enemy, ws_name, input_tp, ws_type, input_metric, simulation=False):
    #
    # Calculate average weapon skill damage.
    #
    # Player: Class which contains all of the player's stats (player.stats),
    #                                     the gearset (player.gearset),
    #                                     the buffs (player.buffs; only including food/whm/geo/cor/brd),
    #                                     and player abilities/spells (player.abilities; including the checkboxes for things like Last Resort)
    #     Attributes also include player.main_job, player.sub_job, player.master_level, player.main_job_level, and player.sub_job_level
    # Enemy: Class which contains the enemy's stats (enemy.stats).
    # ws_name: The name of the weapon skill being used.
    # tp: The TP value at which to use the WS. I apply TP bonus and limit TP to 3000 before this function is called. The TP being used by this function is the effective TP. TP Bonus has already been added when calling this function.
    # ws_type: includes ["melee","ranged","magical"] and is used to separate how the physical/magical portions of the damage contribute. Hybrid WSs are considered "melee" but activate a "hybrid" flag which enables their magical damage.
    #

    # ===========================================================================
    # ===========================================================================
    # Read in the weapon skill information, including the updated player stats (such as Accuracy, Attack, and Crit Rate) from TP scaling.

    verbose_dps = player.abilities.get("Verbose DPS", False)
    very_verbose_dps = player.abilities.get("Very Verbose DPS", False)
    tp_bonus = player.stats.get("TP Bonus",0)
    base_tp = input_tp - tp_bonus

    input_tp = 3000 if input_tp > 3000 else 1000 if input_tp < 1000 else input_tp

    tp = input_tp # TP Bonus is added when calling this function in gui_wsdist.py
    tp = 1000 if tp < 1000 else 3000 if tp > 3000 else tp

    print(f"{ws_name} at {base_tp:.1f} TP (+{tp_bonus:.0f} TP Bonus; Effective TP: {input_tp:.1f} TP)") if (verbose_dps or very_verbose_dps) and simulation else None

    dual_wield = (player.gearset["sub"].get("Type",None) == "Weapon") or (player.gearset["main"]["Skill Type"] == "Hand-to-Hand")

    hover_shot = player.abilities.get("Hover Shot",False)*(ws_type=="ranged")

    ws_info = weaponskill_info(ws_name, tp, player, enemy, player.stats.get("WSC",[]), dual_wield,)

    nhits = ws_info["nhits"]
    wsc = ws_info["wsc"]
    ftp = ws_info["ftp"]
    ftp_rep = ws_info["ftp_rep"]
    ftp_hybrid = ws_info["ftp_hybrid"]
    element = ws_info["element"]
    hybrid = ws_info["hybrid"]
    magical = ws_info["magical"]
    ws_dSTAT = ws_info["dSTAT"]

    crit_rate = ws_info["crit_rate"] if ws_info["crit_rate"] < 1.0 else 1.0
    
    ftp += player.stats.get("ftp",0)
    if hybrid:
        ftp_hybrid += player.stats.get("ftp",0)

    ftp2 = ftp if ftp_rep else 1.0

    # Read in relevant player stat information
    qa = player.stats.get("QA",0)/100 if player.stats.get("QA",0)/100 < 1.0 else 1.0
    ta = player.stats.get("TA",0)/100 if player.stats.get("TA",0)/100 < 1.0 else 1.0
    da = player.stats.get("DA",0)/100 if player.stats.get("DA",0)/100 < 1.0 else 1.0
    oa8_main = player.stats.get("OA8 main",0)/100
    oa7_main = player.stats.get("OA7 main",0)/100
    oa6_main = player.stats.get("OA6 main",0)/100
    oa5_main = player.stats.get("OA5 main",0)/100
    oa4_main = player.stats.get("OA4 main",0)/100
    oa3_main = player.stats.get("OA3 main",0)/100
    oa2_main = player.stats.get("OA2 main",0)/100
    
    oa8_sub = player.stats.get("OA8 sub",0)/100
    oa7_sub = player.stats.get("OA7 sub",0)/100
    oa6_sub = player.stats.get("OA6 sub",0)/100
    oa5_sub = player.stats.get("OA5 sub",0)/100
    oa4_sub = player.stats.get("OA4 sub",0)/100
    oa3_sub = player.stats.get("OA3 sub",0)/100
    oa2_sub = player.stats.get("OA2 sub",0)/100

    oa_list = np.array([player.stats.get("OA3 main",0), # Notice that there is no support for main-hand Kclub. Only the off-hand values support OA4+
            player.stats.get("OA2 main",0),
            player.stats.get("OA8 sub",0),
            player.stats.get("OA7 sub",0),
            player.stats.get("OA6 sub",0),
            player.stats.get("OA5 sub",0),
            player.stats.get("OA4 sub",0),
            player.stats.get("OA3 sub",0),
            player.stats.get("OA2 sub",0),
            ])/100

    pdl_gear = player.stats.get("PDL",0)/100
    pdl_trait = player.stats.get("PDL Trait",0)/100

    wsd = player.stats.get("Weapon Skill Damage",0)/100 # Applies only to the first WS hit.
    ws_trait = player.stats.get("Weapon Skill Damage Trait",0)/100 # WS damage trait from DRG. Applies to all WS hits.
    ws_bonus = get_weapon_bonus(player.gearset["main"]["Name"], player.gearset["ranged"]["Name"], ws_name) # WS damage from Ambuscade weapons and augmented REMA. Applies to all WS hits.

    crit_dmg = player.stats.get("Crit Damage",0)/100 # Crit rate was read in earlier directly from the WS attributes.
    stp = player.stats.get("Store TP",0)/100
    enemy_defense = ws_info["enemy_def"] # I treat all "defense down" debuffs as multiplicative stacking. Otherwise we could end up with negative or zero defense with additive stacking. This results in slightly less damage than additive stacking would.
    enemy_evasion = enemy.stats["Evasion"]

    # Read in delay values now so we can use them in the magical WS section, which return TP for their one magic hit.
    base_delay = (player.stats["Delay1"] + player.stats["Delay2"])/2 
    mdelay = (base_delay - player.stats.get("Martial Arts",0)) * ((1 - player.stats.get("Dual Wield",0)/100))
    ranged_delay = player.stats.get('Ranged Delay',0)
    ammo_delay = player.stats.get("Ammo Delay",0)

    physical_damage = 0 # Calculate the physical damage first, so we can add magical damage to hybrids after.
    magical_damage = 0
    total_damage = 0
    tp_return = 0

    main_skill_type = player.gearset["main"]["Skill Type"]
    sub_skill_type = player.gearset["sub"].get("Skill Type",None) if not main_skill_type=="Hand-to-Hand" else "Hand-to-Hand"

    # We add dSTAT magic accuracy in the magical/hybrid section later.
    magic_accuracy = player.stats.get("Magic Accuracy",0) + player.stats.get("main Magic Accuracy Skill",0) + 100*player.abilities.get("Hover Shot",False)*(ws_type=="ranged")

    if ws_type == "melee" and not magical: # Melee WSs get multi-attacks, so we separate them from ranged weapon skills when calculating damage.


        main_dmg = player.stats["Kick DMG"] if (player.abilities.get("Footwork",False) and ws_name in ["Tornado Kick","Dragon Kick"]) else player.stats["DMG1"] # Footwork allows Kick WSs to use Kick DMG.
        sub_dmg = player.stats["Kick DMG"] if (player.abilities.get("Footwork",False) and ws_name in ["Tornado Kick","Dragon Kick"]) else player.stats["DMG2"]
        fstr_main = get_fstr(main_dmg, player.stats["STR"], enemy.stats["VIT"])
        fstr_sub = get_fstr(sub_dmg, player.stats["STR"], enemy.stats["VIT"])

        player_attack1 = ws_info["player_attack1"]
        player_attack2 = ws_info["player_attack2"]
        player_accuracy1 = ws_info["player_accuracy1"]
        player_accuracy2 = ws_info["player_accuracy2"]


        two_handed_skills = ["Great Sword", "Great Katana", "Great Axe", "Polearm", "Scythe", "Staff",] # I treat Hand-to-Hand separately where needed. Search for "Hand-to-Hand" to find these locations.
        one_handed_skills = ["Axe", "Club", "Dagger", "Sword", "Katana",]

        # Calculate hit rates.
        accuracy1 = player_accuracy1 + player.stats.get("Weapon Skill Accuracy",0)
        accuracy2 = player_accuracy2 + player.stats.get("Weapon Skill Accuracy",0)

        hit_rate_cap_main = 0.99 if main_skill_type in one_handed_skills or main_skill_type == "Hand-to-Hand" else 0.95
        hit_rate_cap_sub = 0.99 if sub_skill_type == "Hand-to-Hand" else 0.95

        hit_rate11 = get_hit_rate(accuracy1+100, enemy_evasion, hit_rate_cap_main) # hit_rate of the first main-hand hit, which gains +100 accuracy (https://www.bg-wiki.com/ffxi/Category:Weapon_Skills)
        hit_rate12 = get_hit_rate(accuracy1, enemy_evasion, hit_rate_cap_main) # hit_rate of all other main-hand hits.
        hit_rate21 = get_hit_rate(accuracy2+100, enemy_evasion, hit_rate_cap_sub)
        hit_rate22 = get_hit_rate(accuracy2, enemy_evasion, hit_rate_cap_sub)

        if not dual_wield:
            hit_rate21 = 0
            hit_rate22 = 0

        hit_rate_matrix = np.array([[hit_rate11, hit_rate21],[hit_rate12, hit_rate22]])

        if not simulation: # Check average damage if not running a simulation

            striking_flourish = player.abilities.get("Striking Flourish",False)
            ternary_flourish = player.abilities.get("Ternary Flourish",False)
            climactic_flourish = player.abilities.get("Climactic Flourish",False)
            sneak_attack = player.abilities.get("Sneak Attack",False)
            trick_attack = player.abilities.get("Trick Attack",False)

            if sneak_attack or trick_attack:
                hit_rate11 = 1.0
                hit_rate21 = 1.0

            sneak_attack_bonus = (player.stats["DEX"] * (1+player.stats.get("Sneak Attack Bonus",0)/100))*sneak_attack
            trick_attack_bonus = (player.stats["AGI"] * (1+player.stats.get("Trick Attack Bonus",0)/100))*trick_attack
            climactic_flourish_bonus = (0.5*player.stats["CHR"] * (1+player.stats.get("Flourish CHR%",0)/100))*climactic_flourish
            striking_flourish_bonus = (1.0*player.stats["CHR"] * (1+player.stats.get("Flourish CHR%",0)/100))*striking_flourish
            ternary_flourish_bonus = (1.0*player.stats["CHR"] * (1+player.stats.get("Flourish CHR%",0)/100))*ternary_flourish

            climactic_crit_dmg = player.stats.get("Climactic Crit Damage",0)/100*climactic_flourish # Crit damage +31% for the first hit when using the DNC Empy+3 head
            striking_crit_rate = player.stats.get("Striking Crit Rate",0)/100*striking_flourish # Crit rate +70% for the first hit when using the DNC Empy+3 body
            vajra_bonus_crit_dmg = 0.3*(player.gearset["main"]["Name"]=="Vajra" and (sneak_attack or trick_attack)) # Crit damage +30% for the first hit.

            first_main_hit_crit_rate = (1.0 if sneak_attack or trick_attack or climactic_flourish else (crit_rate+striking_crit_rate*(crit_rate>0))) # Special crit rate for SA/TA/Flourishes.
            first_main_hit_crit_rate = first_main_hit_crit_rate if first_main_hit_crit_rate < 1.0 else 1.0

            adjusted_crit_dmg = (crit_dmg + vajra_bonus_crit_dmg)*(1+climactic_crit_dmg) # Special crit damage that applies to first hit of SA/TA/ClimacticFlourish. Climactic with DNC Empy head provides a unique Crit Damage that applies separately.


            # Use multi-attack values to estimate the number of hits per weapon. This must include Flourishes, which can force multi-attacks.
            main_hits, sub_hits, _, _, _ = get_ma_rate3(player.main_job, nhits, qa, ta, da, oa_list, dual_wield, hit_rate_matrix, 0, 0, 0, 0, 0, 0, 0, striking_flourish, ternary_flourish, False) # Zero for ranged hit rate, daken, and kick attacks since this is the melee WS check

            # Now calculate damage dealt for these hits.
            # I calculate Hand-to-Hand off-hand attack using STR/2 instead of STR in the player class code, which lowers damage by a few % when compared to attack2 = attack1. I keep attack2 = attack1 in this main code for now.
            player_attack2 = player_attack1 if main_skill_type == "Hand-to-Hand" else player_attack2

            # Calculate how much damage the main hits would do if they were treated as sub-hits.
            main_hit_pdif = get_avg_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
            main_hit_damage = get_avg_phys_damage(main_dmg, fstr_main, wsc, main_hit_pdif, ftp2, crit_rate, crit_dmg, 0, ws_bonus, ws_trait) # Using FTP2, WSD=0, etc
            physical_damage += main_hits*main_hit_damage

            # Calculate the correction to the first hit based on the full set of buffs and bonuses.

            first_main_hit_pdif = get_avg_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, first_main_hit_crit_rate)
            first_main_hit_damage = get_avg_phys_damage(main_dmg, fstr_main, wsc, first_main_hit_pdif, ftp, first_main_hit_crit_rate, adjusted_crit_dmg, wsd, ws_bonus, ws_trait, sneak_attack_bonus, trick_attack_bonus, climactic_flourish_bonus, striking_flourish_bonus, ternary_flourish_bonus)

            # Adds the extra damage gained by those bonuses to the first hit's damage.
            physical_damage += (first_main_hit_damage*hit_rate11 - main_hit_damage*hit_rate11)

            # Striking Flourish also boosts the crit rate for its double attack hit, but doesn't provide the +100% CHR bonus (probably)
            if striking_flourish:
                # Define a new crit rate that adds 70% only if crit_rate>0 already (only for critical hit WSs)
                striking_flourish_crit_rate = crit_rate + striking_crit_rate*(crit_rate>0) # This crit_rate>0 ensures I am not letting non-crit WSs crit.
                striking_flourish_crit_rate = striking_flourish_crit_rate if striking_flourish_crit_rate < 1.0 else 1.0
                striking_flourish_pdif1 = get_avg_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, striking_flourish_crit_rate)
                striking_flourish_DA_damage = get_avg_phys_damage(main_dmg, fstr_main, wsc, striking_flourish_pdif1, ftp2, striking_flourish_crit_rate, crit_dmg, 0, ws_bonus, ws_trait)
                physical_damage += (striking_flourish_DA_damage - main_hit_damage)*hit_rate11 # Add on the difference in damage from a 2nd hit with higher crit.

            # Calculate the damage for off-hand hits, which receive no bonuses. No fancy correction terms are required here.
            offhand_pdif = get_avg_pdif_melee(player_attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
            offhand_damage = get_avg_phys_damage(sub_dmg, fstr_sub, wsc, offhand_pdif, ftp2, crit_rate, crit_dmg, 0, ws_bonus, ws_trait)
            physical_damage += offhand_damage*sub_hits

            # print("------------------------------------------------------")
            # print("first_main_hit: ",player_attack1, main_skill_type, first_main_hit_pdif, first_main_hit_damage,main_hits,hit_rate11,hit_rate12,accuracy1,ftp)
            # print("mainhand: ",player_attack1, main_skill_type, main_hit_pdif, main_hit_damage,main_hits,hit_rate11,hit_rate12,accuracy1,ftp2)
            # print("offhand: ",player_attack2, sub_skill_type, offhand_pdif, offhand_damage,sub_hits,hit_rate21,hit_rate22,accuracy2,ftp2)
            # print("stats: ",wsd,ws_trait,ws_bonus,crit_rate,crit_dmg,player.stats["DEX"],player.stats["STR"])
        
            # Calculate melee WS TP return.
            tp_return += get_tp(hit_rate11, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp) # Calculate TP return from the first main hit, which gains full TP. H2H hits each use half of the total mdelay for TP return, but time between attack rounds is still the same full mdelay.
            tp_return += get_tp(hit_rate21, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp) # Add TP return from the first off-hand hit, which also gains the full TP amount

            # Add TP return from the remaining main+off-hand hits together. All of these hits simply gain 10*(1+stp) TP
            tp_return += 10*(1+stp)*(main_hits+sub_hits - hit_rate11 - hit_rate21) # main_hits and sub_hits already account for hit rates, so we only subtract off the number of first main+sub hits.
            tp_return += (base_tp)*(0.01*(player.gearset["neck"]["Name"]=="Fotia Gorget"))*(0.01*(player.gearset["waist"]["Name"]=="Fotia Belt")) # Fotia gorget/belt each include +1% chance to retain TP on WS (before TP bonus)
            
            # Conserve TP procs return a random amount of TP between 10 and 200 (https://www.bg-wiki.com/ffxi/Conserve_TP). Here I assume the returned TP is uniformly distributed, which matches the testing linked on BG Wiki.
            tp_return += 95 * min(1,player.stats.get("Conserve TP",0)/100)


        else: # Run a proper damage simulation for the weapon skill

            # Do not apply 1-hit bonuses to DPS simulation WSs since the simulation would apply them to all WSs
            striking_flourish = False
            ternary_flourish = False
            climactic_flourish = False
            sneak_attack = False
            trick_attack = False

            sneak_attack_bonus = (player.stats["DEX"] * (1+player.stats.get("Sneak Attack Bonus",0)/100))*sneak_attack
            trick_attack_bonus = (player.stats["AGI"] * (1+player.stats.get("Trick Attack Bonus",0)/100))*trick_attack
            climactic_flourish_bonus = (0.5*player.stats["CHR"] * (1+player.stats.get("Flourish CHR%",0)/100))*climactic_flourish
            striking_flourish_bonus = (1.0*player.stats["CHR"] * (1+player.stats.get("Flourish CHR%",0)/100))*striking_flourish
            ternary_flourish_bonus = (1.0*player.stats["CHR"] * (1+player.stats.get("Flourish CHR%",0)/100))*ternary_flourish

            climactic_crit_dmg = player.stats.get("Climactic Crit Damage",0)/100*climactic_flourish # Crit damage +31% for the first hit when using the DNC Empy+3 head
            striking_crit_rate = player.stats.get("Striking Crit Rate",0)/100*striking_flourish # Crit rate +70% for the first hit when using the DNC Empy+3 body
            vajra_bonus_crit_dmg = 0.3*(player.gearset["main"]["Name"]=="Vajra" and (sneak_attack or trick_attack)) # Crit damage +30% for the first hit.

            first_main_hit_crit_rate = (1.0 if sneak_attack or trick_attack or climactic_flourish else (crit_rate+striking_crit_rate*(crit_rate>0))) # Special crit rate for SA/TA/Flourishes.
            first_main_hit_crit_rate = first_main_hit_crit_rate if first_main_hit_crit_rate < 1.0 else 1.0

            adjusted_crit_dmg = (crit_dmg + vajra_bonus_crit_dmg)*(1+climactic_crit_dmg) # Special crit damage that applies to first hit of SA/TA/ClimacticFlourish. Climactic with DNC Empy head provides a unique Crit Damage that applies separately.



            attempted_hits = 0 # Limited to 8 total attempted hits

            # First main-hand hit
            attempted_hits += 1
            if np.random.uniform() < hit_rate11:
                pdif, crit = get_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, first_main_hit_crit_rate) # Returns both the PDIF and whether or not the hit was a crit.
                phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, wsc, pdif, ftp, crit, adjusted_crit_dmg, wsd, ws_bonus, ws_trait, 0, sneak_attack_bonus, trick_attack_bonus, climactic_flourish_bonus, striking_flourish_bonus, ternary_flourish_bonus)
                physical_damage += phys_dmg_ph
                tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                tp_return += tp_ph
                verbose_output(phys_dmg_ph, 0, tp_ph, crit, "main") if very_verbose_dps else None
            else:
                print(f"    {'Main-hand':<10s}        "+color_text("red","Missed.")) if very_verbose_dps else None

            # First off-hand hit
            if dual_wield:
                attempted_hits += 1
                if np.random.uniform() < hit_rate21:
                    pdif, crit = get_pdif_melee(player_attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                    phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                    physical_damage += phys_dmg_ph
                    tp_ph = get_tp(1, mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay, stp)
                    tp_return += tp_ph
                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "sub") if very_verbose_dps else None
                else:
                    print(f"    {'Off-hand':<10s}        "+color_text("red","Missed.")) if very_verbose_dps else None

            # nhits-1 main-hand hits (Blade: Shun is 5 hits, so this is the 4 extra main-hand hits)
            for i in range(nhits-1):
                if attempted_hits < 8:
                    attempted_hits += 1
                    if np.random.uniform() < hit_rate12:
                        pdif, crit = get_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                        phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                        physical_damage += phys_dmg_ph
                        tp_ph = 10*(1+stp)
                        tp_return += tp_ph
                        verbose_output(phys_dmg_ph, 0, tp_ph, crit, "main") if very_verbose_dps else None
                    else:
                        print(f"    {'Main-hand':<10s}        "+color_text("red","Missed.")) if very_verbose_dps else None

            # Main hit MA check(s): QA > TA > DA > OA8 > OA7 > OA6 > OA5 > OA4 > OA3 > OA2
            # Main-hand gets two multi-attack checks if the WS has at least two native hits and the player is not dual wielding.
            main_hand_multi_attacks = 2 if (not dual_wield) and (nhits > 1) else 1
            for k in range(main_hand_multi_attacks):
                if attempted_hits < 8:
                    if np.random.uniform() < qa:
                        print(f"    Main-hand Quad. Attack:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(3): # 3 bonus hits on a Quad. Attack
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate12:
                                    pdif, crit = get_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < ta:
                        print(f"    Main-hand Triple Attack:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(2):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate12:
                                    pdif, crit = get_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < da:
                        print(f"    Main-hand Double Attack:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(1):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate12:
                                    pdif, crit = get_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa8_main:
                        print(f"    Main-hand OA8:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(7):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate12:
                                    pdif, crit = get_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa7_main:
                        print(f"    Main-hand OA7:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(6):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate12:
                                    pdif, crit = get_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa6_main:
                        print(f"    Main-hand OA6:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(5):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate12:
                                    pdif, crit = get_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa5_main:
                        print(f"    Main-hand OA5:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(4):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate12:
                                    pdif, crit = get_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa4_main:
                        print(f"    Main-hand OA4:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(3):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate12:
                                    pdif, crit = get_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa3_main:
                        print(f"    Main-hand OA3:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(2):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate12:
                                    pdif, crit = get_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa2_main:
                        print(f"    Main-hand OA2:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(1):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate12:
                                    pdif, crit = get_pdif_melee(player_attack1, main_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(main_dmg, fstr_main, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None

            # Off-hand hit MA check.
            if dual_wield:
                if attempted_hits < 8:
                    if np.random.uniform() < qa:
                        print(f"    Off-hand Quad. Attack:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(3):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate22:
                                    pdif, crit = get_pdif_melee(player_attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < ta:
                        print(f"    Off-hand Triple Attack:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(2):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate22:
                                    pdif, crit = get_pdif_melee(player_attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < da:
                        print(f"    Off-hand Double Attack:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(1):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate22:
                                    pdif, crit = get_pdif_melee(player_attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa8_sub:
                        print(f"    Off-hand OA8:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(7):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate22:
                                    pdif, crit = get_pdif_melee(player_attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa7_sub:
                        print(f"    Off-hand OA7:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(6):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate22:
                                    pdif, crit = get_pdif_melee(player_attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa6_sub:
                        print(f"    Off-hand OA6:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(5):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate22:
                                    pdif, crit = get_pdif_melee(player_attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa5_sub:
                        print(f"    Off-hand OA5:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(4):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate22:
                                    pdif, crit = get_pdif_melee(player_attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa4_sub:
                        print(f"    Off-hand OA4:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(3):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate22:
                                    pdif, crit = get_pdif_melee(player_attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa3_sub:
                        print(f"    Off-hand OA3:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(2):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate22:
                                    pdif, crit = get_pdif_melee(player_attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None
                    elif np.random.uniform() < oa2_sub:
                        print(f"    Off-hand OA2:") if (verbose_dps or very_verbose_dps) else None
                        for i in range(1):
                            if attempted_hits < 8:
                                attempted_hits += 1
                                if np.random.uniform() < hit_rate22:
                                    pdif, crit = get_pdif_melee(player_attack2, sub_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                                    phys_dmg_ph = get_phys_damage(sub_dmg, fstr_sub, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait, 0)
                                    physical_damage += phys_dmg_ph
                                    tp_ph = 10*(1+stp)
                                    tp_return += tp_ph
                                    verbose_output(phys_dmg_ph, 0, tp_ph, crit, "other") if very_verbose_dps else None
                                else:
                                    print("                      "+color_text("red","Missed.")) if very_verbose_dps else None

            fotia_chance =  (0.01*(player.gearset["neck"]["Name"]=="Fotia Gorget")) + (0.01*(player.gearset["waist"]["Name"]=="Fotia Belt"))
            if np.random.uniform() < fotia_chance:
                tp_return += (base_tp) # Fotia gorget/belt each include +1% chance to retain TP on WS (before TP bonus)
                fotia_tp = f"+{base_tp:.1f}"
                print(f"    " + color_text("cyan", "Fotia:") + f"                                  {fotia_tp:>7s} TP") if (verbose_dps or very_verbose_dps) else None

            conserve_tp_chance = player.stats.get("Conserve TP",0)/100
            if np.random.uniform() < conserve_tp_chance:
                conserve_tp_return = int(np.random.uniform(10,200))
                tp_return += conserve_tp_return
                conservetp_tp = f"+{conserve_tp_return:.1f}"
                print(f"    " + color_text("cyan", "Conserve TP:") + f"                            {conservetp_tp:>7s} TP") if (verbose_dps or very_verbose_dps) else None

    elif ws_type == "ranged" and not magical:

        ranged_dmg = player.stats.get("Ranged DMG",0)
        ammo_dmg = player.stats.get("Ammo DMG",0)
        fstr_rng = get_fstr2(ranged_dmg, player.stats["STR"], enemy.stats["VIT"])

        player_rangedaccuracy = ws_info["player_rangedaccuracy"]
        player_rangedattack = ws_info["player_rangedattack"]

        sharpshot = player.abilities.get("Sharpshot",False)
        true_shot = player.stats.get("True Shot",0)/100

        crit_rate += player.stats.get("Ranged Crit Rate", 0)/100
        crit_rate = 1 if crit_rate > 1 else crit_rate

        ranged_skills = ["Marksmanship","Archery"] # There are no Throwing weapon skills.
        ranged_skill_type = player.gearset["ranged"].get("Skill Type",None)

        # Calculate ranged hit rates.
        ranged_accuracy = player_rangedaccuracy + player.stats.get("Weapon Skill Accuracy",0) + 100*hover_shot
        hit_rate_cap_ranged = 0.99 if sharpshot else 0.95

        hit_rate_ranged1 = get_hit_rate(ranged_accuracy + 100*hover_shot +100, enemy_evasion, hit_rate_cap_ranged) # Assume first ranged hit gets +100 accuracy.
        hit_rate_ranged2 = get_hit_rate(ranged_accuracy + 100*hover_shot, enemy_evasion, hit_rate_cap_ranged) 

        if not simulation:

            # Calculate average ranged damage
            avg_pdif_rng = get_avg_pdif_ranged(player_rangedattack, ranged_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)

            ranged_hit_damage = get_avg_phys_damage(ranged_dmg+ammo_dmg, fstr_rng, wsc, avg_pdif_rng, ftp,  crit_rate, crit_dmg, wsd, ws_bonus, ws_trait) * (1 + hover_shot) # The amount of damage done by the first hit of the WS if it does not miss
            ranged_hit_damage2 = get_avg_phys_damage(ranged_dmg+ammo_dmg, fstr_rng, wsc, avg_pdif_rng, ftp2,  crit_rate, crit_dmg, 0, ws_bonus, ws_trait) * (1 + hover_shot) # Ranged hits after the first main hit (ie Jishnu's Radiance is a 3-hit Ranged WS.)

            physical_damage += ranged_hit_damage*hit_rate_ranged1 + ranged_hit_damage2*hit_rate_ranged2*(nhits-1)
            physical_damage *= (1 + true_shot)

            # Calculate Ranged WS TP return.
            tp_return = 0
            tp_return += get_tp(hit_rate_ranged1, ranged_delay+ammo_delay, stp) # First main shot TP
            tp_return += 10*(1+stp)*(nhits-1)*hit_rate_ranged2 # TP from other ranged WS hits get 10*(1+stp) TP

        else:

            attempted_hits = 0

            # First ranged hit
            attempted_hits += 1
            if np.random.uniform() < hit_rate_ranged1:
                pdif, crit = get_pdif_ranged(player_rangedattack, ranged_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                phys_dmg_ph = get_phys_damage(ranged_dmg+ammo_dmg, fstr_rng, wsc, pdif, ftp, crit, crit_dmg, wsd, ws_bonus, ws_trait,0) * (1 + hover_shot) * (1 + true_shot)
                physical_damage += phys_dmg_ph
                tp_ph = get_tp(1, ranged_delay+ammo_delay, stp)
                tp_return += tp_ph
                verbose_output(phys_dmg_ph, 0, tp_ph, crit, "ranged") if very_verbose_dps else None
            else:
                print("                      "+color_text("red","Missed.")) if very_verbose_dps else None

            # Additional nhits-1 ranged hits
            for i in range(nhits-1):
                if attempted_hits < 8:
                    if np.random.uniform() < hit_rate_ranged2:
                        pdif, crit = get_pdif_ranged(player_rangedattack, ranged_skill_type, pdl_trait, pdl_gear, enemy_defense, crit_rate)
                        phys_dmg_ph = get_phys_damage(ranged_dmg+ammo_dmg, fstr_rng, wsc, pdif, ftp2, crit, crit_dmg, 0, ws_bonus, ws_trait,1) * (1 + hover_shot) * (1 + true_shot)
                        physical_damage += phys_dmg_ph
                        tp_ph = 10*(1+stp)
                        tp_return += tp_ph
                        verbose_output(phys_dmg_ph, 0, tp_ph, crit, "ranged") if very_verbose_dps else None
                    else:
                        print("                      "+color_text("red","Missed.")) if very_verbose_dps else None


    total_damage += physical_damage

    # ===========================================================================
    # ===========================================================================
    # Treat the magical portion of WSs as an average
    if hybrid or magical:
        # Calculate magical WS damage and the magical portion for hybrid weapon skills now.
        # https://www.ffxiah.com/forum/topic/51313/tachi-jinpu-set/

        true_shot = player.stats.get("True Shot",0)/100
        
        # Read in the relevant magic stats
        magic_damage_stat = player.stats.get("Magic Damage",0) # Some jobs have special/specific magic damage, such as NIN, which has +40 Magic Damage from Job Points which only apply to Ninjutsu spells.
        magic_attack = player.stats.get("Magic Attack",0) # Some equipment has special magic attack, which applies in separate multiplicative terms on a per-element basis. Normally we see (1+matk)/(1+mdef), but Archon Ring uses something like (1+matk)/(1+mdef) * (1+dark_matk)/(1+dark_mdef)
        enemy_magic_defense = enemy.stats.get("Magic Defense",0)
        enemy_magic_evasion = enemy.stats.get("Magic Evasion",0)
        dstat_macc = get_dstat_macc(player.stats["INT"], enemy.stats["INT"]) # Calculate the magic accuracy bonus/penalty from dINT. TODO: This probably applies for dMND on MND-based weapon skills.
        magic_accuracy += dstat_macc 
        magic_hit_rate = get_magic_hit_rate(magic_accuracy, enemy_magic_evasion) if enemy_magic_evasion > 0 else 1.0
        
        magic_crit_rate2 = player.stats.get("Magic Crit Rate II",0)/100
        magic_crit2 = np.random.uniform() < magic_crit_rate2

        # Calculate base magical damage
        if hybrid: # Hybrid WSs use the previous Physical damage as their base damage.
            base_magical_damage = (physical_damage*ftp_hybrid + magic_damage_stat)
        elif magical: # Magical WSs use a purely magical approach to base damage.
            weapon_level = 119
            base_magical_damage = int(((152 + int((weapon_level-99)*2.45)+wsc)*ftp)*(1+player.stats.get("Elemental WS Damage%",0)/100) + ws_dSTAT + magic_damage_stat)


            # Calculate TP return for purely magical weapon skills. This is treated as a single hit (even for dual wielding) with normal TP gain from delay and Store TP.
            magic_delay = (mdelay/2 if (main_skill_type == "Hand-to-Hand") else mdelay) if ws_type=="melee" else ranged_delay+ammo_delay
            tp_return = get_tp(magic_hit_rate, mdelay, stp)
            magic_tp_return = tp_return

        # Calculate the magical damage multiplier.
        if not simulation:
            resist_state = get_resist_state_average(magic_hit_rate)
        else:
            resist_state = get_resist_state(magic_hit_rate)

        magic_attack_ratio = (100 + magic_attack) / (100 + enemy_magic_defense)

         # Archon Ring, Pixie Hairpin +1, Orpheus, and more get their own (1+matk)/(1+mdef) terms.
        element_magic_attack_bonus = 1 + (player.stats.get(f"{element.capitalize()} Elemental Bonus", 0)/100 + player.stats.get("Elemental Bonus",0)/100)

        dayweather = 1.0
        storm_elements = {"Sandstorm II":"earth","Rainstorm II":"water","Windstorm II":"wind","Firestorm II":"fire","Hailstorm II":"ice","Thunderstorm II":"thunder","Aurorastorm II":"light","Voidstorm II":"dark",
                          "Sandstorm":"earth","Rainstorm":"water","Windstorm":"wind","Firestorm":"fire","Hailstorm":"ice","Thunderstorm":"thunder","Aurorastorm":"light","Voidstorm":"dark"}
        active_storm =  player.abilities.get("Storm spell",False)
        if player.gearset["waist"]["Name"]=="Hachirin-no-Obi" and active_storm:
            if element.lower() == storm_elements.get(active_storm,False):
                dayweather = 1.25 if "II" in active_storm else 1.1

        klimaform_bonus = 1.0 + player.abilities.get("Klimaform",False)*player.stats.get("Klimaform Damage%",0)/100 # Klimaform with Empy+3 feet boosts magical WS damage by 25%

        enemy_mdt = 1.0 # Enemy MDT is usually 1.0 (-0%) unless the enemy casts shell or a similar spell/ability.

        affinity = 1 + 0.05*player.stats.get(f"{element} Affinity",0) + 0.05*(player.stats.get(f"{element} Affinity",0)>0) # Elemental Affinity Bonus. Only really applies to Magian Trial staves. Archon Ring is different.

        # Now multiply the magical portion by weapon skill damage as well.
        magic_multiplier = resist_state*magic_attack_ratio*element_magic_attack_bonus*dayweather*klimaform_bonus*enemy_mdt*affinity*(1 + 0.25*magic_crit2) 

        # Multiply base damage by the multiplier
        magical_damage = base_magical_damage * magic_multiplier

        # Magical WS damage still benefits from WSD. Even though hybrid WS physical damage already applied this bonus, it gets applied again on the magical portion.
        magical_damage *= (1+wsd)*(1+ws_bonus)*(1+ws_trait) * (1 + hover_shot) * (1 + true_shot*hybrid*(ws_type == "ranged"))

        verbose_output(0, magical_damage, magic_tp_return if magical else 0, magic_crit2, "hybrid" if hybrid else "magic") if very_verbose_dps and simulation else None

        # Add magical damage to total damage.
        total_damage += magical_damage

    if input_metric=="TP return":
        metric=tp_return
        invert=1
    elif input_metric=="Damage dealt":
        metric=total_damage
        invert=1
    elif input_metric=="Magic accuracy":
        if magical:
            metric_hitrate = magic_hit_rate
        elif ws_type=="melee":
            metric_hitrate = hit_rate11
        elif ws_type=="ranged":
            metric_hitrate = hit_rate_ranged1
        else:
            metric_hitrate = 1 # Ignore accuracy if the ws_type is not known
        metric = metric_hitrate * magic_accuracy
        invert=1
    else:
        metric=total_damage
        invert=1

    if simulation:
        # Cap damage at 99999 for simulations if enabled
        if player.abilities.get("99999", False):
            total_damage = 99999 if total_damage > 99999 else total_damage

        if verbose_dps or very_verbose_dps:
            print(f"    =       Phys. Damage: {physical_damage:>6.0f}")
            print(f"    =       Magic Damage: {magical_damage:>6.0f}")
            print(f"    =       TP Returned:  {tp_return:>6.1f}")
            
        return(total_damage, tp_return)
    else:
        return(metric, [total_damage, tp_return, invert])




if __name__ == "__main__":
    #
    #
    #
    from create_player import *
    import sys
    from gear import *

    main_job = sys.argv[1]
    sub_job = sys.argv[2]
    master_level = int(sys.argv[3])
    gearset = { "main" : Heishi,
                'sub' : Hitaki2,
                'ranged' : Empty,
                'ammo' : Seething_Bomblet,
                'head' : Mochizuki_Hatsuburi,
                'body' : Nyame_Mail30B,
                'hands' : Nyame_Gauntlets30B,
                'legs' : Nyame_Flanchard30B,
                'feet' : Nyame_Sollerets30B,
                'neck' : Fotia_Gorget,
                'waist' : Orpheus_Sash,
                'ear1' : Moonshade_Earring,
                'ear2' : Lugra_Earring_Aug,
                'ring1' : Gere_Ring,
                'ring2' : Cornelia_ring,
                'back' : np.random.choice([k for k in capes if "nin" in k["Jobs"] and "STR Weapon" in k["Name2"] and "(" not in k["Name2"]])}

    Grape_Daifuku2 = {"Name": "Grape Daifuku +1", "Type":"Food","STR":3, "VIT":4, "Food Attack":55, "Food Ranged Attack":55, "Accuracy":85, "Ranged Accuracy":85, "Magic Attack":4}
    buffs = {"food": {},
             "brd": {"Attack": 0, "Ranged Accuracy":0, "Accuracy": 0, "Ranged Accuracy": 0,"STR":0,"DEX":0, "VIT":0, "AGI":0, "INT":0, "MND":0, "CHR":0,},
             "cor": {"Attack%": 0., "Ranged Attack%":0., "Store TP": 0, "Accuracy": 0, "Magic Attack": 0, "DA":0, "Crit Rate": 0},
             "geo": {"Attack%": 0, "Ranged Attack%": 0, "Accuracy": 0, "Ranged Accuracy":0, "STR":0,"DEX":0, "VIT":0, "AGI":0, "INT":0, "MND":0, "CHR":0,},
             "whm": {"MDT":0,"Magic Haste": 0, "STR":0,"DEX":0, "VIT":0, "AGI":0, "INT":0, "MND":0, "CHR":0}, # WHM buffs like boost-STR.
             }
    abilities = {"Ebullience":False,
                        "Aftermath":0,
                        "Sneak Attack":False,
                        "Trick Attack":False,
                        "Footwork":False,
                        "Impetus":False,
                        "Building Flourish":False,
                        "Blood Rage":False,
                        "Mighty Strikes":False,
                        "Double Shot":False,
                        "Velocity Shot":False,
                        "True Shot":False,
                        "Hover Shot":False}


    enemy = create_enemy(apex_toad)
    tp1 = 1000
    tp2 = 1500
    tp0 = 0

    ws_name = "Blade: Chi"
    player = create_player(main_job, sub_job, master_level, gearset, buffs, abilities)

    tp1 += player.stats.get("TP Bonus",0)
    tp2 += player.stats.get("TP Bonus",0)

    tp = np.average([tp1,tp2])
    tp = 1000 if tp < 1000 else 3000 if tp > 3000 else tp

    spell_name = "Ranged Attack"

    x = average_ws(player, enemy, ws_name, tp, "melee", "Damage dealt")
    # x = cast_spell(player, enemy, spell_name, "Ranged Attack")
    # x = average_attack_round(player, enemy)
    print()
    print('----------------')
    print(player.stats)
    for k in player.gearset:
        print(k,player.gearset[k]["Name2"])
    print(x)

    if False:
        import cProfile
        cProfile.run("average_ws(player, enemy, ws_name, tp, \"melee\", \"Damage dealt\")",sort="cumtime")

