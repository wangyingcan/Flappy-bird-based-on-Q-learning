from flappy import FlappyBird
import numpy as np
from algorithms import q_learning

def main(sim,series_size=20, num_series=25, gamma=0.99, alpha=0.7,
        epsilon=0.0001):
    Q = np.load('saveright.npy')
    Q=q_learning(sim,gamma,alpha,epsilon,1,Q)
    return

main(sim=FlappyBird())

