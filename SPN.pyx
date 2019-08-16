#SPN：置换-代换网络。这个模块手动实现了一个SPN
#根据书上的讲解，SPN接受一个64bit的输入，一段密钥，特定的S盒（16x16），P盒（32）。经过异或、代换、与密钥异或后，输出一个64bit的结果。

cdef SPN_base(long long origin, int key, short substitution_box[256], char permutation_box[32], int rnd):
    cpdef output_