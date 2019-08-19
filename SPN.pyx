#SPN：置换-代换网络。这个模块手动实现了一个SPN
cdef SPN_base(long long origin, int key, short substitution_box[256], char permutation_box[32], int rnd):
    cpdef output_
