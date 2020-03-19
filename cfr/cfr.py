import numpy as np


class RegretMin:
    def __init__(self, num_actions, utilities, opponent_strategy):
        self.actions = num_actions
        self.regret_sum = np.zeros(num_actions)
        self.strategy = np.zeros(num_actions)
        self.strategy_sum = np.zeros(num_actions)
        self.opponent_strategy = opponent_strategy
        self.utilities = utilities
        self.norm_sum = 0

    def get_strategy(self):
        self.strategy = np.maximum(self.regret_sum, 0)
        self.norm_sum = np.sum(self.strategy)

        if self.norm_sum > 0:
            self.strategy /= self.norm_sum
        else:
            self.strategy = np.ones(self.actions)/self.actions

        self.strategy_sum += self.strategy

        return self.strategy

    def get_action(self, strategy):
        return np.random.choice(self.actions, p=strategy)


    def train(self, iterations):
        for i in range(iterations):
            # get regret-matched mixed strategy
            strategy = self.get_strategy()
            action = self.get_action(strategy)
            opponent_action = self.get_action(self.opponent_strategy)
            # compute action utilities
            action_utility = self.utilities[:, opponent_action]
            # accumulate action regrets
            self.regret_sum += action_utility - action_utility[action]

    def get_avg_strategy(self): 
        avg_strategy = np.zeros(self.actions)
        norm_sum = np.sum(self.strategy_sum)

        if norm_sum > 0:
            avg_strategy = self.strategy_sum / norm_sum
        else:
            avg_strategy = np.ones(self.actions)/self.actions

        return avg_strategy


if __name__ == '__main__':
    #rps utilities
    utilities = np.array([[[0, -1, 1], [1, 0, -1], [-1, 1, 0]], [[0, 1, -1], [-1, 0, 1], [1, -1, 0]]])

    minimization = RegretMin(3, utilities[0], np.array([.4, .3, .3]))
    minimization.train(100000)
    print(minimization.get_avg_strategy())
            