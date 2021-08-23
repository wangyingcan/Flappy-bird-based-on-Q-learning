from flappy import FlappyBird
import numpy as np
import matplotlib.pyplot as plt
from algorithms import q_learning
import time

'''
sim（内含状态集合行为集的环境）  series_size （训练一局50次失败重开一局） 
num_series（一共5局结束出训练结果）  gamma(折扣因子，用于QL)  alpha(学习速率，用于QL)
epsilon（贪婪算法的参数，ε用于策略评估）
'''
def evaluate_learning(
        sim,series_size=50, num_series=30, gamma=0.99, alpha=0.7,
        epsilon=0.0001):

    '''
    :param sim: The queuing object
    :param series_size: the size of series
    :param num_series: the number of series
    :return: a result policy
    '''
    # initialise Q values

    #Q = 0*np.ones((sim.num_states,sim.num_actions))#如果从头开始训练就是初始化值为0的Q-table
    #Q = np.load('saveright.npy')#这是训练好之后的Q-table（矩阵）
    Q=np.load('save.npy')
    print(Q.shape)#在命令行打印Q-table的(行数，列数),状态很多种，行为只有跳/不跳两种
    figrew, axrew = plt.subplots()#初始化最后的结果折线图，调用matplotlib里的函数
    total_reward_seq = [0]#初始化reward
    total_episodes = 0#初始化游戏回合数

    for series in range(num_series):#进行5局的循环
        print("series = %r/%d" % (series,num_series) ) # Print the current stage
        rewardlist=[]
        for episode in range(series_size):#50次失败后才出局
            Q = q_learning(
                sim, gamma=gamma, alpha=alpha, epsilon=epsilon,
                num_episodes=1, Qtable=Q)#获得从算法模块导入的QL，得到返回的Q-table（也可以说是policy）
            rewardlist.append(
                sim.score)#将每次失败的时候得到的得分加到rewardList列表中---一局之后就有50个得分结果
            total_episodes += 1
        Q2=Q#将获得的policy赋值Q2
        total_reward_seq.append(np.mean(np.array(rewardlist)))#将reward列表的所有值求平均值，将平均值放到总reward里

        np.save('save.npy',Q2)#将Q2的结果存到一个保存训练结果策略的.npy文件中
        print(Q)
    total_reward_seq = np.array(total_reward_seq)#变成自己的数组赋值给自己（数据变一种形式）
    axrew.plot(
        np.arange(0, total_episodes+1, series_size),
        total_reward_seq)#更新图的数据
    axrew.set_xlabel("episodes")#设置那个折线图的x,y坐标的含义
    axrew.set_ylabel("average score")
    return

start = time.time()
evaluate_learning(sim=FlappyBird())#调用上面函数，设置环境为由flappy模块导入的FlappyBird函数
end=time.time()
print(end-start)
plt.title('Average score per series')#设置折线图的标题
plt.tight_layout()#自动调节图x,y的参数以保证整个曲线可以显示与图的区域
#plt.savefig("result_5000.png")
plt.savefig("round5.png")
plt.show()#调用展示折线图结果



