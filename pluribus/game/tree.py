import random
import numpy as np
from itertools import permutations
from pluribus.cfr.node import InfoSet
from pluribus.game.state import LeducState as State
from pluribus.game.hand_eval import leduc_eval
from pluribus.game.card import Card
from copy import copy
from tqdm import tqdm

import pickle
from pluribus.cfr.mccfr import MonteCarloCFR


class Node:
    def __init__(self, state, start_round):
        self.state = state
        self.children = []
        self.is_leaf = state.is_leaf(start_round)
        self.children = {}
        self._value = {}
        self.renorm_mapping = {'2': 'F', '3':'C', '4':'R'}

    def __repr__(self):
        return self.state.__repr__() +  " (" + str(self.state.cards) + ")" 

    def value(self, strategy, action):
        try:
            return self._value[action]
        except:
            self._value[action] = self.rollout(strategy, action)
            return self._value[action]

    def rollout(self, strategy, action):
        num_players = self.state.num_players
        value_estimate = np.zeros(num_players)
        self.node_map = strategy
        playout = self.playout
        s = self.state
        for _ in range(100):
            state = copy(s)
            value_estimate += playout(state, action)

        return value_estimate/100

    def playout(self, state, action):
        if state.is_terminal:
            return np.array(state.payoff())
        
        player = state.turn
        info_set = state.info_set
        node = self.node_map[player][info_set]

        valid_actions = state.valid_actions
        strategy = node.strategy(valid_actions)
        if action in self.renorm_mapping.keys():
            strategy = self.bias_strategy(strategy, action, valid_actions)

        actions = list(strategy.keys())
        prob = list(strategy.values())
        random_action = random.choices(actions, weights=prob)[0]
        new_state = state.add(player, random_action, copy=False)

        return self.playout(new_state, action)

    def bias_strategy(self, strategy, action, valid):
        bias = self.renorm_mapping[action]
        strategy = {action:(strategy[action] if action != bias else strategy[action]*5) 
                    for action in strategy.keys() & valid}
        norm_sum = sum([value for key, value in strategy.items() if key in valid])
        if norm_sum > 0:
            strategy = dict((key, strategy[key]/norm_sum) if key in valid else (key, 0) for key in strategy.keys())
        else:
            num_valid = len(valid)
            strategy = dict((key, 1/num_valid) if key in valid else (key, 0) for key in strategy.keys())

        return strategy

class Nature:
    def __init__(self, state):
        self.children = []
        self.round = state.round
        cards = state.cards
        all_combos = [list(t) for t in permutations(cards, 3)]
        for combo in all_combos:
            copy_state = copy(state)
            copy_state.cards = combo
            self.children.append(Node(copy_state, copy_state.round))

    def __repr__(self):
        return str(self.children)


class Subgame:
    def __init__(self, state):
        self.root = Nature(state)
        
    def build_tree(self, strategy):
        node = self.root
        start_round = node.round
        stack = []
        stack.extend(node.children)
        while stack:
            curr = stack.pop()
            if not curr.is_leaf:
                player = curr.state.turn
                info_set = curr.state.info_set
                node = strategy[player][info_set]
                state = curr.state
                turn = state.turn
                valid_actions = state.valid_actions
                children = {action:Node(state.add(turn, action), start_round) for action in valid_actions}
                curr.children = children
                stack.extend(children.values())

        return self.root

if __name__ == '__main__':
    settings = {'num_players':2, 'num_actions':3, 'hand_eval': leduc_eval,
            'num_rounds':2, 'num_raises':2, 'raise_size':[2,4],
            'num_cards': 3, 'game': 'leduc', 'state': State
        }

    mccfr = MonteCarloCFR(settings)
       
    with open('../blueprint/leduc_strat.p', 'rb') as f:
        blueprint = pickle.load(f)
    mccfr.node_map = blueprint
    mccfr.state_json['cards'] = [Card(12, 1), Card(13, 1), Card(14, 1), Card(12, 2), Card(13, 2), Card(14, 2)]
    state = State(mccfr.state_json)
    subgame = Subgame(state)
    tree = subgame.build_tree(blueprint)
    root = np.random.choice(tree.children)

    while not root.is_leaf:
        root = root.children['C']

    root.value(blueprint, '1')