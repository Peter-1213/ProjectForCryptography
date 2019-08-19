# 实验SPN
import array

GROUP_LENGTH = 16


def new_xor(int0, int1):
    array0 = array.array('B', list(map(int, list(bin(int0)[2:].zfill(GROUP_LENGTH)))))
    array1 = array.array('B', list(map(int, list(bin(int1)[2:].zfill(GROUP_LENGTH)))))
    print(array1)
    if len(array0) != len(array1):
        print('Error')
        return 0
    # xor part:
    for i in range(len(array0)):
        if array0[i] == array1[i]:
            array0[i] = 0
        else:
            array0[i] = 1

    # bin2dec part:
    int0_new = 0
    now_weight = 1
    for i in array0[::-1]:
        int0_new += i * now_weight
        now_weight *= 2
    return int0_new


def substitution_4(int_xbit_to_sub, S_box_xbit):
    int_result_xbit = list(map(int, list(bin(S_box_xbit[int(int_xbit_to_sub, 2)])[2:].zfill(GROUP_LENGTH // 4))))
    print(int_result_xbit)
    return int_result_xbit


S_box_4bit = array.array('B', [4, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7])


def substitution(int_origin):
    int_origin_bin = bin(int_origin)[2:].zfill(GROUP_LENGTH)
    int_result_bin = (substitution_4(int_origin_bin[:GROUP_LENGTH // 4], S_box_4bit) + substitution_4(
        int_origin_bin[GROUP_LENGTH // 4:GROUP_LENGTH // 2], S_box_4bit) +
                      substitution_4(int_origin_bin[GROUP_LENGTH // 2:GROUP_LENGTH * 3 // 4],
                                     S_box_4bit) + substitution_4(int_origin_bin[GROUP_LENGTH * 3 // 4:GROUP_LENGTH],
                                                                  S_box_4bit))
    print(int_result_bin)

    # int origin is a GROUP_LENGTH bit int.


substitution(65534)
