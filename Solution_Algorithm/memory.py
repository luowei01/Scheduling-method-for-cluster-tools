'''
分配方案存储模块：
    用pkl文件保存路径优化后的晶圆加工任务分配方案
    调用此方法，传入任务分配方案，即可方便的读取或保存任务分配方案
'''
import pickle
from Solution_Algorithm.data_source import *
class Memory:
    @staticmethod
    def save(data1):
        global output
        data = data1
        selfref_list = [1, 2, 3]
        selfref_list.append(selfref_list)
        if Tp == A:
            output = open('./Result/zuijia_lujing_A({}）.pkl'.format(N), 'wb')
        elif Tp == B:
            output = open('./Result/zuijia_lujing_B({}）.pkl'.format(N), 'wb')
        elif Tp == C:
            output = open('./Result/zuijia_lujing_C({}）.pkl'.format(N), 'wb')
        elif Tp == D:
            output = open('./Result/zuijia_lujing_D({}）.pkl'.format(N), 'wb')
        elif Tp == E:
            output = open('./Result/zuijia_lujing_E({}）.pkl'.format(N), 'wb')
        # Pickle dictionary using protocol 0.
        pickle.dump(data, output)
        # Pickle the list using the highest protocol available.
        pickle.dump(selfref_list, output, -1)
        output.close()

    # 使用pickle模块从文件中重构python对象
    @staticmethod
    def load():
        global pkl_file
        if Tp == A:
            pkl_file = open('./Result/zuijia_lujing_A({}）.pkl'.format(N), 'rb')
        elif Tp == B:
            pkl_file = open('./Result/zuijia_lujing_B({}）.pkl'.format(N), 'rb')
        elif Tp == C:
            pkl_file = open('./Result/zuijia_lujing_C({}）.pkl'.format(N), 'rb')
        elif Tp == D:
            pkl_file = open('./Result/zuijia_lujing_D({}）.pkl'.format(N), 'rb')
        elif Tp == E:
            pkl_file = open('./Result/zuijia_lujing_E({}）.pkl'.format(N), 'rb')
        data = pickle.load(pkl_file)
        # pprint.pprint(data)
        pkl_file.close()
        return data
