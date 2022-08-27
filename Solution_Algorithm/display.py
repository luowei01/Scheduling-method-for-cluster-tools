"""
可视化展示：
    1.求解过程：目标值随迭代次数增加的变化，反映收敛速度
    2.求解结果：总方案的甘特图展示、调度过程展示
    3.最优解的调度过程中各项数据输出为EXCEL形式保存
"""
from Solution_Algorithm.data_source import *
import matplotlib.pyplot as plt
from colour import Color


def plot_gan_result(order, lujing, i1, i2, et):  # 画出晶圆i1到i2的调度安排结果
    # import numpy as np
    # import matplotlib.animation as animation
    M = len(Tp) - 1
    machines = Machines(Tp)
    arr = ['0']
    for i in range(len(machines)):
        for j in range(len(machines[i])):
            arr.append(machines[i][j])
    # plt.ion()#动态显示窗口
    # fig = plt.figure()
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 显示负号
    plt.subplots_adjust(left=0.069, bottom=0.063, right=0.937, top=0.96, wspace=0.99, hspace=0.99)  # 调整边距
    red = Color("red")
    colors = list(red.range_to(Color("purple"), N))
    # clors = [color.rgb for color in colors]
    color = ['r', 'purple', 'r', 'c', 'm', 'y', 'g', 'grey', 'orange']
    scale_ls = [x * 10 for x in range(len(arr))]
    index_ls = arr
    plt.yticks(scale_ls, index_ls)
    plt.ylabel("加工腔室")
    plt.xlabel("加工时间/s                      完工时间：{}s".format(et))
    plt.title("晶圆调度甘特图")
    # plt.axis([0, 1900, 0, 170])  # xmin, xmax, ymin, ymax
    # # 图例绘制
    # patches = [mpatches.Patch(color=clors[i], label="晶圆{}".format(i + 1)) for i in range(N)]
    # legend1 = plt.legend(handles=patches, bbox_to_anchor=(1, 0), loc='lower left', ncol=1,
    #                      frameon=False)  # lower right lower upper center
    # # plt.legend(loc='best', frameon=False)  # 去掉图例边框
    # legend1.get_frame().set_facecolor('red')  # 设置图例legend背景透明,若无边框,参数无效
    # 更新函数
    # def updata(num):
    for i0 in range(i1, i2 + 1, 1):
        for j0 in range(1, M + 1, 1):
            Ms = lujing[i0 - 1][j0 - 1]
            j = arr.index(Ms)
            plt.barh(y=10 * j, height=8, width=order[i0][j0].xie, left=order[i0][j0].begin, edgecolor="none",
                     color='green')
            plt.barh(y=10 * j, height=8, width=order[i0][j0].process, left=order[i0][j0].begin + order[i0][j0].xie,
                     edgecolor="none", color=color[j0 % 9])
            plt.barh(y=10 * j, height=8, width=order[i0][j0].nei_wait,
                     left=order[i0][j0].begin + order[i0][j0].xie + order[i0][j0].process, edgecolor="none",
                     color='yellow')
            plt.barh(y=10 * j, height=8, width=order[i0][j0].qu,
                     left=order[i0][j0].begin + order[i0][j0].xie + order[i0][j0].process
                          + order[i0][j0].nei_wait, edgecolor="none", color='green')
            # plt.text((order[i0][j0].begin + order[i0][j0].end) / 2, j * 10, str(i0) + "," + str(j0), color='Black',
            #          rotation=0,
            #          fontsize=10, ha='center', va='center')
            plt.text((order[i0][j0].begin + order[i0][j0].end) / 2, j * 10, str(i0), color='Black',
                     rotation=0,
                     fontsize=10, ha='center', va='center')
            # plt.pause(1)
    print("图像已在新窗口打开，关闭图形窗口可继续")
    # plt.ioff()
    # ani = animation.FuncAnimation(fig=fig, func=updata, frames=np.arange(0, 100), interval=100)
    # ani.save('调度.gif')
    plt.show()
