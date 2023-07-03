#
# Created by Kastra on Asura.
# Feel free to /tell in game or send a PM on FFXIAH you have questions, comments, or suggestions.
#
# Version date: 2023 March 09

# This code contains the function used to estimate the average number of attacks per attack round given multi-attack stats and accuracy.
#
from numba import njit
import numpy as np
import random

@njit
def get_ma_rate2(nhits, qa, ta, da, oa3, oa2, dual_wield, hitrate_matrix):
    #
    # Estimate the number of attacks per weapon through simulation. Useful for checking the output from a simple equation.
    #
    hitrate11 = hitrate_matrix[0][0] # Main hand hit rate with the bonus +100 accuracy. Caps at 99%
    hitrate21 = hitrate_matrix[0][1] # Off hand hit rate with the bonus +100 accuracy. Caps at 95%

    hitrate12 = hitrate_matrix[1][0] # Main hand hit rate. Caps at 99%
    hitrate22 = hitrate_matrix[1][1] # Off hand hit rate. Caps at 95%

    n_sim = 1000000
    main_hits_list = np.zeros(n_sim) # List containing number of main hits per simulation. Will take average of this later
    sub_hits_list = np.zeros(n_sim) # List containing number of sub hits per simuation. Will take average of this later
    for k in range(n_sim):
        main_hits = 0
        sub_hits = 0
        total_hits = 0

        main_hits += 1*hitrate11
        total_hits += 1

        sub_hits += 1*hitrate21 if dual_wield else 0
        total_hits +=1 if dual_wield else 0

        for l in range(nhits-1):

            if main_hits + sub_hits >= 8:
                continue

            main_hits += 1*hitrate12
            total_hits += 1

        # Add main MA
        if random.uniform(0,1) < qa:
            for m in range(3):
                if total_hits >= 8:
                    continue
                main_hits += 1*hitrate12
                total_hits += 1
        elif random.uniform(0,1) < ta:
            for m in range(2):
                if total_hits >= 8:
                    continue
                main_hits += 1*hitrate12
                total_hits += 1
        elif random.uniform(0,1) < da:
            for m in range(1):
                if total_hits >= 8:
                    continue
                main_hits += 1*hitrate12
                total_hits += 1
        elif random.uniform(0,1) < oa3:
            for m in range(2):
                if total_hits >= 8:
                    continue
                main_hits += 1*hitrate12
                total_hits += 1
        elif random.uniform(0,1) < oa2:
            for m in range(1):
                if total_hits >= 8:
                    continue
                main_hits += 1*hitrate12
                total_hits += 1

        # Add second MA
        if nhits > 1 or dual_wield:
            if random.uniform(0,1) < qa:
                for m in range(3):
                    if total_hits >= 8:
                        continue
                    if dual_wield:
                        sub_hits += 1*hitrate22
                    elif nhits > 1:
                        main_hits += 1*hitrate12
                    total_hits += 1
            elif random.uniform(0,1) < ta:
                for m in range(2):
                    if total_hits >= 8:
                        continue
                    if dual_wield:
                        sub_hits += 1*hitrate22
                    elif nhits > 1:
                        main_hits += 1*hitrate12
                    total_hits += 1
            elif random.uniform(0,1) < da:
                for m in range(1):
                    if total_hits >= 8:
                        continue
                    if dual_wield:
                        sub_hits += 1*hitrate22
                    elif nhits > 1:
                        main_hits += 1*hitrate12
                    total_hits += 1
            elif random.uniform(0,1) < oa3:
                for m in range(2):
                    if total_hits >= 8:
                        continue
                    if nhits > 1:
                        main_hits += 1*hitrate12
                        total_hits += 1
            elif random.uniform(0,1) < oa2:
                for m in range(1):
                    if total_hits >= 8:
                        continue
                    if nhits > 1:
                        main_hits += 1*hitrate12
                        total_hits += 1

        main_hits_list[k] = main_hits
        sub_hits_list[k] = sub_hits

    main_hits = np.mean(main_hits_list)
    sub_hits = np.mean(sub_hits_list)

    # import matplotlib.pyplot as plt
    # plt.hist(main_hits_list,bins='scott')
    # plt.hist(sub_hits_list,bins='scott')
    # plt.show()

    return(main_hits, sub_hits)

# @njit
# def get_ma_rate3(nhits, qa, ta, da, oa3, oa2, dual_wield_type, hitrate_matrix):
#     dual_wield = True if dual_wield_type == 'Weapon' else False # Check if the item equipped in the dual_wield slot is a weapon. If this line returns an error, check the "gear.py" file to see if the item in the dual_wield slot has a "Type" key. Python is case-sensitive too

#     main_hits = 0
#     sub_hits = 0

#     hitrate11 = hitrate_matrix[0][0] # Main hand hit rate with the bonus +100 accuracy. Caps at 99%
#     hitrate21 = hitrate_matrix[0][1] # Off hand hit rate with the bonus +100 accuracy. Caps at 95%

#     hitrate12 = hitrate_matrix[1][0] # Main hand hit rate. Caps at 99%
#     hitrate22 = hitrate_matrix[1][1] # Off hand hit rate. Caps at 95%


#     main_hits += 1*hitrate11 # Add the first main hit (gets bonus accuracy)
#     main_hits += (nhits-1)*(hitrate12) # Add the remaining natural main hits

#     if dual_wield and main_hits+sub_hits < 8:
#         sub_hits += 1*hitrate21 # Add the first sub hit (gets bonus accuracy)

#     # Add main-hand multi-hits to the first natural hit.
#     main_hits += (max(0,min(3, 8-(main_hits + sub_hits))*qa) + \
#                   max(0,min(2, 8-(main_hits + sub_hits))*(1-qa)*ta) + \
#                   max(0,min(1, 8-(main_hits + sub_hits))*(1-qa)*(1-ta)*da) + \
#                   max(0,min(2, 8-(main_hits + sub_hits))*(1-qa)*(1-ta)*(1-da)*oa3) + \
#                   max(0,min(1, 8-(main_hits + sub_hits))*(1-qa)*(1-ta)*(1-da)*(1-oa3)*oa2))*hitrate12

#     if dual_wield:
#         # Add off-hand multi-hits to the first sub hit.
#         sub_hits += (max(0,min(3, 8-(sub_hits + main_hits)))*qa + \
#                      max(0,min(2, 8-(sub_hits + main_hits)))*(1-qa)*ta + \
#                      max(0,min(1, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*da + \
#                      max(0,min(2, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*(1-da)*oa3 + \
#                      max(0,min(1, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*(1-da)*(1-oa3)*oa2)*hitrate22
#     elif nhits>1:
#         # Add main-hand multi-hits to the second natural hit if not dual wield and if nhits>1
#         main_hits += (max(0,min(3, 8-(sub_hits + main_hits)))*qa + \
#                       max(0,min(2, 8-(sub_hits + main_hits)))*(1-qa)*ta + \
#                       max(0,min(1, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*da + \
#                       max(0,min(2, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*(1-da)*oa3 + \
#                       max(0,min(1, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*(1-da)*(1-oa3)*oa2)*hitrate12

#     return(main_hits, sub_hits)

@njit
def get_ma_rate3(main_job, nhits, qa, ta, da, oa_list, dual_wield, hitrate_matrix, ranged_hitrate2, daken, kickattacks, zanshin, zanhasso, zanshin_hitrate, zanshin_oa2, striking_flourish=False, ternary_flourish=False, tp_round=False,):
    #
    # Calculate the expected number of attacks on a given attack round (nhits=1) or weapon skill (nhits=nhits).
    # Break up the results into main_hits, sub_hits, daken_hits, kickattack_hits, and zanshin_hits. The sum must be no larger than 8.
    # For weapon skills, pass in ranged_hitrate2 = daken = kickattacks = zanshin = zanhasso = zanshin_hitrate = zanshin_oa2 = 0
    #
    main_hits = 0
    sub_hits = 0
    daken_hits = 0
    kickattack_hits = 0

    hitrate11 = hitrate_matrix[0][0] # Main hand hit rate with the bonus +100 accuracy. Caps at 99% for single-handed weapons
    hitrate21 = hitrate_matrix[0][1] # Off hand hit rate with the bonus +100 accuracy. Caps at 95%

    hitrate12 = hitrate_matrix[1][0] # Main hand hit rate. Caps at 99% for single-handed weapons
    hitrate22 = hitrate_matrix[1][1] # Off hand hit rate. Caps at 95%

    main_hits += 1*hitrate11 # Add the first main hit (gets bonus accuracy)
    main_hits += (nhits-1)*(hitrate12) # Add the remaining natural main hits

    if dual_wield and main_hits+sub_hits < 8:
        sub_hits += 1*hitrate21 # Add the first sub hit (gets bonus accuracy)


    # Striking flourish seems to set QA=0, TA=0, and DA=1.0 for the first MA hit only
    if striking_flourish:
        qa_main = 0
        ta_main = 0
        da_main = 1
    elif ternary_flourish:
        qa_main = 0
        ta_main = 1
        da_main = 0
    else:
        qa_main = qa
        ta_main = ta
        da_main = da

    oa3_main = oa_list[0]
    oa2_main = oa_list[1]
    oa8_sub = oa_list[2]
    oa7_sub = oa_list[3]
    oa6_sub = oa_list[4]
    oa5_sub = oa_list[5]
    oa4_sub = oa_list[6]
    oa3_sub = oa_list[7]
    oa2_sub = oa_list[8]

    # Add main-hand multi-hits to the first natural hit. Zanshin included at the very end.
    main_hits += (max(0,min(3, 8-(main_hits + sub_hits))*qa_main) + \
                  max(0,min(2, 8-(main_hits + sub_hits))*(1-qa_main)*ta_main) + \
                  max(0,min(1, 8-(main_hits + sub_hits))*(1-qa_main)*(1-ta_main)*da_main) + \
                  max(0,min(2, 8-(main_hits + sub_hits))*(1-qa_main)*(1-ta_main)*(1-da_main)*oa3_main) + \
                  max(0,min(1, 8-(main_hits + sub_hits))*(1-qa_main)*(1-ta_main)*(1-da_main)*(1-oa3_main)*oa2_main))*hitrate12

    # Zanshin conditions:
    # 1) Last hit to proc
    # 2) Does not trigger on multi-attacks
    # 3) Only gets a chance to proc if the first attack misses.
    # 4) Does not proc on weapon skills

    zanshin_hitrate = 0 if not tp_round else zanshin_hitrate # Do not allow Zanshin to contribute for weapon skills.
    zanshin_bonus = ((1-qa_main)*(1-ta_main)*(1-da_main)*(1-oa3_main)*(1-oa2_main)*(1-hitrate12)*zanshin*zanshin_oa2*2 + \
                    (1-qa_main)*(1-ta_main)*(1-da_main)*(1-oa3_main)*(1-oa2_main)*(1-hitrate12)*zanshin*(1-zanshin_oa2))*zanshin_hitrate

    # Zanshin can proc on successful melee swings for SAM main with Hasso up.
    zanshin_sam_bonus = ((1-qa_main)*(1-ta_main)*(1-da_main)*(1-oa3_main)*(1-oa2_main)*hitrate12*zanhasso*zanshin_oa2*2 + \
                         (1-qa_main)*(1-ta_main)*(1-da_main)*(1-oa3_main)*(1-oa2_main)*hitrate12*zanhasso*(1-zanshin_oa2))*zanshin_hitrate*(main_job=="SAM")

    zanshin_hits = zanshin_bonus + zanshin_sam_bonus
    main_hits += zanshin_hits

    if dual_wield==True:
        # Add off-hand multi-hits to the first sub hit.
        # Assume Kclub will only ever be in off-hand
        sub_hits += (max(0,min(3, 8-(sub_hits + main_hits)))*qa + \
                     max(0,min(2, 8-(sub_hits + main_hits)))*(1-qa)*ta + \
                     max(0,min(1, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*da + \
                     max(0,min(7, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*(1-da)*oa8_sub + \
                     max(0,min(6, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*(1-da)*(1-oa8_sub)*oa7_sub + \
                     max(0,min(5, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*(1-da)*(1-oa8_sub)*(1-oa7_sub)*oa6_sub + \
                     max(0,min(4, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*(1-da)*(1-oa8_sub)*(1-oa7_sub)*(1-oa6_sub)*oa5_sub + \
                     max(0,min(3, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*(1-da)*(1-oa8_sub)*(1-oa7_sub)*(1-oa6_sub)*(1-oa5_sub)*oa4_sub + \
                     max(0,min(2, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*(1-da)*(1-oa8_sub)*(1-oa7_sub)*(1-oa6_sub)*(1-oa5_sub)*(1-oa4_sub)*oa3_sub + \
                     max(0,min(1, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*(1-da)*(1-oa8_sub)*(1-oa7_sub)*(1-oa6_sub)*(1-oa5_sub)*(1-oa4_sub)*(1-oa3_sub)*oa2_sub)*hitrate22
    elif nhits>1:
        # Add main-hand multi-hits to the second natural hit if not dual wield and if nhits>1
        main_hits += (max(0,min(3, 8-(sub_hits + main_hits)))*qa + \
                      max(0,min(2, 8-(sub_hits + main_hits)))*(1-qa)*ta + \
                      max(0,min(1, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*da + \
                      max(0,min(2, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*(1-da)*oa3_main + \
                      max(0,min(1, 8-(sub_hits + main_hits)))*(1-qa)*(1-ta)*(1-da)*(1-oa3_main)*oa2_main)*hitrate12

    if tp_round:
        # I checked in-game as NIN/MNK. Kick Attack animation happens before daken animation, but both can occur on the same attack round
        
        remaining_hits_available = 8 - (main_hits + sub_hits)
        kickattack_hits += min(max(0,remaining_hits_available), 1.0)*kickattacks*hitrate12 # Need to use hitrate21, since hitrate11 gives an extra +100 accuracy for a WS's first hit.
        daken_hits += min(max(0,remaining_hits_available - kickattacks), 1.0)*daken*ranged_hitrate2 # This uses ranged_hitrate2, for the same reason as hitrate21

    return(main_hits, sub_hits, daken_hits, kickattack_hits, zanshin_hits)



if __name__ == "__main__":

    nhits = 5
    qa = 0.03
    ta = 0.06
    da = 0.64
    oa3_main = 0
    oa2_main = 0
    oa8_sub = 0
    oa7_sub = 0
    oa6_sub = 0
    oa5_sub = 0
    oa4_sub = 0
    oa3_sub = 0
    oa2_sub = 0
    oa_list = np.array([oa3_main,oa2_main,oa8_sub,oa7_sub,oa6_sub,oa5_sub,oa4_sub,oa3_sub,oa2_sub],dtype=np.float32)

    hitrate_matrix = np.array([[0.95,0.], [0.95,0.]])
    # hitrate_matrix = np.ones_like(hitrate_matrix)
    dual_wield = True

    # main_hits, sub_hits = get_ma_rate(nhits, qa, ta, da, oa3, oa2, dual_wield_type, hitrate_matrix)
    # print(main_hits, sub_hits, main_hits+sub_hits)
    main_hits, sub_hits = get_ma_rate2(nhits, qa, ta, da, oa3_main, oa2_main, dual_wield, hitrate_matrix,)
    print(main_hits, sub_hits, main_hits+sub_hits)
    main_hits, sub_hits, daken_hits, kickattack_hits, zanshin_hits  = get_ma_rate3("nin", nhits, qa, ta, da, oa_list, dual_wield, hitrate_matrix, 0, 0, 0, 0, 0, 0, 0, False, False, False)
    print(main_hits, sub_hits, main_hits+sub_hits)