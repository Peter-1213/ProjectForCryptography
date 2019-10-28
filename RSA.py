from Crypto.Util import number
import numba


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


def fast_exp_mod_1(b, e, m):
    # 模重平方法
    result = 1
    while e != 0:
        if (e & 1) == 1:
            # ei = 1, then mul
            result = (result * b) % m
        e >>= 1
        # b, b^2, b^4, b^8, ... , b^(2^n)
        b = (b * b) % m
    return result


import time


def generate_RSA_params(bits):
    RSA_p = number.getPrime(bits)
    RSA_q = number.getPrime(bits)
    RSA_N = RSA_q * RSA_p

    RSA_r = (RSA_p - 1) * (RSA_q - 1)
    RSA_e = 65537

    RSA_d = number.inverse(RSA_e, RSA_r)
    return RSA_p, RSA_q, RSA_N, RSA_e, RSA_d


def RSA_with_expon_squraing():
    RSA_p, RSA_q, RSA_N, RSA_e, RSA_d = generate_RSA_params(512)

    n = 3813172987498217391294172983771298749812798372198371
    c = fast_exp_mod_1(n, RSA_e, RSA_N)

    t4 = time.time_ns()
    dec = fast_exp_mod_1(c, RSA_d, RSA_N)
    t5 = time.time_ns()

    print(dec == n, '%fms' % ((t5 - t4) / 10 ** 6))


def RSA_with_CRT():
    RSA_p, RSA_q, RSA_N, RSA_e, RSA_d = generate_RSA_params(512)
    n = 3813172987498217391294172983771298749812798372198371
    c = fast_exp_mod_1(n, RSA_e, RSA_N)

    Q_p = fast_exp_mod_1(RSA_q, RSA_p - 1, RSA_N)
    P_q = fast_exp_mod_1(RSA_p, RSA_q - 1, RSA_N)
    # 以上参数在解密前就可以计算，因此不算解密时间。

    t1 = time.time_ns()
    D_p = RSA_d % (RSA_p - 1)
    C_p = c % RSA_p
    C_q = c % RSA_q
    D_q = RSA_d % (RSA_q - 1)

    M_p = fast_exp_mod_1(C_p, D_p, RSA_p)
    M_q = fast_exp_mod_1(C_q, D_q, RSA_q)

    dec = (M_p * Q_p + M_q * P_q) % RSA_N
    t2 = time.time_ns()
    print(n == dec, '%fms' % ((t2 - t1) / 10 ** 6))


def mont_preprocessing(N, base=10):
    rho = 1
    count = 0  # lN
    while True:
        rho *= base
        count += 1
        if rho > N:
            break
    omega = (-modinv(N, rho)) % rho
    return rho, omega, count


def mont_mul(a, b, omega, N, lN, base=10):
    r = 0
    b_for_cal = b
    for i in range(lN):
        b_i = b_for_cal % base
        b_for_cal = b_for_cal // base
        u = (r % base + b_i * a % base) * omega % base
        r = (r + b_i * a + u * N) // base

    if r >= N:
        r -= N
    return r


#fixme
def mont_exp(a, exp, N, base=10):
    rho, omega, lN = mont_preprocessing(N, base)
    t_bar = mont_mul(1, (rho ** 2) % N, omega, N, lN)
    print(t_bar)
    x_bar = mont_mul(a, (rho ** 2) % N, omega, N, lN)
    print(x_bar)
    exp = list(map(int, list(bin(exp)[2:])))
    print(exp)
    for i in range(len(exp) - 1, -1, -1):
        t_bar = mont_mul(t_bar, t_bar, omega, N, lN, )
        if exp[i] == 1:
            t_bar = mont_mul(t_bar, x_bar, omega, N, lN)
        print(t_bar)
    return mont_mul(t_bar, 1, omega, N, lN)


def mont_exp_1(a, exp, N, base=10):
    rho, omega, lN = mont_preprocessing(N, base)
    r = mont_mul(1, (rho ** 2) % N, omega, N, lN)

    p = mont_mul(a, (rho ** 2) % N, omega, N, lN)

    exp = list(map(int, list(bin(exp)[2:])))
    print(exp)
    for i in range(len(exp) - 1, -1, -1):
        p = mont_mul(p, p, omega, N, lN, )
        if exp[i] == 1:
            r = mont_mul(r, p, omega, N, lN)

    return mont_mul(r, 1, omega, N, lN)


if __name__ == '__main__':
    RSA_with_expon_squraing()
    RSA_with_CRT()
    print(mont_exp_1(5, 8, 7))
