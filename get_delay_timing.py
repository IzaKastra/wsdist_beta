#
# Version date: 2024 June 29
#
from numba import njit

@njit
def get_delay_timing(delay1, delay2, dw, marts, magic_haste, ja_haste, gear_haste):
    #
    # Uses your modified delay to calculate seconds between attack rounds.
    # 1 real-world second per 60 weapon delay.
    #
    # mdelay is the modified weapon delay after accounting for DW and MA
    # This is compared to weapon delay (or average weapon delay when dual wielding) to determine if at the delay floor/cap
    #
    # Apply limits to haste values from gear, magic, and job abilities
    gear_haste  = 256./1024. if  gear_haste > 256./1024. else  gear_haste
    magic_haste = 448./1024. if magic_haste > 448./1024. else magic_haste
    ja_haste    = 256./1024. if    ja_haste > 256./1024. else    ja_haste
    total_haste = gear_haste + magic_haste + ja_haste

    delay = (delay1+delay2) # Effective weapon delay. The delay minimum is 20% of this value. delay2=delay1 if not dual wielding, then this just becomes delay1

    rdelay = (delay-marts)*(1-dw)*(1-total_haste) # Reduced weapon delay, including martial arts, dual wield, and all forms of haste
    rdelay = 0.2*delay if rdelay < 0.2*delay else rdelay # -80% delay cap, including Dual Wield, Martial Arts, and Haste

    delay_reduction = 1 - rdelay/delay # Should be between 0 and 0.8

    tpa = rdelay/60 # Convert reduced delay into real-world seconds.

    return(tpa) # Return "time per attack" in seconds