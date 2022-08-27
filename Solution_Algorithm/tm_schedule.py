"""
目标结果求解(动态规划插入机械手调度)
   1.根据生成的解求解目标值（解：确定好的晶圆加工路径即加工腔任务分配方案   目标值：加入机械手调度后的完工时间），作为评价依据
   2.记录根据生成解进行动态规划（加入机械臂调度）的过程，返回完工时间和晶圆各阶段、加工腔、机械臂等操作时刻信息
"""
from Solution_Algorithm.data_struct import *
from Solution_Algorithm.code import *


# 返回此任务分配方案下进行实时调度的完工时间
# unit_time指进行动态规划时算法进行决策的单位时间，关系到求解结果的准确性和算法运行时间，呈反比关系
def time_scheduling(sol, unit_time):
    # 根据解得到晶圆具体的加工路径
    lujing = path_decode(path(sol))
    lujing = np.delete(lujing, 0, axis=0)
    lujing = np.delete(lujing, 0, axis=1)
    # M = len(Tp) - 1
    # N = 75
    count = 0.0
    num_out = 0
    num_in = 0
    # 派工方案初始化
    O = [[Work_process() for j in range(0, M + 1, 1)] for i in range(0, N + 1, 1)]
    # 加工腔任务初始化
    machines = Machines(Tp)
    arr = []
    for i in range(len(machines)):
        for j in range(len(machines[i])):
            arr.append(machines[i][j])
    wafers = {x: [] for x in arr}
    for i in range(1, N + 1, 1):
        for j in range(1, M + 1, 1):
            Ms = lujing[i - 1][j - 1]
            wafers[Ms].append([i, j])
    # 记录加工腔已完成的最近一次任务
    wafers_last = {x: [0, 0, 0] for x in arr}

    # 记录各加工腔的清洗时间,此参数只有加工路径为C\D\E路径时才需要更新、使用
    clear_time = {"PM{}".format(x): 0.0 for x in range(1, 11, 1)}

    # 记录加工腔已加工晶圆的数量，到达15时进行PM的清洗
    complete_num = {"PM{}".format(x): 0 for x in range(1, 11, 1)}

    # 记录各加工腔清洁的起止时刻
    clear = {"PM{}".format(x): [] for x in range(1, 11, 1)}

    # 记录机械手的最新空闲时刻
    T_new1 = 0.0
    T_new2 = 0.0
    T_new3 = 0.0
    # 记录机械手的操作方案
    TM1_ACS = []
    TM2_ACS = []
    TM3_ACS = []
    # 进行动态时间规划
    while True:
        # 规划完所有调度任务则退出
        if num_out >= N:
            break
        # 时间参量
        count += unit_time
        print("时间规划至：{}s".format(count))

        # 按照时间顺序，对同一时刻所有加工腔任务依次进行规划
        for m in wafers:
            try:
                if count < clear_time[m]:  # 此加工腔清洗还未完成，不做任务安排,跳过
                    continue
            except KeyError:  # 查询不到清洗结束时间，此模块不需要清洗
                pass
            for n in wafers[m]:
                i = n[0]
                j = n[1]
                # Mq,Ms,Mo:[i][j]前一加工模块、当前加工模块和下一加工模块
                if j == 1:
                    Mq = (lujing[i - 1])[j - 1]
                else:
                    Mq = (lujing[i - 1])[j - 2]
                Ms = (lujing[i - 1])[j - 1]
                if j == M:
                    Mo = (lujing[i - 1])[j - 1]
                else:
                    Mo = (lujing[i - 1])[j]

                # 按照约束规则，规划此任务的阶段1
                if O[i][j].state1 == 1:  # 已规划完成的任务不再作安排，保持不变
                    pass
                else:  # 规划未完成的任务
                    if (O[wafers_last[Ms][0]][wafers_last[Ms][1]].end >= count or
                            O[i][j - 1].end >= count):  # 此加工腔的前一任务或待加工晶圆的前一道工序还未完成，等待完成再安排此任务
                        break
                    else:
                        # 路径起点修正为具体的晶圆盒
                        # move:机械臂将晶圆从上一加工腔运至本加工腔的时间
                        if j == 2:
                            if i <= 25:
                                O[i][j].move = TM(Ms='LP1_start', Mo=Ms)
                            elif i <= 50:
                                O[i][j].move = TM(Ms='LP2_start', Mo=Ms)
                            else:
                                O[i][j].move = TM(Ms='LP3_start', Mo=Ms)
                        elif j == M:
                            if i <= 25:
                                O[i][j].move = TM(Ms=Mq, Mo='LP1_end')
                            elif i <= 50:
                                O[i][j].move = TM(Ms=Mq, Mo='LP2_end')
                            else:
                                O[i][j].move = TM(Ms=Mq, Mo='LP3_end')
                        else:
                            O[i][j].move = TM(Ms=Mq, Mo=Ms)
                        # wai_wait:晶圆在该加工模块外的等待时间（离开该模块到进入下一模块的时间，大于机械臂移动时间）
                        # 等待机械臂空闲的损失时间loss
                        if j == 1:
                            O[i][j].wai_wait = 0.0
                        # 此处不完善，待解决
                        else:
                            a = O[i][j].move
                            TM_d = judge_TM(Mq, Ms)
                            if TM_d == 'TM1':
                                b = T_new1 - O[i][j - 1].end + O[i][j].move
                            elif TM_d == 'TM2':
                                b = T_new2 - O[i][j - 1].end + O[i][j].move
                            elif TM_d == 'TM3':
                                b = T_new3 - O[i][j - 1].end + O[i][j].move
                            else:
                                b = 0.0
                            # c =O[ wafers_last[Ms][0]][wafers_last[Ms][1]].end-O[i][j - 1].end
                            O[i][j].wai_wait = round(max(a, b), 1)

                        # begin:晶圆在加工模块的到达时间
                        if i == 1 and j == 1:
                            O[i][j].begin = 0.0
                            num_in += 1
                        elif O[i][j - 1].state2 == 0 and j != 1:
                            break
                        else:
                            if j == 1:
                                if (num_in - num_out) >= (len(arr) - 2):  # 集束设备内承载能力有限
                                    break
                                elif O[i - 1][3].state2 == 0:
                                    break
                                else:
                                    a = round(
                                        (O[i - 1][3].begin + O[i - 1][3].xie + TM1(Ms=list(lujing[i - 2])[2],
                                                                                   Mo=list(lujing[i - 1])[
                                                                                       0])), 1)
                                    b = T_new1
                                    O[i][j].begin = max(a, b)
                                num_in += 1
                            elif j == M:
                                if T_new1 >= O[wafers_last[Ms][0]][M].end:
                                    a = T_new1 + 2 * (TM1(Mq, Ms)) + 5.0
                                else:
                                    a = T_new1 + TM1(Mq, Ms) + 5.0 + 0.2
                                b = round((O[i][j - 1].end + O[i][j].wai_wait), 1)
                                O[i][j].begin = round(max(a, b), 1)
                            else:
                                if wafers_last[Ms] == [0, 0, 0]:
                                    O[i][j].begin = round((O[i][j - 1].end + O[i][j].wai_wait), 1)
                                else:
                                    b = round(O[(wafers_last[Ms][0])][j].end + 5, 1)
                                    a = round((O[i][j - 1].end + O[i][j].wai_wait), 1)
                                    if Tp == C or Tp == D or Tp == E:
                                        try:
                                            c = clear_time[Ms]
                                        except KeyError:
                                            c = 0.0
                                    else:
                                        c = 0.0
                                    O[i][j].begin = max(a, b, c)

                        # 卸:晶圆在加工模块内的卸晶圆时间
                        if j == 1:
                            O[i][j].xie = 0.0
                        else:
                            O[i][j].xie = 5.0

                        # 记录机械手空闲时刻
                        TM_d = judge_TM(Mq, Ms)
                        time = O[i][j].begin + O[i][j].xie
                        if TM_d == 'TM1':
                            T_new1 = max(time, T_new1)
                        elif TM_d == 'TM2':
                            T_new2 = max(time, T_new2)
                        elif TM_d == 'TM3':
                            T_new3 = max(time, T_new3)
                        else:
                            print("error:机械手不存在此操作")

                        # process:该工序加工时间
                        O[i][j].process = Tp[j]

                        # end:晶圆在加工模块的离开时间
                        O[i][j].end_c = round(
                            (O[i][j].begin + O[i][j].xie + O[i][j].process), 1)

                        # 晶圆i的第j道工序已完成，记录下来
                        O[i][j].state1 = 1
                        # 记录加工腔已完成加工的最近一次晶圆信息
                        wafers_last[Ms] = [i, j, 1]
                        # 记录机械臂操作
                        if j != 1:
                            if TM_d == 'TM1':
                                TM1_ACS.append(TM_act(begin=O[i][j - 1].end, end=O[i][j].begin,
                                                      function="将晶圆{}从{}搬运至{}".format(i, Mq, Ms)))
                            elif TM_d == 'TM2':
                                TM2_ACS.append(TM_act(begin=O[i][j - 1].end, end=O[i][j].begin,
                                                      function="将晶圆{}从{}搬运至{}".format(i, Mq, Ms)))
                            elif TM_d == 'TM3':
                                TM3_ACS.append(TM_act(begin=O[i][j - 1].end, end=O[i][j].begin,
                                                      function="将晶圆{}从{}搬运至{}".format(i, Mq, Ms)))
                            else:
                                print("error:机械手不存在此操作")

                            if TM_d == 'TM1':
                                TM1_ACS.append(TM_act(begin=O[i][j].begin, end=O[i][j].begin + O[i][j].xie,
                                                      function="卸载晶圆{}至{}".format(i, Ms)))
                            elif TM_d == 'TM2':
                                TM2_ACS.append(TM_act(begin=O[i][j].begin, end=O[i][j].begin + O[i][j].xie,
                                                      function="卸载晶圆{}至{}".format(i, Ms)))
                            elif TM_d == 'TM3':
                                TM3_ACS.append(TM_act(begin=O[i][j].begin, end=O[i][j].begin + O[i][j].xie,
                                                      function="卸载晶圆{}至{}".format(i, Ms)))
                            else:
                                pass
                        break
                # 按照约束规则，规划此任务的阶段2
                if O[i][j].state2 == 1:  # 已规划完成的任务不再作安排，保持不变
                    continue
                else:  # 规划未完成的任务
                    if (O[wafers_last[Ms][0]][wafers_last[Ms][1]].end_c >= count or
                            O[i][j - 1].end_c >= count):  # 此加工腔的前一任务或待加工晶圆的前一道工序还未完成，等待完成再安排此任务
                        break
                    else:
                        # nei_wait:晶圆在该加工模块内的等待时间
                        if j == 1 or j == M:
                            O[i][j].nei_wait = 0.0
                        else:
                            TM_d = judge_TM(Ms, Mo)
                            time_c = O[i][j].begin + O[i][j].xie + O[i][j].process
                            if TM_d == 'TM1':
                                O[i][j].nei_wait = round(T_new1 - time_c if T_new1 >= time_c else 0.0, 1)
                            elif TM_d == 'TM2':
                                O[i][j].nei_wait = round(T_new2 - time_c if T_new2 >= time_c else 0.0, 1)
                            elif TM_d == 'TM3':
                                O[i][j].nei_wait = round(T_new3 - time_c if T_new3 >= time_c else 0.0, 1)
                            else:
                                print("error:机械手不存在此操作")
                        # qu:晶圆在该加工模块内的取晶圆时间
                        if j == M:
                            O[i][j].qu = 0.0
                        else:
                            O[i][j].qu = 5.
                        # end:晶圆在加工模块的离开时间
                        O[i][j].end = round(
                            (O[i][j].end_c + O[i][j].nei_wait + O[i][j].qu), 1)
                        O[i][j].state2 = 1
                        # 记录加工腔已完成加工的最近一次晶圆信息
                        wafers_last[Ms] = [i, j, 2]
                        if j == M:
                            num_out += 1

                        # 如果使用的加工路径是C/D/E，还需要安排PM加工腔的清洗任务
                        if Tp == C or Tp == D or Tp == E:
                            try:
                                complete_num[Ms] += 1
                                # print(Ms, "已加工晶圆数量", complete_num[Ms])
                                if complete_num[Ms] == 15:
                                    clear_time[Ms] = O[i][j].end + 300.0
                                    clear[Ms].append("第{}s开始，{}s结束".format(O[i][j].end, clear_time[Ms]))
                                    complete_num[Ms] = 0
                            except KeyError:
                                pass
                        if j != M:
                            # 记录机械臂操作
                            TM_d = judge_TM(Mq, Ms)
                            if TM_d == 'TM1':
                                TM1_ACS.append(TM_act(begin=O[i][j].end_c + O[i][j].nei_wait,
                                                      end=O[i][j].end_c + O[i][j].nei_wait + O[i][j].qu,
                                                      function="从{}装载晶圆{}".format(Ms, i)))
                            elif TM_d == 'TM2':
                                TM2_ACS.append(TM_act(begin=O[i][j].end_c + O[i][j].nei_wait,
                                                      end=O[i][j].end_c + O[i][j].nei_wait + O[i][j].qu,
                                                      function="从{}装载晶圆{}".format(Ms, i)))
                            elif TM_d == 'TM3':
                                TM3_ACS.append(TM_act(begin=O[i][j].end_c + O[i][j].nei_wait,
                                                      end=O[i][j].end_c + O[i][j].nei_wait + O[i][j].qu,
                                                      function="从{}装载晶圆{}".format(Ms, i)))
                            else:
                                pass
                        break
    return O, lujing, round(count, 1), [TM1_ACS, TM2_ACS, TM3_ACS], clear
