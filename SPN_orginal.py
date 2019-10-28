# 实验SPN
import array
from random import sample
from time import time

GROUP_LENGTH = 16


def new_xor(array0, key_16bit):
    if len(array0) != len(key_16bit):
        print(len(array0), len(key_16bit))
        print('Error')
        return 0
    # xor part:
    for i in range(len(array0)):
        if array0[i] == key_16bit[i]:
            array0[i] = 0
        else:
            array0[i] = 1

    # bin2dec part:
    # int0_new = 0
    # now_weight = 1
    # for i in array0[::-1]:
    #    int0_new += i * now_weight
    #    now_weight *= 2
    # return int0_new
    return array0


def substitution_4(int_xbit_to_sub, S_box_xbit):
    int_xbit_to_sub = ''.join(map(str, int_xbit_to_sub))
    int_result_xbit = list(map(int, list(bin(S_box_xbit[int(int_xbit_to_sub, 2)])[2:].zfill(GROUP_LENGTH // 4))))
    return int_result_xbit


S_box_4bit = array.array('B', [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7])
S_box_4bit_reversed = array.array('B', [14, 3, 4, 8, 1, 12, 10, 15, 7, 13, 9, 6, 11, 2, 0, 5])


def substitution(int_origin_bin):
    int_result_bin = (substitution_4(int_origin_bin[:GROUP_LENGTH // 4], S_box_4bit) + substitution_4(
        int_origin_bin[GROUP_LENGTH // 4:GROUP_LENGTH // 2], S_box_4bit) +
                      substitution_4(int_origin_bin[GROUP_LENGTH // 2:GROUP_LENGTH * 3 // 4],
                                     S_box_4bit) + substitution_4(int_origin_bin[GROUP_LENGTH * 3 // 4:GROUP_LENGTH],
                                                                  S_box_4bit))
    return int_result_bin


def substitution_reversed(int_origin_bin):
    int_result_bin = (substitution_4(int_origin_bin[:GROUP_LENGTH // 4], S_box_4bit_reversed) + substitution_4(
        int_origin_bin[GROUP_LENGTH // 4:GROUP_LENGTH // 2], S_box_4bit_reversed) +
                      substitution_4(int_origin_bin[GROUP_LENGTH // 2:GROUP_LENGTH * 3 // 4],
                                     S_box_4bit_reversed) + substitution_4(
                int_origin_bin[GROUP_LENGTH * 3 // 4:GROUP_LENGTH], S_box_4bit_reversed))
    return int_result_bin

    # int origin is a GROUP_LENGTH bit int.


P_box_16bit = array.array('B', [1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16])
P_box_16bit_reversed = array.array('B', [1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16])


def permutation(list_of_bits, P_box):
    permutated_list_of_bits = list_of_bits.copy()
    for index, value in enumerate(list_of_bits):
        permutated_list_of_bits[P_box[index] - 1] = value
    return permutated_list_of_bits


def key_generator(seed, r):
    # seed is a 32bit seq. for round r of SPN, a continuous 16 bit sequence from 4r-3
    # is selected from seed.
    r = r + 1
    seed = array.array('B', list(map(int, list(bin(seed)[2:].zfill(32)))))
    return seed[(4 * r - 3 - 1):(4 * r + 13 - 1)]


def four_layer_spn_test(plain, P_box_16bit, seed):
    temp = array.array('B', list(map(int, list(bin(plain)[2:].zfill(GROUP_LENGTH)))))
    for r in range(3):
        temp = new_xor(temp, key_generator(seed, r))
        temp = substitution(temp)
        temp = permutation(temp, P_box_16bit)
    temp = new_xor(temp, key_generator(seed, 3))
    temp = substitution(temp)
    temp = new_xor(temp, key_generator(seed, 4))
    return int(''.join(map(str, temp)), 2)


# four_layer_spn_test(65535, P_box_16bit, 23333333)


def four_layer_spn_decrypt(encrypted, P_box_16bit_reversed, seed):
    temp = array.array('B', list(map(int, list(bin(encrypted)[2:].zfill(GROUP_LENGTH)))))
    temp = new_xor(temp, key_generator(seed, 4))
    temp = substitution_reversed(temp)
    temp = new_xor(temp, key_generator(seed, 3))
    for r in range(2, -1, -1):
        temp = permutation(temp, P_box_16bit_reversed)
        temp = substitution_reversed(temp)
        temp = new_xor(temp, key_generator(seed, r))

    return int(''.join(map(str, temp)), 2)


i = 0


# with open('RandomTest.pdf', 'rb') as to_enc:
#     out = open('enced.dat', 'wb')
#     read_num = to_enc.read(2)
#     while read_num:
#         int_read = unpack('H', read_num)[0]
#         out_int = four_layer_spn_test(int_read, P_box_16bit, 1429496795)
#         out_byte = pack('H', out_int)
#         out.write(out_byte)
#         i += 1
#         if i%100000 == 0:
#             print('test')
#         read_num = to_enc.read(2)

def linear_analysis(T, seed):
    count = {}
    rand_range = 2 ** 16 - 1
    rand_list = sample(range(rand_range), T)
    for rand_input in rand_list:
        rand_out = four_layer_spn_test(rand_input, P_box_16bit, seed)
        y_2 = int(bin(rand_out)[2:].zfill(16)[4:8], 2)
        y_4 = int(bin(rand_out)[2:].zfill(16)[12:], 2)

        x_bit_5 = int(bin(rand_input)[2:].zfill(16)[4])
        x_bit_7 = int(bin(rand_input)[2:].zfill(16)[6])
        x_bit_8 = int(bin(rand_input)[2:].zfill(16)[7])
        for l1 in range(16):
            for l2 in range(16):
                v2_4 = l1 ^ y_2
                v4_4 = l2 ^ y_4
                u2_4 = S_box_4bit_reversed[v2_4]
                u4_4 = S_box_4bit_reversed[v4_4]
                u_bit_8_4 = u2_4 % 2
                u_bit_6_4 = (u2_4 // 4) % 2
                u_bit_16_4 = u4_4 % 2
                u_bit_14_4 = (u4_4 // 4) % 2

                z = x_bit_5 ^ x_bit_7 ^ x_bit_8 ^ u_bit_6_4 ^ u_bit_8_4 ^ u_bit_14_4 ^ u_bit_16_4
                if z == 0:
                    if count.get((l1, l2)) is None:
                        count[(l1, l2)] = 1
                    else:
                        count[(l1, l2)] += 1

    for l1 in range(16):
        for l2 in range(16):
            count[(l1, l2)] = abs(count[(l1, l2)] - T // 2)
    print(max(count.values()))
    return count


def violent_crack(count_key, plain_test_list, cip_test_list):
    count_key = sorted(list(count_key.keys()), key=count_key.get, reverse=True)
    to_iter = list(zip(plain_test_list, cip_test_list))
    for probable_key_20_24, probable_key_28_32 in count_key:
        print(probable_key_20_24, probable_key_28_32)
        for i in range(2**16):
            for j in range(16):
                for k in range(16):
                    seed_probable = i * 2 ** 16 + j * 2 ** 12 + probable_key_20_24 * 2 ** 8 + k * 2 ** 4 + probable_key_28_32
                    for plain_test, cip_test in to_iter:
                        if four_layer_spn_test(plain_test, P_box_16bit, seed_probable) == cip_test:
                            if plain_test == to_iter[-1][0] and cip_test == to_iter[-1][1]:
                                return 1, i, j, k, seed_probable
                            else:
                                continue
                        else:
                            break

        print('wrong!')


def diff_analysis(T, seed, init_xor=2816):
    rand_range = 2 ** 16 - 1
    rand_list = sample(range(rand_range), T)
    input_list = [(i, i^init_xor, four_layer_spn_test(i, P_box_16bit, seed),
                   four_layer_spn_test(i^init_xor, P_box_16bit, seed)) for i in rand_list]
    count = {}
    for x, x_star, y, y_star in input_list:
        y_1 = int(bin(y)[2:].zfill(16)[0:4], 2)
        y_3 = int(bin(y)[2:].zfill(16)[8:12], 2)
        y_2 = int(bin(y)[2:].zfill(16)[4:8], 2)
        y_4 = int(bin(y)[2:].zfill(16)[12:], 2)
        y_star_1 = int(bin(y_star)[2:].zfill(16)[0:4], 2)
        y_star_2 = int(bin(y_star)[2:].zfill(16)[4:8], 2)
        y_star_3 = int(bin(y_star)[2:].zfill(16)[8:12], 2)
        y_star_4 = int(bin(y_star)[2:].zfill(16)[12:], 2)

        if y_1 == y_star_1 and y_3 == y_star_3:
            for l1 in range(16):
                for l2 in range(16):
                    v2_4 = l1 ^ y_2
                    v4_4 = l2 ^ y_4
                    u2_4 = S_box_4bit_reversed[v2_4]
                    u4_4 = S_box_4bit_reversed[v4_4]
                    v_star_2_4 = l1^y_star_2
                    v_star_4_4 = l2^y_star_4
                    u_star_2_4 = S_box_4bit_reversed[v_star_2_4]
                    u_star_4_4 = S_box_4bit_reversed[v_star_4_4]
                    u_2_4_xor = u2_4 ^ u_star_2_4
                    u_4_4_xor = u4_4 ^ u_star_4_4
                    if u_2_4_xor == 6 and u_4_4_xor == 6:
                        if count.get((l1, l2)) is None:
                            count[(l1, l2)] = 1
                        else:
                            count[(l1, l2)] += 1

    print(count.values())
    return count



if __name__ == '__main__':
    key = int('00000000100001010000101000000101', 2)
    plain_list = [i for i in range(127, 65534, 5678)]
    cip_list = [four_layer_spn_test(i, P_box_16bit, key) for i in plain_list]
    time1 = time()
    while True:
        time4 = time()
        count = diff_analysis(2000, key)
        time3 = time()
        result, i, j, k, seed_probable = violent_crack(count, plain_list, cip_list)
        if result == 1:
            print('key=', seed_probable)
            break
    time2 = time()
    print('oringinal:', bin(seed_probable)[2:].zfill(32))
    print('key_get  :', bin(key)[2:].zfill(32))
    print('time elapsed(s):',time3-time4)
    print(time2-time1)
