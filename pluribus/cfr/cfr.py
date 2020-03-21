import numpy as np
from pluribus.kuhn.player import Agent as Player

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

class VanillaCFR:
    def __init__(self, num_players, num_actions, terminal, actions=None):
        self.num_players = num_players
        self.num_actions = num_actions
        self.players = [Player(i) for i in range(num_players)]
        if actions is None:
            self.actions = [i for i in range(num_actions)]
        else:
            self.actions = actions

        self.terminal = terminal
        self.node_map = {}

    def train(self, cards, iterations):
        util = 0
        probabilities = np.ones(self.num_players)
        for i in range(iterations):

            util += cfr(0, np.random.choice(cards), "", probabilities)

        print('average game value {}'.format(util/iterations))

    def payoff(self, curr_player):
        winner = max(self.players)

        pot = 0
        for player in self.players:
            if player != winner:
                pot += player.betting
                
        winner.end_game(pot)


        return pot if curr_player == winner.player_number else curr_player.betting * -1

    
    def cfr(self, player, cards, history, probability):
        plays = len(history)
        
        if history in self.terminal:
            utility = self.payoff(player)
            return utility

        info_set = cards[player] + history

        node = self.node_map.setdefault(info_set, 
                            Node(info_set, self.actions))

        strategy = node.get_strategy(probability[player])
        utilities = np.zeros(self.num_actions)
        next_player = (player + 1) % self.num_players

        node_util = 0
        for action in self.actions:
            next_history = history.append(action)
            probability[player] *= strategy[action] 
            utilities[action] = self.cfr(next_player, cards, next_history, probability)
            node_util += strategy[action] * utilities[action]

        for action in self.actions:
            regret = utilities[action] - node_util
            node.regret_sum[action] += regret * probability[player]

        return node_util


if __name__ == '__main__':
    # rps utilities
    # utilities = np.array([[[0, -1, 1], [1, 0, -1], [-1, 1, 0]], [[0, 1, -1], [-1, 0, 1], [1, -1, 0]]])

    # minimization = RegretMin(3, utilities[0], np.array([.4, .3, .3]))
    # minimization.train(10000)
    # print(minimization.get_avg_strategy())


    # kuhn poker 2 player 
    # 2 actions
    HANDS = [(1,2), (1,3), (2,1), (2,3), (3,1), (3,2)]
    ACTIONS = ['P', 'B']
    TERMINAL = ['PP', 'BB', 'PBP', 'PBB', 'BP']

    kuhn_regret = VanillaCFR(2, 2, TERMINAL, ACTIONS)

    kuhn_regret.train(HANDS, 100)

            