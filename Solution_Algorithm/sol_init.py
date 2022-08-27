import numpy as np
from Solution_Algorithm.data_source import *


# 初始解生成模块
def genInitialSol():
    # 将一个数组随机分为多个（等于并行腔数量）数组
    def divide(lst1, min_size1, split_size1):
        # lst1 = copy.deepcopy(lst1)
        # np.random.seed(0)
        np.random.shuffle(lst1)
        it = iter(lst1)
        from itertools import islice
        size = len(lst1)
        for i in range(split_size1 - 1, 0, -1):
            s = np.random.randint(min_size1, size - min_size1 * i)
            yield list(islice(it, 0, s))
            size -= s
        yield list(it)

    # 将随机生成的各数组进行排序
    def pm_task(lst1, min_size1, split_size1):
        n = list(divide(lst1, min_size1, split_size1))
        for i in n:
            i.sort()
        array = np.full([len(n), N], '.', list)
        for i, j in enumerate(n):
            array[i][0:len(j)] = j
        return array

    # 生成完整的初始解
    num = np.array([i + 1 for i in range(len(Machines(Tp))) for j in Machines(Tp)[i]])  # 模块对应的工序号
    initialSol = np.full([len(num), N], '.', tuple)  # 存放初始解
    k = 0
    for i in Machines(Tp):
        p_task = pm_task(list(range(1, N + 1)), N // len(i) - 2, len(i))
        for j in p_task:
            initialSol[k][0:len(j)] = [[mi, num[k]] for mi in j]
            k += 1
    return initialSol
