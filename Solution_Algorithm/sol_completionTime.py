"""
目标结果求解
    1.根据生成的解求解目标值(快速计算对应加工方案下的近似完工时间，作为评价依据）
"""
from Solution_Algorithm.data_struct import *
from Solution_Algorithm.code import *


# 计算近似完工时间
def completion_time_calculation(sol):
    # 根据解得到晶圆具体的加工路径
    lujing = path_decode(path(sol))
    lujing = np.delete(lujing, 0, axis=0)
    lujing = np.delete(lujing, 0, axis=1)
    # 将工艺路径用到的腔室转为字典，用来记录腔室加工过的晶圆编号
    machines = Machines(Tp)
    arr = []
    for i in range(len(machines)):
        for j in range(len(machines[i])):
            arr.append(machines[i][j])
    wafers = {x: [] for x in arr}
    # 派工总方案
    O = [[Work_process() for j in range(0, M + 1, 1)] for i in range(0, N + 1, 1)]
    for i in range(1, N + 1, 1):
        # print("晶圆" + str(i) + "路径:" + str(list(lujing[i - 1])))
        for j in range(1, M + 1, 1):
            # Ms,Mo:[i][j]当前加工模块和下一加工模块
            Ms = list(lujing[i - 1])[j - 1]
            if j == M:
                Mo = list(lujing[i - 1])[j - 1]
            else:
                Mo = list(lujing[i - 1])[j]
            # 记录此腔室加工过的晶圆编号
            wafers[Ms].append(i)

            # begin:晶圆在加工模块的到达时间
            if i == 1 and j == 1:
                O[i][j].begin = 0.0
            elif j == 1:
                O[i][j].begin = round((O[i - 1][3].begin + O[i - 1][3].xie + TM1(Ms=list(lujing[i - 2])[2],
                                                                                 Mo=list(lujing[i - 1])[0])), 1)
            elif j == M:
                O[i][j].begin = round((O[i][j - 1].end + O[i][j - 1].wai_wait), 1)
            else:
                m = len(wafers[Ms])
                if m == 1:
                    O[i][j].begin = round((O[i][j - 1].end + O[i][j - 1].wai_wait), 1)
                else:
                    if (TM(Ms=list(lujing[(wafers[Ms][m - 2]) - 1])[j],
                           Mo=list(lujing[i - 1])[j - 2]) == 'not exist'):
                        b = round(O[(wafers[Ms][m - 2])][j].end + 5, 1)
                    else:
                        b = round((O[(wafers[Ms][m - 2])][j + 1].begin + O[(wafers[Ms][m - 2])][j + 1].xie +
                                   TM(Ms=list(lujing[(wafers[Ms][m - 2]) - 1])[j], Mo=list(lujing[i - 1])[j - 2]) +
                                   O[i][j - 1].qu + O[i][j - 1].wai_wait), 1)
                    a = round((O[i][j - 1].end + O[i][j - 1].wai_wait), 1)
                    O[i][j].begin = a if a > b else b

            # 卸:晶圆在加工模块内的卸晶圆时间
            if j == 1:
                O[i][j].xie = 0.0
            else:
                O[i][j].xie = 5.0

            # process:该工序加工时间
            O[i][j].process = Tp[j]

            # nei_wait:晶圆在该加工模块内的等待时间
            # qu:晶圆在该加工模块内的取晶圆时间
            if j == M:
                O[i][j].nei_wait = 0.0
                O[i][j].qu = 0.0
            else:
                O[i][j].nei_wait = 0.0
                O[i][j].qu = 5.0

            # end:晶圆在加工模块的离开时间
            O[i][j].end = round((O[i][j].begin + O[i][j].xie + O[i][j].process + O[i][j].nei_wait + O[i][j].qu), 1)

            # long:晶圆在加工模块内包括取卸晶圆的停留时间
            O[i][j].long = round((O[i][j].end - O[i][j].begin), 1)

            # move:晶圆进入下一道工序的机械臂移动时间
            O[i][j].move = TM(Ms, Mo)

            # wai_wait:晶圆在该加工模块外的等待时间（离开该模块到进入下一模块的时间，大于机械臂移动时间）
            if j == M:
                O[i][j].wai_wait = 0.0
            elif j == M - 1:
                O[i][j].wai_wait = O[i][j].move
            else:
                m = len(wafers[Mo])
                if m == 0:
                    O[i][j].wai_wait = round(O[i][j].move, 1)
                else:
                    if (TM(Ms=list(lujing[(wafers[Mo][m - 1]) - 1])[j + 1],
                           Mo=list(lujing[i - 1])[j - 1]) == 'not exist'):
                        b = round(O[(wafers[Mo][m - 1])][j + 1].end - O[i][j].end, 1)
                    else:
                        b = round(O[i][j].move, 1)
                    a = round(O[i][j].move, 1)
                    O[i][j].wai_wait = a if a > b else b
    return max([O[i][M].end for i in range(1, N + 1)])


def completion_time_calculation_O(sol):
    # 根据解得到晶圆具体的加工路径
    lujing = path_decode(path(sol))
    lujing = np.delete(lujing, 0, axis=0)
    lujing = np.delete(lujing, 0, axis=1)
    # 将工艺路径用到的腔室转为字典，用来记录腔室加工过的晶圆编号
    machines = Machines(Tp)
    arr = []
    for i in range(len(machines)):
        for j in range(len(machines[i])):
            arr.append(machines[i][j])
    wafers = {x: [] for x in arr}
    # 派工总方案
    O = [[Work_process() for j in range(0, M + 1, 1)] for i in range(0, N + 1, 1)]
    for i in range(1, N + 1, 1):
        # print("晶圆" + str(i) + "路径:" + str(list(lujing[i - 1])))
        for j in range(1, M + 1, 1):
            # Ms,Mo:[i][j]当前加工模块和下一加工模块
            Ms = list(lujing[i - 1])[j - 1]
            if j == M:
                Mo = list(lujing[i - 1])[j - 1]
            else:
                Mo = list(lujing[i - 1])[j]
            # 记录此腔室加工过的晶圆编号
            wafers[Ms].append(i)

            # begin:晶圆在加工模块的到达时间
            if i == 1 and j == 1:
                O[i][j].begin = 0.0
            elif j == 1:
                O[i][j].begin = round((O[i - 1][3].begin + O[i - 1][3].xie + TM1(Ms=list(lujing[i - 2])[2],
                                                                                 Mo=list(lujing[i - 1])[0])), 1)
            elif j == M:
                O[i][j].begin = round((O[i][j - 1].end + O[i][j - 1].wai_wait), 1)
            else:
                m = len(wafers[Ms])
                if m == 1:
                    O[i][j].begin = round((O[i][j - 1].end + O[i][j - 1].wai_wait), 1)
                else:
                    if (TM(Ms=list(lujing[(wafers[Ms][m - 2]) - 1])[j],
                           Mo=list(lujing[i - 1])[j - 2]) == 'not exist'):
                        b = round(O[(wafers[Ms][m - 2])][j].end + 5, 1)
                    else:
                        b = round((O[(wafers[Ms][m - 2])][j + 1].begin + O[(wafers[Ms][m - 2])][j + 1].xie +
                                   TM(Ms=list(lujing[(wafers[Ms][m - 2]) - 1])[j], Mo=list(lujing[i - 1])[j - 2]) +
                                   O[i][j - 1].qu + O[i][j - 1].wai_wait), 1)
                    a = round((O[i][j - 1].end + O[i][j - 1].wai_wait), 1)
                    O[i][j].begin = a if a > b else b

            # 卸:晶圆在加工模块内的卸晶圆时间
            if j == 1:
                O[i][j].xie = 0.0
            else:
                O[i][j].xie = 5.0

            # process:该工序加工时间
            O[i][j].process = Tp[j]

            # nei_wait:晶圆在该加工模块内的等待时间
            # qu:晶圆在该加工模块内的取晶圆时间
            if j == M:
                O[i][j].nei_wait = 0.0
                O[i][j].qu = 0.0
            else:
                O[i][j].nei_wait = 0.0
                O[i][j].qu = 5.0

            # end:晶圆在加工模块的离开时间
            O[i][j].end = round((O[i][j].begin + O[i][j].xie + O[i][j].process + O[i][j].nei_wait + O[i][j].qu), 1)

            # long:晶圆在加工模块内包括取卸晶圆的停留时间
            O[i][j].long = round((O[i][j].end - O[i][j].begin), 1)

            # move:晶圆进入下一道工序的机械臂移动时间
            O[i][j].move = TM(Ms, Mo)

            # wai_wait:晶圆在该加工模块外的等待时间（离开该模块到进入下一模块的时间，大于机械臂移动时间）
            if j == M:
                O[i][j].wai_wait = 0.0
            elif j == M - 1:
                O[i][j].wai_wait = O[i][j].move
            else:
                m = len(wafers[Mo])
                if m == 0:
                    O[i][j].wai_wait = round(O[i][j].move, 1)
                else:
                    if (TM(Ms=list(lujing[(wafers[Mo][m - 1]) - 1])[j + 1],
                           Mo=list(lujing[i - 1])[j - 1]) == 'not exist'):
                        b = round(O[(wafers[Mo][m - 1])][j + 1].end - O[i][j].end, 1)
                    else:
                        b = round(O[i][j].move, 1)
                    a = round(O[i][j].move, 1)
                    O[i][j].wai_wait = a if a > b else b
    return O, lujing, max([O[i][M].end for i in range(1, N + 1)])
