import numpy as np

def fnv1a_py(msg):

    FNV_PRIME_32 = np.uint32(16777619)
    FNV_OFFSET_32 = np.uint32(2166136261)

    hash = FNV_OFFSET_32

    for i in range(len(msg)):
        v = np.uint32(ord(msg[i]))
        hash = np.uint32(np.bitwise_and( (np.uint64(np.bitwise_xor(v , hash)) * np.uint64(FNV_PRIME_32)) , np.uint32(2**32-1 ) ) )
    
    return hash



