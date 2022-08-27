from multiprocessing import Process, Lock, Manager  # Value , Array
from ctypes import c_bool
from pynput.keyboard import Key, Listener  # ,Controller
import time

from Solution_Algorithm.excel import Excel
from Solution_Algorithm.memory import *
from Solution_Algorithm.display import *
from Solution_Algorithm.sol_init import *
from Solution_Algorithm.sol_action import *
from Solution_Algorithm.sol_completionTime import *
from Solution_Algorithm.tm_schedule import *


def listen(flag1, flag2):
    def on_press(key):
        print('{0} 被按下'.format(key))

    # 释放按钮，按esc按键会退出监听
    def on_release(key):
        print('{0} 被释放'.format(key))
        if key == Key.esc:
            flag1.value = False
            return False
        if key == Key.space:
            flag2.value = not flag2.value

    with Listener(on_press=on_press, on_release=on_release, Daemon=True) as listener:
        listener.join()


def display_obj(flag1, flag2, best_CompleteTime):
    start1 = time.time()
    print("按ESC彻底关闭进程，后续无法再显示窗口\n按空格可显示、隐藏窗口")
    list1 = []
    list2 = []
    plt.rcParams['font.sans-serif'] = ['SimHei']  # show chinese
    plt.rcParams['axes.unicode_minus'] = False  # Show minus sign
    plt.xlabel('Iterations')
    plt.ylabel('Obj Value')
    while flag1.value:
        list1.append(round(time.time() - start1, 1))
        list2.append(best_CompleteTime.value)
        if flag2.value:
            plt.clf()  # 清空并更新迭代数据
            plt.grid()
            plt.plot(list1, list2, color='r')
            plt.pause(0.01)
        else:
            plt.close()
        time.sleep(0.1)
    plt.savefig("./Result/{}工艺路径/{}工艺路径迭代时间曲线({}).png".format(Tp_strname(), Tp_strname(), N))


lock = Lock()


def run_SA(weight, useTimes, score, best_CompleteTime, i, iterateMax):
    global lock
    T = 1000  # 模拟退火温度
    T_min, T_max = 10, 1000
    a = 0.97  # 降温速度
    b = 0.5  # 权重更新系数，控制权重变化速度
    current_Solution = genInitialSol()  # 当前解
    iterate = 0  # 初始迭代次数
    bestSolution1 = current_Solution.copy()
    while iterate < iterateMax.value:  # 终止条件：达到迭代次数，不满足终止条件就缓慢降低温度继续搜索)
        while T > T_min:  # 终止温度
            OperatorIndex, newSolution = selectAndUseOperator(weight, current_Solution, useTimes)
            # 轮盘赌输入初始权重、当前解，得到新解、选择的算子序号
            completeTime = completion_time_calculation(current_Solution)
            new_completeTime = completion_time_calculation(newSolution)
            if new_completeTime <= completeTime:  # 判断新解与旧解的距离
                current_Solution = newSolution.copy()
                if new_completeTime <= best_CompleteTime.value:  # 新解<最优解则替换成最优解
                    with lock:
                        bestSolution1 = copy.deepcopy(newSolution)
                        best_CompleteTime.value = copy.deepcopy(new_completeTime)
                    score[OperatorIndex] += 1.5  # 如果是最优解的话权重增加到1.5
                else:
                    score[OperatorIndex] += 1.2  # 不是最优解仅仅好于旧解的话权重增加1.2
            else:
                if rd.random() < np.exp(completeTime - new_completeTime / 0.3 * T):
                    # 应改成(new_completeTime  - completeTime)，使用模拟退火算法的接受准则在一定标准下接受劣解
                    current_Solution = newSolution.copy()
                    score[OperatorIndex] += 0.8  # 满足接受准则的劣解，权重增加0.8
                else:
                    score[OperatorIndex] += 0.6  # 不满足接受准则权重仅增加0.6
            # 更新算子权重，（1-b）应该放前面，这个例子里取b=0.5，无影响
            weight[OperatorIndex] = weight[OperatorIndex] * b + (1 - b) * (score[OperatorIndex]
                                                                           / useTimes[OperatorIndex])
            print("迭代次数：{}/温度：{}/进程：{}  object:  {}    {}".format(iterate, T, i, best_CompleteTime.value, weight))
            T = a * T  # 温度指数下降
        iterate += 1  # 完成一次降温过程算一次迭代
        T = T_max  # 一次迭代完毕后重新设置初始温度继续迭代
    try:
        if best_CompleteTime.value < completion_time_calculation(Memory.load()):  # 如果此次求解完工时间小于历史求解，则更新
            Memory.save(bestSolution1)
    except FileNotFoundError:
        Memory.save(bestSolution1)


if __name__ == '__main__':
    # 多进程求解
    with Manager() as manager:
        start = time.time()

        # 1.求解最佳加工任务分配方案
        print('第一步：进行加工任务分配方案求解···')
        # 控制程序运行的 标志位
        Flag1 = manager.Value(c_bool, True)
        Flag2 = manager.Value(c_bool, True)
        IterateMax = manager.Value('i', 10)  # 设置算法迭代次数
        if Tp == D or Tp == E:  # 工艺路径D/E晶圆可选择的不同路径数量较少，迭代优无化效果。
            IterateMax.value = 1
        elif Tp == B:  # 工艺路径B实测迭代5次可看到收敛效果
            IterateMax.value = 5
        else:  # 工艺路径A/C需要10次迭代
            IterateMax.value = 10
        # 进程共享全局变量
        # 用列表分别存储8个摧毁算子的权重、次数、分数等信息
        Weight = manager.list([1 for i in range(8)])  # 算子的初始权重，[1,1]
        UseTimes = manager.list([0 for i in range(8)])  # 初始次数，0
        Score = manager.list([1 for i in range(8)])  # 算子初始得分，1
        Best_CompleteTime = manager.Value('d', completion_time_calculation(genInitialSol()))
        ps = [Process(target=display_obj, args=(Flag1, Flag2, Best_CompleteTime,), daemon=True)] + \
             [Process(target=listen, args=(Flag1, Flag2,), daemon=True)] + \
             [Process(target=run_SA, args=(Weight, UseTimes, Score, Best_CompleteTime, i, IterateMax,)) for i in
              range(4)]
        for i in ps:
            i.start()
        for i in ps:
            if i != ps[0] and i != ps[1]:
                i.join()
        Flag1.value = False
        end1 = time.time()

        # 2.求解最佳任务分配方案下的执行策略
        print('第二步：正在进行机械手调度求解···')
        bestSolution = Memory.load()
        O, wafers_path, fact_CompleteTime, TM_acs, Clear = time_scheduling(bestSolution, 0.1)
        end2 = time.time()

        # 3.输出、保存结果
        print('最佳分配方案近似完工时间为{}秒，求解最佳任务分配方案耗时：{}秒'.format(Best_CompleteTime.value, end1 - start))
        print('最佳分配方案标准完工时间为{}秒，求解最佳任务分配方案下的执行策略耗时：{}秒'.format(fact_CompleteTime, end2 - end1))
        np.savetxt("Result/{}工艺路径/{}工艺路径各加工腔任务池({}).txt".format(Tp_strname(), Tp_strname(), N),
                   task_decode(bestSolution).T,
                   encoding='utf_8_sig', fmt='%10s', delimiter=' ')
        np.savetxt("Result/{}工艺路径/{}工艺路径各晶圆加工路径({}).txt".format(Tp_strname(), Tp_strname(), N),
                   path_decode(path(bestSolution)), encoding='utf_8_sig', fmt='%-10s', delimiter=' ')
        Excel.out_order(O, wafers_path, fact_CompleteTime)
        Excel.out_PM(O, wafers_path, fact_CompleteTime)
        Excel.out_TM(TM_acs, fact_CompleteTime)
        if Tp == C or Tp == D or Tp == E:
            Excel.out_clear(Clear, fact_CompleteTime)
        print('全部结果已保存至Result文件夹')
        end3 = time.time()

        plot_gan_result(O, wafers_path, 1, N, fact_CompleteTime)
        print('程序总耗时：{}秒'.format(end3 - start))
