"""
 由初解生成新解，算子的形式决定了在解邻域中搜索的范围和路径，下面的算子分别从大邻域到小邻域的范围对解进行修改，算子的使用利用轮盘赌进行选择。

"""
import random as rd
from Solution_Algorithm.tm_schedule import *


# 定义领域生成算子
def createActions(n):
    action_list = []
    n_swap = n // 2
    # 第一种算子（Swap）：前半段与后半段对应位置一对一交换
    for i in range(n_swap):
        action_list.append([1, i, i + n_swap])
    # 第二中算子（DSwap）：前半段与后半段对应位置二对二交换
    for i in range(0, n_swap, 2):
        action_list.append([2, i, i + n_swap])
    # 第三种算子（Reverse）：指定长度的序列反序
    for i in range(0, n, 4):
        action_list.append([3, i, i + 3])
    return action_list


# 生成邻域
def doAction(node_id_list, action):
    node_id_list_ = copy.deepcopy(node_id_list)
    if action[0] == 1:
        index_1 = action[1]
        index_2 = action[2]
        node_id_list_[index_1], node_id_list_[index_2] = node_id_list_[index_2], node_id_list_[index_1]
        return node_id_list_
    elif action[0] == 2:
        index_1 = action[1]
        index_2 = action[2]
        temporary = [node_id_list_[index_1], node_id_list_[index_1 + 1]]
        node_id_list_[index_1] = node_id_list_[index_2]
        node_id_list_[index_1 + 1] = node_id_list_[index_2 + 1]
        node_id_list_[index_2] = temporary[0]
        node_id_list_[index_2 + 1] = temporary[1]
        return node_id_list_
    elif action[0] == 3:
        index_1 = action[1]
        index_2 = action[2]
        node_id_list_[index_1:index_2 + 1] = list(reversed(node_id_list_[index_1:index_2 + 1]))
        return node_id_list_


# 将一个数组随机分为多个（等于并行腔数量）数组
def divide(lst1, min_size1, split_size1):
    lst1 = copy.deepcopy(lst1)
    # np.random.seed(0)
    np.random.shuffle(lst1)
    it = iter(lst1)
    from itertools import islice
    size = len(lst1)
    for i in range(split_size1 - 1, 0, -1):
        s = np.random.randint(min_size1, size - int(min_size1 * i) + 1)
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


# 定义算子0：全部并行腔的所有任务重新随机分配
def resign_all(current_sol):
    # 随机选择一批并行腔进行任务的重新分配
    sol = copy.deepcopy(current_sol)
    num = np.array([i + 1 for i in range(len(Machines(Tp))) for j in Machines(Tp)[i]])  # 模块对应的工序号
    initialSol = np.full([len(num), N], '.', tuple)  # 存放初始解
    k = 0
    for i in Machines(Tp):
        if len(i) == 1:
            initialSol[k] = sol[k]
            k += 1
        else:
            p_task = pm_task(list(range(1, N + 1)), N // len(i), len(i))
            for j in p_task:
                initialSol[k][0:len(j)] = [[mi, num[k]] for mi in j]
                k += 1
    return initialSol


# 定义算子1：随机选择并行腔，所有任务重新随机分配
def resign_part_all(current_sol):
    # 随机选择一批并行腔进行任务的重新分配
    sol = copy.deepcopy(current_sol)
    num = np.array([i + 1 for i in range(len(Machines(Tp))) for j in Machines(Tp)[i]])  # 模块对应的工序号
    initialSol = np.full([len(num), N], '.', tuple)  # 存放初始解
    k = 0
    r = 0
    while len(Machines(Tp)[r]) == 1:
        r = rd.randint(0, M - 1)
    for i in Machines(Tp):
        if i == Machines(Tp)[r]:
            p_task = pm_task(list(range(1, N + 1)), N // len(i) - 2, len(i))
            for j in p_task:
                initialSol[k][0:len(j)] = [[mi, num[k]] for mi in j]
                k += 1
        else:
            for j in i:
                initialSol[k] = sol[k]
                k += 1
    return initialSol


# 定义算子2：随机选择并行腔,部分任务重新随机分配
def resign_part_part(current_sol):
    # 随机选择一批并行腔进行任务的重新分配
    sol = copy.deepcopy(current_sol)
    num = np.array([i + 1 for i in range(len(Machines(Tp))) for j in Machines(Tp)[i]])  # 模块对应的工序号
    initialSol = np.full([len(num), N], '.', tuple)  # 存放初始解
    k = 0
    r = 0
    while len(Machines(Tp)[r]) == 1:
        r = rd.randint(0, M - 1)
    for i in Machines(Tp):
        if i == Machines(Tp)[r]:
            task1 = []
            task2 = []
            number = []
            for j in i:
                m = [s[0] for s in copy.deepcopy(sol[k]) if s[0] != '.']
                np.random.shuffle(m)
                task1 = task1 + m[0:4]
                task2.append(m[4:])
                number.append(k)
                k += 1
            task1 = list(divide(task1, 4, len(i)))
            for j in range(len(i)):
                m = task2[j] + task1[j]
                m.sort()
                initialSol[number[j]][0:len(m)] = [[mi, num[number[j]]] for mi in m]
        else:
            for j in i:
                initialSol[k] = sol[k]
                k += 1
    return initialSol


# 定义算子3：随机选择并行腔,进行随机任务插入,多的给少的
def resign_insert(current_sol):
    # 随机选择一批并行腔进行任务的重新分配
    sol = copy.deepcopy(current_sol)
    num = np.array([i + 1 for i in range(len(Machines(Tp))) for j in Machines(Tp)[i]])  # 模块对应的工序号
    initialSol = np.full([len(num), N], '.', tuple)  # 存放初始解
    k = 0
    r = 0
    while len(Machines(Tp)[r]) == 1:
        r = rd.randint(0, M - 1)
    for i in Machines(Tp):
        if i == Machines(Tp)[r]:
            task = []
            task_num = []
            number = []
            for j in i:
                m = [s[0] for s in copy.deepcopy(sol[k]) if s[0] != '.']
                task.append(m)
                task_num.append(len(m))
                number.append(k)
                k += 1
            index1 = task_num.index(max(task_num))
            index2 = task_num.index(min(task_num))
            m = rd.randint(0, len(task[index1]) - 1)
            task[index2].append(task[index1][m])
            del task[index1][m]

            for j in range(len(i)):
                m = task[j]
                m.sort()
                initialSol[number[j]][0:len(m)] = [[mi, num[number[j]]] for mi in m]
        else:
            for j in i:
                initialSol[k] = sol[k]
                k += 1
    return initialSol


# 定义算子4：随机选择并行腔,随机选择任务随机位置交换
def resign_swap_rand(current_sol):
    # 随机选择一批并行腔进行任务的重新分配
    sol = copy.deepcopy(current_sol)
    num = np.array([i + 1 for i in range(len(Machines(Tp))) for j in Machines(Tp)[i]])  # 模块对应的工序号
    initialSol = np.full([len(num), N], '.', tuple)  # 存放初始解
    k = 0
    r = 0
    while len(Machines(Tp)[r]) == 1:
        r = rd.randint(0, M - 1)
    for i in Machines(Tp):
        if i == Machines(Tp)[r]:
            task = []
            task_num = []
            number = []
            for j in i:
                m = [s[0] for s in copy.deepcopy(sol[k]) if s[0] != '.']
                task.append(m)
                task_num.append(len(m))
                number.append(k)
                k += 1
            r1, r2 = rd.sample(list(range(len(task))), 2)
            r3 = rd.randint(0, len(task[r1]) - 1)
            r4 = rd.randint(0, len(task[r2]) - 1)
            task[r1].append(task[r2][r4])
            task[r2].append(task[r1][r3])
            del task[r1][r3]
            del task[r2][r4]

            for j in range(len(i)):
                m = task[j]
                m.sort()
                initialSol[number[j]][0:len(m)] = [[mi, num[number[j]]] for mi in m]
        else:
            for j in i:
                initialSol[k] = sol[k]
                k += 1
    return initialSol


# 定义算子5：随机选择并行腔,随机选择任务附件位置交换
def resign_swap_near(current_sol):
    # 随机选择一批并行腔进行任务的重新分配
    sol = copy.deepcopy(current_sol)
    num = np.array([i + 1 for i in range(len(Machines(Tp))) for j in Machines(Tp)[i]])  # 模块对应的工序号
    initialSol = np.full([len(num), N], '.', tuple)  # 存放初始解
    k = 0
    r = 0
    while len(Machines(Tp)[r]) == 1:
        r = rd.randint(0, M - 1)
    for i in Machines(Tp):
        if i == Machines(Tp)[r]:
            task = []
            task_num = []
            number = []
            for j in i:
                m = [s[0] for s in copy.deepcopy(sol[k]) if s[0] != '.']
                task.append(m)
                task_num.append(len(m))
                number.append(k)
                k += 1
            r1, r2 = rd.sample(list(range(len(task))), 2)
            r3 = rd.randint(0, len(task[r1]) - 1)
            if r3 == 0:
                r4 = rd.randint(1, 2)
            elif r3 == len(task[r2]) - 1:
                r4 = rd.randint(r3 - 1, r3)
            elif r3 > len(task[r2]) - 1:
                r4 = len(task[r2]) - 1
            else:
                r4 = rd.randint(r3 - 1, r3 + 1)
            task[r1].append(task[r2][r4])
            task[r2].append(task[r1][r3])
            del task[r1][r3]
            del task[r2][r4]

            for j in range(len(i)):
                m = task[j]
                m.sort()
                initialSol[number[j]][0:len(m)] = [[mi, num[number[j]]] for mi in m]
        else:
            for j in i:
                initialSol[k] = sol[k]
                k += 1
    return initialSol


# 定义算子6：选择任务负荷不对等的加工腔任务均衡调整
def resign_swap_fair(current_sol):
    # 随机选择一批并行腔进行任务的重新分配
    sol = copy.deepcopy(current_sol)
    num = np.array([i + 1 for i in range(len(Machines(Tp))) for j in Machines(Tp)[i]])  # 模块对应的工序号
    initialSol = np.full([len(num), N], '.', tuple)  # 存放初始解
    k = 0
    for i in Machines(Tp):
        if len(i) != 1:
            task = []
            task_num = []
            number = []
            for j in i:
                m = [s[0] for s in copy.deepcopy(sol[k]) if s[0] != '.']
                task.append(m)
                task_num.append(len(m))
                number.append(k)
                k += 1
            if max(task_num) - min(task_num) > 2:
                index1 = task_num.index(max(task_num))
                index2 = task_num.index(min(task_num))
                m = rd.randint(0, len(task[index1]) - 1)
                task[index2].append(task[index1][m])
                del task[index1][m]

            for j in range(len(i)):
                m = task[j]
                m.sort()
                initialSol[number[j]][0:len(m)] = [[mi, num[number[j]]] for mi in m]
        else:
            initialSol[k] = sol[k]
            k += 1
    return initialSol


# 定义算子7：选择等效加工时间最长的并行腔，随机选择任务附近位置交换
def resign_long(current_sol):
    sol = copy.deepcopy(current_sol)
    num = np.array([i + 1 for i in range(len(Machines(Tp))) for j in Machines(Tp)[i]])  # 模块对应的工序号
    initialSol = np.full([len(num), N], '.', tuple)  # 存放初始解
    k = 0
    r = process_time_eq.index(max([process_time_eq[i] for i in range(len(process_time_eq)) if len(Machines(Tp)[i]) != 1]))
    for i in Machines(Tp):
        if i == Machines(Tp)[r]:
            task = []
            task_num = []
            number = []
            for j in i:
                m = [s[0] for s in copy.deepcopy(sol[k]) if s[0] != '.']
                task.append(m)
                task_num.append(len(m))
                number.append(k)
                k += 1
            task_index = [i for i in range(len(task))]
            r1, r2 = rd.sample(task_index, 2)
            r3 = rd.randint(0, len(task[r1]) - 1)
            if r3 == 0:
                r4 = rd.randint(1, 2)
            elif r3 == len(task[r2]) - 1:
                r4 = rd.randint(r3 - 1, r3)
            elif r3 > len(task[r2]) - 1:
                r4 = len(task[r2]) - 1
            else:
                r4 = rd.randint(r3 - 1, r3 + 1)
            task[r1].append(task[r2][r4])
            task[r2].append(task[r1][r3])
            del task[r1][r3]
            del task[r2][r4]

            for j in range(len(i)):
                m = task[j]
                m.sort()
                initialSol[number[j]][0:len(m)] = [[mi, num[number[j]]] for mi in m]
        else:
            for j in i:
                initialSol[k] = sol[k]
                k += 1
    return initialSol


# 定义算子选择轮盘赌
def selectAndUseOperator(Weight, current_sol, UseTimes):
    Operator = -1  # 算子初始值，除0/1外的数
    sol = copy.deepcopy(current_sol)  # 深拷贝,currentSolution之后的改变不影响sol
    new_sol = None
    Roulette = np.array(
        Weight).cumsum()  # 轮盘赌,cumsum()把列表里之前数的和加到当前列，如a=[1,2,3,4]，comsum结果为[1,3,6,10]
    r = rd.uniform(0, max(Roulette))  # 随机生成【0，轮盘赌列表最大数】之间的浮点数
    for i in range(
            len(Roulette)):  # 如wDestroyed = 【1,1】，destroyedRoulette = 【1,2】，判断生成的r在哪个范围内，【0,1】选序列为0的算子，【1,2】选序列为1的算子
        if Roulette[i] >= r:  # 判断是否在某个算子的对应范围内
            if i == 0:  # 在序列为0的算子范围内，选择随机移除
                Operator = i
                new_sol = resign_all(sol)  # 通过算子1产生新解
                UseTimes[i] += 1  # 算子1使用次数累加
                break  # 满足其中一个范围就跳出for循环
            elif i == 1:  # 在序列为1的算子范围内
                Operator = i  # 与上面类似
                new_sol = resign_part_all(sol)
                UseTimes[i] += 1
                break
            elif i == 2:
                Operator = i
                new_sol = resign_part_part(sol)
                UseTimes[i] += 1
                break
            elif i == 3:
                Operator = i
                new_sol = resign_insert(sol)
                UseTimes[i] += 1
                break
            elif i == 4:
                Operator = i
                new_sol = resign_swap_rand(sol)
                UseTimes[i] += 1
                break
            elif i == 5:
                Operator = i
                new_sol = resign_swap_near(sol)
                UseTimes[i] += 1
                break
            elif i == 6:
                Operator = i
                new_sol = resign_swap_fair(sol)
                UseTimes[i] += 1
                break
            elif i == 7:
                Operator = i
                new_sol = resign_long(sol)
                UseTimes[i] += 1
                break
    return Operator, new_sol


def change(x, y):
    # 随机选择一批并行腔进行任务的重新分配
    sol1 = copy.deepcopy(x)
    sol2 = copy.deepcopy(y)
    k = 0
    r = 0
    while len(Machines(Tp)[r]) == 1:
        r = rd.randint(0, M - 1)
    for i in Machines(Tp):
        for j in i:
            if i == Machines(Tp)[r]:
                buffer = sol1[k]
                sol1[k] = sol2[k]
                sol2[k] = buffer
            k += 1
    return sol1, sol2
