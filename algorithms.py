import numpy as np

def q_learning(#Q-learning函数
        env, gamma, alpha, epsilon, num_episodes,Qtable, max_steps=np.inf):#最大时无穷大
    #初始化状态集、动作集、policy表
    num_states = env.num_states
    num_actions = env.num_actions
    policy = get_soft_greedy_policy(epsilon, Qtable)
    for _ in range(num_episodes):
        #获得最初的状态
        s = env.reset()
        steps = 0
        done = False
        while not env.is_terminal() and steps < max_steps:#循环结束条件
            # 选择动作
            a = choose_from_policy(policy, s)
            #由这个状态和动作获得reward和下一个状态
            next_s, r = env.next(a)
            # 利用公式更新Q-table的值
            Qtable[s, a] += alpha * (r + gamma * np.max(Qtable[next_s, :]) - Qtable[s, a])
            #更新policy进行如此的循环
            policy[s, :] = get_soft_greedy_policy(
                epsilon, Qtable[s, :].reshape(1,num_actions))
            s = next_s
            steps += 1
    # return the policy
    return Qtable


def choose_from_policy(policy, state):
    num_actions = policy.shape[1]
    result= np.random.choice(num_actions, p=policy[state, :])#这个代表的是在state的状态下的动作集按policy的概率分布选一个动作
    return result


def get_soft_greedy_policy(epsilon, Q):#ε-greedy用于评估采样
    greedy_policy = get_greedy_policy(Q)#根据Q-table获得policy表
    policy = (1 - epsilon) * greedy_policy + epsilon * np.ones(Q.shape) / Q.shape[1]#由公式更新
    return policy


def get_greedy_policy(Q):#greedy贪心算法用于改进策略
    num_states, num_actions = Q.shape
    policy = np.zeros((num_states, num_actions))#代表policy的和Q-table同形状的表，初始化为0
    dominant_actions = np.argmax(Q, axis=1)#获得Q-table里每个state下动作收益最大的那个
    policy[np.arange(num_states), dominant_actions] = 1.#将上面那些最大reward位置的值设置为1
    return policy#将policy表返回
