from hashlib import md5

length = 5
iter_round = 1000
hash_length = -18
element = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
rainbow_dict_end = {}
string0 = ''


def R_func(hash_content, round):
    i1 = round % 32
    i2 = (round + 13) % 32
    i3 = (round + 21) % 32
    i4 = (round + 4) % 32
    i5 = (round + 9) % 32
    R_func_result = md5(hash_content.encode()).hexdigest()
    return R_func_result[i1] + R_func_result[i2] + R_func_result[i3] + R_func_result[i4] + R_func_result[i5]


def get_n_round_result(hash_content, num_round):
    # num_round 是当前找寻的轮数， 第一轮就是直接R了。
    # 从0开始
    for i in range(num_round, 0, -1):
        r_func_round = iter_round - 1 - i
        hash_content = R_func(hash_content, r_func_round)
        hash_content = md5(hash_content.encode()).hexdigest()[hash_length:]
    return R_func(hash_content, iter_round - 1)


for i in range(0, 2 ** 20, 2 ** 7):
    string0 = hex(i)[2:].zfill(length)
    _r = string0
    for count in range(iter_round):
        _hash = md5(_r.encode()).hexdigest()[hash_length:]
        _r = R_func(_hash, count)
    if not rainbow_dict_end.get(_r):
        rainbow_dict_end[_r] = [string0, ]
    else:
        rainbow_dict_end[_r].append(string0)


def get_origin_text_examine(iter_round, hash_length, input_text):
    _hash_to_find = md5(input_text.encode()).hexdigest()[hash_length:]
    for count in range(iter_round):
        R_result = get_n_round_result(_hash_to_find, count)
        if rainbow_dict_end.get(R_result):
            failed = 0
            # 开始破译：
            content = R_result
            for string_start in rainbow_dict_end[content]:
                _r_now = string_start
                rec = string_start
                find_status = ''
                i = 0
                failed = 0
                while find_status != _hash_to_find:
                    rec = _r_now
                    find_status = md5(_r_now.encode()).hexdigest()[hash_length:]
                    _r_now = R_func(find_status, i)
                    i += 1
                    if i == iter_round - count + 1:
                        failed = 1
                        break
                if md5(rec.encode()).hexdigest()[hash_length:] == _hash_to_find:
                    failed = 0
                    break
            if failed == 0:
                print('succceeeeeeeeeeeeeeeeeeeeeeeed', rec)
                return 1
        else:
            if count == iter_round - 1:
                print('failed')
                return 0
            continue
    print('falied')
    return  0

def unit_test():
    suc = 0
    for i in range(2 ** 18, 2 ** 18 + 100):
        i = hex(i)[2:].zfill(length)
        if get_origin_text_examine(iter_round, hash_length, i) == 1:
            suc += 1
    print(suc / 100)


unit_test()
