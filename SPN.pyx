# cython: language_level=3

import numpy as np
cimport numpy as cnp
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
cdef char [:] new_xor(char[:] array0, char[:] array1):
    if len(array0) != len(array1):
        print(len(array0), len(array1))
        print('Error')
    else:
        for i in range(len(array0)):
            if array0[i] == array1[i]:
                array0[i] = 0
            else:
                array0[i] = 1
        return array0

cdef  S_box_4bit = [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7]
cdef char[16] S_box_4bit_reversed = [14, 3, 4, 8, 1, 12, 10, 15, 7, 13, 9, 6, 11, 2, 0, 5]

@cython.boundscheck(False)
@cython.wraparound(False)
cdef short bin2dec(char [:] bin_array):
    cdef char length = len(bin_array)
    cdef short _sum = 0, status = 1
    cdef char i
    for i in bin_array[::-1]:
        _sum += i*status
        status *= 2
    return _sum

@cython.boundscheck(False)
@cython.wraparound(False)
cdef char [:] dec2bin(short num, int digit):
    list_to_transfer = bin(num).strip('0b').zfill(digit)
    list_to_transfer = list(map(int, list(list_to_transfer)))
    return array.array('B', list_to_transfer)

@cython.boundscheck(False)
@cython.wraparound(False)
cdef char[:] substitution_quarter(char [:] int_xbit_to_sub, char [:] S_box_xbit):
    cdef short _sum = bin2dec(int_xbit_to_sub)
    cdef char sub_reult = S_box_xbit[_sum]
    return dec2bin(sub_reult, 4)

@cython.boundscheck(False)
@cython.wraparound(False)
cdef char[:] substitution(char [:] int_to_sub, char[:] S_box_xbit):
    cdef _array = array.array('B')
    _array = substitution_quarter(int_to_sub[:4], S_box_xbit).base
    _array.extend(substitution_quarter(int_to_sub[4:8], S_box_xbit).base)
    _array.extend(substitution_quarter(int_to_sub[8:12], S_box_xbit).base)
    _array.extend(substitution_quarter(int_to_sub[12:16], S_box_xbit).base)
    return _array


@cython.boundscheck(False)
@cython.wraparound(False)
cdef char [:] permutation(char [:] _to_permute, char [:] P_box_xbit):
    cdef char [:] _return_array  = _to_permute.copy()
    cdef char i
    for i in range(16):
        _return_array[P_box_xbit[i] - 1] = _to_permute[i]
    return _return_array

@cython.boundscheck(False)
@cython.wraparound(False)
cdef char[:] key_generator(seed, r):
    # seed is a 32bit seq. for round r of SPN, a continuous 16 bit sequence from 4r-3
    # is selected from seed.
    r = r+1
    seed = array.array('B', list(map(int, list(bin(seed)[2:].zfill(32)))))
    return seed[(4*r-3-1):(4*r+13-1)]


cdef char [:] P_box_16bit = array.array('B', [1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16])
cdef char [:] P_box_16bit_reversed = array.array('B', [1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16])

@cython.boundscheck(False)
@cython.wraparound(False)
cdef short _SPN(short input_num, int seed):
    cdef char [:] temp = dec2bin(input_num, 16)
    cdef char r
    for r in range(3):
        temp = new_xor(temp, key_generator(seed, r))
        temp = substitution(temp, S_box_4bit)
        temp = permutation(temp, P_box_16bit)
    temp = new_xor(temp, key_generator(seed, 3))
    temp = substitution(temp, S_box_4bit)
    temp = new_xor(temp, key_generator(seed, 4))
 #   print(bin2dec(temp))
    return bin2dec(temp)

@cython.boundscheck(False)
@cython.wraparound(False)
cdef short _SPN_decrypt(short input_num, int seed):
    cdef char [:] temp = dec2bin(input_num, 16)
    temp = new_xor(temp, key_generator(seed, 4))
    temp = substitution(temp, S_box_4bit_reversed)
    temp = new_xor(temp, key_generator(seed, 3))
    cdef char r
    for r in range(2,-1,-1):
        temp = permutation(temp, P_box_16bit_reversed)
        temp = substitution(temp, S_box_4bit_reversed)
        temp = new_xor(temp, key_generator(seed, r))
 #   print(bin2dec(temp))
    return bin2dec(temp)

def SPN(a,b):
    return _SPN(a,b)

def SPN_decrypt(a,b):
    return _SPN_decrypt(a,b)