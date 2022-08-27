"""
便于数据处理，定义下面这些类
"""
import numpy as np
from Solution_Algorithm.data_source import *


# 一个可行解
class Sol:
    def __init__(self):
        self.nodes_seq = None
        self.obj = None
        self.routes = None


# 存储算法参数
class Model:
    def __init__(self):
        self.best_sol = None
        self.node_list = []
        self.node_seq_no_list = []
        self.depot = None
        self.number_of_nodes = 0
        self.opt_type = 0
        self.vehicle_cap = 80
        self.distance = {}
        self.rand_d_max = 0.4
        self.rand_d_min = 0.1
        self.worst_d_max = 5
        self.worst_d_min = 20
        self.regret_n = 5
        self.r1 = 30
        self.r2 = 18
        self.r3 = 12
        self.rho = 0.6
        self.d_weight = np.ones(2) * 10
        self.d_select = np.zeros(2)
        self.d_score = np.zeros(2)
        self.d_history_select = np.zeros(2)
        self.d_history_score = np.zeros(2)
        self.r_weight = np.ones(3) * 10
        self.r_select = np.zeros(3)
        self.r_score = np.zeros(3)
        self.r_history_select = np.zeros(3)
        self.r_history_score = np.zeros(3)


# 加工过程，表示一道工序的多个阶段
class Work_process:
    # 将每一道工序定义为一个类
    def __init__(self, begin=0.0, process=0.0, nei_wait=0.0, wai_wait=0.0, qu=0.0, xie=0.0, move=0.0, state1=0,
                 state2=0,
                 end_c=0.0, end=0.0):
        # 阶段1
        self.move = move
        # 机械臂移动到下一工序的时间
        self.wai_wait = wai_wait
        # 晶圆从上一道工序进入此道工序的外等待时长,大于或等于机械臂移动时间
        self.begin = begin
        # 工序的初始时间
        self.xie = xie
        # 工序卸晶圆的时间
        self.process = process
        #
        self.end_c = end_c
        # 工序的加工时长
        self.state1 = state1  # 0表示未完成，1表示已完成

        # 阶段2
        self.nei_wait = nei_wait
        # 工序的内等待时长
        self.qu = qu
        # 工序取放晶圆的时间
        self.end = end
        # end:晶圆在加工模块的离开时间
        self.state2 = state2  # 0表示未完成，1表示已完成

        self.long = self.begin - self.end
        # long:晶圆在加工模块内包括取卸晶圆的停留时间


# 机械手的操作类
class TM_act:
    # 将每一道工序定义为一个类
    def __init__(self, begin, end, function):
        self.begin = begin
        self.end = end
        self.function = function


# 晶圆
class Wafer:
    def __init__(self, position, M, id):
        self.position = position
        self.M = M
        self.id = id
        self.state = [0]
        for i in range(1, M + 1):
            self.state.append(-1)  # -1,0,1,-1表示未完成


# 晶圆盒
class LP:
    def __init__(self, position, num_nc, num_c, wafers):
        self.position = position
        self.num_nc = num_nc
        self.num_c = num_c
        self.num = self.num_c + self.num_nc
        self.wafers = wafers

    def self_update(self):
        if self.num_c >= 25:
            self.num_c = 0
            self.num_nc = 25


# 单臂机械手
class SingleTM:
    def __init__(self, isoccupy, nowlocation, Ms, Mo, wafer):
        self.isoccupy = isoccupy
        self.nowlocation = nowlocation
        self.Ms = Ms
        self.Mo = Mo
        self.wafer = wafer

    def qu_wafer(self):
        if self.isoccupy == 0:
            self.wafer.position = 'TM'

    def xie_wafer(self):
        if self.isoccupy == 1:
            self.wafer.position = 'PM'

    def move(self):
        self.nowlocation = 'Mo'


# 双臂机械手
class DoubleTM:
    def __init__(self, is_1occupy, is_2occupy, nowlocation1, nowlocation2, Ms1, Mo1, Ms2, Mo2):
        self.is_1occupy = is_1occupy  # 1有没有被占用
        self.is_2occupy = is_2occupy  # 2有没有被占用
        self.nowlocation1 = nowlocation1  # 目前双臂机械手的位置
        self.nowlocation2 = nowlocation2  # 目前双臂机械手的位置
        self.Ms1 = Ms1  # 取晶圆地点
        self.Mo1 = Mo1  # 放晶圆地点
        self.Ms2 = Ms2  # 取晶圆地点
        self.Mo2 = Mo2  # 放晶圆地点


# 加工腔
class PM:
    def __init__(self, position, state, wafer, j):
        self.position = position
        self.state = state
        self.wafer = wafer
        self.j = j
        self.processtime = Tp[self.j]

    def process_wafer(self, t):
        if t == 0:
            self.wafer.state[self.j] = -1
        elif t < self.processtime:
            self.wafer.state[self.j] = 0
        elif t == self.processtime:
            self.wafer.state[self.j] = 1


# 真空锁
class LL:
    def __init__(self, position, state, wafer1, wafer2, j1, j2):
        self.position = position
        self.state = state  # 1为大气
        self.wafer1 = wafer1
        self.wafer1 = wafer2
        self.j1 = j1
        self.j2 = j2
        self.processtime1 = Tp[self.j1]
        self.processtime2 = Tp[self.j2]


# 缓存腔 LLC，LLD
class RM:
    def __init__(self, position, state, wafer, j):
        self.position = position
        self.state = state
        self.wafer = wafer
        self.j = j
