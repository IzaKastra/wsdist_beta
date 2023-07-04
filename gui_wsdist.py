# Add tabs to a "notebook" of ctk
# https://github.com/TomSchimansky/ctk/issues/1104#issuecomment-1402174614
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image
import numpy as np

# Use an external gear.py file
# https://stackoverflow.com/questions/47350078/importing-external-module-in-single-file-exe-created-with-pyinstaller
import sys
import os
sys.path.append(os.path.dirname(sys.executable))
from gear import *

from enemies import *

from idlelib.tooltip import Hovertip # https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter

def load_defaults(app,defaults):
    #
    # Read the input file for default values to use when opening a fresh GUI.
    # This function just places the strings in the input file into the inputs in the GUI.
    # This means if you give Rolls +1200 in the input file, then you will see roll potency for "Rolls +1200".
    # This also means that if you have a typo in your inputs, then the code break. The code is case-sensitive
    #
    app.masterlevel.set(int(defaults.get("ml",20))) ; app.update_special_checkboxes("select job")
    app.mainjob.set(defaults.get("mainjob","NIN").upper()) ; app.select_job(app.mainjob.get(),"main")
    app.subjob.set(defaults.get("subjob","WAR").upper()) ; app.select_job(app.subjob.get(),"sub")

    app.spell_name.set(defaults.get("spell","None"))
    app.ws_name.set(defaults.get("ws","None"))
    app.am_level.set(int(defaults.get("aftermath",0)))
    app.tp1.set(int(defaults.get("mintp",1000)))
    app.tp2.set(int(defaults.get("maxtp",1000)))
    app.tp0.set(int(defaults.get("initialtp",0)))

    app.pdt_req.set(int(defaults.get("pdtreq",100)))
    app.mdt_req.set(int(defaults.get("mdtreq",100)))

    app.whm_on.set(True if defaults.get("whm","False")=="True" else True); app.update_buff_cboxes("whm")
    app.brd_on.set(True if defaults.get("brd","False")=="True" else False); app.update_buff_cboxes("brd")
    app.cor_on.set(True if defaults.get("cor","False")=="True" else False); app.update_buff_cboxes("cor")
    app.geo_on.set(True if defaults.get("geo","False")=="True" else False); app.update_buff_cboxes("geo")

    app.shell5_on.set(True if defaults.get("shell5","True")=="True" else False)
    app.whm_spell1.set(defaults.get("dia","Dia III"))
    app.whm_spell2.set(defaults.get("haste","Haste II"))
    app.whm_spell3.set(defaults.get("boost","None"))
    app.whm_spell4.set(defaults.get("storm","None"))
    app.active_food.set(defaults.get("food","Grape Daifuku"))

    app.brd_potency.set(defaults.get("nsongs","Songs +7"))
    app.song1.set(defaults.get("song1","Honor March"))
    app.song2.set(defaults.get("song2","Victory March"))
    app.song3.set(defaults.get("song3","Minuet V"))
    app.song4.set(defaults.get("song4","Minuet IV"))
    app.song5.set(defaults.get("song5","None"))
    app.marcato_on.set(True if defaults.get("marcato","False")=="True" else False)
    app.soulvoice_on.set(True if defaults.get("soulvoice","False")=="True" else False)

    app.cor_potency.set(defaults.get("nrolls","Rolls +7"))
    app.roll1.set(defaults.get("roll1","Chaos"))
    app.roll2.set(defaults.get("roll2","Samurai"))
    app.job_bonus.set(True if defaults.get("jobbonus","False")=="True" else False)
    app.crooked_on.set(True if defaults.get("crookedcards","False")=="True" else False)
    app.lightshot_on.set(True if defaults.get("lightshot","False")=="True" else False)
    app.roll1_value.set(defaults.get("roll1value","IX"))
    app.roll2_value.set(defaults.get("roll2value","IX"))

    app.geomancy_potency.set(defaults.get("geopotency","100"))
    app.geo_potency.set(defaults.get("nbubble","Geomancy +6"))
    app.indispell.set(defaults.get("indi","Indi-Fury"))
    app.geospell.set(defaults.get("geo","Geo-Frailty"))
    app.entrustspell.set(defaults.get("entrust","None"))
    app.bog_on.set(True if defaults.get("bog","False")=="True" else False)
    app.bolster_on.set(True if defaults.get("bolster","False")=="True" else False)

    # Equip selected default gear.
    app.selected_main.set(value=name2dictionary(defaults.get("main","Heishi Shorinken R15")))
    app.selected_sub.set(value=name2dictionary(defaults.get("sub","Crepuscular Knife")))
    app.selected_ranged.set(value=name2dictionary(defaults.get("ranged","Empty")))
    app.selected_ammo.set(value=name2dictionary(defaults.get("ammo","Seki Shuriken")))
    app.selected_head.set(value=name2dictionary(defaults.get("head","Malignance Chapeau")))
    app.selected_neck.set(value=name2dictionary(defaults.get("neck","Ninja Nodowa +2 R25")))
    app.selected_ear1.set(value=name2dictionary(defaults.get("ear1","Dedition Earring")))
    app.selected_ear2.set(value=name2dictionary(defaults.get("ear2","Telos Earring")))
    app.selected_body.set(value=name2dictionary(defaults.get("body","Tatenashi Haramaki +1 R15")))
    app.selected_hands.set(value=name2dictionary(defaults.get("hands","Malignance Gloves")))
    app.selected_ring1.set(value=name2dictionary(defaults.get("ring1","Gere Ring")))
    app.selected_ring2.set(value=name2dictionary(defaults.get("ring2","Epona's Ring")))
    app.selected_back.set(value=name2dictionary(defaults.get("back","Andartia's Mantle DEX Store TP")))
    app.selected_waist.set(value=name2dictionary(defaults.get("waist","Sailfi Belt +1 R15")))
    app.selected_legs.set(value=name2dictionary(defaults.get("legs","Samnuha Tights")))
    app.selected_feet.set(value=name2dictionary(defaults.get("feet","Malignance Boots")))

    # Update gear icons and tooltips
    for slot in ["main","sub","ranged","ammo","head","neck","ear1","ear2","body","hands","ring1","ring2","back","waist","legs","feet"]:
        app.update_buttons(slot)
            
    # Update enemy input defaults
    app.enemy_magic_defense.set(defaults.get("emagicdefense","0"))
    app.enemy_magic_evasion.set(defaults.get("emagicevasion","0"))
    app.enemy_defense.set(defaults.get("edefense","1338"))
    app.enemy_evasion.set(defaults.get("eevasion","1225"))
    app.enemy_level.set(defaults.get("elevel","135"))
    app.selected_enemy.set(defaults.get("ename","Apex Bat"))
    app.enemy_agi.set(defaults.get("eagi","356"))
    app.enemy_vit.set(defaults.get("evit","289"))
    app.enemy_int.set(defaults.get("eint","267"))
    app.enemy_mnd.set(defaults.get("emnd","267"))

    # Load odyssey rank and TVR ring choices
    app.odyrank.set(defaults.get("odyrank","30"))
    app.tvr_ring.set(defaults.get("tvrring","Cornelia's"))

    # Load damage metrics
    app.tpmetric.set(defaults.get("tpmetric","Time to WS"))
    app.spellmetric.set(defaults.get("spellmetric","Damage dealt"))
    app.wsmetric.set(defaults.get("wsmetric","Damage dealt"))

    # Finally, update the window size based on the input file.
    app.geometry(defaults.get("dimensions","700x885"))

def save_defaults():
    #
    # Write the state of input widgets to an output file.
    #
    with open("defaults.txt","w") as ofile:
        ofile.write("# Basic inputs\n")
        ofile.write(f"ml={app.masterlevel.get()}\n")
        ofile.write(f"mainjob={app.mainjob.get()}\n")
        ofile.write(f"subjob={app.subjob.get()}\n")
        ofile.write(f"aftermath={app.am_level.get()}\n")
        ofile.write(f"mintp={app.tp1.get()}\n")
        ofile.write(f"maxtp={app.tp2.get()}\n")
        ofile.write(f"spell={app.spell_name.get()}\n")
        ofile.write(f"ws={app.ws_name.get()}\n")
        ofile.write(f"initialtp={app.tp0.get()}\n")
        ofile.write(f"odyrank={app.odyrank.get()}\n")
        ofile.write(f"tvrring={app.tvr_ring.get()}\n")

        ofile.write(f"tpmetric={app.tpmetric.get()}\n")
        ofile.write(f"spellmetric={app.spellmetric.get()}\n")
        ofile.write(f"wsmetric={app.wsmetric.get()}\n")

        ofile.write(f"pdtreq={app.pdt_req.get()}\n")
        ofile.write(f"mdtreq={app.mdt_req.get()}\n")

        ofile.write("\n# WHM inputs\n")
        ofile.write(f"whm={app.whm_on.get()}\n")
        ofile.write(f"shell5={app.shell5_on.get()}\n")
        ofile.write(f"dia={app.whm_spell1.get()}\n")
        ofile.write(f"haste={app.whm_spell2.get()}\n")
        ofile.write(f"boost={app.whm_spell3.get()}\n")
        ofile.write(f"storm={app.whm_spell4.get()}\n")

        ofile.write("\n# BRD inputs\n")
        ofile.write(f"brd={app.brd_on.get()}\n")
        ofile.write(f"nsongs={app.brd_potency.get()}\n")
        ofile.write(f"song1={app.song1.get()}\n")
        ofile.write(f"song2={app.song2.get()}\n")
        ofile.write(f"song3={app.song3.get()}\n")
        ofile.write(f"song4={app.song4.get()}\n")
        ofile.write(f"song5={app.song5.get()}\n")
        ofile.write(f"marcato={app.marcato_on.get()}\n")
        ofile.write(f"soulvoice={app.soulvoice_on.get()}\n")

        ofile.write("\n# COR inputs\n")
        ofile.write(f"cor={app.cor_on.get()}\n")
        ofile.write(f"nrolls={app.cor_potency.get()}\n")
        ofile.write(f"roll1value={app.roll1_value.get()}\n")
        ofile.write(f"roll1={app.roll1.get()}\n")
        ofile.write(f"roll2v={app.roll2_value.get()}\n")
        ofile.write(f"roll2={app.roll2.get()}\n")
        ofile.write(f"crookedcards={app.crooked_on.get()}\n")
        ofile.write(f"jobbonus={app.job_bonus.get()}\n")
        ofile.write(f"lightshot={app.lightshot_on.get()}\n")


        ofile.write("\n# GEO inputs\n")
        ofile.write(f"geo={app.geo_on.get()}\n")
        ofile.write(f"nbubble={app.geo_potency.get()}\n")
        ofile.write(f"geopotency={app.geomancy_potency.get()}\n")
        ofile.write(f"indi={app.indispell.get()}\n")
        ofile.write(f"geo={app.geospell.get()}\n")
        ofile.write(f"entrust={app.entrustspell.get()}\n")
        ofile.write(f"blaze={app.bog_on.get()}\n")
        ofile.write(f"bolster={app.bolster_on.get()}\n")

        ofile.write("\n# Enemy inputs\n")
        ofile.write(f"ename={app.selected_enemy.get()}\n")
        ofile.write(f"elevel={app.enemy_level.get()}\n")
        ofile.write(f"eevasion={app.enemy_evasion.get()}\n")
        ofile.write(f"edevense={app.enemy_defense.get()}\n")
        ofile.write(f"emagicevasion={app.enemy_magic_evasion.get()}\n")
        ofile.write(f"emagicdefense={app.enemy_magic_defense.get()}\n")
        ofile.write(f"eagi={app.enemy_agi.get()}\n")
        ofile.write(f"evit={app.enemy_vit.get()}\n")
        ofile.write(f"eint={app.enemy_int.get()}\n")
        ofile.write(f"emnd={app.enemy_mnd.get()}\n")

        ofile.write("\n# Equipment and food inputs\n")
        ofile.write(f"food={app.active_food.get()}\n")
        ofile.write(f"main={eval(app.selected_main.get())['Name2']}\n")
        ofile.write(f"sub={eval(app.selected_sub.get())['Name2']}\n")
        ofile.write(f"ranged={eval(app.selected_ranged.get())['Name2']}\n")
        ofile.write(f"ammo={eval(app.selected_ammo.get())['Name2']}\n")
        ofile.write(f"head={eval(app.selected_head.get())['Name2']}\n")
        ofile.write(f"neck={eval(app.selected_neck.get())['Name2']}\n")
        ofile.write(f"ear1={eval(app.selected_ear1.get())['Name2']}\n")
        ofile.write(f"ear2={eval(app.selected_ear2.get())['Name2']}\n")
        ofile.write(f"body={eval(app.selected_body.get())['Name2']}\n")
        ofile.write(f"hands={eval(app.selected_hands.get())['Name2']}\n")
        ofile.write(f"ring1={eval(app.selected_ring1.get())['Name2']}\n")
        ofile.write(f"ring2={eval(app.selected_ring2.get())['Name2']}\n")
        ofile.write(f"back={eval(app.selected_back.get())['Name2']}\n")
        ofile.write(f"waist={eval(app.selected_waist.get())['Name2']}\n")
        ofile.write(f"legs={eval(app.selected_legs.get())['Name2']}\n")
        ofile.write(f"feet={eval(app.selected_feet.get())['Name2']}\n")

        # Save the current window size. Most/all of the widgets use a specific size anyway, so resizing the window is mostly pointless for now.
        ofile.write("\n# Window size:  widthxheight\n")
        ofile.write(f"dimensions={app.winfo_width()}x{app.winfo_height()}")

def name2dictionary(name):
    #
    # Given an item name ("Adhemar Bonnet +1A"), find the dictionary (adhemar_bonnet_A) which contains that item's stats.
    # First check Name2, then check Name. This is so you don't mix up different augment paths.
    # Name is mostly for finding the icon anyway.
    #
    for i,k in enumerate(all_gear):
        gear_name = k["Name2"] if "Name2" in k else k["Name"]
        if name == gear_name:
            return(all_gear[i])
    return(Empty)



class App(tk.Tk):



    def __init__(self): # Run on creation of a new "App" instance to define the defaults of the "App"
        super().__init__() # What does this do exactly? Inherits all attributes from the parent, which is the thing in parenthesis (tk.Tk). super is useless on the parent class itself, (called call App:    -without parenthesis)

        mystyle = ttk.Style()
        mystyle.theme_use('vista')   # choose other theme
        mystyle.configure('MyStyle.TLabelframe', borderwidth=3, relief='solid', labelmargins=5)
        mystyle.configure('MyStyle.TLabelframe.Label', font=('courier', 35, 'bold'))

        # Adjust the hover color of ALL ttk.Buttons
        # https://tkdocs.com/shipman/ttk-map.html
        # https://stackoverflow.com/questions/63953288/how-to-stop-changing-of-color-when-hovering-over-button-in-tkinter
        # mystyle.map('TButton',background=[('active','!pressed', 'black')])  # Button background color when active (mouseover) but not pressed
        # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')

        # Build the basic app.
        self.title("Kastra FFXI Damage Simulator (Beta: 2023 July 4)")
        self.horizontal = False
        if not self.horizontal:
            self.geometry("700x885")
            # self.minsize(width=700,height=950)
            self.resizable(True,True)
        else:
            self.resizable(True, True)

        self.notebook = ttk.Notebook(self, )
        self.notebook.pack(fill="both",expand=1)
        self.inputs_tab = ttk.Frame(self.notebook)
        self.select_gear_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.inputs_tab, text="Inputs")
        self.notebook.add(self.select_gear_tab, text="Optimize")
        self.notebook.add(self.stats_tab, text="Player Stats")

        # tkinter Menu  https://blog.teclado.com/how-to-add-menu-to-tkinter-app/
        self.menu_bar = tk.Menu(self)
        self.file_menu = tk.Menu(self.menu_bar,tearoff=False)
        self.file_menu.add_command(label="Save Defaults", command=save_defaults)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Close GUI", command=self.destroy)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.config(menu=self.menu_bar)


# =============================================================================================================================
# =============================================================================================================================
#  Frame 1: Contains player and enemy inputs
# =============================================================================================================================
# =============================================================================================================================


        # self.inputs_frame = ttk.LabelFrame(self,borderwidth=3,width=676,height=250,text="Main Frame1")
        self.inputs_frame = ttk.Frame(self.inputs_tab,borderwidth=3,width=676,height=250)
        self.inputs_frame.grid(row=0, column=0, padx=2, pady=0, sticky="nw")
        # self.frame1.grid_columnconfigure((0,1),weight=1)
        # self.frame1.grid_propagate(0)

        self.player_inputs_frame = ttk.LabelFrame(self.inputs_frame,borderwidth=3,width=250,height=250,text="  Basic Inputs  ")
        self.player_inputs_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nw")
        self.player_inputs_frame.grid_propagate(0)
        if True:
            self.masterlevel_label = ttk.Label(self.player_inputs_frame,text="Master Lv.")
            self.masterlevel_label.grid(row=0, column=0, sticky="w", padx=0, pady=1)
            self.masterlevel = tk.IntVar(value=20)
            self.masterlevel_box = ttk.Combobox(self.player_inputs_frame, textvariable=self.masterlevel, values=tuple(np.arange(50,-1,-1)),state="readonly",)
            # self.masterlevel_box = ttk.Entry(self.player_inputs_frame,textvariable=self.masterlevel,justify="right")
            self.masterlevel_box.configure(width=6)
            self.masterlevel_box.grid(row=0,column=1,padx=0,pady=1,sticky='w')
            self.masterlevel_box.bind('<<ComboboxSelected>>', lambda event, trigger="select_job": self.update_special_checkboxes(trigger))

            self.mainjob_label = ttk.Label(self.player_inputs_frame,text="Main Job:",width=15)
            self.mainjob_label.grid(row=1, column=0, padx=0, pady=1, sticky="w")
            self.subjob_label = ttk.Label(self.player_inputs_frame,text="Sub Job:",width=15)
            self.subjob_label.grid(row=2, column=0, padx=0, pady=1, sticky="w")

            self.main_jobs = sorted(["NIN", "DRK", "SCH", "RDM", "BLM", "SAM", "DRG", "WHM", "WAR", "COR","BRD", "THF", "MNK", "DNC", "BST", "RUN", "RNG", "PUP", "BLU", "GEO", "PLD"])
            self.mainjob = tk.StringVar(value="NIN")
            self.mainjob_box = ttk.Combobox(self.player_inputs_frame, textvariable=self.mainjob, values=self.main_jobs,state="readonly",)
            self.mainjob_box.config(width=11,)
            self.mainjob_box.grid(row=1, column=1, padx=0, pady=1, sticky='e')
            self.mainjob_box.bind('<<ComboboxSelected>>', lambda event, entry=self.mainjob_box: self.select_job(entry.get(),"main"))
            # self.mainjob_box.bind('<<ComboboxSelected>>', lambda event, entry=combobox, text=text:update(entry.get(), entry=text))

            self.sub_jobs = sorted(["NIN", "DRK", "SCH", "RDM", "BLM", "SAM", "DRG", "WHM", "WAR", "COR","BRD", "THF", "MNK", "DNC", "BST", "RUN", "RNG", "PUP", "BLU", "GEO", "PLD"]) + ["None"]
            self.subjob = tk.StringVar(value="WAR")
            self.subjob_box = ttk.Combobox(self.player_inputs_frame, textvariable=self.subjob, values=self.sub_jobs,state="readonly")
            self.subjob_box.config(width=11,)
            self.subjob_box.grid(row=2, column=1, padx=0, pady=1, sticky='e')
            self.subjob_box.bind('<<ComboboxSelected>>', lambda event, entry=self.subjob_box: self.select_job(entry.get(),"sub"))

            self.am_label = ttk.Label(self.player_inputs_frame,text="Aftermath Lv.",width=15)
            self.am_label.grid(row=3, column=0, padx=0, pady=1, sticky="e")
            self.aftermath_list = [0, 1, 2, 3]
            self.am_level = tk.IntVar(value=0)
            self.am_level_box = ttk.Combobox(self.player_inputs_frame, values=self.aftermath_list, textvariable=self.am_level,state="readonly",)
            self.am_level_box.config(width=17,)
            self.am_level_box.grid(row=3, column=1, padx=0, pady=1,sticky='e',columnspan=1)



            self.spell_dict = {"NIN":["Doton: Ichi","Doton: Ni","Doton: San","Suiton: Ichi","Suiton: Ni","Suiton: San","Huton: Ichi","Huton: Ni","Huton: San","Katon: Ichi","Katon: Ni","Katon: San","Hyoton: Ichi","Hyoton: Ni","Hyoton: San", "Raiton: Ichi","Raiton: Ni","Raiton: San","Ranged Attack"],
                        "BLM":["Stone","Stone II","Stone III","Stone IV","Stone V","Stone VI","Stoneja",
                                "Water","Water II","Water III","Water IV","Water V","Water VI","Waterja",
                                "Aero","Aero II","Aero III","Aero IV","Aero V","Aero VI","Aeroja",
                                "Fire","Fire II","Fire III","Fire IV","Fire V","Fire VI","Firaja",
                                "Blizzard","Blizzard II","Blizzard III","Blizzard IV","Blizzard V","Blizzard VI","Blizzaja",
                                "Thunder","Thunder II","Thunder III","Thunder IV","Thunder V","Thunder VI", "Thundaja","Impact",
                                "Ranged Attack"],
                        "RDM":["Stone","Stone II","Stone III","Stone IV","Stone V",
                                "Water","Water II","Water III","Water IV","Water V",
                                "Aero","Aero II","Aero III","Aero IV","Aero V",
                                "Fire","Fire II","Fire III","Fire IV","Fire V",
                                "Blizzard","Blizzard II","Blizzard III","Blizzard IV","Blizzard V",
                                "Thunder","Thunder II","Thunder III","Thunder IV","Thunder V","Impact","Ranged Attack"],
                        "GEO":["Stone","Stone II","Stone III","Stone IV","Stone V",
                                "Water","Water II","Water III","Water IV","Water V",
                                "Aero","Aero II","Aero III","Aero IV","Aero V",
                                "Fire","Fire II","Fire III","Fire IV","Fire V",
                                "Blizzard","Blizzard II","Blizzard III","Blizzard IV","Blizzard V",
                                "Thunder","Thunder II","Thunder III","Thunder IV","Thunder V","Impact"],
                        "SCH":["Stone","Stone II","Stone III","Stone IV","Stone V","Geohelix II",
                                "Water","Water II","Water III","Water IV","Water V","Hydrohelix II",
                                "Aero","Aero II","Aero III","Aero IV","Aero V","Anemohelix II",
                                "Fire","Fire II","Fire III","Fire IV","Fire V","Pyrohelix II",
                                "Blizzard","Blizzard II","Blizzard III","Blizzard IV","Blizzard V","Cryohelix II",
                                "Thunder","Thunder II","Thunder III","Thunder IV","Thunder V","Ionohelix II",
                                "Luminohelix II", "Noctohelix II","Kaustra","Impact",],
                        "DRK":["Stone","Stone II","Stone III",
                                "Water","Water II","Water III",
                                "Aero","Aero II","Aero III",
                                "Fire","Fire II","Fire III",
                                "Blizzard","Blizzard II","Blizzard III",
                                "Thunder","Thunder II","Thunder III","Impact"],
                        "COR":["Ranged Attack","Earth Shot", "Water Shot", "Wind Shot", "Fire Shot", "Ice Shot", "Thunder Shot"],
                        "RNG":["Ranged Attack"],
                        "SAM":["Ranged Attack"],
                        "THF":["Ranged Attack"],
                        }

            self.spell_list_label = ttk.Label(self.player_inputs_frame,text="Spell",width=15)
            self.spell_list_label.grid(row=4, column=0, padx=0, pady=1, sticky="e")
            self.spell_list = self.spell_dict.get(self.mainjob.get(),["None"])
            self.spell_name = tk.StringVar(value=self.spell_dict.get(self.mainjob.get(),["None"])[0],)
            self.spell_box = ttk.Combobox(self.player_inputs_frame, values=self.spell_list, textvariable=self.spell_name,state="readonly",height=30)
            self.spell_box.config(width=17,)
            self.spell_box.grid(row=4, column=1, padx=0, pady=1,sticky='e')


            self.ws_dict = {"Katana": ["Blade: Retsu", "Blade: Teki", "Blade: To", "Blade: Chi", "Blade: Ei", "Blade: Jin", "Blade: Ten", "Blade: Ku", "Blade: Yu", "Blade: Metsu", "Blade: Kamu", "Blade: Hi", "Blade: Shun", "Zesho Meppo",],
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

            self.ranged_ws = self.ws_dict["Archery"] + self.ws_dict["Marksmanship"]

            # Currently equipped gear. Used to display the 4x4 grid of equipment and update the weapon skill drop down list.
            self.equipped_gear = {
                'main' : Heishi,
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
                'back' : np.random.choice([k for k in capes if self.mainjob.get().lower() in k["Jobs"] and "DEX Store TP" in k["Name2"] and "Ranged" not in k["Name2"]])}

            self.selected_main = tk.StringVar(value=self.equipped_gear["main"])
            self.selected_sub = tk.StringVar(value=self.equipped_gear["sub"])
            self.selected_ranged = tk.StringVar(value=self.equipped_gear["ranged"])
            self.selected_ammo = tk.StringVar(value=self.equipped_gear["ammo"])
            self.selected_head = tk.StringVar(value=self.equipped_gear["head"])
            self.selected_neck = tk.StringVar(value=self.equipped_gear["neck"])
            self.selected_ear1 = tk.StringVar(value=self.equipped_gear["ear1"])
            self.selected_ear2 = tk.StringVar(value=self.equipped_gear["ear2"])
            self.selected_body = tk.StringVar(value=self.equipped_gear["body"])
            self.selected_hands = tk.StringVar(value=self.equipped_gear["hands"])
            self.selected_ring1 = tk.StringVar(value=self.equipped_gear["ring1"])
            self.selected_ring2 = tk.StringVar(value=self.equipped_gear["ring2"])
            self.selected_back = tk.StringVar(value=self.equipped_gear["back"])
            self.selected_waist = tk.StringVar(value=self.equipped_gear["waist"])
            self.selected_legs = tk.StringVar(value=self.equipped_gear["legs"])
            self.selected_feet = tk.StringVar(value=self.equipped_gear["feet"])


            self.ws_list_label = ttk.Label(self.player_inputs_frame,text="Weapon Skill",width=15)
            self.ws_list_label.grid(row=5, column=0, padx=0, pady=1, sticky="e")
            self.main_wpn_type = self.equipped_gear["main"].get("Skill Type","None")
            self.ranged_wpn_type = self.equipped_gear["ranged"].get("Skill Type","None")
            self.ws_list = np.unique(self.ws_dict.get(self.main_wpn_type,["None"]) + self.ws_dict.get(self.ranged_wpn_type,["None"]))
            self.ws_name = tk.StringVar(value=self.ws_list[0])
            self.ws_box = ttk.Combobox(self.player_inputs_frame, values=self.ws_list, textvariable=self.ws_name,state="readonly",height=30,)

            self.ws_box.config(width=17,)
            self.ws_box.grid(row=5, column=1, padx=0, pady=1,sticky='e',columnspan=1)


            # Add labels and text entries (https://github.com/TomSchimansky/ctk/wiki/Entry)
            self.min_tp_label = ttk.Label(self.player_inputs_frame,text="Min. TP:")
            self.min_tp_label.grid(row=6, column=0, sticky="w", padx=0, pady=1)
            self.tp1 = tk.IntVar(value=1000)
            self.min_tp = ttk.Entry(self.player_inputs_frame,textvariable=self.tp1,justify="right")
            self.min_tp.configure(width=6)
            self.min_tp.grid(row=6,column=1,padx=0,pady=1,sticky='w')

            self.max_tp_label = ttk.Label(self.player_inputs_frame,text="Max. TP:")
            self.max_tp_label.grid(row=7, column=0, sticky="w", padx=0, pady=1)
            self.tp2 = tk.IntVar(value=1300)
            self.max_tp = ttk.Entry(self.player_inputs_frame,textvariable=self.tp2,justify="right",)
            self.max_tp.configure(width=6)
            self.max_tp.grid(row=7,column=1,padx=0,pady=1,sticky='w')

            self.start_tp_label = ttk.Label(self.player_inputs_frame,text="Initial TP:")
            self.start_tp_label.grid(row=8, column=0, sticky="w", padx=0, pady=1)
            self.tp0 = tk.IntVar(value=0)
            self.start_tp = ttk.Entry(self.player_inputs_frame,textvariable=self.tp0,justify="right")
            self.start_tp.configure(width=6)
            self.start_tp.grid(row=8, column=1,padx=0,pady=1,sticky='w')

        # ===========================================================================
        # ===========================================================================
        # Define a new scrollable frame which holds the full list of checkbox abilities. We'll hide abilities not useable by the selected main/subjob combo


        self.ja_toggles_frame = ttk.LabelFrame(self.inputs_frame, borderwidth=3,text="  Special Toggles  ")
        self.ja_toggles_frame.grid(row=0,column=1,padx=0,pady=0,sticky="nw")

        self.ja_scrollframe = ttk.Frame(self.ja_toggles_frame)
        self.ja_scrollframe.pack(fill=tk.BOTH, expand=1)

        self.ja_canvas = tk.Canvas(self.ja_scrollframe,height=225,width=150)
        self.ja_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.ja_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.ja_canvas))
        self.ja_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.ja_canvas)) 

        self.ja_scrollbar = ttk.Scrollbar(self.ja_scrollframe, orient=tk.VERTICAL, command=self.ja_canvas.yview)
        self.ja_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ja_canvas.configure(yscrollcommand=self.ja_scrollbar.set)
        self.ja_canvas.bind("<Configure>", lambda event: self.ja_canvas.configure(scrollregion=self.ja_canvas.bbox("all")))

        self.ja_frame = ttk.Frame(self.ja_canvas)


        # Note: the order and row number of these toggles (at this moment) does not matter at all. They get reorganized when swapping jobs and a job swap is trigged when the code starts.
        self.magic_burst_value = tk.BooleanVar()
        self.magic_burst_toggle = ttk.Checkbutton(self.ja_frame,variable=self.magic_burst_value, text="Magic Burst",width=-25, command=lambda event="magic_burst": self.update_special_checkboxes(event))
        self.magic_burst_toggle.state(["!alternate"])
        self.magic_burst_toggle.grid(row=0,column=0,sticky="n")

        self.warcry_value = tk.BooleanVar()
        self.warcry_toggle = ttk.Checkbutton(self.ja_frame,variable=self.warcry_value, text="Warcry",width=-25, command=lambda event="warcry": self.update_special_checkboxes(event))
        self.warycry_tip = Hovertip(self.warcry_toggle,"Attack +((war_level)/4)+4.75)/256*100 (%)\nWAR mainjob: TP Bonus +700\nWAR mainjob: Attack +60",hover_delay=500)
        self.warcry_toggle.state(["!alternate"])
        self.warcry_toggle.grid(row=1,column=0,sticky="n")

        self.berserk_value = tk.BooleanVar()
        self.berserk_toggle = ttk.Checkbutton(self.ja_frame,variable=self.berserk_value, text="Berserk",width=-25, command=lambda event="berserk": self.update_special_checkboxes(event))
        self.berserk_tip = Hovertip(self.berserk_toggle,"Attack +25% (256/1024)\nWAR mainjob: Attack +10% (100/1024)\nWAR mainjob: Attack +40\nConqueror equipped: Attack +8.5%\nConqueror equipped: Crit Rate +14%",hover_delay=500)
        self.berserk_toggle.state(["!alternate"])
        self.berserk_toggle.grid(row=2,column=0,sticky="n")

        self.aggressor_value = tk.BooleanVar()
        self.aggressor_toggle = ttk.Checkbutton(self.ja_frame,variable=self.aggressor_value, text="Aggressor",width=-25, command=lambda event="aggressor": self.update_special_checkboxes(event))
        self.aggressor_tip = Hovertip(self.aggressor_toggle,"Accuracy +25\nWAR mainjob: Accuracy +20",hover_delay=500)
        self.aggressor_toggle.state(["!alternate"])
        self.aggressor_toggle.grid(row=2,column=0,sticky="n")

        self.mighty_strikes_value = tk.BooleanVar()
        self.mighty_strikes_toggle = ttk.Checkbutton(self.ja_frame,variable=self.mighty_strikes_value, text="Mighty Strikes",width=-25, command=lambda event="mighty_strikes": self.update_special_checkboxes(event))
        self.mighty_strikes_tip = Hovertip(self.mighty_strikes_toggle,"Crit Rate = 100%\nAccuracy +40",hover_delay=500)
        self.mighty_strikes_toggle.state(["!alternate"])
        self.mighty_strikes_toggle.grid(row=3,column=0,sticky="n")

        self.focus_value = tk.BooleanVar()
        self.focus_toggle = ttk.Checkbutton(self.ja_frame,variable=self.focus_value, text="Focus",width=-25, command=lambda event="focus": self.update_special_checkboxes(event))
        self.focus_tip = Hovertip(self.focus_toggle,"Crit Rate +20%\nAccuracy +120",hover_delay=500)
        self.focus_toggle.state(["!alternate"])
        self.focus_toggle.grid(row=4,column=0,sticky="n")

        self.footwork_value = tk.BooleanVar()
        self.footwork_toggle = ttk.Checkbutton(self.ja_frame,variable=self.footwork_value, text="Footwork",width=-25, command=lambda event="footwork": self.update_special_checkboxes(event))
        self.footwork_tip = Hovertip(self.footwork_toggle,"Kick Attacks +20%\nKick Attacks Attack +26% (260/1024)\nKick DMG +40\nDragon/Tornado Kick use \"Kick DMG\" instead of \"H2H DMG\"",hover_delay=500)
        self.footwork_toggle.state(["!alternate"])
        self.footwork_toggle.grid(row=5,column=0,sticky="n")

        self.impetus_value = tk.BooleanVar()
        self.impetus_toggle = ttk.Checkbutton(self.ja_frame,variable=self.impetus_value, text="Impetus",width=-25, command=lambda event="impetus": self.update_special_checkboxes(event))
        self.impetus_tip = Hovertip(self.impetus_toggle,"Crit Rate +45%\nAttack +136\nAccuracy +45\nBhikku Cylas equipped: Crit Damage +45%\n(assumes 90% max potency)",hover_delay=500)
        self.impetus_toggle.state(["!alternate"])
        self.impetus_toggle.grid(row=6,column=0,sticky="n")

        self.manafont_value = tk.BooleanVar()
        self.manafont_toggle = ttk.Checkbutton(self.ja_frame,variable=self.manafont_value, text="Manafont",width=-25, command=lambda event="manafont": self.update_special_checkboxes(event))
        self.manafont_tip = Hovertip(self.manafont_toggle,"Magic Damage +60",hover_delay=500)
        self.manafont_toggle.state(["!alternate"])
        self.manafont_toggle.grid(row=7,column=0,sticky="n")

        self.manawell_value = tk.BooleanVar()
        self.manawell_toggle = ttk.Checkbutton(self.ja_frame,variable=self.manawell_value, text="Manawell",width=-25, command=lambda event="manawell": self.update_special_checkboxes(event))
        self.manawell_tip = Hovertip(self.manawell_toggle,"Magic Damage +20",hover_delay=500)
        self.manawell_toggle.state(["!alternate"])
        self.manawell_toggle.grid(row=8,column=0,sticky="n")

        self.chainspell_value = tk.BooleanVar()
        self.chainspell_toggle = ttk.Checkbutton(self.ja_frame,variable=self.chainspell_value, text="Chainspell",width=-25, command=lambda event="chainspell": self.update_special_checkboxes(event))
        self.chainspell_tip = Hovertip(self.chainspell_toggle,"Magic Damage +40",hover_delay=500)
        self.chainspell_toggle.state(["!alternate"])
        self.chainspell_toggle.grid(row=9,column=0,sticky="n")

        self.composure_value = tk.BooleanVar()
        self.composure_toggle = ttk.Checkbutton(self.ja_frame,variable=self.composure_value, text="Composure",width=-25, command=lambda event="composure": self.update_special_checkboxes(event))
        self.composuretip = Hovertip(self.composure_toggle,"Accuracy +20",hover_delay=500)
        self.composure_toggle.state(["!alternate"])
        self.composure_toggle.grid(row=10,column=0,sticky="n")

        self.conspirator_value = tk.BooleanVar()
        self.conspirator_toggle = ttk.Checkbutton(self.ja_frame,variable=self.conspirator_value, text="Conspirator",width=-25, command=lambda event="conspirator": self.update_special_checkboxes(event))
        self.conspiratortip = Hovertip(self.conspirator_toggle,"Accuracy +45\nSubtle Blow +50\n(assumes 6 players on enmity list)",hover_delay=500)
        self.conspirator_toggle.state(["!alternate"])
        self.conspirator_toggle.grid(row=11,column=0,sticky="n")

        self.enlight_value = tk.BooleanVar()
        self.enlight_toggle = ttk.Checkbutton(self.ja_frame,variable=self.enlight_value, text="Enlight II",width=-25, command=lambda event="enlight": self.update_special_checkboxes(event))
        self.enlighttip = Hovertip(self.enlight_toggle,"Accuracy +112\n(assumes 80% max potency with 600 Divine Magic Skill)",hover_delay=500)
        self.enlight_toggle.state(["!alternate"])
        self.enlight_toggle.grid(row=12,column=0,sticky="n")

        self.last_resort_value = tk.BooleanVar()
        self.last_resort_toggle = ttk.Checkbutton(self.ja_frame,variable=self.last_resort_value, text="Last Resort",width=-25, command=lambda event="last_resort": self.update_special_checkboxes(event))
        self.lastresort_tip = Hovertip(self.last_resort_toggle,"Attack +25% (256/1024)\n2-handed weapon equipped: JA Haste +15%\nDRK mainjob: Attack +10% (100/1024)\nDRK mainjob: Attack +40\n2-handed weapon equipped & DRK mainjob: JA Haste +10%",hover_delay=500)
        self.last_resort_toggle.state(["!alternate"])
        self.last_resort_toggle.grid(row=13,column=0,sticky="n")

        self.endark_value = tk.BooleanVar()
        self.endark_toggle = ttk.Checkbutton(self.ja_frame,variable=self.endark_value, text="Endark II",width=-25, command=lambda event="endark": self.update_special_checkboxes(event))
        self.endarktip = Hovertip(self.endark_toggle,"Accuracy +16\nAttack +120\n(assumes 80% max potency with 600 Dark Magic Skill)",hover_delay=500)
        self.endark_toggle.state(["!alternate"])
        self.endark_toggle.grid(row=14,column=0,sticky="n")

        self.sharpshot_value = tk.BooleanVar()
        self.sharpshot_toggle = ttk.Checkbutton(self.ja_frame,variable=self.sharpshot_value, text="Sharpshot",width=-25, command=lambda event="sharpshot": self.update_special_checkboxes(event))
        self.sharpshot_tip = Hovertip(self.sharpshot_toggle,"Ranged Accuracy +40\nRNG mainjob: Ranged Attack +40",hover_delay=500)
        self.sharpshot_toggle.state(["!alternate"])
        self.sharpshot_toggle.grid(row=15,column=0,sticky="n")

        self.enlightenment_value = tk.BooleanVar()
        self.enlightenment_toggle = ttk.Checkbutton(self.ja_frame,variable=self.enlightenment_value, text="Enlightenment",width=-25, command=lambda event="enlightenment": self.update_special_checkboxes(event))
        self.enlightenmenttip = Hovertip(self.enlightenment_toggle,"INT+20\nMND+20",hover_delay=500)
        self.enlightenment_toggle.state(["!alternate"])
        self.enlightenment_toggle.grid(row=16,column=0,sticky="n")

        self.velocity_shot_value = tk.BooleanVar()
        self.velocity_shot_toggle = ttk.Checkbutton(self.ja_frame,variable=self.velocity_shot_value, text="Velocity Shot",width=-25, command=lambda event="velocity_shot": self.update_special_checkboxes(event))
        self.velocityshottip = Hovertip(self.velocity_shot_toggle,"Ranged Attack +40\nJA Haste -15% (needs testing)\nRanged Attack +15% (152/1024)",hover_delay=500)
        self.velocity_shot_toggle.state(["!alternate"])
        self.velocity_shot_toggle.grid(row=17,column=0,sticky="n")

        self.double_shot_value = tk.BooleanVar()
        self.double_shot_toggle = ttk.Checkbutton(self.ja_frame,variable=self.double_shot_value, text="Double Shot",width=-25, command=lambda event="double_shot": self.update_special_checkboxes(event))
        self.double_shot_toggle.state(["!alternate"])
        self.double_shot_toggle.grid(row=18,column=0,sticky="n")

        self.hover_shot_value = tk.BooleanVar()
        self.hover_shot_toggle = ttk.Checkbutton(self.ja_frame,variable=self.hover_shot_value, text="Hover Shot",width=-25, command=lambda event="hover_shot": self.update_special_checkboxes(event))
        self.hovershottip = Hovertip(self.hover_shot_toggle,"Damage x2\nRanged Accuracy +100\nMagic Accuracy +100",hover_delay=500)
        self.hover_shot_toggle.state(["!alternate"])
        self.hover_shot_toggle.grid(row=19,column=0,sticky="n")

        self.hasso_value = tk.BooleanVar()
        self.hasso_toggle = ttk.Checkbutton(self.ja_frame,variable=self.hasso_value, text="Hasso",width=-25, command=lambda event="hasso": self.update_special_checkboxes(event))
        self.hassotip = Hovertip(self.hasso_toggle,"2-handed weapon equipped:\n    STR +(sam_level)/7\n    JA Haste +10%\n    Accuracy +10\n    SAM mainjob: STR +20\n    SAM mainjob: ZanHasso",hover_delay=500)
        self.hasso_toggle.state(["!alternate"])
        self.hasso_toggle.grid(row=20,column=0,sticky="n")

        self.sange_value = tk.BooleanVar()
        self.sange_toggle = ttk.Checkbutton(self.ja_frame,variable=self.sange_value, text="Sange",width=-25, command=lambda event="sange": self.update_special_checkboxes(event))
        self.sangetip = Hovertip(self.sange_toggle,"Daken = 100%\nRanged Accuracy +100",hover_delay=500)
        self.sange_toggle.state(["!alternate"])
        self.sange_toggle.grid(row=21,column=0,sticky="n")

        self.innin_value = tk.BooleanVar()
        self.innin_toggle = ttk.Checkbutton(self.ja_frame,variable=self.innin_value, text="Innin",width=-25, command=lambda event="innin": self.update_special_checkboxes(event))
        self.innintip = Hovertip(self.innin_toggle,"Accuracy +20\nSkillchain bonus +5%\nMagic Burst Damage +5\nCrit Rate +24%\nNinjutsu Damage +24%\nEvasion -24\n(assumes 70% potency)",hover_delay=500)
        self.innin_toggle.state(["!alternate"])
        self.innin_toggle.grid(row=22,column=0,sticky="n")

        self.futae_value = tk.BooleanVar()
        self.futae_toggle = ttk.Checkbutton(self.ja_frame,variable=self.futae_value, text="Futae",width=-25, command=lambda event="futae": self.update_special_checkboxes(event))
        self.futaetip = Hovertip(self.futae_toggle,"Ninjutsu Damage +50%\nNinjutsu Magic Damage +100",hover_delay=500)
        self.futae_toggle.state(["!alternate"])
        self.futae_toggle.grid(row=23,column=0,sticky="n")

        self.natures_meditation_value = tk.BooleanVar()
        self.natures_meditation_toggle = ttk.Checkbutton(self.ja_frame,variable=self.natures_meditation_value, text="Nature's Meditation",width=-25, command=lambda event="natures_meditation": self.update_special_checkboxes(event))
        self.natures_meditation_tip = Hovertip(self.natures_meditation_toggle,"Attack +20%",hover_delay=500)
        self.natures_meditation_toggle.state(["!alternate"])
        self.natures_meditation_toggle.grid(row=24,column=0,sticky="n")

        self.triple_shot_value = tk.BooleanVar()
        self.triple_shot_toggle = ttk.Checkbutton(self.ja_frame,variable=self.triple_shot_value, text="Triple Shot",width=-25, command=lambda event="triple_shot": self.update_special_checkboxes(event))
        self.triple_shot_toggle.state(["!alternate"])
        self.triple_shot_toggle.grid(row=25,column=0,sticky="n")

        self.building_flourish_value = tk.BooleanVar()
        self.building_flourish_toggle = ttk.Checkbutton(self.ja_frame,variable=self.building_flourish_value, text="Building Flourish",width=-25, command=lambda event="building_flourish": self.update_special_checkboxes(event))
        self.building_tip = Hovertip(self.building_flourish_toggle,"Crit Rate +10%\nAttack +25%\nAccuracy +40\nWeapon Skill Damage +20% (JP Gifts)",hover_delay=500)
        self.building_flourish_toggle.state(["!alternate"])
        self.building_flourish_toggle.grid(row=26,column=0,sticky="n")

        self.climactic_flourish_value = tk.BooleanVar()
        self.climactic_flourish_toggle = ttk.Checkbutton(self.ja_frame,variable=self.climactic_flourish_value, text="Climactic Flourish",width=-25, command=lambda event="climactic_flourish": self.update_special_checkboxes(event))
        self.climactic_flourish_toggle.state(["!alternate"])
        self.climactic_flourish_toggle.grid(row=27,column=0,sticky="n")

        self.striking_flourish_value = tk.BooleanVar()
        self.striking_flourish_toggle = ttk.Checkbutton(self.ja_frame,variable=self.striking_flourish_value, text="Striking Flourish",width=-25, command=lambda event="striking_flourish": self.update_special_checkboxes(event))
        self.striking_flourish_toggle.state(["!alternate"])
        self.striking_flourish_toggle.grid(row=28,column=0,sticky="n")

        self.ternary_flourish_value = tk.BooleanVar()
        self.ternary_flourish_toggle = ttk.Checkbutton(self.ja_frame,variable=self.ternary_flourish_value, text="Ternary Flourish",width=-25, command=lambda event="ternary_flourish": self.update_special_checkboxes(event))
        self.ternary_flourish_toggle.state(["!alternate"])
        self.ternary_flourish_toggle.grid(row=29,column=0,sticky="n")

        self.saber_dance_value = tk.BooleanVar()
        self.saber_dance_toggle = ttk.Checkbutton(self.ja_frame,variable=self.saber_dance_value, text="Saber Dance",width=-25, command=lambda event="saber_dance": self.update_special_checkboxes(event))
        self.saber_dance_tip = Hovertip(self.saber_dance_toggle,"DA +25%",hover_delay=500)
        self.saber_dance_toggle.state(["!alternate"])
        self.saber_dance_toggle.grid(row=30,column=0,sticky="n")

        self.ebullience_value = tk.BooleanVar()
        self.ebullience_toggle = ttk.Checkbutton(self.ja_frame,variable=self.ebullience_value, text="Ebullience",width=-25, command=lambda event="ebullience": self.update_special_checkboxes(event))
        self.ebulliencetip = Hovertip(self.ebullience_toggle,"Magic Spell Damage +20%\nSCH mainjob: Magic Damage +40.",hover_delay=500)
        self.ebullience_toggle.state(["!alternate"])
        self.ebullience_toggle.grid(row=31,column=0,sticky="n")

        self.theurgic_focus_value = tk.BooleanVar()
        self.theurgic_focus_toggle = ttk.Checkbutton(self.ja_frame,variable=self.theurgic_focus_value, text="Theurgic Focus",width=-25, command=lambda event="theurgic_focus": self.update_special_checkboxes(event))
        self.theurgic_focus_toggle.state(["!alternate"])
        self.theurgic_focus_toggle.grid(row=32,column=0,sticky="n")

        self.swordplay_value = tk.BooleanVar()
        self.swordplay_toggle = ttk.Checkbutton(self.ja_frame,variable=self.swordplay_value, text="Swordplay",width=-25, command=lambda event="swordplay": self.update_special_checkboxes(event))
        self.swordplaytip = Hovertip(self.swordplay_toggle,"Accuracy +54\nEvasion+54\nUses 90% max potency",hover_delay=500)
        self.swordplay_toggle.state(["!alternate"])
        self.swordplay_toggle.grid(row=33,column=0,sticky="n")

        self.true_shot_value = tk.BooleanVar()
        self.true_shot_toggle = ttk.Checkbutton(self.ja_frame,variable=self.true_shot_value, text="True Shot",width=-25, command=lambda event="true_shot": self.update_special_checkboxes(event))
        self.true_shot_toggle.state(["!alternate"])
        self.true_shot_toggle.grid(row=34,column=0,sticky="n")

        self.sneak_attack_value = tk.BooleanVar()
        self.sneak_attack_toggle = ttk.Checkbutton(self.ja_frame,variable=self.sneak_attack_value, text="Sneak Attack",width=-25, command=lambda event="sneak_attack": self.update_special_checkboxes(event))
        self.sneak_attack_toggle.state(["!alternate"])
        self.sneak_attack_toggle.grid(row=35,column=0,sticky="n")

        self.trick_attack_value = tk.BooleanVar()
        self.trick_attack_toggle = ttk.Checkbutton(self.ja_frame,variable=self.trick_attack_value, text="Trick Attack",width=-25, command=lambda event="trick_attack": self.update_special_checkboxes(event))
        self.trick_attack_toggle.state(["!alternate"])
        self.trick_attack_toggle.grid(row=36,column=0,sticky="n")

        self.blood_rage_value = tk.BooleanVar()
        self.blood_rage_toggle = ttk.Checkbutton(self.ja_frame,variable=self.blood_rage_value, text="Blood Rage",width=-25, command=lambda event="blood_rage": self.update_special_checkboxes(event))
        self.bloodragetip = Hovertip(self.blood_rage_toggle,"Crit Rate +40%\n(20% base +20% JP Gifts)",hover_delay=500)
        self.blood_rage_toggle.state(["!alternate"])
        self.blood_rage_toggle.grid(row=37,column=0,sticky="n")

        self.distract3_value = tk.BooleanVar()
        self.distract3_toggle = ttk.Checkbutton(self.ja_frame,variable=self.distract3_value, text="Distract III",width=-25, command=lambda event="distract3": self.update_special_checkboxes(event))
        self.distract3tip = Hovertip(self.distract3_toggle,"Enemy Evasion -280\n(-130 base, +58% gear potency, +39% Saboteur potency)",hover_delay=500)
        self.distract3_toggle.state(["!alternate"])
        self.distract3_toggle.grid(row=38,column=0,sticky="n")

        self.barrage_value = tk.BooleanVar()
        self.barrage_toggle = ttk.Checkbutton(self.ja_frame,variable=self.barrage_value, text="Barrage",width=-25, command=lambda event="barrage": self.update_special_checkboxes(event))
        self.barrage_toggle.state(["!alternate"])
        self.barrage_toggle.grid(row=39,column=0,sticky="n")

        self.haste_samba_value = tk.BooleanVar()
        self.haste_samba_toggle = ttk.Checkbutton(self.ja_frame,variable=self.haste_samba_value, text="Haste Samba",width=-25, command=lambda event="haste_samba": self.update_special_checkboxes(event))
        self.hastesamba_tip = Hovertip(self.haste_samba_toggle,"JA Haste: +5%\nDNC mainjob: JA Haste +5%",hover_delay=500)
        self.haste_samba_toggle.state(["!alternate"])
        self.haste_samba_toggle.grid(row=40,column=0,sticky="n")

        self.klimaform_value = tk.BooleanVar()
        self.klimaform_toggle = ttk.Checkbutton(self.ja_frame,variable=self.klimaform_value, text="Klimaform",width=-25, command=lambda event="klimaform": self.update_special_checkboxes(event))
        self.klimaform_tip = Hovertip(self.klimaform_toggle,"Magic Accuracy +15",hover_delay=500)
        self.klimaform_toggle.state(["!alternate"])
        self.klimaform_toggle.grid(row=41,column=0,sticky="n")

        self.divine_emblem_value = tk.BooleanVar()
        self.divine_emblem_toggle = ttk.Checkbutton(self.ja_frame,variable=self.divine_emblem_value, text="Divine Emblem",width=-25, command=lambda event="divine_emblem": self.update_special_checkboxes(event))
        self.divine_emblem_tip = Hovertip(self.divine_emblem_toggle,"Magic Damage +40",hover_delay=500)
        self.divine_emblem_toggle.state(["!alternate"])
        self.divine_emblem_toggle.grid(row=42,column=0,sticky="n")

        self.angon_value = tk.BooleanVar()
        self.angon_toggle = ttk.Checkbutton(self.ja_frame,variable=self.angon_value, text="Angon",width=-25, command=lambda event="angon": self.update_special_checkboxes(event))
        self.angon_tip = Hovertip(self.divine_emblem_toggle,"Enemy Defense -20%",hover_delay=500)
        self.angon_toggle.state(["!alternate"])
        self.angon_toggle.grid(row=43,column=0,sticky="n")

        self.ja_canvas.create_window((0,0),window=self.ja_frame, anchor="nw")
        # ===========================================================================
        # ===========================================================================

        self.enemy_inputs_frame = ttk.LabelFrame(self.inputs_frame,borderwidth=3,width=676/2-1,height=250,text="  Enemy Inputs  ")
        self.enemy_inputs_frame.grid(row=0, column=2, padx=0, pady=0, sticky="ne")

        self.enemy_location_frame = ttk.Frame(self.enemy_inputs_frame)
        self.enemy_location_frame.grid(row=0,column=0,pady=10)
        # self.enemy_location_frame.grid_columnconfigure(0,weight=1)
        # self.enemy_location_frame.grid_rowconfigure(0,weight=1)
        if True:
            self.selected_enemy = tk.StringVar(value="Apex Bat")
            self.enemy_combo = ttk.Combobox(self.enemy_location_frame, values=list(preset_enemies.keys()),textvariable=self.selected_enemy, state="readonly")
            self.enemy_combo.grid(row=0,column=0)
            self.enemy_combo.bind('<<ComboboxSelected>>', lambda event, entry=self.enemy_combo: self.select_enemy(entry.get()))
            self.enemy_location_var = tk.StringVar(value=preset_enemies[self.selected_enemy.get()]["Location"])
            self.enemy_location = ttk.Label(self.enemy_location_frame, textvariable=self.enemy_location_var)
            self.enemy_location.grid(row=1,column=0,padx=0,pady=0)

        self.enemy_stats_frame = ttk.Frame(self.enemy_inputs_frame,)
        self.enemy_stats_frame.grid(row=1,column=0)
        if True:
            self.enemy_level = tk.IntVar(value=preset_enemies[self.selected_enemy.get()]["Level"])
            self.enemy_level_label = ttk.Label(self.enemy_stats_frame,text="Level: ")
            self.enemy_level_label.grid(row=0,column=0, sticky="nw",padx=0,pady=2)
            self.enemy_level_entry = ttk.Entry(self.enemy_stats_frame,textvariable=self.enemy_level,width=8)
            self.enemy_level_entry.grid(row=0,column=1,sticky="nw",padx=0,pady=2)

            self.enemy_evasion = tk.IntVar(value=preset_enemies[self.selected_enemy.get()]["Evasion"])
            self.enemy_evasion_label = ttk.Label(self.enemy_stats_frame,text="Evasion: ")
            self.enemy_evasion_label.grid(row=1,column=0, sticky="nw",padx=0,pady=2)
            self.enemy_evasion_entry = ttk.Entry(self.enemy_stats_frame,textvariable=self.enemy_evasion,width=8)
            self.enemy_evasion_entry.grid(row=1,column=1,sticky="nw",padx=0,pady=2)

            self.enemy_defense = tk.IntVar(value=preset_enemies[self.selected_enemy.get()]["Defense"])
            self.enemy_defense_label = ttk.Label(self.enemy_stats_frame,text="Defense: ")
            self.enemy_defense_label.grid(row=2,column=0, sticky="nw",padx=0,pady=2)
            self.enemy_defense_entry = ttk.Entry(self.enemy_stats_frame,textvariable=self.enemy_defense,width=8)
            self.enemy_defense_entry.grid(row=2,column=1,sticky="nw",padx=0,pady=2)

            self.enemy_magic_defense = tk.IntVar(value=preset_enemies[self.selected_enemy.get()]["Magic Defense"])
            self.enemy_magic_defense_label = ttk.Label(self.enemy_stats_frame,text="Magic Defense: ")
            self.enemy_magic_defense_label.grid(row=3,column=0, sticky="nw",padx=0,pady=2)
            self.enemy_magic_defense_entry = ttk.Entry(self.enemy_stats_frame,textvariable=self.enemy_magic_defense,width=8)
            self.enemy_magic_defense_entry.grid(row=3,column=1,sticky="nw",padx=0,pady=2)

            self.enemy_magic_evasion = tk.IntVar(value=preset_enemies[self.selected_enemy.get()]["Magic Evasion"])
            self.enemy_magic_evasion_label = ttk.Label(self.enemy_stats_frame,text="Magic Evasion: ")
            self.enemy_magic_evasion_label.grid(row=4,column=0, sticky="nw",padx=0,pady=2)
            self.enemy_magic_evasion_entry = ttk.Entry(self.enemy_stats_frame,textvariable=self.enemy_magic_evasion,width=8)
            self.enemy_magic_evasion_entry.grid(row=4,column=1,sticky="nw",padx=0,pady=2)

        self.enemy_stats_frame2 = ttk.Frame(self.enemy_inputs_frame,)
        self.enemy_stats_frame2.grid(row=1,column=1,padx=10)
        if True:
            self.enemy_agi = tk.IntVar(value=preset_enemies[self.selected_enemy.get()]["AGI"])
            self.enemy_agi_label = ttk.Label(self.enemy_stats_frame2,text="AGI: ")
            self.enemy_agi_label.grid(row=0,column=0, sticky="nw",padx=0,pady=2)
            self.enemy_agi_entry = ttk.Entry(self.enemy_stats_frame2,textvariable=self.enemy_agi,width=8)
            self.enemy_agi_entry.grid(row=0,column=1,sticky="nw",padx=0,pady=2)

            self.enemy_vit = tk.IntVar(value=preset_enemies[self.selected_enemy.get()]["VIT"])
            self.enemy_vit_label = ttk.Label(self.enemy_stats_frame2,text="VIT: ")
            self.enemy_vit_label.grid(row=1,column=0, sticky="nw",padx=0,pady=2)
            self.enemy_vit_entry = ttk.Entry(self.enemy_stats_frame2,textvariable=self.enemy_vit,width=8)
            self.enemy_vit_entry.grid(row=1,column=1,sticky="nw",padx=0,pady=2)

            self.enemy_int = tk.IntVar(value=preset_enemies[self.selected_enemy.get()]["INT"])
            self.enemy_int_label = ttk.Label(self.enemy_stats_frame2,text="INT: ")
            self.enemy_int_label.grid(row=2,column=0, sticky="nw",padx=0,pady=2)
            self.enemy_int_entry = ttk.Entry(self.enemy_stats_frame2,textvariable=self.enemy_int,width=8)
            self.enemy_int_entry.grid(row=2,column=1,sticky="nw",padx=0,pady=2)

            self.enemy_mnd = tk.IntVar(value=preset_enemies[self.selected_enemy.get()]["MND"])
            self.enemy_mnd_label = ttk.Label(self.enemy_stats_frame2,text="MND: ")
            self.enemy_mnd_label.grid(row=3,column=0, sticky="nw",padx=0,pady=2)
            self.enemy_mnd_entry = ttk.Entry(self.enemy_stats_frame2,textvariable=self.enemy_mnd,width=8)
            self.enemy_mnd_entry.grid(row=3,column=1,sticky="nw",padx=0,pady=2)

# =============================================================================================================================
# =============================================================================================================================
#  Frame 2: Contains buffs from WHM/Food/BRD/COR/GEO
# =============================================================================================================================
# =============================================================================================================================

        self.buffs_frame = ttk.LabelFrame(self.inputs_tab,borderwidth=3,width=676,height=250,text="  Active Buffs  ")
        # self.buffs_frame = ttk.Frame(self,width=676,height=250,)
        self.buffs_frame.grid(row=1, column=0, padx=2, pady=0, sticky="w")
        self.buffs_frame.grid_propagate(0)

        if True:
            self.whm_frame = ttk.Frame(self.buffs_frame,width=165,height=250)
            self.whm_frame.grid(row=0,column=0,padx=15,pady=0,sticky="n")

            self.whm_on = tk.BooleanVar(value=True)
            self.whm_cbox = ttk.Checkbutton(self.whm_frame,variable=self.whm_on,text="White Magic",command=lambda trigger="whm": self.update_buff_cboxes(trigger))
            # self.whm_cbox.state(['!alternate']) 
            self.whm_cbox.grid(row=0,column=0,sticky="nw",padx=0,pady=2)

            self.shell5_on = tk.BooleanVar(value=True)
            self.shell5_cbox = ttk.Checkbutton(self.whm_frame,variable=self.shell5_on,text="Shell V")
            self.shell5_cbox.grid(row=1,column=0,sticky="nw",padx=0,pady=2)

            self.whm_spells1 = ["None"] + ["Dia","Dia II","Dia III"]
            self.whm_spell1 = tk.StringVar(value="Dia III")
            self.whm_combo1 = ttk.Combobox(self.whm_frame, values=self.whm_spells1, textvariable=self.whm_spell1,state="readonly")
            self.whm_combo1.grid(row=2,column=0,sticky="nw",padx=0,pady=2)

            self.whm_spells2 = ["None"] + ["Haste","Haste II"] 
            self.whm_spell2 = tk.StringVar(value="Haste II")
            self.whm_combo2 = ttk.Combobox(self.whm_frame, values=self.whm_spells2, textvariable=self.whm_spell2,state="readonly")
            self.whm_combo2.grid(row=3,column=0,sticky="nw",padx=0,pady=2)

            self.whm_stat_spells = ["None"] + ["Boost-STR","Boost-DEX","Boost-VIT","Boost-AGI","Boost-INT","Boost-MND","Boost-CHR"]
            self.whm_spell3 = tk.StringVar(value="None")
            self.whm_combo3 = ttk.Combobox(self.whm_frame, values=self.whm_stat_spells, textvariable=self.whm_spell3,state="readonly")
            self.whm_combo3.grid(row=4,column=0,sticky="nw",padx=0,pady=2)

            self.whm_spells4 = ["None"] +["Sandstorm II","Rainstorm II","Windstorm II","Firestorm II","Hailstorm II","Thunderstorm II","Aurorastorm II","Voidstorm II"]
            self.whm_spell4 = tk.StringVar(value="None")
            self.whm_combo4 = ttk.Combobox(self.whm_frame, values=self.whm_spells4, textvariable=self.whm_spell4,state="readonly")
            self.whm_combo4.grid(row=5,column=0,sticky="nw",padx=0,pady=2)

            self.food_frame = ttk.LabelFrame(self.whm_frame, text="  Active Food  ")
            self.food_frame.grid(row=6,column=0,sticky="nw",padx=0,pady=10)
            self.active_food = tk.StringVar(value="Grape Daifuku")
            self.food_combo = ttk.Combobox(self.food_frame, values=["None"] + [k["Name"] for k in all_food], textvariable=self.active_food,state="readonly")
            self.food_combo.grid(row=0,column=0,sticky="nw",padx=0,pady=2)
            

        if True:
            self.brd_frame = ttk.Frame(self.buffs_frame,width=165,height=250)
            self.brd_frame.grid(row=0,column=1,padx=15,pady=0,sticky="n")


            self.brd_on = tk.BooleanVar(value=False)
            self.brd_cbox = ttk.Checkbutton(self.brd_frame,variable=self.brd_on,text="Songs",command=lambda trigger="brd": self.update_buff_cboxes(trigger))
            # self.brd_cbox.state(['!alternate']) 
            self.brd_cbox.grid(row=0,column=0,sticky="nw")
            self.brd_potency = tk.StringVar(value="Songs +7")
            self.brd_combo1 = ttk.Combobox(self.brd_frame, values=["Songs +9","Songs +8","Songs +7","Songs +6","Songs +5","Songs +4","Songs +3","Songs +2","Songs +1","Songs +0"], textvariable=self.brd_potency,state="readonly")
            self.brd_combo1.grid(row=1,column=0,sticky="nw",padx=0,pady=2)


            self.song_list = ["Blade Madrigal","Sword Madrigal","Minuet V","Minuet IV","Minuet III","Honor March","Victory March","Adv. March","Hunter's Prelude","Archer's Prelude","Sinewy Etude","Herculean Etude","Dextrous Etude","Uncanny Etude","Vivacious Etude","Vital Etude","Quick Etude","Swift Etude","Learned Etude","Sage Etude","Spirited Etude","Logical Etude","Enchanting Etude","Bewitching Etude"]

            self.song1 = tk.StringVar(value="Honor March")
            self.brd_combo2 = ttk.Combobox(self.brd_frame, values=self.song_list + ["None"], textvariable=self.song1,state="readonly")
            self.brd_combo2.grid(row=2,column=0,sticky="nw",padx=0,pady=2)
            self.brd_combo2.bind('<<ComboboxSelected>>', lambda event, entry="song1": self.select_song(entry))

            self.song2 = tk.StringVar(value="Victory March")
            self.brd_combo3 = ttk.Combobox(self.brd_frame, values=[k for k in self.song_list if k not in [self.song1.get()]] + ["None"], textvariable=self.song2,state="readonly")
            self.brd_combo3.grid(row=3,column=0,sticky="nw",padx=0,pady=2)
            self.brd_combo3.bind('<<ComboboxSelected>>', lambda event, entry="song2": self.select_song(entry))

            self.song3 = tk.StringVar(value="Minuet V")
            self.brd_combo4 = ttk.Combobox(self.brd_frame, values=[k for k in self.song_list if k not in [self.song1.get(),self.song2.get()]] + ["None"], textvariable=self.song3,state="readonly")
            self.brd_combo4.grid(row=4,column=0,sticky="nw",padx=0,pady=2)
            self.brd_combo4.bind('<<ComboboxSelected>>', lambda event, entry="song3": self.select_song(entry))

            self.song4 = tk.StringVar(value="Minuet IV")
            self.brd_combo5 = ttk.Combobox(self.brd_frame, values=[k for k in self.song_list if k not in [self.song1.get(),self.song2.get(),self.song3.get(),]] + ["None"], textvariable=self.song4,state="readonly")
            self.brd_combo5.grid(row=5,column=0,sticky="nw",padx=0,pady=2)
            self.brd_combo5.bind('<<ComboboxSelected>>', lambda event, entry="song4": self.select_song(entry))

            self.song5 = tk.StringVar(value="None")
            self.brd_combo6 = ttk.Combobox(self.brd_frame, values=[k for k in self.song_list if k not in [self.song1.get(),self.song2.get(),self.song3.get(),self.song4.get()]] + ["None"], textvariable=self.song5,state="readonly")
            self.brd_combo6.grid(row=6,column=0,sticky="nw",padx=0,pady=2)
            self.brd_combo6.bind('<<ComboboxSelected>>', lambda event, entry="song5": self.select_song(entry))

            self.marcato_on = tk.BooleanVar(value=False)
            self.marcato_cbox = ttk.Checkbutton(self.brd_frame,variable=self.marcato_on, text="Marcato",command=lambda trigger="marcato": self.update_buff_cboxes(trigger))
            # self.marcato_cbox.state(['!alternate']) 
            self.marcato_cbox.configure(state="disabled")
            self.marcato_cbox.grid(row=7,column=0,sticky="nw",padx=0,pady=2)

            self.soulvoice_on = tk.BooleanVar(value=False)
            self.soul_voice_cbox = ttk.Checkbutton(self.brd_frame,variable=self.soulvoice_on,text="Soul Voice",command=lambda trigger="soulvoice": self.update_buff_cboxes(trigger))
            # self.soul_voice_cbox.state(['!alternate']) 
            self.soul_voice_cbox.configure(state="disabled")
            self.soul_voice_cbox.grid(row=8,column=0,sticky="nw",padx=0,pady=2)

        if True:
            self.cor_frame = ttk.Frame(self.buffs_frame,width=165,height=250)
            self.cor_frame.grid(row=0,column=2,padx=15,pady=0,sticky="n")

            self.cor_on = tk.BooleanVar(value=False)
            self.cor_cbox = ttk.Checkbutton(self.cor_frame,variable=self.cor_on,text="Rolls",command=lambda trigger="cor": self.update_buff_cboxes(trigger))
            # self.cor_cbox.state(['!alternate']) 
            self.cor_cbox.grid(row=0,column=0,sticky="nw",padx=0,pady=2)
            self.cor_potency = tk.StringVar(value="Rolls +7")
            self.cor_combo1 = ttk.Combobox(self.cor_frame, values=["Rolls +8","Rolls +7","Rolls +6","Rolls +5","Rolls +3","Rolls +0"], textvariable=self.cor_potency,state="readonly",width=15)
            self.cor_combo1.grid(row=1,column=0,pady=2)

            self.roll_list = sorted(["Chaos", "Fighter's", "Hunter's", "Rogue's", "Samurai", "Wizard's", "Warlock's", "Monk's", "Tactician's"]) + ["None"]

            self.roll1_frame = ttk.Frame(self.cor_frame)
            self.roll1_frame.grid(row=2,column=0,padx=0,pady=2)
            self.roll1_value = tk.StringVar(value="XI")
            self.roll1vbox = ttk.Combobox(self.roll1_frame, values=["I","II","III","IV","V","VI","VII","VIII","IX","X","XI"],textvariable=self.roll1_value,state="readonly",width=3)
            self.roll1vbox.grid(row=0,column=0,padx=1,pady=1)
            self.roll1 = tk.StringVar(value="Chaos")
            self.roll1_combo = ttk.Combobox(self.roll1_frame,values=self.roll_list,textvariable=self.roll1,state="readonly",width=10)
            self.roll1_combo.grid(row=0,column=1,padx=1,pady=2,sticky="nw")
            self.roll1_combo.bind('<<ComboboxSelected>>', lambda event, entry="roll1": self.select_roll(entry))

            self.roll2_frame = ttk.Frame(self.cor_frame)
            self.roll2_frame.grid(row=3,column=0,padx=0,pady=0)
            self.roll2_value = tk.StringVar(value="XI")
            self.roll2vbox = ttk.Combobox(self.roll2_frame, values=["I","II","III","IV","V","VI","VII","VIII","IX","X","XI"],textvariable=self.roll2_value,state="readonly",width=3)
            self.roll2vbox.grid(row=0,column=0,padx=1,pady=1)
            self.roll2 = tk.StringVar(value="Samurai")
            self.roll2_combo = ttk.Combobox(self.roll2_frame,values=self.roll_list,textvariable=self.roll2,state="readonly",width=10)
            self.roll2_combo.grid(row=0,column=1,padx=1,pady=2,sticky="nw")
            self.roll2_combo.bind('<<ComboboxSelected>>', lambda event, entry="roll2": self.select_roll(entry))

            self.job_bonus = tk.BooleanVar(value=False)
            self.cor_jobbonus_cbox = ttk.Checkbutton(self.cor_frame,variable=self.job_bonus,text="Job Bonus",)
            # self.cor_jobbonus_cbox.state(['!alternate']) 
            self.cor_jobbonus_cbox.configure(state="disabled")
            self.cor_jobbonus_cbox.grid(row=4,column=0,sticky="nw",padx=0,pady=2)


            self.crooked_on = tk.BooleanVar(value=False)
            self.crooked_cbox = ttk.Checkbutton(self.cor_frame,variable=self.crooked_on,text="Crooked Cards",)
            # self.crooked_cbox.state(['!alternate']) 
            self.crooked_cbox.configure(state="disabled")
            self.crooked_cbox.grid(row=5,column=0,sticky="nw",padx=0,pady=2)


            self.lightshot_on = tk.BooleanVar(value=False)
            self.lightshot_cbox = ttk.Checkbutton(self.cor_frame,variable=self.lightshot_on,text="Light Shot",)
            # self.lightshot_cbox.state(['!alternate']) 
            self.lightshot_cbox.configure(state="disabled")
            self.lightshot_cbox.grid(row=6,column=0,sticky="nw",padx=0,pady=2)



        if True:
            self.geo_frame = ttk.Frame(self.buffs_frame,width=165,height=250)
            self.geo_frame.grid(row=0,column=3,padx=15,pady=0,sticky="n")

            self.geomancy_spells = ["Acumen", "Fury", "Precision", "Focus", "Haste", "STR", "DEX", "VIT", "AGI", "INT", "MND", "CHR", "Frailty", "Torpor", "Malaise", "Languor"]
            self.geo_on = tk.BooleanVar(value=False)
            self.geo_cbox = ttk.Checkbutton(self.geo_frame,variable=self.geo_on,text="Geomancy",command=lambda trigger="geo": self.update_buff_cboxes(trigger))
            # self.geo_cbox.state(['!alternate']) 
            self.geo_cbox.grid(row=0,column=0,sticky="nw",pady=2)
            self.geo_potency = tk.StringVar(value="Geomancy +6")
            self.geo_combo1 = ttk.Combobox(self.geo_frame, values=["Geomancy +10","Geomancy +7","Geomancy +6","Geomancy +5","Geomancy +0"], textvariable=self.geo_potency,state="readonly")
            self.geo_combo1.grid(row=1,column=0,pady=2)

            self.indispell = tk.StringVar(value="Indi-Fury")
            self.geo_indi = ttk.Combobox(self.geo_frame, values=[f"Indi-{k}" for k in self.geomancy_spells] + ["None"], textvariable=self.indispell,state="readonly")
            self.geo_indi.grid(row=2,column=0,sticky="nw",padx=0,pady=2)
            self.geo_indi.bind('<<ComboboxSelected>>', lambda event, entry="indi": self.select_bubble(entry))

            self.geospell = tk.StringVar(value="Geo-Frailty")
            self.geo_geo = ttk.Combobox(self.geo_frame, values=[f"Geo-{k}" for k in self.geomancy_spells] + ["None"], textvariable=self.geospell,state="readonly")
            self.geo_geo.grid(row=3,column=0,sticky="nw",padx=0,pady=2)
            self.geo_geo.bind('<<ComboboxSelected>>', lambda event, entry="geo": self.select_bubble(entry))

            self.entrustspell = tk.StringVar(value="Entrust-STR")
            self.geo_entrust = ttk.Combobox(self.geo_frame, values=[f"Entrust-{k}" for k in self.geomancy_spells] + ["None"], textvariable=self.entrustspell,state="readonly")
            self.geo_entrust.grid(row=4,column=0,sticky="nw",padx=0,pady=2)
            self.geo_entrust.bind('<<ComboboxSelected>>', lambda event, entry="entrust": self.select_bubble(entry))

            self.bog_on = tk.BooleanVar(value=False)
            self.blaze_of_glory_cbox = ttk.Checkbutton(self.geo_frame,variable=self.bog_on,text="Blaze of Glory",command=lambda trigger="bog": self.update_buff_cboxes(trigger))
            # self.blaze_of_glory_cbox.state(['!alternate']) 
            self.blaze_of_glory_cbox.configure(state="disabled")
            self.blaze_of_glory_cbox.grid(row=5,column=0,sticky="nw",padx=0,pady=2)

            self.bolster_on = tk.BooleanVar(value=False)
            self.bolster_cbox = ttk.Checkbutton(self.geo_frame,variable=self.bolster_on,text="Bolster",command=lambda trigger="bolster": self.update_buff_cboxes(trigger))
            # self.bolster_cbox.state(['!alternate']) 
            self.bolster_cbox.configure(state="disabled")
            self.bolster_cbox.grid(row=6,column=0,sticky="nw",padx=0,pady=2)

            self.geo_potency_frame = ttk.Frame(self.geo_frame)
            self.geo_potency_frame.grid(row=7,column=0,sticky="nw",pady=2)
            self.geo_potency_label = ttk.Label(self.geo_potency_frame,text="Potency: ")
            self.geo_potency_label.grid(row=0,column=0,padx=0,pady=2)
            self.geomancy_potency = tk.IntVar(value=100)
            self.geo_potency_entry = ttk.Entry(self.geo_potency_frame,textvariable=self.geomancy_potency,width=8)
            self.geo_potency_tip = Hovertip(self.geo_potency_entry,f"Geomancy potency for enfeeble-based bubbles.\nEnhancing-based bubbles will remain at 100% potency.",hover_delay=500)
            self.geo_potency_entry.grid(row=0,column=1,sticky="ne",padx=0,pady=2)

# =============================================================================================================================
# =============================================================================================================================
#  Frame 3: Contains the equipped armor, quicklook buttons, and a radio list to equip new armor
# =============================================================================================================================
# =============================================================================================================================

        if not self.horizontal:

            # self.equipment_frame = ttk.LabelFrame(self,borderwidth=3,width=676,height=350,text="Main Frame3")
            self.equipment_frame = ttk.Frame(self.inputs_tab,width=676,height=350)
            self.equipment_frame.grid_propagate(0)
            self.equipment_frame.grid(row=2, column=0, padx=2, pady=0, sticky="w")
        else:
            self.quicklook_tab = ttk.Frame(self.notebook)
            self.notebook.add(self.quicklook_tab, text="Quicklook")
            self.equipment_frame = ttk.Frame(self.quicklook_tab,width=676,height=350)
            self.equipment_frame.grid_propagate(0)
            self.equipment_frame.grid(row=0, column=0, padx=2, pady=0, sticky="w")


        # self.frame3.grid_propagate(0)
        self.frame31 = ttk.LabelFrame(self.equipment_frame,borderwidth=3,width=250,height=350,text="  Equipped Items  ")
        # self.frame31 = ttk.Frame(self.equipment_frame,width=250,height=340)
        self.frame31.grid(row=0, column=0, padx=0, pady=0, sticky="w")
        self.frame31.grid_propagate(0)
        self.frame31.grid_columnconfigure((0),weight=1) # Column 0 expands in the horizontal direction to fill blank space, effectively centering column1 in the frame. Weight=1 is how fast it expands; 2 is twice as fast, but it's all relative so no reason to change it with only one column

        if True:
            self.main_img = self.item2image(self.equipped_gear["main"]["Name"])
            self.sub_img = self.item2image(self.equipped_gear["sub"]["Name"])
            self.ranged_img = self.item2image(self.equipped_gear["ranged"]["Name"])
            self.ammo_img = self.item2image(self.equipped_gear["ammo"]["Name"])
            self.head_img = self.item2image(self.equipped_gear["head"]["Name"])
            self.neck_img = self.item2image(self.equipped_gear["neck"]["Name"])
            self.ear1_img = self.item2image(self.equipped_gear["ear1"]["Name"])
            self.ear2_img = self.item2image(self.equipped_gear["ear2"]["Name"])
            self.body_img = self.item2image(self.equipped_gear["body"]["Name"])
            self.hands_img = self.item2image(self.equipped_gear["hands"]["Name"])
            self.ring1_img = self.item2image(self.equipped_gear["ring1"]["Name"])
            self.ring2_img = self.item2image(self.equipped_gear["ring2"]["Name"])
            self.back_img = self.item2image(self.equipped_gear["back"]["Name"])
            self.waist_img = self.item2image(self.equipped_gear["waist"]["Name"])
            self.legs_img = self.item2image(self.equipped_gear["legs"]["Name"])
            self.feet_img = self.item2image(self.equipped_gear["feet"]["Name"])
            
            self.copy_set_frame = ttk.Frame(self.frame31)
            self.copy_set_frame.grid(row=0,column=0,padx=0,pady=1)

            self.copy2tp = ttk.Button(self.copy_set_frame,text="Copy to TP set",width=15)
            self.copy2tp.grid(row=2,column=0,padx=1,pady=1)
            self.copy2ws = ttk.Button(self.copy_set_frame,text="Copy to WS set",width=15)
            self.copy2ws.grid(row=2,column=1,padx=1,pady=1)
            self.export_gearswap = ttk.Button(self.copy_set_frame,text="Copy set to clipboard",width=32,command=self.export2gearswap)
            self.export_gearswap_tip = Hovertip(self.export_gearswap,"Copy the currently displayed gear to clipboard with a gearswap.lua format.",hover_delay=500)
            self.export_gearswap.grid(row=3,column=0,padx=0,pady=1,columnspan=2)
            self.copy2tp.state(["disabled"])
            self.copy2ws.state(["disabled"])

            self.eframe = ttk.Frame(self.frame31,)
            self.eframe.grid(row=1,column=0,padx=0,pady=0)

            self.button_main = ttk.Button(self.eframe, image=self.main_img, text=None,compound="image",command=lambda: self.update_radio_list(self.main_radio_frame)) # self.radio_main.tkraise()
            self.button_main.grid(row=0,column=0,padx=0,pady=0,)
            self.button_sub = ttk.Button(self.eframe, image=self.sub_img, text=None,compound="image",command=lambda: self.update_radio_list(self.sub_radio_frame))
            self.button_sub.grid(row=0,column=1,padx=0,pady=0,)
            self.button_ranged = ttk.Button(self.eframe, image=self.ranged_img, text=None,compound="image",command=lambda: self.update_radio_list(self.ranged_radio_frame))
            self.button_ranged.grid(row=0,column=2,padx=0,pady=0,)
            self.button_ammo = ttk.Button(self.eframe, image=self.ammo_img, text=None,compound="image",command=lambda: self.update_radio_list(self.ammo_radio_frame))
            self.button_ammo.grid(row=0,column=3,padx=0,pady=0,)
            # -----------------------------------
            self.button_head = ttk.Button(self.eframe, image=self.head_img, text=None,compound="image",command=lambda: self.update_radio_list(self.head_radio_frame))
            self.button_head.grid(row=1,column=0,padx=0,pady=0,)
            self.button_neck = ttk.Button(self.eframe, image=self.neck_img, text=None,compound="image",command=lambda: self.update_radio_list(self.neck_radio_frame))
            self.button_neck.grid(row=1,column=1,padx=0,pady=0,)
            self.button_ear1 = ttk.Button(self.eframe, image=self.ear1_img, text=None,compound="image",command=lambda: self.update_radio_list(self.ear1_radio_frame))
            self.button_ear1.grid(row=1,column=2,padx=0,pady=0,)
            self.button_ear2 = ttk.Button(self.eframe, image=self.ear2_img, text=None,compound="image",command=lambda: self.update_radio_list(self.ear2_radio_frame))
            self.button_ear2.grid(row=1,column=3,padx=0,pady=0,)
            # self.ear2Tip = Hovertip(self.button_ear2,"Novio Earring",hover_delay=100)
            # -----------------------------------
            self.button_body = ttk.Button(self.eframe, image=self.body_img, text=None,compound="image",command=lambda: self.update_radio_list(self.body_radio_frame))
            self.button_body.grid(row=2,column=0,padx=0,pady=0,)
            self.button_hands = ttk.Button(self.eframe, image=self.hands_img, text=None,compound="image",command=lambda: self.update_radio_list(self.hands_radio_frame))
            self.button_hands.grid(row=2,column=1,padx=0,pady=0,)
            self.button_ring1 = ttk.Button(self.eframe, image=self.ring1_img, text=None,compound="image",command=lambda: self.update_radio_list(self.ring1_radio_frame))
            self.button_ring1.grid(row=2,column=2,padx=0,pady=0,)
            self.button_ring2 = ttk.Button(self.eframe, image=self.ring2_img, text=None,compound="image",command=lambda: self.update_radio_list(self.ring2_radio_frame))
            self.button_ring2.grid(row=2,column=3,padx=0,pady=0,)
            # -----------------------------------
            self.button_back = ttk.Button(self.eframe, image=self.back_img, text=None,compound="image",command=lambda: self.update_radio_list(self.back_radio_frame))
            self.button_back.grid(row=3,column=0,padx=0,pady=0,)
            self.button_waist = ttk.Button(self.eframe, image=self.waist_img, text=None,compound="image",command=lambda: self.update_radio_list(self.waist_radio_frame))
            self.button_waist.grid(row=3,column=1,padx=0,pady=0,)
            self.button_legs = ttk.Button(self.eframe, image=self.legs_img, text=None,compound="image",command=lambda: self.update_radio_list(self.legs_radio_frame))
            self.button_legs.grid(row=3,column=2,padx=0,pady=0,)
            self.button_feet = ttk.Button(self.eframe, image=self.feet_img, text=None,compound="image",command=lambda: self.update_radio_list(self.feet_radio_frame))
            self.button_feet.grid(row=3,column=3,padx=0,pady=0,)

            self.quickframe = ttk.Frame(self.frame31)
            self.quickframe.grid(row=2,column=0,padx=0,pady=0)

            self.quick_ws = ttk.Button(self.quickframe,text="Quicklook WS",width=15,command=lambda trigger="quicklook ws": self.run_optimize(trigger))
            self.quick_ws.grid(row=0,column=0,padx=1,pady=1)
            self.quick_spell = ttk.Button(self.quickframe,text="Quicklook spell",width=15,command=lambda trigger="quicklook spell": self.run_optimize(trigger))
            self.quick_spell.grid(row=0,column=1,padx=1,pady=1)
            self.quick_tp = ttk.Button(self.quickframe,text="Quicklook TP",width=15,command=lambda trigger="quicklook tp": self.run_optimize(trigger))
            self.quick_tp.grid(row=1,column=0,padx=1,pady=1)
            self.quick_stats = ttk.Button(self.quickframe,text="Show stats",width=15,command=lambda trigger="stats": self.run_optimize(trigger))
            self.quick_stats.grid(row=1,column=1,padx=1,pady=1)

            self.quickdamage_frame = ttk.Frame(self.frame31)
            self.quickdamage_frame.grid(row=3,column=0,padx=0,pady=5)

            self.quickdamage = ttk.Label(self.quickdamage_frame, text=f"{'Average Damage = ':>17s}{0.0:>9.1f}",font="Courier 10")
            self.quickdamage.grid(row=0,column=0,padx=0,pady=1)
            self.quicktp = ttk.Label(self.quickdamage_frame, text=f"{'Average TP = ':>17s}{0.0:>9.1f}",font="Courier 10")
            self.quicktp.grid(row=1,column=0,padx=0,pady=1)

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================

        # This frame holds all of the LabelFrames (one for each slot)
        self.radio_frame = ttk.Frame(self.equipment_frame,borderwidth=3,width=310)
        self.radio_frame.grid(row=0, column=1, padx=0, pady=0, sticky="n")

# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.main_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select main  ")
        self.main_radio_frame.pack(fill=tk.BOTH, expand=1)

        # Scrollable base frame for the main-hand slot
        self.main_scrollframe = ttk.Frame(self.main_radio_frame)
        self.main_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The main-hand canvas
        self.main_canvas = tk.Canvas(self.main_scrollframe,height=320,width=390)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.main_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.main_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.main_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.main_canvas)) 

        self.main_radio_scrollbar = ttk.Scrollbar(self.main_scrollframe, orient=tk.VERTICAL, command=self.main_canvas.yview)
        self.main_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_canvas.configure(yscrollcommand=self.main_radio_scrollbar.set)
        self.main_canvas.bind("<Configure>", lambda event: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.radio_main = ttk.Frame(self.main_canvas)
        self.update_buttons("main")
        self.x_main = [] # List to contain all of the individual radio button widgets for the main slot
        for n,k in enumerate(sorted(mains, key=lambda d: d["Name2"])):
            self.x_main.append(ttk.Radiobutton(self.radio_main, text=k["Name2"], value=k, variable=self.selected_main,command=lambda: self.update_buttons("main"))) # width=-60  sets the MINIMUM text length at 60 average font characters
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_main[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.main_canvas.create_window((0,0),window=self.radio_main, anchor="nw")




# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text
        self.sub_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select sub  ")
        self.sub_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.sub_radio_frame.pack_forget()

        # Scrollable base frame for the sub-hand slot
        self.sub_scrollframe = ttk.Frame(self.sub_radio_frame)
        self.sub_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The sub-hand canvas
        self.sub_canvas = tk.Canvas(self.sub_scrollframe,height=320,width=390)
        self.sub_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.sub_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.sub_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.sub_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.sub_canvas)) 

        self.sub_radio_scrollbar = ttk.Scrollbar(self.sub_scrollframe, orient=tk.VERTICAL, command=self.sub_canvas.yview)
        self.sub_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sub_canvas.configure(yscrollcommand=self.sub_radio_scrollbar.set)
        self.sub_canvas.bind("<Configure>", lambda event: self.sub_canvas.configure(scrollregion=self.sub_canvas.bbox("all")))


        self.radio_sub = ttk.Frame(self.sub_canvas)
        self.update_buttons("sub")
        self.x_sub = []
        for n,k in enumerate(sorted(subs+grips, key=lambda d: d["Name2"])):
            self.x_sub.append(ttk.Radiobutton(self.radio_sub, text=k["Name2"], value=k, variable=self.selected_sub,command=lambda: self.update_buttons("sub")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_sub[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.sub_canvas.create_window((0,0),window=self.radio_sub, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text
        self.ranged_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select ranged  ")
        self.ranged_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.ranged_radio_frame.pack_forget()

        # Scrollable base frame for the ranged-hand slot
        self.ranged_scrollframe = ttk.Frame(self.ranged_radio_frame)
        self.ranged_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The ranged-hand canvas
        self.ranged_canvas = tk.Canvas(self.ranged_scrollframe,height=320,width=390)
        self.ranged_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.ranged_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.ranged_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.ranged_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.ranged_canvas)) 

        self.ranged_radio_scrollbar = ttk.Scrollbar(self.ranged_scrollframe, orient=tk.VERTICAL, command=self.ranged_canvas.yview)
        self.ranged_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ranged_canvas.configure(yscrollcommand=self.ranged_radio_scrollbar.set)
        self.ranged_canvas.bind("<Configure>", lambda event: self.ranged_canvas.configure(scrollregion=self.ranged_canvas.bbox("all")))


        self.radio_ranged = ttk.Frame(self.ranged_canvas)
        self.update_buttons("ranged")
        self.x_ranged = []
        for n,k in enumerate(sorted(ranged, key=lambda d: d["Name2"])):
            self.x_ranged.append(ttk.Radiobutton(self.radio_ranged, text=k["Name2"], value=k, variable=self.selected_ranged,command=lambda: self.update_buttons("ranged")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_ranged[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.ranged_canvas.create_window((0,0),window=self.radio_ranged, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text
        self.ammo_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select ammo  ")
        self.ammo_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.ammo_radio_frame.pack_forget()

        # Scrollable base frame for the ammo-hand slot
        self.ammo_scrollframe = ttk.Frame(self.ammo_radio_frame)
        self.ammo_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The ammo-hand canvas
        self.ammo_canvas = tk.Canvas(self.ammo_scrollframe,height=320,width=390)
        self.ammo_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.ammo_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.ammo_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.ammo_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.ammo_canvas)) 

        self.ammo_radio_scrollbar = ttk.Scrollbar(self.ammo_scrollframe, orient=tk.VERTICAL, command=self.ammo_canvas.yview)
        self.ammo_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ammo_canvas.configure(yscrollcommand=self.ammo_radio_scrollbar.set)
        self.ammo_canvas.bind("<Configure>", lambda event: self.ammo_canvas.configure(scrollregion=self.ammo_canvas.bbox("all")))


        self.radio_ammo = ttk.Frame(self.ammo_canvas)
        self.update_buttons("ammo")
        self.x_ammo = []
        for n,k in enumerate(sorted(ammos, key=lambda d: d["Name2"])):
            self.x_ammo.append(ttk.Radiobutton(self.radio_ammo, text=k["Name2"], value=k, variable=self.selected_ammo,command=lambda: self.update_buttons("ammo")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_ammo[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.ammo_canvas.create_window((0,0),window=self.radio_ammo, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text
        self.head_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select head  ")
        self.head_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.head_radio_frame.pack_forget()

        # Scrollable base frame for the head-hand slot
        self.head_scrollframe = ttk.Frame(self.head_radio_frame)
        self.head_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The head-hand canvas
        self.head_canvas = tk.Canvas(self.head_scrollframe,height=320,width=390)
        self.head_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.head_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.head_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.head_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.head_canvas)) 

        self.head_radio_scrollbar = ttk.Scrollbar(self.head_scrollframe, orient=tk.VERTICAL, command=self.head_canvas.yview)
        self.head_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.head_canvas.configure(yscrollcommand=self.head_radio_scrollbar.set)
        self.head_canvas.bind("<Configure>", lambda event: self.head_canvas.configure(scrollregion=self.head_canvas.bbox("all")))


        self.radio_head = ttk.Frame(self.head_canvas)
        self.update_buttons("head")
        self.x_head = []
        for n,k in enumerate(sorted(heads, key=lambda d: d["Name2"])):
            self.x_head.append(ttk.Radiobutton(self.radio_head, text=k["Name2"], value=k, variable=self.selected_head,command=lambda: self.update_buttons("head")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_head[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.head_canvas.create_window((0,0),window=self.radio_head, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text
        self.neck_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select neck  ")
        self.neck_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.neck_radio_frame.pack_forget()

        # Scrollable base frame for the neck-hand slot
        self.neck_scrollframe = ttk.Frame(self.neck_radio_frame)
        self.neck_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The neck-hand canvas
        self.neck_canvas = tk.Canvas(self.neck_scrollframe,height=320,width=390)
        self.neck_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.neck_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.neck_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.neck_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.neck_canvas)) 

        self.neck_radio_scrollbar = ttk.Scrollbar(self.neck_scrollframe, orient=tk.VERTICAL, command=self.neck_canvas.yview)
        self.neck_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.neck_canvas.configure(yscrollcommand=self.neck_radio_scrollbar.set)
        self.neck_canvas.bind("<Configure>", lambda event: self.neck_canvas.configure(scrollregion=self.neck_canvas.bbox("all")))


        self.radio_neck = ttk.Frame(self.neck_canvas)
        self.update_buttons("neck")
        self.x_neck = []
        for n,k in enumerate(sorted(necks, key=lambda d: d["Name2"])):
            self.x_neck.append(ttk.Radiobutton(self.radio_neck, text=k["Name2"], value=k, variable=self.selected_neck,command=lambda: self.update_buttons("neck")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_neck[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.neck_canvas.create_window((0,0),window=self.radio_neck, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text
        self.ear1_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select ear1  ")
        self.ear1_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.ear1_radio_frame.pack_forget()

        # Scrollable base frame for the ear1-hand slot
        self.ear1_scrollframe = ttk.Frame(self.ear1_radio_frame)
        self.ear1_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The ear1-hand canvas
        self.ear1_canvas = tk.Canvas(self.ear1_scrollframe,height=320,width=390)
        self.ear1_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.ear1_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.ear1_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.ear1_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.ear1_canvas)) 

        self.ear1_radio_scrollbar = ttk.Scrollbar(self.ear1_scrollframe, orient=tk.VERTICAL, command=self.ear1_canvas.yview)
        self.ear1_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ear1_canvas.configure(yscrollcommand=self.ear1_radio_scrollbar.set)
        self.ear1_canvas.bind("<Configure>", lambda event: self.ear1_canvas.configure(scrollregion=self.ear1_canvas.bbox("all")))


        self.radio_ear1 = ttk.Frame(self.ear1_canvas)
        self.update_buttons("ear1")
        self.x_ear1 = []
        for n,k in enumerate(sorted(ears, key=lambda d: d["Name2"])):
            self.x_ear1.append(ttk.Radiobutton(self.radio_ear1, text=k["Name2"], value=k, variable=self.selected_ear1,command=lambda: self.update_buttons("ear1")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_ear1[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.ear1_canvas.create_window((0,0),window=self.radio_ear1, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text
        self.ear2_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select ear2  ")
        self.ear2_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.ear2_radio_frame.pack_forget()

        # Scrollable base frame for the ear2-hand slot
        self.ear2_scrollframe = ttk.Frame(self.ear2_radio_frame)
        self.ear2_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The ear2-hand canvas
        self.ear2_canvas = tk.Canvas(self.ear2_scrollframe,height=320,width=390)
        self.ear2_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.ear2_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.ear2_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.ear2_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.ear2_canvas)) 

        self.ear2_radio_scrollbar = ttk.Scrollbar(self.ear2_scrollframe, orient=tk.VERTICAL, command=self.ear2_canvas.yview)
        self.ear2_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ear2_canvas.configure(yscrollcommand=self.ear2_radio_scrollbar.set)
        self.ear2_canvas.bind("<Configure>", lambda event: self.ear2_canvas.configure(scrollregion=self.ear2_canvas.bbox("all")))


        self.radio_ear2 = ttk.Frame(self.ear2_canvas)
        self.update_buttons("ear2")
        self.x_ear2 = []
        for n,k in enumerate(sorted(ears2, key=lambda d: d["Name2"])):
            self.x_ear2.append(ttk.Radiobutton(self.radio_ear2, text=k["Name2"], value=k, variable=self.selected_ear2,command=lambda: self.update_buttons("ear2")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_ear2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.ear2_canvas.create_window((0,0),window=self.radio_ear2, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text
        self.body_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select body  ")
        self.body_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.body_radio_frame.pack_forget()

        # Scrollable base frame for the body-hand slot
        self.body_scrollframe = ttk.Frame(self.body_radio_frame)
        self.body_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The body-hand canvas
        self.body_canvas = tk.Canvas(self.body_scrollframe,height=320,width=390)
        self.body_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.body_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.body_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.body_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.body_canvas)) 

        self.body_radio_scrollbar = ttk.Scrollbar(self.body_scrollframe, orient=tk.VERTICAL, command=self.body_canvas.yview)
        self.body_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.body_canvas.configure(yscrollcommand=self.body_radio_scrollbar.set)
        self.body_canvas.bind("<Configure>", lambda event: self.body_canvas.configure(scrollregion=self.body_canvas.bbox("all")))


        self.radio_body = ttk.Frame(self.body_canvas)
        self.update_buttons("body")
        self.x_body = []
        for n,k in enumerate(sorted(bodies, key=lambda d: d["Name2"])):
            self.x_body.append(ttk.Radiobutton(self.radio_body, text=k["Name2"], value=k, variable=self.selected_body,command=lambda: self.update_buttons("body")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_body[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.body_canvas.create_window((0,0),window=self.radio_body, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text
        self.hands_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select hands  ")
        self.hands_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.hands_radio_frame.pack_forget()

        # Scrollable base frame for the hands-hand slot
        self.hands_scrollframe = ttk.Frame(self.hands_radio_frame)
        self.hands_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The hands-hand canvas
        self.hands_canvas = tk.Canvas(self.hands_scrollframe,height=320,width=390)
        self.hands_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.hands_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.hands_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.hands_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.hands_canvas)) 

        self.hands_radio_scrollbar = ttk.Scrollbar(self.hands_scrollframe, orient=tk.VERTICAL, command=self.hands_canvas.yview)
        self.hands_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hands_canvas.configure(yscrollcommand=self.hands_radio_scrollbar.set)
        self.hands_canvas.bind("<Configure>", lambda event: self.hands_canvas.configure(scrollregion=self.hands_canvas.bbox("all")))


        self.radio_hands = ttk.Frame(self.hands_canvas)
        self.update_buttons("hands")
        self.x_hands = []
        for n,k in enumerate(sorted(hands, key=lambda d: d["Name2"])):
            self.x_hands.append(ttk.Radiobutton(self.radio_hands, text=k["Name2"], value=k, variable=self.selected_hands,command=lambda: self.update_buttons("hands")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_hands[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.hands_canvas.create_window((0,0),window=self.radio_hands, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text
        self.ring1_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select ring1  ")
        self.ring1_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.ring1_radio_frame.pack_forget()

        # Scrollable base frame for the ring1-hand slot
        self.ring1_scrollframe = ttk.Frame(self.ring1_radio_frame)
        self.ring1_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The ring1-hand canvas
        self.ring1_canvas = tk.Canvas(self.ring1_scrollframe,height=320,width=390)
        self.ring1_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.ring1_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.ring1_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.ring1_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.ring1_canvas)) 

        self.ring1_radio_scrollbar = ttk.Scrollbar(self.ring1_scrollframe, orient=tk.VERTICAL, command=self.ring1_canvas.yview)
        self.ring1_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ring1_canvas.configure(yscrollcommand=self.ring1_radio_scrollbar.set)
        self.ring1_canvas.bind("<Configure>", lambda event: self.ring1_canvas.configure(scrollregion=self.ring1_canvas.bbox("all")))


        self.radio_ring1 = ttk.Frame(self.ring1_canvas)
        self.update_buttons("ring1")
        self.x_ring1 = []
        for n,k in enumerate(sorted(rings, key=lambda d: d["Name2"])):
            self.x_ring1.append(ttk.Radiobutton(self.radio_ring1, text=k["Name2"], value=k, variable=self.selected_ring1,command=lambda: self.update_buttons("ring1")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_ring1[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.ring1_canvas.create_window((0,0),window=self.radio_ring1, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text
        self.ring2_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select ring2  ")
        self.ring2_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.ring2_radio_frame.pack_forget()

        # Scrollable base frame for the ring2-hand slot
        self.ring2_scrollframe = ttk.Frame(self.ring2_radio_frame)
        self.ring2_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The ring2-hand canvas
        self.ring2_canvas = tk.Canvas(self.ring2_scrollframe,height=320,width=390)
        self.ring2_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.ring2_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.ring2_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.ring2_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.ring2_canvas)) 

        self.ring2_radio_scrollbar = ttk.Scrollbar(self.ring2_scrollframe, orient=tk.VERTICAL, command=self.ring2_canvas.yview)
        self.ring2_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ring2_canvas.configure(yscrollcommand=self.ring2_radio_scrollbar.set)
        self.ring2_canvas.bind("<Configure>", lambda event: self.ring2_canvas.configure(scrollregion=self.ring2_canvas.bbox("all")))


        self.radio_ring2 = ttk.Frame(self.ring2_canvas)
        self.update_buttons("ring2")
        self.x_ring2 = []
        for n,k in enumerate(sorted(rings2, key=lambda d: d["Name2"])):
            self.x_ring2.append(ttk.Radiobutton(self.radio_ring2, text=k["Name2"], value=k, variable=self.selected_ring2,command=lambda: self.update_buttons("ring2")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_ring2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.ring2_canvas.create_window((0,0),window=self.radio_ring2, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text
        self.back_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select back  ")
        self.back_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.back_radio_frame.pack_forget()

        # Scrollable base frame for the back-hand slot
        self.back_scrollframe = ttk.Frame(self.back_radio_frame)
        self.back_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The back-hand canvas
        self.back_canvas = tk.Canvas(self.back_scrollframe,height=320,width=390)
        self.back_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.back_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.back_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.back_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.back_canvas)) 

        self.back_radio_scrollbar = ttk.Scrollbar(self.back_scrollframe, orient=tk.VERTICAL, command=self.back_canvas.yview)
        self.back_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.back_canvas.configure(yscrollcommand=self.back_radio_scrollbar.set)
        self.back_canvas.bind("<Configure>", lambda event: self.back_canvas.configure(scrollregion=self.back_canvas.bbox("all")))


        self.radio_back = ttk.Frame(self.back_canvas)
        self.update_buttons("back")
        self.x_back = []
        for n,k in enumerate(sorted(capes, key=lambda d: d["Name2"])):
            self.x_back.append(ttk.Radiobutton(self.radio_back, text=k["Name2"], value=k, variable=self.selected_back,command=lambda: self.update_buttons("back")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_back[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.back_canvas.create_window((0,0),window=self.radio_back, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text
        self.waist_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select waist  ")
        self.waist_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.waist_radio_frame.pack_forget()

        # Scrollable base frame for the waist-hand slot
        self.waist_scrollframe = ttk.Frame(self.waist_radio_frame)
        self.waist_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The waist-hand canvas
        self.waist_canvas = tk.Canvas(self.waist_scrollframe,height=320,width=390)
        self.waist_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.waist_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.waist_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.waist_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.waist_canvas)) 

        self.waist_radio_scrollbar = ttk.Scrollbar(self.waist_scrollframe, orient=tk.VERTICAL, command=self.waist_canvas.yview)
        self.waist_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.waist_canvas.configure(yscrollcommand=self.waist_radio_scrollbar.set)
        self.waist_canvas.bind("<Configure>", lambda event: self.waist_canvas.configure(scrollregion=self.waist_canvas.bbox("all")))


        self.radio_waist = ttk.Frame(self.waist_canvas)
        self.update_buttons("waist")
        self.x_waist = []
        for n,k in enumerate(sorted(waists, key=lambda d: d["Name2"])):
            self.x_waist.append(ttk.Radiobutton(self.radio_waist, text=k["Name2"], value=k, variable=self.selected_waist,command=lambda: self.update_buttons("waist")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_waist[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.waist_canvas.create_window((0,0),window=self.radio_waist, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        self.legs_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select legs  ")
        self.legs_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.legs_radio_frame.pack_forget()

        # Scrollable base frame for the legs-hand slot
        self.legs_scrollframe = ttk.Frame(self.legs_radio_frame)
        self.legs_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The legs-hand canvas
        self.legs_canvas = tk.Canvas(self.legs_scrollframe,height=320,width=390)
        self.legs_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.legs_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.legs_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.legs_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.legs_canvas)) 

        self.legs_radio_scrollbar = ttk.Scrollbar(self.legs_scrollframe, orient=tk.VERTICAL, command=self.legs_canvas.yview)
        self.legs_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.legs_canvas.configure(yscrollcommand=self.legs_radio_scrollbar.set)
        self.legs_canvas.bind("<Configure>", lambda event: self.legs_canvas.configure(scrollregion=self.legs_canvas.bbox("all")))


        self.radio_legs = ttk.Frame(self.legs_canvas)
        self.update_buttons("legs")
        self.x_legs = []
        for n,k in enumerate(sorted(legs, key=lambda d: d["Name2"])):
            self.x_legs.append(ttk.Radiobutton(self.radio_legs, text=k["Name2"], value=k, variable=self.selected_legs,command=lambda: self.update_buttons("legs")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_legs[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.legs_canvas.create_window((0,0),window=self.radio_legs, anchor="nw")
# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        self.feet_radio_frame = ttk.LabelFrame(self.radio_frame, text="  select feet  ")
        self.feet_radio_frame.pack(fill=tk.BOTH, expand=1)
        self.feet_radio_frame.pack_forget()

        # Scrollable base frame for the feet-hand slot
        self.feet_scrollframe = ttk.Frame(self.feet_radio_frame)
        self.feet_scrollframe.pack(fill=tk.BOTH, expand=1)

        # The feet-hand canvas
        self.feet_canvas = tk.Canvas(self.feet_scrollframe,height=320,width=390)
        self.feet_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.feet_scrollframe.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.feet_canvas)) # We must mouse-over the scrollable frame to use the mousewheel
        self.feet_scrollframe.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.feet_canvas)) 

        self.feet_radio_scrollbar = ttk.Scrollbar(self.feet_scrollframe, orient=tk.VERTICAL, command=self.feet_canvas.yview)
        self.feet_radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.feet_canvas.configure(yscrollcommand=self.feet_radio_scrollbar.set)
        self.feet_canvas.bind("<Configure>", lambda event: self.feet_canvas.configure(scrollregion=self.feet_canvas.bbox("all")))


        self.radio_feet = ttk.Frame(self.feet_canvas)
        self.update_buttons("feet")
        self.x_feet = []
        for n,k in enumerate(sorted(feet, key=lambda d: d["Name2"])):
            self.x_feet.append(ttk.Radiobutton(self.radio_feet, text=k["Name2"], value=k, variable=self.selected_feet,command=lambda: self.update_buttons("feet")))
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_feet[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.feet_canvas.create_window((0,0),window=self.radio_feet, anchor="nw")
# ====================================================================================================================================================================================




        self.frame4 = ttk.Frame(self.select_gear_tab,width=676,height=650)
        self.frame4.grid_propagate(0)
        self.frame4.grid(row=0, column=0, padx=2, pady=0)
        self.frame4.grid_columnconfigure((0,1),weight=1) # Column 0 expands in the horizontal direction to fill blank space, effectively centering column1 in the frame. Weight=1 is how fast it expands; 2 is twice as fast, but it's all relative so no reason to change it with only one column
        self.frame4.grid_rowconfigure((0,1),weight=1) # Column 0 expands in the horizontal direction to fill blank space, effectively centering column1 in the frame. Weight=1 is how fast it expands; 2 is twice as fast, but it's all relative so no reason to change it with only one column


        self.frame41 = ttk.Frame(self.frame4,width=250,height=450,)

        self.frame41.grid(row=0, column=0, padx=0, pady=0,)
        self.frame41.grid_propagate(0)
        self.frame41.grid_columnconfigure((0,1),weight=1) # Column 0 expands in the horizontal direction to fill blank space, effectively centering column1 in the frame. Weight=1 is how fast it expands; 2 is twice as fast, but it's all relative so no reason to change it with only one column
        self.frame41.grid_rowconfigure((0,1),weight=1) # Column 0 expands in the horizontal direction to fill blank space, effectively centering column1 in the frame. Weight=1 is how fast it expands; 2 is twice as fast, but it's all relative so no reason to change it with only one column

        if True:
            self.sbframe = ttk.Frame(self.frame41)
            self.sbframe.grid(row=0,column=0,padx=0,pady=0)
            self.sbframe.grid_columnconfigure((0,1),weight=1) # Column 0 expands in the horizontal direction to fill blank space, effectively centering column1 in the frame. Weight=1 is how fast it expands; 2 is twice as fast, but it's all relative so no reason to change it with only one column
            self.sbframe.grid_rowconfigure((0,1),weight=1) # Column 0 expands in the horizontal direction to fill blank space, effectively centering column1 in the frame. Weight=1 is how fast it expands; 2 is twice as fast, but it's all relative so no reason to change it with only one column

            dim = 48
            self.dim_image = tk.PhotoImage(file=f"icons32/65537.png") # 1x1 pixel image. This allows us to define the exact pixel dimensions of TKinter buttons.

            self.button2_main = tk.Button(self.sbframe, image=self.dim_image, text="main",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.main_cbox_frame)) # self.radio_main.tkraise()
            self.button2_main.grid(row=0,column=0,padx=0,pady=0,)
            self.button2_sub = tk.Button(self.sbframe, image=self.dim_image, text="sub",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.sub_cbox_frame)) # self.radio_main.tkraise()
            self.button2_sub.grid(row=0,column=1,padx=0,pady=0,)
            self.button2_ranged = tk.Button(self.sbframe, image=self.dim_image, text="ranged",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.ranged_cbox_frame)) # self.radio_main.tkraise()
            self.button2_ranged.grid(row=0,column=2,padx=0,pady=0,)
            self.button2_ammo = tk.Button(self.sbframe, image=self.dim_image, text="ammo",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.ammo_cbox_frame)) # self.radio_main.tkraise()
            self.button2_ammo.grid(row=0,column=3,padx=0,pady=0,)

            self.button2_head = tk.Button(self.sbframe, image=self.dim_image, text="head",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.head_cbox_frame)) # self.radio_main.tkraise()
            self.button2_head.grid(row=1,column=0,padx=0,pady=0,)
            self.button2_neck = tk.Button(self.sbframe, image=self.dim_image, text="neck",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.neck_cbox_frame)) # self.radio_main.tkraise()
            self.button2_neck.grid(row=1,column=1,padx=0,pady=0,)
            self.button2_ear1 = tk.Button(self.sbframe, image=self.dim_image, text="ear1",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.ear1_cbox_frame)) # self.radio_main.tkraise()
            self.button2_ear1.grid(row=1,column=2,padx=0,pady=0,)
            self.button2_ear2 = tk.Button(self.sbframe, image=self.dim_image, text="ear2",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.ear2_cbox_frame)) # self.radio_main.tkraise()
            self.button2_ear2.grid(row=1,column=3,padx=0,pady=0,)

            self.button2_body = tk.Button(self.sbframe, image=self.dim_image, text="body",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.body_cbox_frame)) # self.radio_main.tkraise()
            self.button2_body.grid(row=2,column=0,padx=0,pady=0,)
            self.button2_hands = tk.Button(self.sbframe, image=self.dim_image, text="hands",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.hands_cbox_frame)) # self.radio_main.tkraise()
            self.button2_hands.grid(row=2,column=1,padx=0,pady=0,)
            self.button2_ring1 = tk.Button(self.sbframe, image=self.dim_image, text="ring1",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.ring1_cbox_frame)) # self.radio_main.tkraise()
            self.button2_ring1.grid(row=2,column=2,padx=0,pady=0,)
            self.button2_ring2 = tk.Button(self.sbframe, image=self.dim_image, text="ring2",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.ring2_cbox_frame)) # self.radio_main.tkraise()
            self.button2_ring2.grid(row=2,column=3,padx=0,pady=0,)

            self.button2_back = tk.Button(self.sbframe, image=self.dim_image, text="back",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.back_cbox_frame)) # self.radio_main.tkraise()
            self.button2_back.grid(row=3,column=0,padx=0,pady=0,)
            self.button2_waist = tk.Button(self.sbframe, image=self.dim_image, text="waist",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.waist_cbox_frame)) # self.radio_main.tkraise()
            self.button2_waist.grid(row=3,column=1,padx=0,pady=0,)
            self.button2_legs = tk.Button(self.sbframe, image=self.dim_image, text="legs",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.legs_cbox_frame)) # self.radio_main.tkraise()
            self.button2_legs.grid(row=3,column=2,padx=0,pady=0,)
            self.button2_feet = tk.Button(self.sbframe, image=self.dim_image, text="feet",compound=tk.CENTER,height=dim,width=dim,command=lambda: self.update_cbox_list(self.feet_cbox_frame)) # self.radio_main.tkraise()
            self.button2_feet.grid(row=3,column=3,padx=0,pady=0,)


            self.select_button_frame = ttk.Frame(self.frame41,)
            self.select_button_frame.grid(row=1,column=0,padx=0,pady=0,)

            self.selectall = tk.Button(self.select_button_frame,text="Select all",image=self.dim_image,compound=tk.CENTER,width=100,height=30,command=lambda: self.select_cboxes("select all"))
            self.selectall_tip = Hovertip(self.selectall,"Select all items in the currently displayed list.",hover_delay=500)
            self.selectall.grid(row=0,column=0,padx=1,pady=1)
            self.unselectall = tk.Button(self.select_button_frame,text="Unselect all",image=self.dim_image,compound=tk.CENTER,width=100,height=30,command=lambda: self.select_cboxes("unselect all"))
            self.unselectall_tip = Hovertip(self.unselectall,"Unselect all items in the currently displayed list.",hover_delay=500)
            self.unselectall.grid(row=0,column=1,padx=1,pady=1)
            self.selectALL = tk.Button(self.select_button_frame,text="Select ALL",image=self.dim_image,compound=tk.CENTER,width=100,height=30,command=lambda: self.select_cboxes("select ALL"))
            self.selectALL_tip = Hovertip(self.selectALL,"Select all items in all lists.",hover_delay=500)
            self.selectALL.grid(row=1,column=0,padx=1,pady=1)
            self.selectfile = tk.Button(self.select_button_frame,text="Select from\nFile",image=self.dim_image,compound=tk.CENTER,width=100,height=30,command=lambda: self.select_cboxes("select file"))
            self.selectfile_tip = Hovertip(self.selectfile,"Select all items in all lists which are present in an input file.\nInput file must use the \"//gs export all\" format.",hover_delay=500)
            self.selectfile.grid(row=1,column=1,padx=1,pady=1)

# ====================================================================================================================================================================================

        self.select_frame = ttk.Frame(self.frame41,)
        self.select_frame.grid(row=2,column=0,padx=0,pady=25)

        self.odyrank = tk.IntVar(value=30)
        self.odyrank_select = ttk.Combobox(self.select_frame, textvariable=self.odyrank,values=[30, 25, 20, 15, 0],state="readonly",width=5)
        self.odyrank_tip = Hovertip(self.odyrank_select,"Only select Odyssey equipment with this rank when using the \"Select ___\" buttons.",hover_delay=500)
        self.odyrank_select.grid(row=0,column=1,padx=0,pady=0,sticky="e")
        self.odyrank_label = ttk.Label(self.select_frame,text="Odyssey Rank", width=15)
        self.odyrank_label.grid(row=0,column=0,padx=0,pady=0,sticky="w")

        self.tvr_ring = tk.StringVar(value="Cornelia's")
        self.tvr_ring_select = ttk.Combobox(self.select_frame, textvariable=self.tvr_ring,values=["Cornelia's","Ephramad's","Fickblix's","Gurebu-Ogurebu's","Lehko Habhoka's","Medada's","Ragelise's"],state="readonly",width=20)
        self.tvr_ring_tip = Hovertip(self.tvr_ring_select,"Only select this ring when using the \"Select ___\" buttons.",hover_delay=500)
        self.tvr_ring_select.grid(row=1,column=1,padx=0,pady=0,sticky="e")
        self.tvr_ring_label = ttk.Label(self.select_frame,text="TVR Ring", width=15)
        self.tvr_ring_label.grid(row=1,column=0,padx=0,pady=0,sticky="w")




        self.conditions_frame = ttk.Frame(self.frame4,)
        self.conditions_frame.grid(row=1,column=0,padx=0,pady=0)

        self.dt_label = ttk.Label(self.conditions_frame,text="Note: Use negative values for DT sets")
        self.dt_label.grid(row=0,column=0,padx=0,pady=1,sticky='w',columnspan=2)

        self.pdt_label = ttk.Label(self.conditions_frame,text="PDT requirement:")
        self.pdt_label.grid(row=1, column=0, sticky="w", padx=0, pady=1)
        self.pdt_req = tk.StringVar(value="100")
        self.pdt_entry = ttk.Entry(self.conditions_frame,textvariable=self.pdt_req,justify="right")
        self.pdt_tip = Hovertip(self.pdt_entry,f"The automated set finder will try to find the best set that has no more PDT than this value.\nNegative values are good, positive values are bad.\nCaps at +100 to allow the set finder to function.",hover_delay=500)
        self.pdt_entry.configure(width=6)
        self.pdt_entry.grid(row=1,column=1,padx=0,pady=1,sticky='w')

        self.mdt_label = ttk.Label(self.conditions_frame,text="MDT requirement:")
        self.mdt_label.grid(row=2, column=0, sticky="w", padx=0, pady=1)
        self.mdt_req = tk.StringVar(value="100")
        self.mdt_entry = ttk.Entry(self.conditions_frame,textvariable=self.mdt_req,justify="right")
        self.mdt_tip = Hovertip(self.mdt_entry,f"The automated set finder will try to find the best set that has no more MDT than this value.\nNegative values are good, positive values are bad.\nCaps at +100 to allow the set finder to function.",hover_delay=500)
        self.mdt_entry.configure(width=6)
        self.mdt_entry.grid(row=2,column=1,padx=0,pady=1,sticky='w')

        # self.sb_label = ttk.Label(self.conditions_frame,text="Subtle Blow requirement:")
        # self.sb_label.grid(row=2, column=0, sticky="w", padx=0, pady=1)
        # self.sb_req = tk.StringVar(value="0")
        # self.sb_entry = ttk.Entry(self.conditions_frame,textvariable=self.sb_req,justify="right")
        # self.sb_entry.configure(width=6)
        # self.sb_entry.grid(row=2,column=1,padx=0,pady=1,sticky='w')

        self.tpmetric_label = ttk.Label(self.conditions_frame,text="TP Metric:")
        self.tpmetric_label.grid(row=3, column=0, sticky="w", padx=0, pady=1)
        self.tpmetric = tk.StringVar(value="Time to WS")
        self.tpmetric_combo = ttk.Combobox(self.conditions_frame, values=["Time to WS","TP return","Damage dealt","DPS",], textvariable=self.tpmetric,state="readonly",width=15)
        self.tpmetric_combo_tip = Hovertip(self.tpmetric_combo,f"Choose what the algorithm prioritizes when building melee TP sets.\nTime to WS: Minimize real-world time to reach min. TP\nTP return: Maximize TP return per attack round; ignores damage dealt\nDamage dealt: Maximize damage dealt per attack round; ignores TP return\nDPS: Maximize damage per second during TP phase\n\nI personally do not trust the DPS metric since it ignores the WS phase.\nYou may get more total DPS from a faster TP set that let's you WS more often.",hover_delay=500)
        self.tpmetric_combo.grid(row=3,column=1,sticky="nw",padx=0,pady=2)

        self.spellmetric_label = ttk.Label(self.conditions_frame,text="Spell Metric:")
        self.spellmetric_label.grid(row=4, column=0, sticky="w", padx=0, pady=1)
        self.spellmetric = tk.StringVar(value="Damage dealt")
        self.spellmetric_combo = ttk.Combobox(self.conditions_frame, values=["Damage dealt","TP return","Damage > TP", "TP > Damage"], textvariable=self.spellmetric,state="readonly",width=15)
        self.spellmetric_combo_tip = Hovertip(self.spellmetric_combo,f"Choose what the algorithm prioritizes when building spellcasting and ranged attack sets.\nTP Return: Maximize TP return per attack; ignores damage dealt\nDamage dealt: Maximize damage dealt per attack; ignores TP return\Damage > TP: Maximize Damage*Damage*TP\nTP > Damage: Maximize Damage*TP*TP",hover_delay=500)
        self.spellmetric_combo.grid(row=4,column=1,sticky="nw",padx=0,pady=2)

        self.wsmetric_label = ttk.Label(self.conditions_frame,text="WS Metric:")
        self.wsmetric_label.grid(row=5, column=0, sticky="w", padx=0, pady=1)
        self.wsmetric = tk.StringVar(value="Damage dealt")
        self.wsmetric_combo = ttk.Combobox(self.conditions_frame, values=["Damage dealt","TP return","Magic accuracy"], textvariable=self.wsmetric,state="readonly",width=15)
        self.wsmetric_combo_tip = Hovertip(self.wsmetric_combo,f"Choose what the algorithm prioritizes when building WS sets.\nTP Return: Maximize TP return; ignores damage dealt.\nDamage Dealt: Maximize damage dealt; ignores TP return\nMagic accuracy: Maximize magic_accuracy*hitrate. Useful for things like Ageha, Full Break, Guillotine, Sniper Shot, etc",hover_delay=500)
        self.wsmetric_combo.grid(row=5,column=1,sticky="nw",padx=0,pady=2)


        # self.next_best_entry = ttk.Entry(self.self.conditions_frame,textvariable=self.next_best_value,justify="right")
        # self.next_best_entry.grid(row=5,column=1,sticky="w",padyx=0,pady=1)
        # self.next_best_entry.configure(width=4)


        self.run_frame = ttk.Frame(self.frame4)
        self.run_frame.grid(row=1,column=1,padx=0,pady=0)

        self.next_best_frame = ttk.Frame(self.run_frame)
        self.next_best_frame.grid(row=0,column=0,columnspan=2,padx=0,pady=10)
        self.next_best_toggle = tk.BooleanVar(value=False)
        self.next_best_checkbox = ttk.Checkbutton(self.next_best_frame, text="Print equipment with\nsimilar results?", variable=self.next_best_toggle) 
        self.next_best_checkbox.grid(row=1, column=0, sticky="nw", padx=0, pady=1)
        self.next_best_tip = Hovertip(self.next_best_checkbox,f"Prints a list of equipment, for each gear slot, within _% of the best item in that slot.\n_% defined by the entry box beside this checkbox.\nI recommend 1~2% at most.",hover_delay=500)
        self.next_best_value = tk.IntVar(value=1)
        self.next_best_entry = ttk.Entry(self.next_best_frame,textvariable=self.next_best_value,justify="right",)
        self.next_best_entry.configure(width=5)
        self.next_best_entry.grid(row=1,column=1,padx=5,pady=1,sticky='w')



        self.run_ws = tk.Button(self.run_frame,text="Optimize WS",image=self.dim_image,compound=tk.CENTER,width=100,height=30,command=lambda: self.run_optimize("run ws")) # dim_image = dimensional image = 1x1 pixel image used to allow exact pixel dimensions for Tk buttons.
        self.run_ws_tip = Hovertip(self.run_ws,f"Automatically find the best weapon skill set based on the Inputs and selected gear.",hover_delay=500)
        self.run_ws.grid(row=1,column=0,padx=0,pady=0)

        self.run_spell = tk.Button(self.run_frame,text="Optimize Magic",image=self.dim_image,compound=tk.CENTER,width=100,height=30,command=lambda: self.run_optimize("run magic"))
        self.run_spell_tip = Hovertip(self.run_spell,f"Automatically find the best magic or ranged attack set based on the Inputs and selected gear.",hover_delay=500)
        self.run_spell.grid(row=1,column=1,padx=0,pady=0)

        self.run_tp = tk.Button(self.run_frame,text="Optimize TP",image=self.dim_image,compound=tk.CENTER,width=100,height=30,command=lambda: self.run_optimize("run tp"))
        self.run_tp_tip = Hovertip(self.run_tp,"Automatically find the best melee TP set based on the Inputs and selected gear.",hover_delay=500)
        self.run_tp.grid(row=2,column=0,padx=0,pady=0)

        self.equip_best_set = tk.Button(self.run_frame,text="Equip best set",image=self.dim_image,compound=tk.CENTER,width=100,height=30,command=lambda: self.update_equipment())
        self.equip_best_tip = Hovertip(self.equip_best_set,"Equip the most recently obtained best set to the Inputs tab.",hover_delay=500)
        self.equip_best_set.configure(state="disabled")
        self.equip_best_set.grid(row=2,column=1,padx=0,pady=0)


# ====================================================================================================================================================================================

        self.checkbox_frame = ttk.Frame(self.frame4,borderwidth=3,width=310)
        self.checkbox_frame.grid(row=0, column=1, padx=0, pady=0)

# ====================================================================================================================================================================================
        # Label frame unique to main-hand slot. It remains fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.main_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select main  ")
        self.main_cbox_frame.pack(fill=tk.BOTH, expand=1)


        # Scrollable base frame for the main-hand slot
        self.main_scrollframe2 = ttk.Frame(self.main_cbox_frame)
        self.main_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The main-hand canvas
        self.main_canvas2 = tk.Canvas(self.main_scrollframe2,height=320,width=390)
        self.main_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.main_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.main_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.main_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.main_canvas2)) 

        self.main_cbox_scrollbar = ttk.Scrollbar(self.main_scrollframe2, orient=tk.VERTICAL, command=self.main_canvas2.yview)
        self.main_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_canvas2.configure(yscrollcommand=self.main_cbox_scrollbar.set)
        self.main_canvas2.bind("<Configure>", lambda event: self.main_canvas2.configure(scrollregion=self.main_canvas2.bbox("all")))


            # self.bolster_on = tk.BooleanVar(value=False)
            # self.bolster_cbox = ttk.Checkbutton(self.geo_frame,variable=self.bolster_on,text="Bolster",command=lambda trigger="bolster": self.update_buff_cboxes(trigger))
            # # self.bolster_cbox.state(['!alternate']) 
            # self.bolster_cbox.configure(state="disabled")
            # self.bolster_cbox.grid(row=6,column=0,sticky="nw",padx=0,pady=2)

        self.cbox_main = ttk.Frame(self.main_canvas2)
        self.x_main2 = [] # List to contain all of the individual checkbox button widgets for the main slot
        self.x_main2_var = []
        for n,k in enumerate(sorted(mains, key=lambda d: d["Name2"])):
            self.x_main2_var.append(tk.BooleanVar(value=False))
            self.x_main2.append(ttk.Checkbutton(self.cbox_main, text=k["Name2"], variable=self.x_main2_var[n],)) 
            self.x_main2[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_main2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.main_canvas2.create_window((0,0),window=self.cbox_main, anchor="nw")



# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to sub-hand slot. It resubs fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.sub_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select sub  ")
        self.sub_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.sub_cbox_frame.pack_forget()

        # Scrollable base frame for the sub-hand slot
        self.sub_scrollframe2 = ttk.Frame(self.sub_cbox_frame)
        self.sub_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The sub-hand canvas
        self.sub_canvas2 = tk.Canvas(self.sub_scrollframe2,height=320,width=390)
        self.sub_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.sub_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.sub_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.sub_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.sub_canvas2)) 

        self.sub_cbox_scrollbar = ttk.Scrollbar(self.sub_scrollframe2, orient=tk.VERTICAL, command=self.sub_canvas2.yview)
        self.sub_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sub_canvas2.configure(yscrollcommand=self.sub_cbox_scrollbar.set)
        self.sub_canvas2.bind("<Configure>", lambda event: self.sub_canvas2.configure(scrollregion=self.sub_canvas2.bbox("all")))


        self.cbox_sub = ttk.Frame(self.sub_canvas2)
        self.x_sub2 = [] # List to contain all of the individual checkbox button widgets for the sub slot
        self.x_sub2_var = [] # List to contain all of the individual checkbox button widgets for the sub slot
        for n,k in enumerate(sorted(subs+grips, key=lambda d: d["Name2"])):
            self.x_sub2_var.append(tk.BooleanVar(value=False))
            self.x_sub2.append(ttk.Checkbutton(self.cbox_sub, text=k["Name2"], variable=self.x_sub2_var[n],)) 
            self.x_sub2[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_sub2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.sub_canvas2.create_window((0,0),window=self.cbox_sub, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to ranged-hand slot. It rerangeds fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.ranged_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select ranged  ")
        self.ranged_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.ranged_cbox_frame.pack_forget()


        # Scrollable base frame for the ranged-hand slot
        self.ranged_scrollframe2 = ttk.Frame(self.ranged_cbox_frame)
        self.ranged_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The ranged-hand canvas
        self.ranged_canvas2 = tk.Canvas(self.ranged_scrollframe2,height=320,width=390)
        self.ranged_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.ranged_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.ranged_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.ranged_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.ranged_canvas2)) 

        self.ranged_cbox_scrollbar = ttk.Scrollbar(self.ranged_scrollframe2, orient=tk.VERTICAL, command=self.ranged_canvas2.yview)
        self.ranged_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ranged_canvas2.configure(yscrollcommand=self.ranged_cbox_scrollbar.set)
        self.ranged_canvas2.bind("<Configure>", lambda event: self.ranged_canvas2.configure(scrollregion=self.ranged_canvas2.bbox("all")))


        self.cbox_ranged = ttk.Frame(self.ranged_canvas2)
        self.x_ranged2 = [] # List to contain all of the individual checkbox button widgets for the ranged slot
        self.x_ranged2_var = [] # List to contain all of the individual checkbox button widgets for the ranged slot
        for n,k in enumerate(sorted(ranged, key=lambda d: d["Name2"])):
            self.x_ranged2_var.append(tk.BooleanVar(value=False))
            self.x_ranged2.append(ttk.Checkbutton(self.cbox_ranged, text=k["Name2"], variable=self.x_ranged2_var[n],)) 
            self.x_ranged2[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_ranged2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.ranged_canvas2.create_window((0,0),window=self.cbox_ranged, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to ammo-hand slot. It reammos fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.ammo_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select ammo  ")
        self.ammo_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.ammo_cbox_frame.pack_forget()


        # Scrollable base frame for the ammo-hand slot
        self.ammo_scrollframe2 = ttk.Frame(self.ammo_cbox_frame)
        self.ammo_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The ammo-hand canvas
        self.ammo_canvas2 = tk.Canvas(self.ammo_scrollframe2,height=320,width=390)
        self.ammo_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.ammo_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.ammo_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.ammo_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.ammo_canvas2)) 

        self.ammo_cbox_scrollbar = ttk.Scrollbar(self.ammo_scrollframe2, orient=tk.VERTICAL, command=self.ammo_canvas2.yview)
        self.ammo_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ammo_canvas2.configure(yscrollcommand=self.ammo_cbox_scrollbar.set)
        self.ammo_canvas2.bind("<Configure>", lambda event: self.ammo_canvas2.configure(scrollregion=self.ammo_canvas2.bbox("all")))


        self.cbox_ammo = ttk.Frame(self.ammo_canvas2)
        self.x_ammo2 = [] # List to contain all of the individual checkbox button widgets for the ammo slot
        self.x_ammo2_var = []
        for n,k in enumerate(sorted(ammos, key=lambda d: d["Name2"])):
            self.x_ammo2_var.append(tk.BooleanVar(value=False))            
            self.x_ammo2.append(ttk.Checkbutton(self.cbox_ammo, text=k["Name2"], variable=self.x_ammo2_var[n])) 
            self.x_ammo2[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_ammo2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.ammo_canvas2.create_window((0,0),window=self.cbox_ammo, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to head-hand slot. It reheads fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.head_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select head  ")
        self.head_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.head_cbox_frame.pack_forget()


        # Scrollable base frame for the head-hand slot
        self.head_scrollframe2 = ttk.Frame(self.head_cbox_frame)
        self.head_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The head-hand canvas
        self.head_canvas2 = tk.Canvas(self.head_scrollframe2,height=320,width=390)
        self.head_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.head_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.head_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.head_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.head_canvas2)) 

        self.head_cbox_scrollbar = ttk.Scrollbar(self.head_scrollframe2, orient=tk.VERTICAL, command=self.head_canvas2.yview)
        self.head_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.head_canvas2.configure(yscrollcommand=self.head_cbox_scrollbar.set)
        self.head_canvas2.bind("<Configure>", lambda event: self.head_canvas2.configure(scrollregion=self.head_canvas2.bbox("all")))


        self.cbox_head = ttk.Frame(self.head_canvas2)
        self.x_head2 = [] # List to contain all of the individual checkbox button widgets for the head slot
        self.x_head2_var = []
        for n,k in enumerate(sorted(heads, key=lambda d: d["Name2"])):
            self.x_head2_var.append(tk.BooleanVar(value=False))
            self.x_head2.append(ttk.Checkbutton(self.cbox_head, text=k["Name2"], variable=self.x_head2_var[n],)) 
            self.x_head2[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_head2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.head_canvas2.create_window((0,0),window=self.cbox_head, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to neck-hand slot. It renecks fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.neck_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select neck  ")
        self.neck_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.neck_cbox_frame.pack_forget()


        # Scrollable base frame for the neck-hand slot
        self.neck_scrollframe2 = ttk.Frame(self.neck_cbox_frame)
        self.neck_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The neck-hand canvas
        self.neck_canvas2 = tk.Canvas(self.neck_scrollframe2,height=320,width=390)
        self.neck_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.neck_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.neck_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.neck_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.neck_canvas2)) 

        self.neck_cbox_scrollbar = ttk.Scrollbar(self.neck_scrollframe2, orient=tk.VERTICAL, command=self.neck_canvas2.yview)
        self.neck_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.neck_canvas2.configure(yscrollcommand=self.neck_cbox_scrollbar.set)
        self.neck_canvas2.bind("<Configure>", lambda event: self.neck_canvas2.configure(scrollregion=self.neck_canvas2.bbox("all")))


        self.cbox_neck = ttk.Frame(self.neck_canvas2)
        self.x_neck2 = [] # List to contain all of the individual checkbox button widgets for the neck slot
        self.x_neck2_var = []
        for n,k in enumerate(sorted(necks, key=lambda d: d["Name2"])):
            self.x_neck2_var.append(tk.BooleanVar(value=False))
            self.x_neck2.append(ttk.Checkbutton(self.cbox_neck, text=k["Name2"], variable=self.x_neck2_var[n],)) 
            self.x_neck2[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_neck2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.neck_canvas2.create_window((0,0),window=self.cbox_neck, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to ear1-hand slot. It reear1s fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.ear1_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select ear1  ")
        self.ear1_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.ear1_cbox_frame.pack_forget()


        # Scrollable base frame for the ear1-hand slot
        self.ear1_scrollframe2 = ttk.Frame(self.ear1_cbox_frame)
        self.ear1_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The ear1-hand canvas
        self.ear1_canvas2 = tk.Canvas(self.ear1_scrollframe2,height=320,width=390)
        self.ear1_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.ear1_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.ear1_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.ear1_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.ear1_canvas2)) 

        self.ear1_cbox_scrollbar = ttk.Scrollbar(self.ear1_scrollframe2, orient=tk.VERTICAL, command=self.ear1_canvas2.yview)
        self.ear1_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ear1_canvas2.configure(yscrollcommand=self.ear1_cbox_scrollbar.set)
        self.ear1_canvas2.bind("<Configure>", lambda event: self.ear1_canvas2.configure(scrollregion=self.ear1_canvas2.bbox("all")))


        self.cbox_ear1 = ttk.Frame(self.ear1_canvas2)
        self.x_ear12 = [] # List to contain all of the individual checkbox button widgets for the ear1 slot
        self.x_ear12_var = []
        for n,k in enumerate(sorted(ears, key=lambda d: d["Name2"])):
            self.x_ear12_var.append(tk.BooleanVar(value=False))
            self.x_ear12.append(ttk.Checkbutton(self.cbox_ear1, text=k["Name2"], variable=self.x_ear12_var[n],)) 
            self.x_ear12[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_ear12[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.ear1_canvas2.create_window((0,0),window=self.cbox_ear1, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to ear2-hand slot. It reear2s fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.ear2_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select ear2  ")
        self.ear2_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.ear2_cbox_frame.pack_forget()


        # Scrollable base frame for the ear2-hand slot
        self.ear2_scrollframe2 = ttk.Frame(self.ear2_cbox_frame)
        self.ear2_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The ear2-hand canvas
        self.ear2_canvas2 = tk.Canvas(self.ear2_scrollframe2,height=320,width=390)
        self.ear2_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.ear2_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.ear2_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.ear2_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.ear2_canvas2)) 

        self.ear2_cbox_scrollbar = ttk.Scrollbar(self.ear2_scrollframe2, orient=tk.VERTICAL, command=self.ear2_canvas2.yview)
        self.ear2_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ear2_canvas2.configure(yscrollcommand=self.ear2_cbox_scrollbar.set)
        self.ear2_canvas2.bind("<Configure>", lambda event: self.ear2_canvas2.configure(scrollregion=self.ear2_canvas2.bbox("all")))


        self.cbox_ear2 = ttk.Frame(self.ear2_canvas2)
        self.x_ear22 = [] # List to contain all of the individual checkbox button widgets for the ear2 slot
        self.x_ear22_var = []
        for n,k in enumerate(sorted(ears2, key=lambda d: d["Name2"])):
            self.x_ear22_var.append(tk.BooleanVar(value=False))
            self.x_ear22.append(ttk.Checkbutton(self.cbox_ear2, text=k["Name2"], variable=self.x_ear22_var[n],)) 
            self.x_ear22[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_ear22[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.ear2_canvas2.create_window((0,0),window=self.cbox_ear2, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to body-hand slot. It rebodys fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.body_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select body  ")
        self.body_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.body_cbox_frame.pack_forget()


        # Scrollable base frame for the body-hand slot
        self.body_scrollframe2 = ttk.Frame(self.body_cbox_frame)
        self.body_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The body-hand canvas
        self.body_canvas2 = tk.Canvas(self.body_scrollframe2,height=320,width=390)
        self.body_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.body_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.body_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.body_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.body_canvas2)) 

        self.body_cbox_scrollbar = ttk.Scrollbar(self.body_scrollframe2, orient=tk.VERTICAL, command=self.body_canvas2.yview)
        self.body_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.body_canvas2.configure(yscrollcommand=self.body_cbox_scrollbar.set)
        self.body_canvas2.bind("<Configure>", lambda event: self.body_canvas2.configure(scrollregion=self.body_canvas2.bbox("all")))


        self.cbox_body = ttk.Frame(self.body_canvas2)
        self.x_body2 = [] # List to contain all of the individual checkbox button widgets for the body slot
        self.x_body2_var = []
        for n,k in enumerate(sorted(bodies, key=lambda d: d["Name2"])):
            self.x_body2_var.append(tk.BooleanVar(value=False))
            self.x_body2.append(ttk.Checkbutton(self.cbox_body, text=k["Name2"], variable=self.x_body2_var[n],)) 
            self.x_body2[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_body2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.body_canvas2.create_window((0,0),window=self.cbox_body, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to hands-hand slot. It rehandss fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.hands_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select hands  ")
        self.hands_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.hands_cbox_frame.pack_forget()


        # Scrollable base frame for the hands-hand slot
        self.hands_scrollframe2 = ttk.Frame(self.hands_cbox_frame)
        self.hands_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The hands-hand canvas
        self.hands_canvas2 = tk.Canvas(self.hands_scrollframe2,height=320,width=390)
        self.hands_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.hands_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.hands_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.hands_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.hands_canvas2)) 

        self.hands_cbox_scrollbar = ttk.Scrollbar(self.hands_scrollframe2, orient=tk.VERTICAL, command=self.hands_canvas2.yview)
        self.hands_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hands_canvas2.configure(yscrollcommand=self.hands_cbox_scrollbar.set)
        self.hands_canvas2.bind("<Configure>", lambda event: self.hands_canvas2.configure(scrollregion=self.hands_canvas2.bbox("all")))


        self.cbox_hands = ttk.Frame(self.hands_canvas2)
        self.x_hands2 = [] # List to contain all of the individual checkbox button widgets for the hands slot
        self.x_hands2_var = []
        for n,k in enumerate(sorted(hands, key=lambda d: d["Name2"])):
            self.x_hands2_var.append(tk.BooleanVar(value=False))
            self.x_hands2.append(ttk.Checkbutton(self.cbox_hands, text=k["Name2"], variable=self.x_hands2_var[n],)) 
            self.x_hands2[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_hands2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.hands_canvas2.create_window((0,0),window=self.cbox_hands, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to ring1-hand slot. It rering1s fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.ring1_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select ring1  ")
        self.ring1_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.ring1_cbox_frame.pack_forget()


        # Scrollable base frame for the ring1-hand slot
        self.ring1_scrollframe2 = ttk.Frame(self.ring1_cbox_frame)
        self.ring1_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The ring1-hand canvas
        self.ring1_canvas2 = tk.Canvas(self.ring1_scrollframe2,height=320,width=390)
        self.ring1_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.ring1_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.ring1_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.ring1_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.ring1_canvas2)) 

        self.ring1_cbox_scrollbar = ttk.Scrollbar(self.ring1_scrollframe2, orient=tk.VERTICAL, command=self.ring1_canvas2.yview)
        self.ring1_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ring1_canvas2.configure(yscrollcommand=self.ring1_cbox_scrollbar.set)
        self.ring1_canvas2.bind("<Configure>", lambda event: self.ring1_canvas2.configure(scrollregion=self.ring1_canvas2.bbox("all")))


        self.cbox_ring1 = ttk.Frame(self.ring1_canvas2)
        self.x_ring12 = [] # List to contain all of the individual checkbox button widgets for the ring1 slot
        self.x_ring12_var = []
        for n,k in enumerate(sorted(rings, key=lambda d: d["Name2"])):
            self.x_ring12_var.append(tk.BooleanVar(value=False))
            self.x_ring12.append(ttk.Checkbutton(self.cbox_ring1, text=k["Name2"], variable=self.x_ring12_var[n],)) 
            self.x_ring12[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_ring12[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.ring1_canvas2.create_window((0,0),window=self.cbox_ring1, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to ring2-hand slot. It rering2s fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.ring2_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select ring2  ")
        self.ring2_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.ring2_cbox_frame.pack_forget()


        # Scrollable base frame for the ring2-hand slot
        self.ring2_scrollframe2 = ttk.Frame(self.ring2_cbox_frame)
        self.ring2_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The ring2-hand canvas
        self.ring2_canvas2 = tk.Canvas(self.ring2_scrollframe2,height=320,width=390)
        self.ring2_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.ring2_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.ring2_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.ring2_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.ring2_canvas2)) 

        self.ring2_cbox_scrollbar = ttk.Scrollbar(self.ring2_scrollframe2, orient=tk.VERTICAL, command=self.ring2_canvas2.yview)
        self.ring2_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ring2_canvas2.configure(yscrollcommand=self.ring2_cbox_scrollbar.set)
        self.ring2_canvas2.bind("<Configure>", lambda event: self.ring2_canvas2.configure(scrollregion=self.ring2_canvas2.bbox("all")))


        self.cbox_ring2 = ttk.Frame(self.ring2_canvas2)
        self.x_ring22 = [] # List to contain all of the individual checkbox button widgets for the ring2 slot
        self.x_ring22_var = []
        for n,k in enumerate(sorted(rings2, key=lambda d: d["Name2"])):
            self.x_ring22_var.append(tk.BooleanVar(value=False))
            self.x_ring22.append(ttk.Checkbutton(self.cbox_ring2, text=k["Name2"], variable=self.x_ring22_var[n],)) 
            self.x_ring22[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_ring22[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.ring2_canvas2.create_window((0,0),window=self.cbox_ring2, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to back-hand slot. It rebacks fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.back_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select back  ")
        self.back_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.back_cbox_frame.pack_forget()


        # Scrollable base frame for the back-hand slot
        self.back_scrollframe2 = ttk.Frame(self.back_cbox_frame)
        self.back_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The back-hand canvas
        self.back_canvas2 = tk.Canvas(self.back_scrollframe2,height=320,width=390)
        self.back_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.back_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.back_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.back_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.back_canvas2)) 

        self.back_cbox_scrollbar = ttk.Scrollbar(self.back_scrollframe2, orient=tk.VERTICAL, command=self.back_canvas2.yview)
        self.back_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.back_canvas2.configure(yscrollcommand=self.back_cbox_scrollbar.set)
        self.back_canvas2.bind("<Configure>", lambda event: self.back_canvas2.configure(scrollregion=self.back_canvas2.bbox("all")))


        self.cbox_back = ttk.Frame(self.back_canvas2)
        self.x_back2 = [] # List to contain all of the individual checkbox button widgets for the back slot
        self.x_back2_var = []
        for n,k in enumerate(sorted(capes, key=lambda d: d["Name2"])):
            self.x_back2_var.append(tk.BooleanVar(value=False))
            self.x_back2.append(ttk.Checkbutton(self.cbox_back, text=k["Name2"], variable=self.x_back2_var[n],)) 
            self.x_back2[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_back2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.back_canvas2.create_window((0,0),window=self.cbox_back, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to waist-hand slot. It rewaists fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.waist_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select waist  ")
        self.waist_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.waist_cbox_frame.pack_forget()


        # Scrollable base frame for the waist-hand slot
        self.waist_scrollframe2 = ttk.Frame(self.waist_cbox_frame)
        self.waist_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The waist-hand canvas
        self.waist_canvas2 = tk.Canvas(self.waist_scrollframe2,height=320,width=390)
        self.waist_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.waist_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.waist_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.waist_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.waist_canvas2)) 

        self.waist_cbox_scrollbar = ttk.Scrollbar(self.waist_scrollframe2, orient=tk.VERTICAL, command=self.waist_canvas2.yview)
        self.waist_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.waist_canvas2.configure(yscrollcommand=self.waist_cbox_scrollbar.set)
        self.waist_canvas2.bind("<Configure>", lambda event: self.waist_canvas2.configure(scrollregion=self.waist_canvas2.bbox("all")))


        self.cbox_waist = ttk.Frame(self.waist_canvas2)
        self.x_waist2 = [] # List to contain all of the individual checkbox button widgets for the waist slot
        self.x_waist2_var = []
        for n,k in enumerate(sorted(waists, key=lambda d: d["Name2"])):
            self.x_waist2_var.append(tk.BooleanVar(value=False))
            self.x_waist2.append(ttk.Checkbutton(self.cbox_waist, text=k["Name2"], variable=self.x_waist2_var[n],)) 
            self.x_waist2[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_waist2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.waist_canvas2.create_window((0,0),window=self.cbox_waist, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to legs-hand slot. It relegss fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.legs_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select legs  ")
        self.legs_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.legs_cbox_frame.pack_forget()


        # Scrollable base frame for the legs-hand slot
        self.legs_scrollframe2 = ttk.Frame(self.legs_cbox_frame)
        self.legs_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The legs-hand canvas
        self.legs_canvas2 = tk.Canvas(self.legs_scrollframe2,height=320,width=390)
        self.legs_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.legs_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.legs_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.legs_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.legs_canvas2)) 

        self.legs_cbox_scrollbar = ttk.Scrollbar(self.legs_scrollframe2, orient=tk.VERTICAL, command=self.legs_canvas2.yview)
        self.legs_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.legs_canvas2.configure(yscrollcommand=self.legs_cbox_scrollbar.set)
        self.legs_canvas2.bind("<Configure>", lambda event: self.legs_canvas2.configure(scrollregion=self.legs_canvas2.bbox("all")))


        self.cbox_legs = ttk.Frame(self.legs_canvas2)
        self.x_legs2 = [] # List to contain all of the individual checkbox button widgets for the legs slot
        self.x_legs2_var = []
        for n,k in enumerate(sorted(legs, key=lambda d: d["Name2"])):
            self.x_legs2_var.append(tk.BooleanVar(value=False))
            self.x_legs2.append(ttk.Checkbutton(self.cbox_legs, text=k["Name2"], variable=self.x_legs2_var[n],)) 
            self.x_legs2[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_legs2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.legs_canvas2.create_window((0,0),window=self.cbox_legs, anchor="nw")

# ====================================================================================================================================================================================
# ====================================================================================================================================================================================
        # Label frame unique to feet-hand slot. It refeets fixed to always view the label text. We simply forget and re-place it when we want to see another slot's frame
        self.feet_cbox_frame = ttk.LabelFrame(self.checkbox_frame, text="  select feet  ")
        self.feet_cbox_frame.pack(fill=tk.BOTH, expand=1)
        self.feet_cbox_frame.pack_forget()


        # Scrollable base frame for the feet-hand slot
        self.feet_scrollframe2 = ttk.Frame(self.feet_cbox_frame)
        self.feet_scrollframe2.pack(fill=tk.BOTH, expand=1)

        # The feet-hand canvas
        self.feet_canvas2 = tk.Canvas(self.feet_scrollframe2,height=320,width=390)
        self.feet_canvas2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.feet_scrollframe2.bind('<Enter>', lambda event: self._bound_to_mousewheel(event, self.feet_canvas2)) # We must mouse-over the scrollable frame to use the mousewheel
        self.feet_scrollframe2.bind('<Leave>', lambda event: self._unbound_to_mousewheel(event, self.feet_canvas2)) 

        self.feet_cbox_scrollbar = ttk.Scrollbar(self.feet_scrollframe2, orient=tk.VERTICAL, command=self.feet_canvas2.yview)
        self.feet_cbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.feet_canvas2.configure(yscrollcommand=self.feet_cbox_scrollbar.set)
        self.feet_canvas2.bind("<Configure>", lambda event: self.feet_canvas2.configure(scrollregion=self.feet_canvas2.bbox("all")))


        self.cbox_feet = ttk.Frame(self.feet_canvas2)
        self.x_feet2 = [] # List to contain all of the individual checkbox button widgets for the feet slot
        self.x_feet2_var = []
        for n,k in enumerate(sorted(feet, key=lambda d: d["Name2"])):
            self.x_feet2_var.append(tk.BooleanVar(value=False))
            self.x_feet2.append(ttk.Checkbutton(self.cbox_feet, text=k["Name2"], variable=self.x_feet2_var[n],)) 
            self.x_feet2[n].state(['!alternate'])
            if self.mainjob.get().lower() in k["Jobs"]:
                self.x_feet2[n].grid(row=n,column=0,padx=0,pady=0,sticky='w')
        self.feet_canvas2.create_window((0,0),window=self.cbox_feet, anchor="nw")

# ====================================================================================================================================================================================


        self.stats_frame = ttk.Frame(self.stats_tab,width=676,height=350)
        self.stats_frame.grid_propagate(0)
        self.stats_frame.grid(row=0, column=0, padx=2, pady=0)
        self.stats_frame.grid_columnconfigure((0,1),weight=1) # Column 0 expands in the horizontal direction to fill blank space, effectively centering column1 in the frame. Weight=1 is how fast it expands; 2 is twice as fast, but it's all relative so no reason to change it with only one column
        self.stats_frame.grid_rowconfigure((0,1),weight=1) # Column 0 expands in the horizontal direction to fill blank space, effectively centering column1 in the frame. Weight=1 is how fast it expands; 2 is twice as fast, but it's all relative so no reason to change it with only one column

    
        self.wip_text = tk.Label(self.stats_frame,text="Work in progress.\n\n For now, just click the \"Show Stats\" button in the Inputs Tab to print a list of all of the player's stats in alphabetical order.\nIf the stat doesn't show up in the output, then the stat has zero value.")
        self.wip_text.grid(row=0,column=0)


        melee_stats = ["Attack1","Attack2","Accuracy1","Accuracy2","DA","TA","QA","Zanshin","ZanHasso","Kick Attacks","Attack%"]
        ranged_stats = ["Ranged Attack","Ranged Accuracy","Double Shot","Triple Shot","Quad Shot","Daken","Ranged Attack%","Ranged Crit Damage"]
        magic_stats = ["Magic Attack","Magic Accuracy","Magic Damage","Magic Accuracy Skill","Magic Burst Damage","Magic Burst Damage II","Magic Burst Damage Trait",]
        parameters = ["STR","DEX","VIT","AGI","INT","MND","CHR"]
        ws_stats = ["Weapon Skill Damage","Weapon Skill Damage Trait","Weapon Skill Bonus","TP Bonus","Skillchain Bonus"]
        phys_stats = ["PDL","PDL Trait","Crit Rate","Crit Damage"]
        def_stats = ["PDT","MDT","DT","Evasion","Magic Evasion","Magic Defense","Subtle Blow","Subtle Blow II"]
        delay_stats = ["Gear Haste","Magic Haste","JA Haste","Delay Reduction","Dual Wield","Martial Arts"]
        extra_stats = ["Store TP","Regain","Fencer","Occult Acumen","Recycle","True Shot"]
        skill_stats = ["Hand-to-Hand Skill","Dagger Skill","Sword Skill","Great Sword Skill","Axe Skill","Great Axe Skill","Scythe Skill","Polearm Skill","Katana Skill","Great Katana Skill","Club Skill","Staff Skill","Evasion Skill","Divine Magic Skill","Elemental Magic Skill","Dark Magic Skill","Ninjutsu Skill","Summoning Magic Skill","Blue Magic Skill"]



# ==========================================================================================
# Mouse wheel to only work when the mouse cursor hovers over a widget: 
# https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
    def _bound_to_mousewheel(self, event, canvas):
        canvas.bind_all("<MouseWheel>", lambda event: self._on_mousewheel(event, canvas))

    def _unbound_to_mousewheel(self, event, canvas):
        canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event, canvas):
        canvas.yview_scroll(int(-1*(event.delta/60)), "units")

# self.radio_frame.bind('<Enter>', self._bound_to_mousewheel) # If your mouse moves over a widget (does not trigger on hidden/forgotten widgets)
# self.radio_frame.bind('<Leave>', self._unbound_to_mousewheel) # If your mouse moves off of a widget (does not trigger on hidden/forgotten widgets)
# ==========================================================================================

# ==========================================================================================

    def select_job(self,event,job_type):
        #
        # The code starts by showing all items for all slots in order to ensure that the scroll region in each slot is always sufficient for each job individually.
        # After selecting a main job, this function will hide the items that the selected main job can not use.
        #
        if job_type=="main":
            count = 0
            for radio_subframe in [self.radio_main,self.radio_sub,self.radio_ranged,self.radio_ammo,self.radio_head,self.radio_neck,self.radio_ear1,self.radio_ear2,self.radio_body,self.radio_hands,self.radio_ring1,self.radio_ring2,self.radio_back,self.radio_waist,self.radio_legs,self.radio_feet]:
                for x in radio_subframe.winfo_children(): # winfo_children(): https://stackoverflow.com/questions/7290071/getting-every-child-widget-of-a-tkinter-window
                    item_dict = eval(x.cget("value")) #  using cget() to get the value: https://www.tutorialspoint.com/get-the-text-of-a-button-widget-in-tkinter
                    if event.lower() not in item_dict["Jobs"]:
                        x.grid_forget()
                    else:
                        x.grid(row=count,column=0,padx=0,pady=0,sticky="w")
                        count += 1
            # radio_subframe.bind("<Configure>", self.reset_scrollregion)
            radio_subframe.bind("<Configure>", self.reset_radio_scrollregion)
            

            for cbox_subframe in [self.cbox_main, self.cbox_sub, self.cbox_ranged, self.cbox_ammo, self.cbox_head, self.cbox_neck, self.cbox_ear1, self.cbox_ear2, self.cbox_body, self.cbox_hands, self.cbox_ring1, self.cbox_ring2, self.cbox_back, self.cbox_waist, self.cbox_legs, self.cbox_feet,]:
                for cbox in cbox_subframe.winfo_children():
                    label = cbox.cget("text") # The text displayed for each checkbox is the "Name2" key
                    item_dict = name2dictionary(label) # Item dictionary, containing all stats. We just need the "Jobs" value here, though.
                    if event.lower() not in item_dict["Jobs"]:
                        cbox.grid_forget()
                    else:
                        cbox.grid(row=count,column=0,padx=0,pady=0,sticky="w")
                        count += 1
            cbox_subframe.bind("<Configure>", self.reset_cbox_scrollregion)

            self.select_cboxes("unselect ALL") # Unselect every item

                        
                        

            # Update the spell list.
            self.spell_box.configure(values=self.spell_dict.get(event,["None"]))
            self.spell_name.set(self.spell_dict.get(event,["None"])[0])
            
            # Allow the user to select the subjob as their main job.
            if event==self.subjob.get():
                self.subjob_box.set("None")

            # Hide the main job from the subjob list.
            updated_subjobs = [k for k in self.sub_jobs if self.mainjob.get() != k]
            self.subjob_box.configure(values=updated_subjobs)

        if job_type=="sub":
            if event == self.mainjob.get():
                self.subjob_box.set("None")

        # Update the special toggle checkboxes. Disable all checkboxes and hide those not useable by main/sub combo.
        self.update_special_checkboxes("select_job")


    def select_cboxes(self,trigger):
        #
        # The code starts by showing all items for all slots in order to ensure that the scroll region in each slot is always sufficient for each job individually.
        # After selecting a main job, this function will hide the items that the selected main job can not use.
        #
        # TODO: Dictionary these buttons/checkboxes/radio
        #
        tvr_rings = ["Cornelia's","Ephramad's","Fickblix's","Gurebu-Ogurebu's","Lehko Habhoka's","Medada's","Ragelise's"]
        jse_ear_names = {"nin":"Hattori","drk":"Heathen","blm":"Wicce","rdm":"Lethargy","drg":"Peltast","whm":"Ebers","sam":"Kasuga","sch":"Arbatel","war":"Boii","cor":"Chasseur","brd":"Fili","thf":"Skulker","mnk":"Bhikku","dnc":"Maculele","bst":"Nukumi","geo":"Azimuth","pld":"Chevalier","rng":"Amini","blu":"Hashishin","run":"Erilaz","pup":"Karagoz"}

        cbox_lists = {"main":[self.main_cbox_frame,self.x_main2,self.x_main2_var],
                        "sub":[self.sub_cbox_frame,self.x_sub2,self.x_sub2_var],
                        "ranged":[self.ranged_cbox_frame,self.x_ranged2,self.x_ranged2_var],
                        "ammo":[self.ammo_cbox_frame,self.x_ammo2,self.x_ammo2_var],
                        "head":[self.head_cbox_frame,self.x_head2,self.x_head2_var],
                        "neck":[self.neck_cbox_frame, self.x_neck2,self.x_neck2_var],
                        "ear1":[self.ear1_cbox_frame,self.x_ear12,self.x_ear12_var],
                        "ear2":[self.ear2_cbox_frame,self.x_ear22,self.x_ear22_var],
                        "body":[self.body_cbox_frame,self.x_body2,self.x_body2_var],
                        "hands":[self.hands_cbox_frame,self.x_hands2,self.x_hands2_var],
                        "ring1":[self.ring1_cbox_frame,self.x_ring12,self.x_ring12_var],
                        "ring2":[self.ring2_cbox_frame,self.x_ring22,self.x_ring22_var],
                        "back":[self.back_cbox_frame,self.x_back2,self.x_back2_var],
                        "waist":[self.waist_cbox_frame,self.x_waist2,self.x_waist2_var],
                        "legs":[self.legs_cbox_frame,self.x_legs2,self.x_legs2_var],
                        "feet":[self.feet_cbox_frame,self.x_feet2,self.x_feet2_var],}


        items0 = [] # Raw item names from "//gs export all". Many abbreviated.
        items = [] # Full item names. We'll do a match with the item_list.txt file to convert abbreviated names to full names.
        if trigger=="select file":
            filename = filedialog.askopenfilename(
            title='Open a file',
            initialdir='./',)

            if len(filename) > 0:
                with open(filename, "r") as ifile:
                    for line in ifile:
                        try:
                            items0.append(line.split('"')[1]) # Assume that all item names in the input file are within FIRST occurrence of double quotes.
                        except:
                            continue

                item_name_map = np.loadtxt("item_list.txt",unpack=True,delimiter=";",usecols=(1,2),dtype=str)

                for item0 in items0:
                    # Strip the + from item names ("Eerie Cloak +1" becomes "Eerie Cloak").
                    item01 = "".join(item0.split(" +")[0:-1]) if "+" in item0 else item0
                    indices = [i for i,k in enumerate(item_name_map[1]) if item01 in k] # Index of matching names. Simply looks for substring in item name. 
                    items0 = [item_name_map[0][i] for i in indices]

                    # Append each of the matches to the items list, which is a list of full item names that the gear.py file uses as the "Name" value.
                    for k in items0:
                        items.append(k.lower())


        if "select" in trigger:
            for slot in cbox_lists:
                if (cbox_lists[slot][0].winfo_ismapped()) or (trigger in ["select ALL", "select file", "unselect ALL"]): # Find the currently displayed checkbox list. https://stackoverflow.com/questions/46377192/check-if-a-tkinter-widget-is-visible
                    for i,item in enumerate(cbox_lists[slot][2]):

                        label = cbox_lists[slot][1][i].cget("text") # The text displayed for each checkbox is the "Name2" key
                        d = name2dictionary(label) # Item dictionary, containing all stats. We just need the "Rank", "Name", and "Jobs" values.

                        # First Select/Unselect everything in the list.
                        item.set(False if "un" in trigger else (True if self.mainjob.get().lower() in d["Jobs"] else False))

                        # Deselect items not in the [items] list. (items not in the input file)
                        if trigger=="select file" and d["Name"].lower() not in items:
                            item.set(False)

                        # TVR Ring check
                        if slot in ["ring1","ring2"] and " ".join(label.split()[0:-1]) in tvr_rings and " ".join(label.split()[0:-1])!=self.tvr_ring.get():
                            item.set(False)

                        # Odyssey Rank check
                        if d.get("Rank",self.odyrank.get())!=self.odyrank.get():
                            item.set(False)

                        # Unselect Path A Nyame
                        if "Nyame" in label and "A"==label[-1]:
                            item.set(False)

                        # Unselect JSE +2 Earrings
                        if jse_ear_names[self.mainjob.get().lower()] in label and "+2" in label:
                            item.set(False)

                        # Unselect JSE +1 necks
                        if slot=="neck" and "R20" in label: 
                            item.set(False)

                        # Unselect night time Lugra Earring +1 R15
                        if slot in ["ear1","ear2"] and "(night)" in label: 
                            item.set(False)

                        # Unselect final stage Prime weapons for now.
                        if slot in ["main","sub"] and "III" in label: 
                            item.set(False)


    def name2dictionary(self, name):
        #
        # Given an item name ("Adhemar Bonnet +1A"), find the dictionary (adhemar_bonnet_A) which contains that item's stats.
        # This will be used often, may as well make it a function, even if it is inefficient.
        # First check Name2, then check Name. This is so you don't mix up different augment paths.
        # Name is mostly for finding the icon anyway.
        #
        for i,k in enumerate(all_gear):
            gear_name = k["Name2"] if "Name2" in k else k["Name"]
            if name == gear_name:
                return(all_gear[i])
        return(Empty)

    def reset_radio_scrollregion(self, event):
        #
        # Reset the radio frame scrollbar regions when changing jobs
        # Resetting scroll region: https://stackoverflow.com/questions/47008899/tkinter-dynamic-scrollbar-for-a-dynamic-gui-not-updating-with-gui
        #
        # self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        for canvas_frame in [self.main_canvas, self.sub_canvas, self.ranged_canvas, self.ammo_canvas, self.head_canvas, self.neck_canvas, self.ear1_canvas, self.ear2_canvas, self.body_canvas, self.hands_canvas, self.ring1_canvas, self.ring2_canvas, self.back_canvas, self.waist_canvas, self.legs_canvas, self.feet_canvas,]:
            canvas_frame.configure(scrollregion=canvas_frame.bbox("all"))

    def reset_cbox_scrollregion(self, event):
        #
        # Reset the checkbox frame scrollbar regions when changing jobs
        #
        for canvas_frame in [self.main_canvas2, self.sub_canvas2, self.ranged_canvas2, self.ammo_canvas2, self.head_canvas2, self.neck_canvas2, self.ear1_canvas2, self.ear2_canvas2, self.body_canvas2, self.hands_canvas2, self.ring1_canvas2, self.ring2_canvas2, self.back_canvas2, self.waist_canvas2, self.legs_canvas2, self.feet_canvas2,]:
            canvas_frame.configure(scrollregion=canvas_frame.bbox("all"))

    def select_song(self,event):
        #
        # The code starts by showing all items for all slots in order to ensure that the scroll region in each slot is always sufficient for each job individually.
        # After selecting a main job, this function will hide the items that the selected main job can not use.
        #
        if event=="song1":
            self.brd_combo3.configure(values=[k for k in self.song_list if k not in [self.song1.get()]]) # 2nd song shouldnt show first song
            self.brd_combo4.configure(values=[k for k in self.song_list if k not in [self.song1.get(),self.song2.get()]])
            self.brd_combo5.configure(values=[k for k in self.song_list if k not in [self.song1.get(),self.song2.get(),self.song3.get()]])
            self.brd_combo6.configure(values=[k for k in self.song_list if k not in [self.song1.get(),self.song2.get(),self.song3.get(),self.song4.get()]])
            for k in [self.brd_combo3,self.brd_combo4,self.brd_combo5,self.brd_combo6]:
                if self.song1.get()==k.get():
                    k.set(value="None")
        elif event=="song2":
            self.brd_combo4.configure(values=[k for k in self.song_list if k not in [self.song1.get(),self.song2.get()]])
            self.brd_combo5.configure(values=[k for k in self.song_list if k not in [self.song1.get(),self.song2.get(),self.song3.get()]])
            self.brd_combo6.configure(values=[k for k in self.song_list if k not in [self.song1.get(),self.song2.get(),self.song3.get(),self.song4.get()]])
            for k in [self.brd_combo4,self.brd_combo5,self.brd_combo6]:
                if self.song2.get()==k.get():
                    k.set(value="None")
        elif event=="song3":
            self.brd_combo5.configure(values=[k for k in self.song_list if k not in [self.song1.get(),self.song2.get(),self.song3.get()]])
            self.brd_combo6.configure(values=[k for k in self.song_list if k not in [self.song1.get(),self.song2.get(),self.song3.get(),self.song4.get()]])
            for k in [self.brd_combo5,self.brd_combo6]:
                if self.song3.get()==k.get():
                    k.set(value="None")
        elif event=="song4":
            self.brd_combo6.configure(values=[k for k in self.song_list if k not in [self.song1.get(),self.song2.get(),self.song3.get(),self.song4.get()]])
            for k in [self.brd_combo6,self.brd_combo6]:
                if self.song4.get()==k.get():
                    k.set(value="None")

    def select_roll(self,event):
        #
        #
        #
        if event=="roll1" and self.roll1_combo.get()==self.roll2_combo.get():
            self.roll2_combo.set(value="None")

        if event=="roll2" and self.roll2_combo.get()==self.roll1_combo.get():
            self.roll1_combo.set(value="None")

    def select_bubble(self,event):
        #
        #
        #
        if event=="indi":
            for k in [self.geo_geo, self.geo_entrust]:
                if self.geo_indi.get().split("-")[-1]==k.get().split("-")[-1]:
                    k.set("None")
        if event=="geo":
            for k in [self.geo_indi, self.geo_entrust]:
                if self.geo_geo.get().split("-")[-1]==k.get().split("-")[-1]:
                    k.set("None")
        if event=="entrust":
            for k in [self.geo_indi, self.geo_geo]:
                if self.geo_entrust.get().split("-")[-1]==k.get().split("-")[-1]:
                    k.set("None")

    def collect_buffs(self,):
        #
        # Create a dictionary containing the sum of all buffs from WHM/Food/BRD/COR/GEO
        # We read in the buffs.py file to use the list of buff names and their potencies.
        #
        # Define BRD buffs
        brd_on = self.brd_on.get()
        song1 = self.song1.get()
        song2 = self.song2.get()
        song3 = self.song3.get()
        song4 = self.song4.get()
        song5 = self.song5.get()
        active_songs = [song1, song2, song3, song4, song5]
        marcato = self.marcato_on.get()
        soulvoice = self.soulvoice_on.get()
        nsong = int(self.brd_potency.get().split()[-1])

        # Minuets cap at Songs+8
        brd_min5_attack  = ((brd["Minuet V"]["Attack"][0] + min(8,nsong)*brd["Minuet V"]["Attack"][1])*(1.0+0.5*marcato if song1=="Minuet V" else 1.0) if "Minuet V" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_min4_attack  = ((brd["Minuet IV"]["Attack"][0] + min(8,nsong)*brd["Minuet IV"]["Attack"][1])*(1.0+0.5*marcato if song1=="Minuet IV" else 1.0) if "Minuet IV" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_min3_attack  = ((brd["Minuet III"]["Attack"][0] + min(8,nsong)*brd["Minuet III"]["Attack"][1])*(1.0+0.5*marcato if song1=="Minuet III" else 1.0) if "Minuet III" in active_songs else 0)*(1.0+1.0*soulvoice)

        # Honor March caps at Songs+4
        brd_hm_accuracy        = ((brd["Honor March"]["Accuracy"][0] + min(4,nsong)*brd["Honor March"]["Accuracy"][1])*(1.0+0.5*marcato if song1=="Honor March" else 1.0) if "Honor March" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_hm_rangedaccuracy  = ((brd["Honor March"]["Ranged Accuracy"][0] + min(4,nsong)*brd["Honor March"]["Ranged Accuracy"][1])*(1.0+0.5*marcato if song1=="Honor March" else 1.0) if "Honor March" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_hm_attack          = ((brd["Honor March"]["Attack"][0] + min(4,nsong)*brd["Honor March"]["Attack"][1])*(1.0+0.5*marcato if song1=="Honor March" else 1.0) if "Honor March" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_hm_rangedattack    = ((brd["Honor March"]["Ranged Attack"][0] + min(4,nsong)*brd["Honor March"]["Ranged Attack"][1])*(1.0+0.5*marcato if song1=="Honor March" else 1.0) if "Honor March" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_hm_haste           = ((brd["Honor March"]["Magic Haste"][0] + min(4,nsong)*brd["Honor March"]["Magic Haste"][1])*(1.0+0.5*marcato if song1=="Honor March" else 1.0) if "Honor March" in active_songs else 0)*(1.0+1.0*soulvoice)

        # Madrigals cap at Songs+9
        brd_swordmad_accuracy  = ((brd["Sword Madrigal"]["Accuracy"][0] + min(9,nsong)*brd["Sword Madrigal"]["Accuracy"][1])*(1.0+0.5*marcato if song1=="Sword Madrigal" else 1.0) if "Sword Madrigal" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_blademad_accuracy  = ((brd["Blade Madrigal"]["Accuracy"][0] + min(9,nsong)*brd["Blade Madrigal"]["Accuracy"][1])*(1.0+0.5*marcato if song1=="Blade Madrigal" else 1.0) if "Blade Madrigal" in active_songs else 0)*(1.0+1.0*soulvoice)

        # Madrigals cap at Songs+8
        brd_hunter_rangedaccuracy  = ((brd["Hunter's Prelude"]["Ranged Accuracy"][0] + min(8,nsong)*brd["Hunter's Prelude"]["Ranged Accuracy"][1])*(1.0+0.5*marcato if song1=="Hunter's Prelude" else 1.0) if "Hunter's Prelude" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_archer_rangedaccuracy  = ((brd["Archer's Prelude"]["Ranged Accuracy"][0] + min(8,nsong)*brd["Archer's Prelude"]["Ranged Accuracy"][1])*(1.0+0.5*marcato if song1=="Archer's Prelude" else 1.0) if "Archer's Prelude" in active_songs else 0)*(1.0+1.0*soulvoice)

        # Marches cap at Songs+8
        brd_vmarch_haste  = ((brd["Victory March"]["Magic Haste"][0] + min(8,nsong)*brd["Victory March"]["Magic Haste"][1])*(1.0+0.5*marcato if song1=="Victory March" else 1.0) if "Victory March" in active_songs else 0)*(1.0+1.0*soulvoice)

        brd_amarch_haste  = ((brd["Advancing March"]["Magic Haste"][0] + min(8,nsong)*brd["Advancing March"]["Magic Haste"][1])*(1.0+0.5*marcato if song1=="Advancing March" else 1.0) if "Advancing March" in active_songs else 0)*(1.0+1.0*soulvoice)


        brd_attack = brd_on*int(brd_min5_attack + brd_min4_attack + brd_min3_attack + brd_hm_attack)
        brd_accuracy = brd_on*int(brd_hm_accuracy + brd_swordmad_accuracy + brd_blademad_accuracy)
        brd_rangedaccuracy = brd_on*int(brd_hm_rangedaccuracy + brd_hunter_rangedaccuracy + brd_archer_rangedaccuracy)
        brd_haste = brd_on*(brd_vmarch_haste + brd_amarch_haste + brd_hm_haste)

        # Etudes cap at Songs+9
        brd_str = ((brd["Sinewy Etude"]["STR"][0] + min(9,nsong)*brd["Sinewy Etude"]["STR"][1])*(1.0+0.5*marcato if song1=="Sinewy Etude" else 1.0) if "Sinewy Etude" in active_songs else 0)*(1.0+1.0*soulvoice) + ((brd["Herculean Etude"]["STR"][0] + min(9,nsong)*brd["Herculean Etude"]["STR"][1])*(1.0+0.5*marcato if song1=="Herculean Etude" else 1.0) if "Herculean Etude" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_dex = ((brd["Dextrous Etude"]["DEX"][0] + min(9,nsong)*brd["Dextrous Etude"]["DEX"][1])*(1.0+0.5*marcato if song1=="Dextrous Etude" else 1.0) if "Dextrous Etude" in active_songs else 0)*(1.0+1.0*soulvoice) + ((brd["Uncanny Etude"]["DEX"][0] + min(9,nsong)*brd["Uncanny Etude"]["DEX"][1])*(1.0+0.5*marcato if song1=="Uncanny Etude" else 1.0) if "Uncanny Etude" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_vit = ((brd["Vivavious Etude"]["VIT"][0] + min(9,nsong)*brd["Vivavious Etude"]["VIT"][1])*(1.0+0.5*marcato if song1=="Vivavious Etude" else 1.0) if "Vivavious Etude" in active_songs else 0)*(1.0+1.0*soulvoice) + ((brd["Vital Etude"]["VIT"][0] + min(9,nsong)*brd["Vital Etude"]["VIT"][1])*(1.0+0.5*marcato if song1=="Vital Etude" else 1.0) if "Vital Etude" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_agi = ((brd["Quick Etude"]["AGI"][0] + min(9,nsong)*brd["Quick Etude"]["AGI"][1])*(1.0+0.5*marcato if song1=="Quick Etude" else 1.0) if "Quick Etude" in active_songs else 0)*(1.0+1.0*soulvoice) + ((brd["Swift Etude"]["AGI"][0] + min(9,nsong)*brd["Swift Etude"]["AGI"][1])*(1.0+0.5*marcato if song1=="Swift Etude" else 1.0) if "Swift Etude" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_int = ((brd["Learned Etude"]["INT"][0] + min(9,nsong)*brd["Learned Etude"]["INT"][1])*(1.0+0.5*marcato if song1=="Learned Etude" else 1.0) if "Learned Etude" in active_songs else 0)*(1.0+1.0*soulvoice) + ((brd["Sage Etude"]["INT"][0] + min(9,nsong)*brd["Sage Etude"]["INT"][1])*(1.0+0.5*marcato if song1=="Sage Etude" else 1.0) if "Sage Etude" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_mnd = ((brd["Spirited Etude"]["MND"][0] + min(9,nsong)*brd["Spirited Etude"]["MND"][1])*(1.0+0.5*marcato if song1=="Spirited Etude" else 1.0) if "Spirited Etude" in active_songs else 0)*(1.0+1.0*soulvoice) + ((brd["Logical Etude"]["MND"][0] + min(9,nsong)*brd["Logical Etude"]["MND"][1])*(1.0+0.5*marcato if song1=="Logical Etude" else 1.0) if "Logical Etude" in active_songs else 0)*(1.0+1.0*soulvoice)
        brd_chr = ((brd["Enchanting Etude"]["CHR"][0] + min(9,nsong)*brd["Enchanting Etude"]["CHR"][1])*(1.0+0.5*marcato if song1=="Enchanting Etude" else 1.0) if "Enchanting Etude" in active_songs else 0)*(1.0+1.0*soulvoice) + ((brd["Bewitching Etude"]["CHR"][0] + min(9,nsong)*brd["Bewitching Etude"]["CHR"][1])*(1.0+0.5*marcato if song1=="Bewitching Etude" else 1.0) if "Bewitching Etude" in active_songs else 0)*(1.0+1.0*soulvoice)

        # Define COR buffs: Total bonus stat obtained from a set potency roll with "Rolls +nroll" bonus from gear.

        roman = {"I":1,"II":2,"III":3,"IV":4,"V":5,"VI":6,"VII":7,"VIII":8,"IX":9,"X":10,"XI":11}
        
        cor_on = self.cor_on.get()
        roll1 = self.roll1.get()
        roll2 = self.roll2.get()
        active_rolls = [roll1, roll2]
        nroll = int(self.cor_potency.get().split()[-1])
        job_bonus = self.job_bonus.get()
        roll_potency1 = str(roman[self.roll1_value.get()])
        roll_potency2 = str(roman[self.roll2_value.get()])
        cor_sam = cor["Samurai"]["Store TP"][0].get(roll_potency1 if "Samurai"==active_rolls[0] else roll_potency2 if "Samurai"==active_rolls[1] else 0,0) + nroll*cor["Samurai"]["Store TP"][1] + job_bonus*cor["Samurai"]["Store TP"][2] if "Samurai" in active_rolls else 0
        cor_chaos = cor["Chaos"]["Attack%"][0].get(roll_potency1 if "Chaos"==active_rolls[0] else roll_potency2 if "Chaos"==active_rolls[1] else 0,0) + nroll*cor["Chaos"]["Attack%"][1] + job_bonus*cor["Chaos"]["Attack%"][2] if "Chaos" in active_rolls else 0
        cor_hunter = cor["Hunter"]["Accuracy"][0].get(roll_potency1 if "Hunter's"==active_rolls[0] else roll_potency2 if "Hunter's"==active_rolls[1] else 0,0) + nroll*cor["Hunter"]["Accuracy"][1] + job_bonus*cor["Hunter"]["Accuracy"][2] if "Hunter's" in active_rolls else 0
        cor_rogue = cor["Rogue"]["Crit Rate"][0].get(roll_potency1 if "Rogue's"==active_rolls[0] else roll_potency2 if "Rogue's"==active_rolls[1] else 0,0) + nroll*cor["Rogue"]["Crit Rate"][1] + job_bonus*cor["Rogue"]["Crit Rate"][2] if "Rogue's" in active_rolls else 0
        cor_wizard = cor["Wizard"]["Magic Attack"][0].get(roll_potency1 if "Wizard's"==active_rolls[0] else roll_potency2 if "Wizard's"==active_rolls[1] else 0,0) + nroll*cor["Wizard"]["Magic Attack"][1] + job_bonus*cor["Wizard"]["Magic Attack"][2] if "Wizard's" in active_rolls else 0
        cor_warlock = cor["Warlock"]["Magic Accuracy"][0].get(roll_potency1 if "Warlock's"==active_rolls[0] else roll_potency2 if "Warlock's"==active_rolls[1] else 0,0) + nroll*cor["Warlock"]["Magic Accuracy"][1] + job_bonus*cor["Warlock"]["Magic Accuracy"][2] if "Warlock's" in active_rolls else 0
        cor_fighter = cor["Fighter"]["DA"][0].get(roll_potency1 if "Fighter's"==active_rolls[0] else roll_potency2 if "Fighter's"==active_rolls[1] else 0,0) + nroll*cor["Fighter"]["DA"][1] + job_bonus*cor["Fighter"]["DA"][2] if "Fighter's" in active_rolls else 0
        cor_monks = cor["Monk"]["Subtle Blow"][0].get(roll_potency1 if "Monk's"==active_rolls[0] else roll_potency2 if "Monk's"==active_rolls[1] else 0,0) + nroll*cor["Monk"]["Subtle Blow"][1] + job_bonus*cor["Monk"]["Subtle Blow"][2] if "Monk's" in active_rolls else 0
        cor_tact = cor["Tactician"]["Regain"][0].get(roll_potency1 if "Tactician's"==active_rolls[0] else roll_potency2 if "Tactician's"==active_rolls[1] else 0,0) + nroll*cor["Tactician"]["Regain"][1] + job_bonus*cor["Tactician"]["Regain"][2] if "Tactician's" in active_rolls else 0
        crooked = self.crooked_on.get()
        cor_stp = cor_on*cor_sam*(1.0+0.2*crooked if roll1=="Samurai" else 1.0)
        cor_attack = cor_on*cor_chaos*(1.0+0.2*crooked if roll1=="Chaos" else 1.0)
        cor_accuracy = cor_on*cor_hunter*(1.0+0.2*crooked if roll1=="Hunter's" else 1.0)
        cor_critrate = cor_on*cor_rogue*(1.0+0.2*crooked if roll1=="Rogue's" else 1.0)
        cor_magicattack = cor_on*cor_wizard*(1.0+0.2*crooked if roll1=="Wizard's" else 1.0)
        cor_da = cor_on*cor_fighter*(1.0+0.2*crooked if roll1=="Fighter's" else 1.0)
        cor_regain = cor_on*cor_tact*(1.0+0.2*crooked if roll1=="Tactician's" else 1.0)
        cor_subtleblow = cor_on*cor_monks*(1.0+0.2*crooked if roll1=="Monk's" else 1.0)
        cor_magicaccuracy = cor_on*cor_warlock*(1.0+0.2*crooked if roll1=="Warlock's" else 1.0)


        # Define GEO buffs
        geo_on = self.geo_on.get()
        nbubble = int(self.geo_potency.get().split()[-1])
        indibubble = self.indispell.get()
        geobubble = self.geospell.get()
        geomancy_potency = float(self.geomancy_potency.get())/100
        geomancy_potency = 0 if geomancy_potency < 0 else geomancy_potency
        geomancy_potency = 1 if geomancy_potency > 1 else geomancy_potency
        active_bubbles = [indibubble.split("-")[-1],geobubble.split("-")[-1]]
        entrust = self.entrustspell.get()
        blazeofglory = self.bog_on.get()
        bolster = self.bolster_on.get()
        geo_attack = geo_on*((geo["Fury"]["Attack%"][0] + nbubble*geo["Fury"]["Attack%"][1] if "Fury" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-Fury"))*(1.0+1.0*bolster) + (geo["Fury"]["Attack%"][0] if entrust == "Entrust-Fury" else 0))
        geo_accuracy = geo_on*((geo["Precision"]["Accuracy"][0] + nbubble*geo["Precision"]["Accuracy"][1] if "Precision" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-Precision"))*(1.0+1.0*bolster) + (geo["Precision"]["Accuracy"][0] if entrust == "Entrust-Precision" else 0))
        geo_haste = geo_on*((geo["Haste"]["Magic Haste"][0] + nbubble*geo["Haste"]["Magic Haste"][1] if "Haste" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-Haste"))*(1.0+1.0*bolster) + (geo["Haste"]["Magic Haste"][0] if entrust == "Entrust-Haste" else 0))
        geo_magicaccuracy = geo_on*((geo["Focus"]["Magic Accuracy"][0] + nbubble*geo["Focus"]["Magic Accuracy"][1] if "Focus" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-Focus"))*(1.0+1.0*bolster) + (geo["Focus"]["Magic Accuracy"][0] if entrust == "Entrust-Focus" else 0))
        geo_magicattack = geo_on*((geo["Acumen"]["Magic Attack"][0] + nbubble*geo["Acumen"]["Magic Attack"][1] if "Acumen" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-Acumen"))*(1.0+1.0*bolster) + (geo["Acumen"]["Magic Attack"][0] if entrust == "Entrust-Acumen" else 0))
        geo_str = geo_on*((geo["STR"]["STR"][0] + nbubble*geo["STR"]["STR"][1] if "STR" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-STR"))*(1.0+1.0*bolster) + (geo["STR"]["STR"][0] if entrust == "Entrust-STR" else 0))
        geo_dex = geo_on*((geo["DEX"]["DEX"][0] + nbubble*geo["DEX"]["DEX"][1] if "DEX" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-DEX"))*(1.0+1.0*bolster) + (geo["DEX"]["DEX"][0] if entrust == "Entrust-DEX" else 0))
        geo_vit = geo_on*((geo["VIT"]["VIT"][0] + nbubble*geo["VIT"]["VIT"][1] if "VIT" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-VIT"))*(1.0+1.0*bolster) + (geo["VIT"]["VIT"][0] if entrust == "Entrust-VIT" else 0))
        geo_agi = geo_on*((geo["AGI"]["AGI"][0] + nbubble*geo["AGI"]["AGI"][1] if "AGI" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-AGI"))*(1.0+1.0*bolster) + (geo["AGI"]["AGI"][0] if entrust == "Entrust-AGI" else 0))
        geo_int = geo_on*((geo["INT"]["INT"][0] + nbubble*geo["INT"]["INT"][1] if "INT" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-INT"))*(1.0+1.0*bolster) + (geo["INT"]["INT"][0] if entrust == "Entrust-INT" else 0))
        geo_mnd = geo_on*((geo["MND"]["MND"][0] + nbubble*geo["MND"]["MND"][1] if "MND" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-MND"))*(1.0+1.0*bolster) + (geo["MND"]["MND"][0] if entrust == "Entrust-MND" else 0))
        geo_chr = geo_on*((geo["CHR"]["CHR"][0] + nbubble*geo["CHR"]["CHR"][1] if "CHR" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-CHR"))*(1.0+1.0*bolster) + (geo["CHR"]["CHR"][0] if entrust == "Entrust-CHR" else 0))

        frailty_potency = (geomancy_potency)*(geo_on*((geo["Frailty"]["Defense"][0] + nbubble*geo["Frailty"]["Defense"][1] if "Frailty" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-Frailty"))*(1.0+1.0*bolster) + (geo["Frailty"]["Defense"][0] if entrust == "Entrust-Frailty" else 0)))
        malaise_potency = (geomancy_potency)*(geo_on*((geo["Malaise"]["Magic Defense"][0] + nbubble*geo["Malaise"]["Magic Defense"][1] if "Malaise" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-Malaise"))*(1.0+1.0*bolster) + (geo["Malaise"]["Magic Defense"][0] if entrust == "Entrust-Malaise" else 0)))
        torpor_potency = (geomancy_potency)*(geo_on*((geo["Torpor"]["Evasion"][0] + nbubble*geo["Torpor"]["Evasion"][1] if "Torpor" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-Torpor"))*(1.0+1.0*bolster) + (geo["Torpor"]["Evasion"][0] if entrust == "Entrust-Torpor" else 0)))
        languor_potency = (geomancy_potency)*(geo_on*((geo["Languor"]["Magic Evasion"][0] + nbubble*geo["Languor"]["Magic Evasion"][1] if "Languor" in active_bubbles else 0)*(1.0+0.5*blazeofglory*(geobubble=="Geo-Languor"))*(1.0+1.0*bolster) + (geo["Languor"]["Magic Evasion"][0] if entrust == "Entrust-Languor" else 0)))

        # Define buffs from white magic:
        whm_on = self.whm_on.get()

        whm_haste = whm_on*(whm["Haste"]["Magic Haste"]*(self.whm_spell2.get() == "Haste") + whm["Haste II"]["Magic Haste"]*(self.whm_spell2.get() == "Haste II"))
        whm_str   = whm_on*(whm["Boost-STR"]["STR"]*(self.whm_spell3.get()=="Boost-STR") + 7*(self.whm_spell4.get()=="Firestorm II")    + 3*(self.whm_spell4.get()=="Voidstorm II"))
        whm_dex   = whm_on*(whm["Boost-DEX"]["DEX"]*(self.whm_spell3.get()=="Boost-DEX") + 7*(self.whm_spell4.get()=="Thunderstorm II") + 3*(self.whm_spell4.get()=="Voidstorm II"))
        whm_vit   = whm_on*(whm["Boost-VIT"]["VIT"]*(self.whm_spell3.get()=="Boost-VIT") + 7*(self.whm_spell4.get()=="Sandstorm II")    + 3*(self.whm_spell4.get()=="Voidstorm II"))
        whm_agi   = whm_on*(whm["Boost-AGI"]["AGI"]*(self.whm_spell3.get()=="Boost-AGI") + 7*(self.whm_spell4.get()=="Windstorm II")    + 3*(self.whm_spell4.get()=="Voidstorm II"))
        whm_int   = whm_on*(whm["Boost-INT"]["INT"]*(self.whm_spell3.get()=="Boost-INT") + 7*(self.whm_spell4.get()=="Hailstorm II")    + 3*(self.whm_spell4.get()=="Voidstorm II"))
        whm_mnd   = whm_on*(whm["Boost-MND"]["MND"]*(self.whm_spell3.get()=="Boost-MND") + 7*(self.whm_spell4.get()=="Rainstorm II")    + 3*(self.whm_spell4.get()=="Voidstorm II"))
        whm_chr   = whm_on*(whm["Boost-CHR"]["CHR"]*(self.whm_spell3.get()=="Boost-CHR") + 7*(self.whm_spell4.get()=="Aurorastorm II")  + 3*(self.whm_spell4.get()=="Voidstorm II"))


        buffs = {"brd": {"Attack": brd_attack, "Accuracy": brd_accuracy, "Ranged Accuracy": brd_rangedaccuracy, "Ranged Attack": brd_attack,"Magic Haste":brd_haste, "STR":brd_str,"DEX":brd_dex, "VIT":brd_vit, "AGI":brd_agi, "INT":brd_int, "MND":brd_mnd, "CHR":brd_chr,},
                    "cor": {"Attack%": cor_attack, "Ranged Attack%": cor_attack, "Store TP": cor_stp, "Accuracy": cor_accuracy, "Magic Attack": cor_magicattack, "Magic Accuracy":cor_magicaccuracy, "DA":cor_da, "Crit Rate": cor_critrate, "Subtle Blow":cor_subtleblow, "Regain":cor_regain},
                    "whm": {"Magic Haste": whm_haste, "STR":whm_str,"DEX":whm_dex, "VIT":whm_vit, "AGI":whm_agi, "INT":whm_int, "MND":whm_mnd, "CHR":whm_chr},
                    "geo": {"Attack%": geo_attack, "Ranged Attack%": geo_attack, "Accuracy": geo_accuracy, "Ranged Accuracy":geo_accuracy, "Magic Accuracy":geo_magicaccuracy, "Magic Attack":geo_magicattack, "STR":geo_str,"DEX":geo_dex, "VIT":geo_vit, "AGI":geo_agi, "INT":geo_int, "MND":geo_mnd, "CHR":geo_chr,"Magic Haste":geo_haste},
                    "food":{},} # Food is added below

        # Define Dia
        dia_dictionary = {"None":0,
                            "Dia": 104./1024+(28./1024*self.lightshot_on.get()),
                            "Dia II": 156./1024+(28./1024*self.lightshot_on.get()),
                            "Dia III": 208./1024+(28./1024*self.lightshot_on.get()),
        }
        dia_potency = dia_dictionary[self.whm_spell1.get()] if whm_on else 0.0



        for food in all_food:
            if food["Name"] == self.active_food.get():
                buffs["food"]["Food Attack"] = food.get("Attack",0)
                buffs["food"]["Food Ranged Attack"] = food.get("Ranged Attack",0)
                buffs["food"]["Accuracy"] = food.get("Accuracy",0)
                buffs["food"]["Ranged Accuracy"] = food.get("Ranged Accuracy",0)
                buffs["food"]["Magic Accuracy"] = food.get("Magic Accuracy",0)
                buffs["food"]["Magic Attack"] = food.get("Magic Attack",0)
                buffs["food"]["DA"] = food.get("DA",0)
                buffs["food"]["Weapon Skill Damage"] = food.get("Weapon Skill Damage",0)
                buffs["food"]["STR"] = food.get("STR",0)
                buffs["food"]["DEX"] = food.get("DEX",0)
                buffs["food"]["VIT"] = food.get("VIT",0)
                buffs["food"]["AGI"] = food.get("AGI",0)
                buffs["food"]["INT"] = food.get("INT",0)
                buffs["food"]["MND"] = food.get("MND",0)
                buffs["food"]["CHR"] = food.get("CHR",0)


        # Define your enemy stats based on the enemy tab.
        enemy = create_enemy({
            "Name":self.selected_enemy.get(),
            "Location":self.enemy_location_var.get(),
            "Level":self.enemy_level_entry.get(),
            "AGI":self.enemy_agi.get(),
            "VIT":self.enemy_vit.get(),
            "INT":self.enemy_int.get(),
            "MND":self.enemy_mnd.get(),
            "Defense":self.enemy_defense.get(),
            "Magic Defense":self.enemy_magic_defense.get(),
            "Evasion":self.enemy_evasion.get(),
            "Magic Evasion":self.enemy_magic_evasion.get(),
            })

        # Decrease enemy stats based on debuffs selected.
        # TODO: Box Step, DEF/EVA- weapon skills.
        enemy_reduced_defense = enemy.stats["Defense"] * (1-dia_potency) * (1-frailty_potency) * (1 - 0.2*self.angon_value.get())
        enemy.stats["Defense"] = enemy_reduced_defense if enemy_reduced_defense > 1 else 1 # Minimum enemy defense value is 1 for the purposes of this code.
        enemy.stats["Magic Defense"] = (enemy.stats["Magic Defense"] - malaise_potency) if (enemy.stats["Magic Defense"]- malaise_potency) > -50 else -50
        enemy.stats["Evasion"] -= (torpor_potency + 280*self.distract3_value.get())
        enemy.stats["Magic Evasion"] -= languor_potency

        # TODO: update tooltip for enemy stats when changing Dia and Geomany comboboxes

        return(buffs, enemy)

    def run_optimize(self,trigger):
        #
        # Test a given gearset, either with a quick look or an optimization
        #
        abilities = {"Magic Burst":self.magic_burst_value.get(),
                     "Warcry":self.warcry_value.get(),
                     "Berserk":self.berserk_value.get(),
                     "Aggressor":self.aggressor_value.get(),
                     "Mighty Strikes":self.mighty_strikes_value.get(),
                     "Focus":self.focus_value.get(),
                     "Footwork":self.footwork_value.get(),
                     "Impetus":self.impetus_value.get(),
                     "Manafont":self.manafont_value.get(),
                     "Manawell":self.manawell_value.get(),
                     "Chainspell":self.chainspell_value.get(),
                     "Composure":self.composure_value.get(),
                     "Conspirator":self.conspirator_value.get(),
                     "Divine Emblem":self.divine_emblem_value.get(),
                     "Enlight II":self.enlight_value.get(),
                     "Last Resort":self.last_resort_value.get(),
                     "Endark II":self.endark_value.get(),
                     "Sharpshot":self.sharpshot_value.get(),
                     "Barrage":self.barrage_value.get(),
                     "Velocity Shot":self.velocity_shot_value.get(),
                     "Double Shot":self.double_shot_value.get(),
                     "Hover Shot":self.hover_shot_value.get(),
                     "Hasso":self.hasso_value.get(),
                     "Sange":self.sange_value.get(),
                     "Shell V":self.shell5_on.get(),
                     "Innin":self.innin_value.get(),
                     "Futae":self.futae_value.get(),
                     "Nature's Meditation":self.natures_meditation_value.get(),
                     "Triple Shot":self.triple_shot_value.get(),
                     "Building Flourish":self.building_flourish_value.get(),
                     "Climactic Flourish":self.climactic_flourish_value.get(),
                     "Striking Flourish":self.striking_flourish_value.get(),
                     "Ternary Flourish":self.ternary_flourish_value.get(),
                     "Saber Dance":self.saber_dance_value.get(),
                     "Storm spell":self.whm_spell4.get(),
                     "Ebullience":self.ebullience_value.get(),
                     "Enlightenment":self.enlightenment_value.get(),
                     "Swordplay":self.swordplay_value.get(),
                     "True Shot":self.true_shot_value.get(),
                     "Sneak Attack":self.sneak_attack_value.get(),
                     "Trick Attack":self.trick_attack_value.get(),
                     "Blood Rage":self.blood_rage_value.get(),
                     "Aftermath":self.am_level.get(),
                     "Haste Samba":self.haste_samba_value.get(),
                     "Klimaform":self.klimaform_value.get(),
                     "Distract III":self.distract3_value.get()}


        gearset = {
            "main":eval(self.selected_main.get()),
            "sub":eval(self.selected_sub.get()),
            "ranged":eval(self.selected_ranged.get()),
            "ammo":eval(self.selected_ammo.get()),
            "head":eval(self.selected_head.get()),
            "neck":eval(self.selected_neck.get()),
            "ear1":eval(self.selected_ear1.get()),
            "ear2":eval(self.selected_ear2.get()),
            "body":eval(self.selected_body.get()),
            "hands":eval(self.selected_hands.get()),
            "ring1":eval(self.selected_ring1.get()),
            "ring2":eval(self.selected_ring2.get()),
            "back":eval(self.selected_back.get()),
            "waist":eval(self.selected_waist.get()),
            "legs":eval(self.selected_legs.get()),
            "feet":eval(self.selected_feet.get()),
        }

        buffs, enemy = self.collect_buffs() # The enemy is defined with the buffs to easily handle debuffs like Dia and Frailty

        player = create_player(self.mainjob.get().lower(), self.subjob.get().lower(), self.masterlevel.get(), gearset, buffs, abilities)

        effective_tp = (self.tp2.get() + self.tp1.get()) / 2 + player.stats.get("TP Bonus",0)
        effective_tp = 1000 if effective_tp < 1000 else 3000 if effective_tp > 3000 else effective_tp

        spell_name = self.spell_name.get()

        if "ton: " in spell_name:
            spell_type = "Ninjutsu"
        elif " Shot"==spell_name[-5:]:
            spell_type = "Quick Draw"
        elif "Banish" in spell_name or "Holy" in spell_name:
            spell_type = "Divine Magic"
        elif spell_name in ["Ranged Attack","Barrage"]:
            spell_type = "Ranged Attack"
        else:
            spell_type = "Elemental Magic"

        ws_name = self.ws_name.get()

        if trigger in ["quicklook ws","quicklook spell"]:
            if trigger=="quicklook ws":
                if ws_name=="None":
                    print("No weapon skill selected.")
                    return
                ws_type = "ranged" if ws_name in self.ranged_ws else "melee"
                outputs = average_ws(player, enemy, ws_name, effective_tp, ws_type, "Damage dealt")
            elif trigger=="quicklook spell":
                if spell_name=="None":
                    print("No spell selected.")
                    return
                outputs = cast_spell(player, enemy, spell_name, spell_type, "Damage dealt")

            avg_dmg = outputs[1][0]
            avg_tp = outputs[1][1]
            self.quickdamage.configure(text=f"{'Average Damage = ':>17s}{avg_dmg:>9.1f}")
            self.quicktp.configure(text=f"{'Average TP = ':>17s}{avg_tp:>9.1f}")

        elif trigger=="quicklook tp":
            outputs = average_attack_round(player, enemy, self.tp0.get(), self.tp1.get(),"Time to WS")
            avg_time = outputs[0]
            avg_tp = outputs[1][1]
            self.quickdamage.configure(text=f"{'Time per WS = ':>17}{avg_time:>7.3f} s")
            self.quicktp.configure(text=f"{'Avg TP/Round = ':>17}{avg_tp:>9.1f}")

        elif trigger=="stats":
            player = create_player(self.mainjob.get().lower(), self.subjob.get().lower(), self.masterlevel.get(), gearset, buffs, abilities)
            s = ["STR","DEX","VIT","AGI","INT","MND","CHR","Accuracy1","Accuracy2","Attack1","Attack2","Ranged Accuracy","Ranged Attack","DA","TA","QA","Store TP","Weapon Skill Damage","Double Shot","Triple Shot","Quad Shot","Gear Haste","Magic Haste","JA Haste","Dual Wield","Delay Reduction"]
            # for stat in s:
            #     print(stat+":",player.stats.get(stat,0))
            print("======================= Player stats =======================")
            for stat in player.stats:
                print(f"{stat:>30s}  =  {player.stats[stat]}")
            print("============================================================")
            print("======================= Enemy  stats =======================")
            for stat in enemy.stats:
                print(f"{stat:>15s}  =  {enemy.stats[stat]}")
            print("============================================================")

        if "run" in trigger:
            # Run the set optimizer.
            
            conditions = {"PDT":int(self.pdt_req.get()) if int(self.pdt_req.get()) <= 100 else 100,"MDT":int(self.mdt_req.get()) if int(self.mdt_req.get()) <= 100 else 100}
            # conditions["PDT"] = conditions["PDT"] * -1 if conditions["PDT"] > 0 else conditions["PDT"] # Allow the user to input positive or negative values to avoid confusion.
            # conditions["MDT"] = conditions["MDT"] * -1 if conditions["MDT"] > 0 else conditions["MDT"]

            cbox_lists = {"main":[self.x_main2,self.x_main2_var],
                            "sub":[self.x_sub2,self.x_sub2_var],
                            "ranged":[self.x_ranged2,self.x_ranged2_var],
                            "ammo":[self.x_ammo2,self.x_ammo2_var],
                            "head":[self.x_head2,self.x_head2_var],
                            "neck":[self.x_neck2,self.x_neck2_var],
                            "ear1":[self.x_ear12,self.x_ear12_var],
                            "ear2":[self.x_ear22,self.x_ear22_var],
                            "body":[self.x_body2,self.x_body2_var],
                            "hands":[self.x_hands2,self.x_hands2_var],
                            "ring1":[self.x_ring12,self.x_ring12_var],
                            "ring2":[self.x_ring22,self.x_ring22_var],
                            "back":[self.x_back2,self.x_back2_var],
                            "waist":[self.x_waist2,self.x_waist2_var],
                            "legs":[self.x_legs2,self.x_legs2_var],
                            "feet":[self.x_feet2,self.x_feet2_var],}


            check_gear = {"main":[],"sub":[],"ranged":[],"ammo":[],"head":[],"neck":[],"ear1":[],"ear2":[],"body":[],"hands":[],"ring1":[],"ring2":[],"back":[],"waist":[],"legs":[],"feet":[]} # Dictionary of lists. The keys are the gear slots, while the values are lists containing item dictionaries of the equipment to be checked.
            check_slots = ["main","sub","ranged","ammo","head","neck","ear1","ear2","body","hands","ring1","ring2","back","waist","legs","feet"] # Slot names to check. This gets filtered later with .remove()
            remove_slots = []
            for slot in check_slots:
                gear_to_check = []
                for i,cbox in enumerate(cbox_lists[slot][0]):
                    item_name = cbox_lists[slot][0][i].cget("text")
                    if cbox_lists[slot][1][i].get():
                        gear_to_check.append(name2dictionary(item_name))
                if len(gear_to_check) > 0:
                    check_gear[slot] = gear_to_check # Appends the whole list, preserving the gear slot order.
                else:
                    remove_slots.append(slot)
            for slot in remove_slots:
                check_slots.remove(slot)

            print_swaps = self.next_best_toggle.get()
            next_best_percent = self.next_best_value.get()

            if sum([len(k) for k in check_slots])==0:
                print("No equipment selected.")
            else:
                if trigger=="run ws":
                    if ws_name=="None":
                        print("No weapon skill selected.")
                        return

                    self.best_player, self.best_output = build_set(self.mainjob.get().lower(), self.subjob.get().lower(), self.masterlevel.get(), buffs, abilities, enemy, ws_name, spell_name, "weapon skill", self.tp0.get(), self.tp1.get(), self.tp2.get(), check_gear, gearset, conditions.get("PDT",100), conditions.get("MDT",100), self.wsmetric.get(), print_swaps, next_best_percent, )
                elif trigger=="run magic":
                    if spell_name=="None":
                        print("No spell selected.")
                        return
                    self.best_player, self.best_output = build_set(self.mainjob.get().lower(), self.subjob.get().lower(), self.masterlevel.get(), buffs, abilities, enemy, ws_name, spell_name, "spell cast", self.tp0.get(), self.tp1.get(), self.tp2.get(), check_gear, gearset, conditions.get("PDT",100), conditions.get("MDT",100), self.spellmetric.get(), print_swaps, next_best_percent, )
                elif trigger=="run tp":
                    self.best_player, self.best_output = build_set(self.mainjob.get().lower(), self.subjob.get().lower(), self.masterlevel.get(), buffs, abilities, enemy, ws_name, spell_name, "attack round", self.tp0.get(), self.tp1.get(), self.tp2.get(), check_gear, gearset, conditions.get("PDT",100), conditions.get("MDT",100), self.tpmetric.get(), print_swaps, next_best_percent, )

                # print(self.best_player.stats)
                # print(self.best_output)
                self.equip_best_set.configure(state="active")


    def select_enemy(self,value):
        #
        # Update the displayed enemy stats in the entry boxes
        #        
        # Read the selected enemy's stats
        new_enemy = preset_enemies[value]

        # Delete the old entries
        self.enemy_agi_entry.delete(0,tk.END)
        self.enemy_vit_entry.delete(0,tk.END)
        self.enemy_int_entry.delete(0,tk.END)
        self.enemy_mnd_entry.delete(0,tk.END)
        self.enemy_level_entry.delete(0,tk.END)
        self.enemy_evasion_entry.delete(0,tk.END)
        self.enemy_defense_entry.delete(0,tk.END)
        self.enemy_magic_evasion_entry.delete(0,tk.END)
        self.enemy_magic_defense_entry.delete(0,tk.END)

        # Insert the new entries
        self.enemy_agi_entry.insert(0,new_enemy["AGI"])
        self.enemy_vit_entry.insert(0,new_enemy["VIT"])
        self.enemy_int_entry.insert(0,new_enemy["INT"])
        self.enemy_mnd_entry.insert(0,new_enemy["MND"])
        self.enemy_level_entry.insert(0,new_enemy["Level"])
        self.enemy_evasion_entry.insert(0,new_enemy["Evasion"])
        self.enemy_defense_entry.insert(0,new_enemy["Defense"])
        self.enemy_magic_evasion_entry.insert(0,new_enemy["Magic Evasion"])
        self.enemy_magic_defense_entry.insert(0,new_enemy["Magic Defense"])

        self.enemy_location_var.set(new_enemy["Location"])

    def get_short_name(self, item_name):
        #
        # Given a full item name, return the abbreviated item name that "//gs export" uses.
        #
        items = np.loadtxt('item_list.txt',dtype=str, delimiter=";", unpack=True)
        short_name = items[2][np.where(np.array([k.lower() for k in items[1]])==item_name.lower())][0]
        return(short_name)

    def export2gearswap(self,):
        #
        # Print the equipped gear in a copy/pastable lua format.
        #
        main = f"main=\"{self.get_short_name(eval(self.selected_main.get())['Name'])}\",\n"
        sub = f"sub=\"{self.get_short_name(eval(self.selected_sub.get())['Name'])}\",\n"
        ranged = f"ranged=\"{self.get_short_name(eval(self.selected_ranged.get())['Name'])}\",\n"
        ammo = f"ammo=\"{self.get_short_name(eval(self.selected_ammo.get())['Name'])}\",\n"
        head = f"head=\"{self.get_short_name(eval(self.selected_head.get())['Name'])}\",\n"
        neck = f"neck=\"{self.get_short_name(eval(self.selected_neck.get())['Name'])}\",\n"
        ear1 = f"ear1=\"{self.get_short_name(eval(self.selected_ear1.get())['Name'])}\",\n"
        ear2 = f"ear2=\"{self.get_short_name(eval(self.selected_ear2.get())['Name'])}\",\n"
        body = f"body=\"{self.get_short_name(eval(self.selected_body.get())['Name'])}\",\n"
        hands = f"hands=\"{self.get_short_name(eval(self.selected_hands.get())['Name'])}\",\n"
        ring1 = f"ring1=\"{self.get_short_name(eval(self.selected_ring1.get())['Name'])}\",\n"
        ring2 = f"ring2=\"{self.get_short_name(eval(self.selected_ring2.get())['Name'])}\",\n"
        back = f"back=\"{self.get_short_name(eval(self.selected_back.get())['Name'])}\",\n"
        waist = f"waist=\"{self.get_short_name(eval(self.selected_waist.get())['Name'])}\",\n"
        legs = f"legs=\"{self.get_short_name(eval(self.selected_legs.get())['Name'])}\",\n"
        feet = f"feet=\"{self.get_short_name(eval(self.selected_feet.get())['Name'])}\",\n"

        line = (main+sub+ranged+ammo+head+body+hands+legs+feet+neck+waist+ear1+ear2+ring1+ring2+back).replace("\"empty\"","Empty")
        # print("==========")
        # print(line)
        # print("==========")

        app.clipboard_clear()
        app.clipboard_append(line)

    def select_spell(self,value):
        print(value)
    def select_aftermath(self,value):
        print(value)

    def update_radio_list(self, frame0):
        #
        # Hide all radio button frames, then show frame0
        #
        frames = [self.main_radio_frame, self.sub_radio_frame, self.ranged_radio_frame, self.ammo_radio_frame, self.head_radio_frame, self.neck_radio_frame, self.ear1_radio_frame, self.ear2_radio_frame, self.body_radio_frame, self.hands_radio_frame, self.ring1_radio_frame, self.ring2_radio_frame, self.back_radio_frame, self.waist_radio_frame, self.legs_radio_frame, self.feet_radio_frame,]
        for frame in frames:
            frame.pack_forget()
        frame0.pack(fill=tk.BOTH, expand=1)
        return

    def update_cbox_list(self, frame0):
        #
        # Hide all checkbox frames, then show frame0
        #
        frames = [self.main_cbox_frame, self.sub_cbox_frame, self.ranged_cbox_frame, self.ammo_cbox_frame, self.head_cbox_frame, self.neck_cbox_frame, self.ear1_cbox_frame, self.ear2_cbox_frame, self.body_cbox_frame, self.hands_cbox_frame, self.ring1_cbox_frame, self.ring2_cbox_frame, self.back_cbox_frame, self.waist_cbox_frame, self.legs_cbox_frame, self.feet_cbox_frame,]
        for frame in frames:
            frame.pack_forget()
        frame0.pack(fill=tk.BOTH, expand=1)
        return

    def item2image(self, item_name):
        #
        # Given an item's name, return that image's icon.
        #
        items = np.loadtxt('item_list.txt',dtype=str, delimiter=";", unpack=True)

        path32 = "icons32/"
        use_32x32_icons = True
        if use_32x32_icons:
            try:
                id = items[0][np.where(np.array([k.lower() for k in items[1]])==item_name.lower())][0]
                img = tk.PhotoImage(file=f"{path32}/{id}.png")
            except IndexError:
                img = tk.PhotoImage(file=f"{path32}/65536.png")
            except FileNotFoundError:
                id = items[0][np.where(np.array([k.lower() for k in items[1]])==item_name.lower())][0]
                print(f"File not found: icons32/{id}.png  ({item_name})")
                img = tk.PhotoImage(file=f"{path32}/65536.png")
        return(img)


    def update_buff_cboxes(self,trigger):
        #
        # Update the buff checkboxes based on selected throughout that frame.
        # For example: Turn off Marcato if Soul Voice is selected.
        #
        if trigger=="brd":
            if not self.brd_on.get():
                self.soulvoice_on.set(value=False)
                self.marcato_on.set(value=False)
                self.soul_voice_cbox.configure(state="disabled")
                self.marcato_cbox.configure(state="disabled")
            else:
                self.soul_voice_cbox.configure(state="enabled")
                self.marcato_cbox.configure(state="enabled")
        if trigger=="marcato":
            self.soulvoice_on.set(value=False)
        elif trigger=="soulvoice":
            self.marcato_on.set(value=False)

        if trigger=="cor":
            if not self.cor_on.get():
                self.crooked_on.set(value=False)
                self.job_bonus.set(value=False)
                self.lightshot_on.set(value=False)
                self.cor_jobbonus_cbox.configure(state="disabled")
                self.crooked_cbox.configure(state="disabled")
                self.lightshot_cbox.configure(state="disabled")
            else:
                self.cor_jobbonus_cbox.configure(state="enabled")
                self.crooked_cbox.configure(state="enabled")
                self.lightshot_cbox.configure(state="enabled")

        if trigger=="geo":
            if not self.geo_on.get():
                self.bog_on.set(value=False)
                self.bolster_on.set(value=False)
                self.blaze_of_glory_cbox.configure(state="disabled")
                self.bolster_cbox.configure(state="disabled")
            else:
                self.blaze_of_glory_cbox.configure(state="enabled")
                self.bolster_cbox.configure(state="enabled")
        if trigger=="bog":
            self.bolster_on.set(value=False)
        elif trigger=="bolster":
            self.bog_on.set(value=False)

        if trigger=="whm":
            if not self.whm_on.get():
                self.shell5_on.set(value=False)
                self.shell5_cbox.configure(state="disabled")
            else:
                self.shell5_on.set(value=True)
                self.shell5_cbox.configure(state="enabled")




    def update_equipment(self,):
        #
        # Equip the gear saved in the self.best_player.gearset dictionary (output from automated set optimizer)
        # Update the equipment images and tooltips
        #
        # Equip each item.
        self.selected_main.set(value=self.best_player.gearset["main"])
        self.selected_sub.set(value=self.best_player.gearset["sub"])
        self.selected_ranged.set(value=self.best_player.gearset["ranged"])
        self.selected_ammo.set(value=self.best_player.gearset["ammo"])
        self.selected_head.set(value=self.best_player.gearset["head"])
        self.selected_neck.set(value=self.best_player.gearset["neck"])
        self.selected_ear1.set(value=self.best_player.gearset["ear1"])
        self.selected_ear2.set(value=self.best_player.gearset["ear2"])
        self.selected_body.set(value=self.best_player.gearset["body"])
        self.selected_hands.set(value=self.best_player.gearset["hands"])
        self.selected_ring1.set(value=self.best_player.gearset["ring1"])
        self.selected_ring2.set(value=self.best_player.gearset["ring2"])
        self.selected_back.set(value=self.best_player.gearset["back"])
        self.selected_waist.set(value=self.best_player.gearset["waist"])
        self.selected_legs.set(value=self.best_player.gearset["legs"])
        self.selected_feet.set(value=self.best_player.gearset["feet"])

        # Update the equipment icons and tool tips
        for slot in self.best_player.gearset:
            self.update_buttons(slot)

        # Automatically move to the inputs tab (https://stackoverflow.com/questions/61691042/how-can-i-change-tab-with-button-in-tkinter)
        self.notebook.select(self.inputs_tab)
        

    def update_buttons(self, slot):
        #
        # Refresh the image and tooltip for one of the gear slot buttons.
        #
        if slot=="main":
            # Update the displayed icon first
            self.main_img = self.item2image(eval(self.selected_main.get())["Name"]) 
            self.button_main.configure(image=self.main_img)
            
            # Update the tooltip next.
            new_tooltip = self.format_tooltip_stats(eval(self.selected_main.get()))
            self.mainTip = Hovertip(self.button_main,new_tooltip,hover_delay=100)

            # Unequip off-hand weapon/shield if equipping main-hand 2-handed weapon.
            if (eval(self.selected_main.get()).get("Skill Type","None") in ["Great Sword", "Great Katana", "Great Axe", "Polearm", "Scythe", "Staff", "Hand-to-Hand"]) and (eval(self.selected_sub.get()).get("Type","None")!="Grip"):
                self.sub_img = self.item2image("Empty")
                self.button_sub.configure(image=self.sub_img)
                new_tooltip = self.format_tooltip_stats(Empty)
                self.subTip = Hovertip(self.button_sub,new_tooltip,hover_delay=100)
                self.selected_sub.set(Empty)

            # Unequip off-hand grip if equipping main-hand 1-handed weapon.
            if (eval(self.selected_main.get()).get("Skill Type","None") in ["Axe", "Club", "Dagger", "Sword", "Katana",]) and (eval(self.selected_sub.get()).get("Type","None")=="Grip"):
                self.sub_img = self.item2image("Empty")
                self.button_sub.configure(image=self.sub_img)
                new_tooltip = self.format_tooltip_stats(Empty)
                self.subTip = Hovertip(self.button_sub,new_tooltip,hover_delay=100)
                self.selected_sub.set(Empty)

        elif slot=="sub":
            self.sub_img = self.item2image(eval(self.selected_sub.get())["Name"]) 
            self.button_sub.configure(image=self.sub_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_sub.get()))
            self.subTip = Hovertip(self.button_sub,new_tooltip,hover_delay=100)
        elif slot=="ranged":
            self.ranged_img = self.item2image(eval(self.selected_ranged.get())["Name"]) 
            self.button_ranged.configure(image=self.ranged_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_ranged.get()))
            self.rangedTip = Hovertip(self.button_ranged,new_tooltip,hover_delay=100)

            # Unequip non-bullets when equipping a gun.
            if (eval(self.selected_ranged.get()).get("Type","None")=="Gun") and (eval(self.selected_ammo.get()).get("Type","None")!="Bullet"):
                self.ammo_img = self.item2image("Empty")
                self.button_ammo.configure(image=self.ammo_img)
                new_tooltip = self.format_tooltip_stats(Empty)
                self.ammoTip = Hovertip(self.button_ammo,new_tooltip,hover_delay=100)
                self.selected_ammo.set(Empty)
            # Unequip non-arrows when equipping a bow.
            if (eval(self.selected_ranged.get()).get("Type","None")=="Bow") and (eval(self.selected_ammo.get()).get("Type","None")!="Arrow"):
                self.ammo_img = self.item2image("Empty")
                self.button_ammo.configure(image=self.ammo_img)
                new_tooltip = self.format_tooltip_stats(Empty)
                self.ammoTip = Hovertip(self.button_ammo,new_tooltip,hover_delay=100)
                self.selected_ammo.set(Empty)
            # Unequip non-bolts when equipping a crossbow.
            if (eval(self.selected_ranged.get()).get("Type","None")=="Crossbow") and (eval(self.selected_ammo.get()).get("Type","None")!="Bolt"):
                self.ammo_img = self.item2image("Empty")
                self.button_ammo.configure(image=self.ammo_img)
                new_tooltip = self.format_tooltip_stats(Empty)
                self.ammoTip = Hovertip(self.button_ammo,new_tooltip,hover_delay=100)
                self.selected_ammo.set(Empty)


        elif slot=="ammo":
            self.ammo_img = self.item2image(eval(self.selected_ammo.get())["Name"]) 
            self.button_ammo.configure(image=self.ammo_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_ammo.get()))
            self.ammoTip = Hovertip(self.button_ammo,new_tooltip,hover_delay=100)
        elif slot=="head":
            self.head_img = self.item2image(eval(self.selected_head.get())["Name"]) 
            self.button_head.configure(image=self.head_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_head.get()))
            self.headTip = Hovertip(self.button_head,new_tooltip,hover_delay=100)
            # Unequip the body slot when equipping headgear with a cloak equipped.
            if ("Cloak" in eval(self.selected_body.get())["Name"]) and (eval(self.selected_head.get())["Name"]!="Empty"):
                self.body_img = self.item2image("Empty")
                self.button_body.configure(image=self.body_img)
                new_tooltip = self.format_tooltip_stats(Empty)
                self.bodyTip = Hovertip(self.button_head,new_tooltip,hover_delay=100)
                self.selected_body.set(Empty)
        elif slot=="neck":
            self.neck_img = self.item2image(eval(self.selected_neck.get())["Name"]) 
            self.button_neck.configure(image=self.neck_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_neck.get()))
            self.neckTip = Hovertip(self.button_neck,new_tooltip,hover_delay=100)
        elif slot=="ear1":
            self.ear1_img = self.item2image(eval(self.selected_ear1.get())["Name"]) 
            self.button_ear1.configure(image=self.ear1_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_ear1.get()))
            self.ear1Tip = Hovertip(self.button_ear1,new_tooltip,hover_delay=100)
        elif slot=="ear2":
            self.ear2_img = self.item2image(eval(self.selected_ear2.get())["Name"]) 
            self.button_ear2.configure(image=self.ear2_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_ear2.get()))
            self.ear2Tip = Hovertip(self.button_ear2,new_tooltip,hover_delay=100)
        elif slot=="body":
            self.body_img = self.item2image(eval(self.selected_body.get())["Name"]) 
            self.button_body.configure(image=self.body_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_body.get()))
            self.bodyTip = Hovertip(self.button_body,new_tooltip,hover_delay=100)
            # Unequip the head slot when equipping cloaks.
            if ("Cloak" in eval(self.selected_body.get())["Name"]):
                self.head_img = self.item2image("Empty")
                self.button_head.configure(image=self.head_img)
                new_tooltip = self.format_tooltip_stats(Empty)
                self.headTip = Hovertip(self.button_head,new_tooltip,hover_delay=100)
                self.selected_head.set(Empty)

        elif slot=="hands":
            self.hands_img = self.item2image(eval(self.selected_hands.get())["Name"]) 
            self.button_hands.configure(image=self.hands_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_hands.get()))
            self.handsTip = Hovertip(self.button_hands,new_tooltip,hover_delay=100)
        elif slot=="ring1":
            self.ring1_img = self.item2image(eval(self.selected_ring1.get())["Name"]) 
            self.button_ring1.configure(image=self.ring1_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_ring1.get()))
            self.ring1Tip = Hovertip(self.button_ring1,new_tooltip,hover_delay=100)
        elif slot=="ring2":
            self.ring2_img = self.item2image(eval(self.selected_ring2.get())["Name"]) 
            self.button_ring2.configure(image=self.ring2_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_ring2.get()))
            self.ring2Tip = Hovertip(self.button_ring2,new_tooltip,hover_delay=100)
        elif slot=="back":
            self.back_img = self.item2image(eval(self.selected_back.get())["Name"]) 
            self.button_back.configure(image=self.back_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_back.get()))
            self.backTip = Hovertip(self.button_back,new_tooltip,hover_delay=100)
        elif slot=="waist":
            self.waist_img = self.item2image(eval(self.selected_waist.get())["Name"]) 
            self.button_waist.configure(image=self.waist_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_waist.get()))
            self.waistTip = Hovertip(self.button_waist,new_tooltip,hover_delay=100)
        elif slot=="legs":
            self.legs_img = self.item2image(eval(self.selected_legs.get())["Name"]) 
            self.button_legs.configure(image=self.legs_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_legs.get()))
            self.legsTip = Hovertip(self.button_legs,new_tooltip,hover_delay=100)
        elif slot=="feet":
            self.feet_img = self.item2image(eval(self.selected_feet.get())["Name"]) 
            self.button_feet.configure(image=self.feet_img)
            new_tooltip = self.format_tooltip_stats(eval(self.selected_feet.get()))
            self.feetTip = Hovertip(self.button_feet,new_tooltip,hover_delay=100)


        if slot in ["main"]:
            # For main and ranged slots, update the WS list.
            self.main_wpn_type = eval(self.selected_main.get()).get("Skill Type","None")
            self.ws_list = self.ws_dict.get(self.main_wpn_type,["None"]) + self.ws_dict.get(self.ranged_wpn_type,["None"])
            self.ws_box.config(values=self.ws_list,)
            if self.ws_name.get() not in self.ws_list:
                self.ws_name.set(self.ws_list[0])

        if slot in ["ranged"]:
            # For main and ranged slots, update the WS list.
            self.ranged_wpn_type = eval(self.selected_ranged.get()).get("Skill Type","None")
            self.ws_list = self.ws_dict.get(self.main_wpn_type,["None"]) + self.ws_dict.get(self.ranged_wpn_type,["None"])
            self.ws_box.config(values=self.ws_list,)
            if self.ws_name.get() not in self.ws_list:
                self.ws_name.set(self.ws_list[0])

    def format_tooltip_stats(self, item):
        #
        # Given a dictionary containing an item's stats, create a tooltip string to display with that item's icon
        #
        ignore_stats = ["Jobs","Name","Name2","Type","Skill Type","Rank"] # Do not include these stats in the tooltip
        wpn_stats = ["DMG","Delay"] # DMG and Delay show up first if available
        base_stats = ["STR", "DEX", "VIT", "AGI", "INT", "MND", "CHR"] # Base parameters show up on their own line.
        main_stats = ["Accuracy","Attack","Ranged Accuracy","Ranged Attack","Magic Accuracy","Magic Damage","Magic Attack"]
        all_stats = ["Striking Crit Rate","Climactic Crit Damage","Klimaform Damage%","Ebullience Bonus","Occult Acumen","Futae Bonus","WSC","Zanshin OA2","Recycle","Double Shot Damage%","Triple Shot Damage%","Ranged Crit Damage","Blood Pact Damage","Rank", "Kick Attacks", "Kick Attacks DMG", "Martial Arts", "Sneak Attack Bonus", "Trick Attack Bonus", "Double Shot", "True Shot","Zanshin", "Hasso", "Quick Draw Damage", "Quick Draw Magic Accuracy", "Quick Draw Damage%", "Triple Shot","Magic Crit Rate II","Magic Burst Accuracy","Fencer","JA Haste","Accuracy", "AGI", "Attack", "Axe Skill", "CHR", "Club Skill", "Crit Damage", "Crit Rate", "DA", "DA Damage%", "Dagger Skill", "Daken", "Dark Affinity", "Dark Elemental Bonus", "Delay", "DEX", "DMG", "Dual Wield", "Earth Affinity", "Earth Elemental Bonus", "Elemental Bonus", "Elemental Magic Skill", "Fire Affinity", "Fire Elemental Bonus", "ftp", "Gear Haste", "Great Axe Skill", "Great Katana Skill", "Great Sword Skill", "Hand-to-Hand Skill", "Ice Affinity", "Ice Elemental Bonus", "INT", "Jobs", "Katana Skill", "Light Affinity", "Light Elemental Bonus", "Magic Accuracy Skill", "Magic Accuracy", "Magic Attack", "Magic Burst Damage II", "Magic Burst Damage", "Magic Damage", "MND", "Name", "Name2", "Ninjutsu Damage%", "Ninjutsu Magic Attack","Ninjutsu Magic Accuracy", "Ninjutsu Skill", "OA2", "OA3", "OA4", "OA5", "OA6", "OA7", "OA8", "PDL", "Polearm Skill", "QA", "Ranged Accuracy", "Ranged Attack", "Scythe Skill", "Skill Type", "Skillchain Bonus", "Staff Skill", "Store TP", "STR", "Sword Skill", "TA", "TA Damage%", "Throwing Skill", "Thunder Affinity", "Thunder Elemental Bonus", "TP Bonus", "Type", "VIT", "Water Affinity", "Water Elemental Bonus", "Weapon Skill Accuracy", "Weapon Skill Damage", "Weather", "Wind Affinity", "Wind Elemental Bonus","Polearm Skill","Marksmanship Skill","Archery Skill"]
        def_stats = ["Evasion","Magic Evasion", "Magic Defense","DT","MDT","PDT","MDT2","PDT2","Subtle Blow","Subtle Blow II",]

        tooltip = f"{item['Name2']}\n" # Start with the item's unique name

        nl = False # nl = NL = New Line: insert a new line to force a line break
        for k in wpn_stats:
            if item.get(k,False):
                tooltip += f"{k}:{item[k]},"
                nl = True
            if k=="Delay" and nl:
                tooltip += "\n"

        nl = False
        for k in base_stats:
            if item.get(k,False):
                tooltip += f"{k}:{item[k]},"
                nl = True
            if nl and k=="CHR":
                tooltip += "\n"

        nl = False
        for k in main_stats:
            if item.get(k,False):
                tooltip += f"{k}:{item[k]},"
                nl = True
            if "Attack" in k and nl:
                tooltip += "\n"
                nl = False
        for k in item:
            if k in base_stats or k in ignore_stats or k in main_stats or k in wpn_stats or k in def_stats:
                continue
            tooltip += f"{k}:{item[k]}\n"

        nl = False
        for k in def_stats:
            if item.get(k,False):
                tooltip += f"{k}:{item[k]},"
                nl = True
            if "Def" in k and nl:
                tooltip += "\n"
                nl = False

        return(tooltip)

    def update_special_checkboxes(self,trigger):
        #
        # Disable and/or hide specific checkboxes based on the user's main/subjob and other checkboxes enabled.
        #
        # Create a list containing: [[checkbox_object, job_required, ML required for subjob use]] to loop over
        special_checkbox_toggles = [[self.aggressor_toggle, self.aggressor_value,"war",0],
                                    [self.barrage_toggle, self.barrage_value, "rng", 0], [self.berserk_toggle, self.berserk_value,"war",0], [self.blood_rage_toggle, self.blood_rage_value,"war",999],[self.building_flourish_toggle, self.building_flourish_value,"dnc",5],
                                    [self.chainspell_toggle, self.chainspell_value,"rdm",999],[self.climactic_flourish_toggle, self.climactic_flourish_value,"dnc",999], [self.composure_toggle, self.composure_value,"rdm",999],[self.conspirator_toggle, self.conspirator_value,"thf",0], 
                                    [self.distract3_toggle, self.distract3_value,"rdm",999],[self.divine_emblem_toggle, self.divine_emblem_value,"pld",999], [self.double_shot_toggle, self.double_shot_value,"rng",999], 
                                    [self.ebullience_toggle, self.ebullience_value,"sch",30],[self.endark_toggle, self.endark_value,"drk",0],[self.enlight_toggle, self.enlight_value,"pld",999],[self.enlightenment_toggle, self.enlightenment_value,"sch",999],
                                    [self.focus_toggle, self.focus_value,"mnk",0], [self.footwork_toggle, self.footwork_value,"mnk",999], [self.futae_toggle, self.futae_value,"nin",999],
                                    [self.hasso_toggle, self.hasso_value,"sam",0],[self.haste_samba_toggle, self.haste_samba_value,"dnc",0],[self.hover_shot_toggle, self.hover_shot_value,"rng",999],
                                    [self.impetus_toggle, self.impetus_value,"mnk",999],[self.innin_toggle, self.innin_value,"nin",999],
                                    [self.klimaform_toggle, self.klimaform_value,"sch",0],
                                    [self.last_resort_toggle, self.last_resort_value,"drk",0],
                                    [self.manafont_toggle, self.manafont_value,"blm",999], [self.manawell_toggle, self.manawell_value,"blm",999],[self.mighty_strikes_toggle, self.mighty_strikes_value,"war",999],
                                    [self.natures_meditation_toggle, self.natures_meditation_value,"blu",0],
                                    [self.saber_dance_toggle, self.saber_dance_value,"dnc",999],[self.sange_toggle, self.sange_value,"nin",999], [self.sharpshot_toggle, self.sharpshot_value,"rng",0],[self.sneak_attack_toggle, self.sneak_attack_value,"thf",0], [self.striking_flourish_toggle, self.striking_flourish_value,"dnc",999],[self.swordplay_toggle, self.swordplay_value,"run",0], 
                                    [self.ternary_flourish_toggle, self.ternary_flourish_value,"dnc",999], [self.theurgic_focus_toggle, self.theurgic_focus_value,"geo",999],[self.trick_attack_toggle, self.trick_attack_value,"thf",0],[self.triple_shot_toggle, self.triple_shot_value,"cor",999],
                                    [self.velocity_shot_toggle, self.velocity_shot_value,"rng",999], 
                                    [self.warcry_toggle, self.warcry_value,"war",0],]


        # Disable and hide everything, then show only the toggles that the user's main/sub combo can use.
        # This method does not allow for two entries of the same checkbox. Things like magic burst and True Shot, which can be used by multiple jobs, are dealt with manually
        if trigger=="select_job":

            for i,k in enumerate(special_checkbox_toggles):

                # Set all values to False and hide all special toggle checkboxes
                k[1].set(False)
                k[0].grid_forget()

                mb_jobs = ["whm","blm","rdm","pld","drk","nin","blu","sch","geo"] # Magic Burst jobs
                ts_jobs = ["rng","cor"] # True Shot jobs
                if self.mainjob.get().lower() in mb_jobs or self.subjob.get().lower() in mb_jobs:
                    self.magic_burst_toggle.grid(row=1,column=0,sticky="n")
                else:
                    self.magic_burst_toggle.grid_forget()
                    self.magic_burst_value.set(False)
                if self.mainjob.get().lower() in ts_jobs or self.subjob.get().lower() in ts_jobs:
                    self.true_shot_toggle.grid(row=2,column=0,sticky="n")
                else:
                    self.true_shot_toggle.grid_forget()
                    self.true_shot_value.set(False)

                self.angon_value.set(False) # All jobs can use Angon, but disable it when swapping jobs just to be consistent.
                self.angon_toggle.grid(row=0,column=0,sticky="n")


                # Re-display checkboxes that can be used by the selected main/subjob combination
                if (k[2].upper()==self.mainjob.get()) or (k[2].upper()==self.subjob.get() and int(self.masterlevel.get())>=k[3]):
                    k[0].grid(row=i+2,column=0,sticky="n")


        # Climactic/Striking/Ternary flourishes can not exist together. Disable the others when one is enabled.
        if trigger=="climactic_flourish" and self.climactic_flourish_value.get():
            self.striking_flourish_value.set(False)
            self.ternary_flourish_value.set(False)
        if trigger=="striking_flourish" and self.striking_flourish_value.get():
            self.climactic_flourish_value.set(False)
            self.ternary_flourish_value.set(False)
        if trigger=="ternary_flourish" and self.ternary_flourish_value.get():
            self.striking_flourish_value.set(False)
            self.climactic_flourish_value.set(False)

        # Barrage and Double/Triple Shot can not exist together. Disable the others when one is enabled.
        if trigger=="barrage" and self.barrage_value.get():
            self.double_shot_value.set(False)
            self.triple_shot_value.set(False)
        if trigger=="double_shot" and self.double_shot_value.get():
            self.barrage_value.set(False)
            self.triple_shot_value.set(False)
        if trigger=="triple_shot" and self.triple_shot_value.get():
            self.barrage_value.set(False)
            self.double_shot_value.set(False)


        # # Update the scroll region of the box
        # self.ja_canvas.configure(scrollregion=self.ja_canvas.bbox("all"))

if __name__ == "__main__":
    from create_player import *
    from actions import *
    from buffs import *
    from wsdist import *

    app = App()

    # Sleep for 5 ms to prevent the lag that occurs when dragging/resizing a window with many widgets (https://stackoverflow.com/questions/71884285/tkinter-root-window-mouse-drag-motion-becomes-slower)
    from time import sleep 
    def on_configure(e):
        if e.widget == app:
            sleep(0.005)
    app.bind('<Configure>', on_configure)
    app.wait_visibility()


    # Update the GUI entries before starting mainloop based on an input file.
    # https://mail.python.org/pipermail/tkinter-discuss/2008-April/001392.html
    defaults = {}
    try:
        with open("defaults.txt","r") as ifile:
            for line in ifile:
                if line!="\n" and line[0]!="#":
                    key,value = line.strip().split("=")
                    defaults[key]=value
    except:
        print("Failed to read input file \"defaults.txt\"")

    load_defaults(app,defaults) # If the input file fails to load, then it'll load a set of default defaults.

    app.mainloop()
