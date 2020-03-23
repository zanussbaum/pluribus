import numpy as np
import random

class RegretMin:
    def __init__(self, num_actions, utilities, opponent_strategy):
        self.actions = num_actions
        self.regret_sum = np.zeros(num_actions)
        self.strategy = np.zeros(num_actions)
        self.strategy_sum = np.zeros(num_actions)
        self.opponent_strategy = opponent_strategy
        self.utilities = utilities

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


class Node(RegretMin):
    def __init__(self, info_set, num_actions):
        self.info_set = info_set
        self.actions = num_actions
        self.regret_sum = np.zeros(num_actions)
        self.strategy = np.zeros(num_actions)
        self.strategy_sum = np.zeros(num_actions)

    def get_strategy(self, weight):
        self.strategy = np.maximum(self.regret_sum, 0)
        self.norm_sum = np.sum(self.strategy)

        if self.norm_sum > 0:
            self.strategy /= self.norm_sum
        else:
            self.strategy = np.ones(self.actions)/self.actions

        self.strategy_sum += self.strategy * weight

        return self.strategy

    def __repr__(self):
        return 'info: {} strategy: {} regret: {}'.format(self.info_set, self.strategy, self.regret_sum)

class VanillaCFR:
    def __init__(self, num_players, num_actions, terminal, actions=None):
        self.num_players = num_players
        self.num_actions = num_actions
        if actions is None:
            self.actions = [i for i in range(num_actions)]
        else:
            self.actions = actions

        self.terminal = terminal
        self.node_map = {}

    def train(self, cards, iterations):
        util = 0
        for i in range(iterations):
            np.random.shuffle(cards)
            util += self.cfr(0, cards, "", 1, 1)

        print('average game value {}'.format(util/iterations))
        
        for key in sorted(self.node_map.keys(), key=lambda x: (len(x), x)):
            node = self.node_map[key]
            strategy = node.get_avg_strategy()
            print("{}: P: {} B: {}".format(key, strategy[0], strategy[1]))
        
    def payoff(self, curr_player, history, cards):
        winner = np.argmax(cards[:self.num_players])
        if history == "PBP":
            return -1 if curr_player == 0 else 1
        elif history == "BP":
            return 1 if curr_player == 0 else -1
        m = 1 if winner == curr_player else -1
        if history == "PP":
            return m
        if history in ["BB", "PBB"]:
            return m*2

    
    def cfr(self, player, cards, history, pi1, pi2):
        plays = len(history)
        
        if history in self.terminal:
            utility = self.payoff(player, history, cards)
            return utility

        info_set = str(cards[player]) + history

        node = self.node_map.setdefault(info_set, 
                            Node(info_set, self.num_actions))

        prob = pi1 if player == 0 else pi2
        strategy = node.get_strategy(prob)
        utilities = np.zeros(self.num_actions)
        next_player = (player + 1) % self.num_players

        node_util = 0
        for i, action in enumerate(self.actions):
            next_history = history + action
            utilities[i] = -1 * self.cfr(next_player, cards, next_history, pi1 * strategy[i], pi2) if player == 0 else \
                -1 * self.cfr(next_player, cards, next_history, pi1, pi2 * strategy[i])
            node_util += strategy[i] * utilities[i]

        next_prob = pi1 if next_player == 0 else pi2
        for i, action in enumerate(self.actions):
            regret = utilities[i] - node_util
            node.regret_sum[i] += regret * next_prob


        return node_util


if __name__ == '__main__':
    # rps utilities
    # utilities = np.array([[[0, -1, 1], [1, 0, -1], [-1, 1, 0]], [[0, 1, -1], [-1, 0, 1], [1, -1, 0]]])

    # minimization = RegretMin(3, utilities[0], np.array([.4, .3, .3]))
    # minimization.train(10000)
    # print(minimization.get_avg_strategy())


    # kuhn poker 2 player 
    # 2 actions
    cards = [i for i in range(3)]
    ACTIONS = ['P', 'B']
    TERMINAL = ["PP", "PBP", "PBB", "BP", "BB"]

    kuhn_regret = VanillaCFR(2, 2, TERMINAL, ACTIONS)

    kuhn_regret.train(cards, 100000)

            