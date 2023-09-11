#
# Created by Kastra on Asura.
# Feel free to /tell in game or send a PM on FFXIAH you have questions, comments, or suggestions.
#
# Version date: 2023 May 12
#
# This file contains a list of buffs that may be provided to a gear set when simulating damage.
#
import numpy as np

# Simple list of buffs and their potencies.
# Currently incomplete and not necessarily in final form.

# Format is [Base, Bonus].
# For Example: GEO Acumen uses [15,3]. So with +6 geomancy, it would be Base+Bonus*6 = 15+3*6 Magic Attack with Acumen

cor = {"Chaos": {"Attack%":[{"1":0.0625,"2":0.0781,"3":0.0937,"4":0.25,"5":0.1093,"6":0.1250,"7":0.1562,"8":0.0312,"9":0.1718,"10":0.1875,"11":0.3125}, 32./1024, 100./1024],},
       "Samurai": {"Store TP":[{"1":8,"2":32,"3":10,"4":12,"5":14,"6":4,"7":16,"8":20,"9":22,"10":24,"11":40},4,10]},
       "Rogue": {"Crit Rate":[{"1":1,"2":2,"3":3,"4":4,"5":10,"6":5,"7":6,"8":7,"9":1,"10":8,"11":14},1,5]},
       "Monk": {"Subtle Blow":[{"1":8,"2":10,"3":32,"4":12,"5":14,"6":16,"7":4,"8":20,"9":22,"10":24,"11":40},4,10]},
       "Fighter": {"DA":[{"1":1,"2":2,"3":3,"4":4,"5":10,"6":5,"7":6,"8":6,"9":1,"10":7,"11":15},1,5]},
       "Hunter": {"Accuracy":[{"1":10,"2":13,"3":15,"4":40,"5":18,"6":20,"7":25,"8":5,"9":28,"10":30,"11":50},5,15]},
       "Wizard": {"Magic Attack":[{"1":4,"2":6,"3":8,"4":10,"5":25,"6":12,"7":14,"8":17,"9":2,"10":20,"11":30},2,10]},
       "Warlock": {"Magic Accuracy":[{"1":10,"2":13,"3":15,"4":40,"5":18,"6":20,"7":25,"8":5,"9":28,"10":30,"11":50},5,15]},
       "Tactician": {"Regain":[{"1":10,"2":10,"3":10,"4":10,"5":30,"6":10,"7":10,"8":0,"9":20,"10":20,"11":40},2,10]}}

brd = {"Minuet": {"Attack": [32+25, 3.2], "Ranged Attack": [32+25, 3.2]},
        "Minuet II": {"Attack": [64+25, 6.2], "Ranged Attack": [64+25, 6.2]},
        "Minuet III": {"Attack": [96+25, 9.5], "Ranged Attack": [96+25, 9.5]},
        "Minuet IV": {"Attack": [112+25, 11.2], "Ranged Attack": [112+25, 11.2]},
        "Minuet V": {"Attack": [124+25, 12.375], "Ranged Attack": [124+25, 12.375]},
        "Sword Madrigal": {"Accuracy": [45, 4.5]},
        "Blade Madrigal": {"Accuracy": [60, 6]},
        "Advancing March": {"Magic Haste": [108./1024, 11.8/1024]},
        "Victory March": {"Magic Haste": [163./1024, 16.25/1024]},
        "Honor March": {"Magic Haste": [126./1024, 12./1024], "Attack": [168, 16], "Ranged Attack": [168, 16], "Accuracy": [42, 4], "Ranged Accuracy": [42, 4]},
        "Sinewy Etude":{"STR":[9,1]},
        "Herculean Etude":{"STR":[15,1]},
        "Dextrous Etude":{"DEX":[9,1]},
        "Uncanny Etude":{"DEX":[15,1]},
        "Vivacious Etude":{"VIT":[9,1]},
        "Vital Etude":{"VIT":[15,1]},
        "Quick Etude":{"AGI":[9,1]},
        "Swift Etude":{"AGI":[15,1]},
        "Learned Etude":{"INT":[9,1]},
        "Sage Etude":{"INT":[15,1]},
        "Spirited Etude":{"MND":[9,1]},
        "Logical Etude":{"MND":[15,1]},
        "Enchanting Etude":{"CHR":[9,1]},
        "Bewitching Etude":{"CHR":[15,1]},
        "Hunter's Prelude":{"Ranged Accuracy":[45,4.5]},
        "Archer's Prelude":{"Ranged Accuracy":[60,6]},
        }

geo = {"Fury": {"Attack%": [0.347,0.027], "Ranged Attack%": [0.347,0.027]},
       "Acumen": {"Magic Attack": [15,3]},
       "Focus": {"Magic Accuracy":[50,5]},
       "Haste": {"Magic Haste": [29.9/100, 1.1/100]},
       "Precision": {"Accuracy": [50,5], "Ranged Accuracy": [50,5]},
       "Frailty": {"Defense":[0.148,0.027]},
       "Torpor": {"Evasion":[50,5]},
       "Malaise": {"Magic Defense":[15,3]},
       "Languor":{"Magic Evasion":[50,5]},
       "STR":{"STR":[25,2]},
       "DEX":{"DEX":[25,2]},
       "VIT":{"VIT":[25,2]},
       "AGI":{"AGI":[25,2]},
       "INT":{"INT":[25,2]},
       "MND":{"MND":[25,2]},
       "CHR":{"CHR":[25,2]}}

whm = {"Haste":{"Magic Haste":150/1024},
       "Haste II":{"Magic Haste":307/1024},
       "Boost-STR":{"STR":25},
       "Boost-DEX":{"DEX":25},
       "Boost-VIT":{"VIT":25},
       "Boost-AGI":{"AGI":25},
       "Boost-INT":{"INT":25},
       "Boost-MND":{"MND":25},
       "Boost-CHR":{"CHR":25},
       "Gain-STR":{"STR":65},
       "Gain-DEX":{"DEX":65},
       "Gain-VIT":{"VIT":65},
       "Gain-AGI":{"AGI":65},
       "Gain-INT":{"INT":65},
       "Gain-MND":{"MND":65},
       "Gain-CHR":{"CHR":65}}
