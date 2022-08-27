"""
搜索方式即算法选择：退火算法和遗传算法串行组合：
    为了兼顾求解效率和解的质量，遗传算法的初始解不随机生成，而是经过退火算法的筛选和处理得到，这样能够更好更快地得到最优解。
"""
import random
import time
from multiprocessing import Process, Lock, Manager, Value  # , Array

from Solution_Algorithm.memory import *
from Solution_Algorithm.sol_action import *
from Solution_Algorithm.sol_completionTime import *
from Solution_Algorithm.sol_init import *

lock = Lock()


def run_SA(best_CompleteTime, i):
    global lock
    T = 1000  # 模拟退火温度
    a = 0.97  # 降温速度
    b = 0.5  # 权重更新系数，控制权重变化速度
    # 用列表分别存储8个摧毁算子的权重、次数、分数等信息
    weight = [1 for i in range(8)]  # 算子的初始权重，[1,1]
    UseTimes = [0 for i in range(8)]  # 初始次数，0
    Score = [1 for i in range(8)]  # 算子初始得分，1
    current_Solution = genInitialSol()  # 当前解
    # best_CompleteTime.value = time_scheduling_end(bestSolution, 1)
    iterx, iterxMax = 0, 10  # 初始迭代次数、最大迭代次数10
    # global T, current_Solution, best_CompleteTime.value, bestSolution, iterx
    while iterx < iterxMax:  # 终止条件：达到迭代次数，不满足终止条件就缓慢降低温度继续搜索)
        while T > 10:  # 终止温度
            OperatorIndex, newSolution = selectAndUseOperator(weight, current_Solution, UseTimes)
            # 轮盘赌输入初始权重、当前解，得到新解、选择的算子序号
            completeTime = completion_time_calculation(current_Solution)
            new_completeTime = completion_time_calculation(newSolution)
            # completeTime = time_scheduling_end(current_Solution, 1)
            # new_completeTime = time_scheduling_end(newSolution, 1)
            if new_completeTime <= completeTime:  # 判断新解与旧解的距离
                current_Solution = newSolution.copy()
                if new_completeTime <= best_CompleteTime.value:  # 新解<最优解则替换成最优解
                    with lock:
                        bestSolution1 = copy.deepcopy(newSolution)
                        Memory.save(bestSolution1)
                        best_CompleteTime.value = copy.deepcopy(new_completeTime)
                    Score[OperatorIndex] += 1.5  # 如果是最优解的话权重增加到1.5
                else:
                    Score[OperatorIndex] += 1.2  # 不是最优解仅仅好于旧解的话权重增加1.2
            else:
                if rd.random() < np.exp(completeTime - new_completeTime / 0.3 * T):
                    # if rd.random() < np.exp(- new_completeTime / T):
                    # 应改成(new_completeTime  - completeTime)，使用模拟退火算法的接受准则在一定标准下接受劣解
                    current_Solution = newSolution.copy()
                    Score[OperatorIndex] += 0.8  # 满足接受准则的劣解，权重增加0.8
                else:
                    Score[OperatorIndex] += 0.6  # 不满足接受准则权重仅增加0.6
            # 更新算子权重，（1-b）应该放前面，这个例子里取b=0.5，无影响
            weight[OperatorIndex] = weight[OperatorIndex] * b + (1 - b) * \
                                    (Score[OperatorIndex] / UseTimes[OperatorIndex])
            print("{}/{}  object:  {}    {}".format(iterx, T, best_CompleteTime.value, weight))
            T = a * T  # 温度指数下降
        iterx += 1  # 完成一次降温过程算一次迭代
        T = 1000  # 一次迭代完毕后重新设置初始温度继续迭代
    # np.savetxt("../Result/退火算法最优解-加工腔任务分配.txt", bestSolution.T, fmt='%-10s', delimiter=' ')


def run_GA(group_num, times):
    start = time.time()  # 用于记录程序运行时间
    random.seed()
    group = []
    choice = []
    res_group = []
    # group_init = simulated_annealing(N, 0.9, 10000, 1, group_num, 100, 32)
    for i in range(group_num):
        # answer = GA.random_answer()  # 每次将一个随机解加入进来
        answer = genInitialSol()
        group.append(answer)  # 每次将它对应的长度也就是时间加入进来
        t = completion_time_calculation(answer)
        choice.append(1 / t)  # 时间越小的解越优秀
    choice = [item / sum(choice) for item in choice]  # 归一化
    for i in range(1, len(choice)):  # 在0-1之间随机取一个随机数，落在其中的概率就和归一化概率相同
        choice[i] += choice[i - 1]  # 把choice搞成叠加的形式,例如choice[1]=choice[1]+choice[0]
    for i in range(times):  # 对于迭代次数，每迭代一次产生一个新的族群
        print("第{}次进化：".format(i + 1))
        new_group = []
        for j in range(group_num // 2):  # 对于每个每个族群，要进行总数量除以2的迭代次数，就可以产生一个新的族群
            team = []  # 然后每一次进行交换的时候，需要产生两个解，或者说选择两个解进行交换
            for t in range(2):
                y = random.random()  # 先产生一个随机数，这个随机数根据其在0到1之间的距离位置判断
                if choice[0] >= y:  # 如果它小于第一个数的话，那么选择序号那么选择序号为0的
                    team.append(group[0])
                    continue
                for tt in range(1, len(choice)):
                    if choice[tt - 1] < y <= choice[tt]:  # 如果大于tt-1小于tt,那么就将其判断为tt，这样子选择了两个解之后就开始进行交换隐私
                        team.append(group[tt])
                        break
            new_group.extend(change(team[0], team[1]))
        group = new_group
        mid_group = [completion_time_calculation(item) for item in new_group]
        min_index = mid_group.index(min(mid_group))
        res_group.append([new_group[min_index], min(mid_group)])
    res_group.sort(key=lambda x: x[1], reverse=False)
    for j in range(2):
        print(res_group[0][j])
    end = time.time()
    print(end - start, 's')
    return res_group[0][0]


