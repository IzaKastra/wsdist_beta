'''
File containing code to calculate TP returned from an attack round or weapon skill.

Author: Kastra (Asura)
'''
def get_tp(swings, mdelay, stp, zanshin=False):
    #
    # Calculate the TP return from an attack round based on the number of swings that landed, the modified weapon delay, and store TP.
    # For weaponskills, only the first main and sub hits gain full TP, the others only get 10*(1+store_TP) TP.
    # Only the first main and off-hand hits of a weapon skill use this function if they pass the accuracy check.
    #
    if mdelay <= 180.:
        base_tp = int(61.+((mdelay-180.)*63./360.))
    elif mdelay <= 540.:
        base_tp = int(61.+((mdelay-180.)*88./360.))
    elif mdelay <= 630:
        base_tp = int(149.+((mdelay-540.)*20./360.))
    elif mdelay <= 720:
        base_tp = int(154.+((mdelay-630.)*28./360.))
    elif mdelay <= 900:
        base_tp = int(161.+((mdelay-720.)*24./360.))
    else:
        base_tp = int(173.+((mdelay-900.)*28./360.))

    zanshin_bonus = 30*5*zanshin # +30 TP per Ikishoten merit on SAM, applied before Store TP: https://www.bg-wiki.com/ffxi/Ikishoten 
    base_tp += zanshin_bonus
    
    return(swings*int(base_tp*(1.+stp)))
