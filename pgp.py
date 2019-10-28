import zipfile
from Crypto.Cipher import AES
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Util import number, Padding
from random import randint



# 预备 生成两对椭圆曲线密钥，一对AES密钥
'''
NIST P-256:
y^2 = x^3-3x+41058363725152142129326129780047268409114441015993725554835256314039467401291
modulo p = FFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
G x = 48439561293906451759052585252797914202762949526041747995844080717082404635286
G y = 36134250956749795798585127919587881956611106672985015071877198253568414405109
'''
key1 = ECC.generate(curve='P-256')
key1_pub = key1.public_key()
key2 = ECC.generate(curve='P-256')
key2_pub = key2.public_key()
collect_d = key1.d

point_G = ECC.EccPoint(x=48439561293906451759052585252797914202762949526041747995844080717082404635286,
                       y=36134250956749795798585127919587881956611106672985015071877198253568414405109,
                       curve='P-256')

# 这里很奇怪，所有的地方都对ECC的实际应用语焉不详，都说“有办法把明文编码到椭圆曲线上”，但却从来不说怎么编码。
# 这里我们就用一个比较naive的方法，就是把它反过来，把点本身当成明文，而要做的AES_key就是把点hash一下，取前面的32位。

AES_key_point = ECC.generate(curve='p256').pointQ
AES_key = SHA256.new(str(AES_key_point.xy).encode()).hexdigest()[:32].encode()

print(key1_pub)
print(key1)

# 第一步 hash一下文件，并签名
filename_origin = 'SPN.pyx'
h = SHA256.new()

with open(filename_origin, 'rb') as fi:
    file_bytestring = fi.read()
    h.update(file_bytestring)
    hash_bytestring = h.digest()

filename_hash = 'SPN.pyx.hash'
fi_hash = open(filename_hash, 'wb')
fi_hash.write(hash_bytestring)
fi_hash.close()

# ECC签名过程：
# 发布者生成一个随机数k，作为临时私钥，生成对应公钥p_temp。
# S = k^-1(Hash(m) + priv * p_temp_x) mod p, p是椭圆曲线的阶
# 验证：
# P = S^-1 *Hash(m) *G + S^-1 * p_temp_x * pub

N = int('FFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551', 16)
k = randint(0, N)
p_temp = point_G * k
k_inv = number.inverse(k, N)
hash_message = int(h.hexdigest(), 16)

# 签名, 用key1
S = k_inv * (hash_message + int(key1.d * p_temp.x)) % N
S_inv = number.inverse(S, N)
P = point_G * S_inv * hash_message + key1_pub.pointQ * S_inv * p_temp.x
assert P.x == p_temp.x

filename_sign = filename_origin + '.sign'
file_sign = open(filename_sign, 'w')
file_sign.write(str(S))
file_sign.close()

# 第二步 把文件揉在一起并压缩（这里我们就直接打包在一起，然后压缩）

filename_zip = filename_origin + '.zip'
z = zipfile.ZipFile(filename_zip, 'w', zipfile.ZIP_LZMA)
z.write(filename_origin)
z.write(filename_hash)
z.write(filename_sign)
z.close()

# 第三步 打开压缩文件，然后用AES加密
cipher = AES.new(key=AES_key, mode=AES.MODE_CBC)
with open(filename_zip, 'rb') as fi_zip:
    zip_bin = fi_zip.read()
zip_bin_padded = Padding.pad(zip_bin, AES.block_size)
zip_bin_padded_encrypted = cipher.encrypt(zip_bin_padded)
with open(filename_zip + '.encrypted', 'wb') as fi_zip_enc:
    fi_zip_enc.write(zip_bin_padded_encrypted)

iv = cipher.iv

# 第四步 加密一开始的AES key
rand_r = randint(12345678987654321, 98765432123456789)
ECC_enc_p1 = AES_key_point + key2_pub.pointQ * rand_r
ECC_enc_p2 = point_G * rand_r

# 第五步 已经是发送过程了。要发送的有：
# 初始向量IV， 加密后的AES key for AES(P1, P2)
# 文件，整个压缩包
# pubkey, p_temp.x 用于ECC签名验证

# 第六步 接受并解密AES key
result_point = ECC_enc_p1 + (-ECC_enc_p2 * key2.d)
print(str(result_point.xy).encode() == str(AES_key_point.xy).encode())

AES_key_dec = SHA256.new(str(result_point.xy).encode()).hexdigest()[:32].encode()
AES_key = SHA256.new(str(AES_key_point.xy).encode()).hexdigest()[:32].encode()

assert AES_key_dec == AES_key

# 第七步 解密文件
file_encrypted = open(filename_zip + '.encrypted', 'rb')
file_enced_bin = file_encrypted.read()

cipher_dec = AES.new(AES_key_dec, AES.MODE_CBC, iv)
plain = Padding.unpad(cipher_dec.decrypt(file_enced_bin), AES.block_size)

file_decrypted = open(filename_zip + 'dec.zip', 'wb')
file_decrypted.write(plain)
file_encrypted.close()
file_decrypted.close()

# 第八步 打开压缩包 解压缩
z_new = zipfile.ZipFile(filename_zip + 'dec.zip')
z_new.extractall('./dec')

# 第九步 验证签名
hash_fi = open('./dec/' + filename_hash, 'rb')
hash_message = hash_fi.read()
hash_fi.close()

S_inv = number.inverse(S, N)
P = point_G * S_inv * int.from_bytes(hash_message, 'big') + key1_pub.pointQ * S_inv * p_temp.x
if int(p_temp.x) == int(P.x):
    print('Signature Verified')
else:
    print('Signature verification failed!')

# 到这里就完了
# todo: 包装成函数形式
