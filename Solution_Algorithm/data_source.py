"""
此模块用于保存题目中的数据，根据这些数据构造一些方法，方便调用
另外，当工艺路、设备模块数量、加工时间等数据改变时，可以在此添加或修改数据、调用方法，保证了调度模型的通用性
也可考虑读取txt文件的方法，这里为了方便，在编写程序时直接写入列表中
"""
#
N = 25
# 集束设备A各路径下各腔室加工时间，LP-AL-LLA/LLB-PM-LLA/LLB-LP
A = [0.0, 0.0, 10.0, 15.0, 75.0, 60.0, 70.0, 0.0]
A_machines = [['LP_start'], ['AL'], ['AS2', 'BS2'], ['PM3', 'PM4'], ['PM1', 'PM2', 'PM5', 'PM6'], ['AS1', 'BS1'],
              ['LP_end']]
B = [0.0, 0.0, 10.0, 15.0, 35.0, 30.0, 45.0, 0.0]
B_machines = [['LP_start'], ['AL'], ['AS2', 'BS2'], ['PM3', 'PM4'], ['PM1', 'PM2', 'PM5', 'PM6'], ['AS1', 'BS1'],
              ['LP_end']]
# 集束设备B各路径下各腔室加工时间，LP-AL-LLA/LLB-PM-LLA/LLB-LP
C = [0.0, 0.0, 10.0, 15.0, 70.0, 0.0, 70.0, 100.0, 40.0, 55.0, 20.0, 0.0]
C_machines = [['LP_start'], ['AL'], ['AS2', 'BS2'], ['PM7', 'PM8'], ['LLC'], ['PM2'], ['PM4', 'PM5'], ['LLD'], ['PM10'],
              ['AS1', 'BS1'], ['LP_end']]
D = [0.0, 0.0, 10.0, 15.0, 85.0, 70.0, 0.0, 90.0, 80.0, 45.0, 20.0, 0.0]
D_machines = [['LP_start'], ['AL'], ['AS2', 'BS2'], ['PM7', 'PM8'], ['PM9', 'PM10'], ['LLC'], ['PM3'], ['PM1'], ['LLD'],
              ['AS1', 'BS1'], ['LP_end']]
E = [0.0, 0.0, 10.0, 15.0, 85.0, 0.0, 75.0, 70.0, 85.0, 45.0, 20.0, 0.0]
E_machines = [['LP_start'], ['AL'], ['AS2', 'BS2'], ['PM7', 'PM8'], ['LLC'], ['PM1'], ['PM3'], ['PM6'], ['LLD'],
              ['AS1', 'BS1'], ['LP_end']]


def Tp_strname():
    if Tp == A:
        return 'A'
    elif Tp == B:
        return 'B'
    elif Tp == C:
        return 'C'
    elif Tp == D:
        return 'D'
    elif Tp == E:
        return 'E'


def judge_input():
    m = input("请选择晶圆加工的工艺路径:[A/B/C/D/E]")
    if m == 'A':
        return A
    elif m == 'B':
        return B
    elif m == 'C':
        return C
    elif m == 'D':
        return D
    elif m == 'E':
        return E
    else:
        print("输入错误，请注意大小写")
        return judge_input()


# Tp = judge_input()  # 选择工艺路径
Tp = A
M = len(Tp) - 1
# TM1机械手在LP1，LP2,LP3,AL,LLA,LLB的移动时间
TM1_DATA = [
    [0.0, 1.0, 2.0, 3.0, 3.0, 4.0],
    [1.0, 0.0, 1.0, 2.5, 3.5, 3.5],
    [2.0, 1.0, 0.0, 2.0, 4.0, 3.0],
    [3.0, 2.5, 2.0, 0.0, 2.5, 2.0],
    [3.0, 3.5, 4.0, 2.5, 0.0, 1.0],
    [4.0, 3.5, 3.0, 2.0, 1.0, 0.0]
]


# TM1在两个模块的移动时间
def TM1(Ms, Mo):
    dingyi = {"LP_start": 1, "LP_end": 1, "LP1_start": 0, "LP1_end": 0, "LP2_start": 1, "LP2_end": 1, "LP3_start": 2,
              "LP3_end": 2, "AL": 3, "AS2": 4, "BS2": 5, "AS1": 4, "BS1": 5}
    return TM1_DATA[dingyi[str(Ms)]][dingyi[str(Mo)]]


# TM2在两个模块的移动时间
def TM2(Ms, Mo):
    if Tp == A or Tp == B:
        dingyi = {"BS1": 7, "AS1": 8, "BS2": 7, "AS2": 8, "PM1": 1, "PM2": 2, "PM3": 3, "PM4": 4, "PM5": 5, "PM6": 6}
    else:
        dingyi = {"BS1": 7, "AS1": 8, "BS2": 7, "AS2": 8, "PM9": 1, "PM7": 2, "LLC": 3, "LLD": 4, "PM8": 5, "PM10": 6}
    a = abs(dingyi[str(Ms)] - dingyi[str(Mo)])
    return 0.4 * (a if (a <= 4) else (8 - a))


# TM3在两个模块的移动时间
def TM3(Ms, Mo):
    if Tp == A or Tp == B:
        return 'not exist'
    else:
        dingyi = {"LLD": 7, "LLC": 8, "PM1": 1, "PM2": 2, "PM3": 3, "PM4": 4, "PM5": 5, "PM6": 6}
        a = abs(dingyi[str(Ms)] - dingyi[str(Mo)])
        return 0.4 * (a if (a <= 4) else (8 - a))


# 晶圆从Ms到Mo的机械臂移动时间
def TM(Ms, Mo):
    try:
        return TM1(Ms, Mo)
    except KeyError:
        try:
            return TM2(Ms, Mo)
        except KeyError:
            try:
                return TM3(Ms, Mo)
            except KeyError:
                return 'not exist'


# 判断晶圆从Ms到Mo的使用的机械臂
def judge_TM(Ms, Mo):
    try:
        TM1(Ms, Mo)
        return 'TM1'
    except KeyError:
        try:
            TM2(Ms, Mo)
            return 'TM2'
        except KeyError:
            try:
                TM3(Ms, Mo)
                return 'TM3'
            except KeyError:
                return 'not exist'


# 返回所选工艺路径用到的加工腔
def Machines(Tp):
    if Tp == A:
        return A_machines
    elif Tp == B:
        return B_machines
    elif Tp == C:
        return C_machines
    elif Tp == D:
        return D_machines
    elif Tp == E:
        return E_machines
    else:
        return None


def position(TM, Ms):
    TM1_position = {"LP_start": 1, "LP_end": 1, "LP1_start": 0, "LP1_end": 0, "LP2_start": 1, "LP2_end": 1,
                    "LP3_start": 2, "LP3_end": 2, "AL": 3, "AS2": 4, "BS2": 5, "AS1": 4,
                    "BS1": 5}
    if Tp == A or Tp == B:
        TM2_position = {"BS1": 7, "AS1": 8, "BS2": 7, "AS2": 8, "PM1": 1, "PM2": 2, "PM3": 3, "PM4": 4, "PM5": 5,
                        "PM6": 6}
        TM3_position = "not exist"
    else:
        TM2_position = {"BS1": 7, "AS1": 8, "BS2": 7, "AS2": 8, "PM9": 1, "PM7": 2, "LLC": 3, "LLD": 4, "PM8": 5,
                        "PM10": 6}
        TM3_position = {"LLD": 7, "LLC": 8, "PM1": 1, "PM2": 2, "PM3": 3, "PM4": 4, "PM5": 5, "PM6": 6}
    if TM == 'TM1':
        return TM1_position[Ms]
    elif TM == 'TM2':
        return TM2_position[Ms]
    elif TM == 'TM3':
        return TM3_position[Ms]
    else:
        return 'not exist'


process_time_eq = [Tp[i + 1] / len(Machines(Tp)[i]) for i in range(len(Machines(Tp)))]  # 等效加工时间
