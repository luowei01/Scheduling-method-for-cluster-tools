"""
    对晶圆路径、加工腔任务分配进行编码并实现相互的转换
"""
import numpy as np
import copy
from Solution_Algorithm.data_source import *


# 全体晶圆路径编码：名称转数组形式
def path_code(w_path):
    k = copy.copy(w_path)
    k = np.delete(k, 0, axis=1)
    k = np.delete(k, 0, axis=0)
    code = {i[j]: j for i in Machines(Tp) for j in range(len(i))}
    return np.array([[code[j] for j in i] for i in k])


# 全体晶圆路径解码:纯数组转名称形式
def path_decode(w_path):
    n = np.array([[Machines(Tp)[j][i[j]] for j in range(len(Machines(Tp)))] for i in w_path])
    a = ['晶圆{}'.format(i + 1) for i in range(len(n))]
    b = ['编号'] + ['工序{}'.format(i + 1) for i in range(len(Machines(Tp)))]
    n = np.column_stack((a, n))
    n = np.row_stack((b, n))
    return n


# 全体晶圆路径转加工腔任务:纯数组相互转化
def task(w_path1):
    a = 0
    b = []
    for i in Machines(Tp):
        b.append(a)
        a = a + len(i)
    b = np.array(b)
    w_path = copy.deepcopy(w_path1)
    d = [[] for i in range(len(Machines(Tp))) for j in Machines(Tp)[i]]
    num = [i + 1 for i in range(len(Machines(Tp))) for j in Machines(Tp)[i]]  # 模块对应的工序号
    for i in range(len(w_path)):
        w_path[i] = w_path[i] + b
        for j in w_path[i]:
            d[j].append([i + 1, num[j]])
    array = np.full([len(d), len(max(d, key=lambda x: len(x)))], '.', object)
    for i, j in enumerate(d):
        array[i][0:len(j)] = j
    return array


# 全体加工腔任务转晶圆路径:纯数组的加工腔任务转纯数组的晶圆路经
def path(p_task):
    a = [[] for j in range(N)]
    for i in range(len(p_task)):
        for j in p_task[i]:
            if j[0] != '.':
                a[int(j[0] - 1)].append(i)
    a = np.array(a)
    b = []
    c = 0
    for i in Machines(Tp):
        b.append(c)
        c = c + len(i)
    b = np.array(b)
    for i in range(len(a)):
        a[i] = a[i] - b
    return a


# 全体加工腔任务编码:删去首列加工腔名称，化为纯数组计算
def task_code(p_task):
    k = copy.deepcopy(p_task)
    k = np.delete(k, 0, axis=1)
    # k = np.delete (k,0,axis = 0)
    return k


# 全体加工腔任务解码：首列添加对应的加工腔名称
def task_decode(p_task):
    h = copy.deepcopy(p_task)
    a = [j for i in Machines(Tp) for j in i]
    h = np.column_stack((a, h))
    return h


Tp_number = [[j for j in range(len(i))] for i in Machines(Tp)]  # tp工艺路径下并行腔编号
Tp_para_num = [len(i) for i in Tp_number]  # tp工艺路径下并行腔的数量


# 工艺路径编码:求给定工艺路径的所有晶圆加工的可走路线
def Tp_code(p_path):
    # @ 执行组合排列的函数
    def doExchange(array):
        # 当数组大于等于2个的时候
        if len(array) >= 2:
            # 第一个数组的长度
            len1 = len(array[0])
            # 第二个数组的长度
            len2 = len(array[1])
            # 2个数组产生的组合数
            lenBoth = len1 * len2
            #  申明一个新数组,做数据暂存
            items = [[] for i in range(lenBoth)]
            # 申明新数组的索引
            index = 0
            # 2层嵌套循环,将组合放到新数组中
            for i in range(len1):
                for j in range(len2):
                    a = copy.copy(array[0][i])
                    if type(a) == int:
                        a = [a, array[1][j]]
                    else:
                        a.append(array[1][j])
                    items[index] = a
                    index = index + 1
            # 将新组合的数组并到原数组中
            newArr = [[] for i in range((len(array) - 1))]
            for i in range(2, len(array)):
                newArr[i - 1] = array[i]
            newArr[0] = items
            # 执行回调
            return doExchange(newArr)
        else:
            return array[0]

    # m = [[j for j in range(len(i))] for i in p_path if (len(i) != 1)]#去除非并行腔编码
    # m = [[j for j in range(len(i))] for i in p_path]  # 保留非并行腔编码
    return np.array(doExchange(Tp_number))


# 工艺路径解码：求所有数字路径的对应加工腔
def Tp_decode(p_path):
    n = np.array([[Machines(Tp)[j][i[j]] for j in range(len(Machines(Tp)))] for i in p_path])
    a = ['晶圆{}'.format(i + 1) for i in range(len(n))]
    b = ['编号'] + ['工序{}'.format(i + 1) for i in range(len(Machines(Tp)))]
    n = np.column_stack((a, n))
    n = np.row_stack((b, n))
    return n
