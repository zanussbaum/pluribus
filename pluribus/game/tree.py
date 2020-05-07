import random
import numpy as np
from itertools import permutations
from pluribus.cfr.node import InfoSet
from pluribus.game.hand import HoldemHand as Hand
from pluribus.game.hand_eval import leduc_eval
from pluribus.game.card import Card
from copy import deepcopy
from tqdm import tqdm


class Node:
    def __init__(self, hand, start_round):
        self.hand = hand
        self.children = []
        self.is_leaf = hand.is_leaf(start_round)
        self.children = {}
        self._value = {}
        self.renorm_mapping = {'2': 'F', '3':'C', '4':'R'}

    def __repr__(self):
        return self.hand.__repr__() +  " (" + str(self.hand.cards) + ")" 

    def value(self, strategy, action):
        try:
            return self._value[action]
        except:
            self._value[action] = self.rollout(strategy, action)
            return self._value[action]

    def rollout(self, strategy, action):
        num_players = self.hand.num_players
        value_estimate = np.zeros(num_players)
        self.node_map = strategy
        playout = self.playout
        for _ in range(100):
            hand = deepcopy(self.hand)
            value_estimate += playout(hand, action)

        return value_estimate/100

    def playout(self, hand, action):
        while not hand.is_terminal():
            player = hand.turn
            info_set = hand.info_set(player)
            player_nodes = self.node_map[player]
            node = player_nodes.setdefault(info_set,
                                            InfoSet(info_set, hand.actions, hand))

            valid_actions = node.valid_actions()
            strategy = node.curr_strategy
            if action in self.renorm_mapping.keys():
                strategy = self.bias_strategy(strategy, action, valid_actions)

            actions = list(strategy.keys())
            prob = list(strategy.values())
            random_action = random.choices(actions, weights=prob)[0]
            hand = hand.add(player, random_action, copy=False)

        return np.array(hand.payoff())

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
    def __init__(self, hand):
        self.children = []
        self.round = hand.round
        cards = hand.cards
        all_combos = [list(t) for t in permutations(cards, 3)]
        for combo in all_combos:
            copy_hand = deepcopy(hand)
            copy_hand.cards = combo
            self.children.append(Node(copy_hand, copy_hand.round))

    def __repr__(self):
        return str(self.children)


class Subgame:
    def __init__(self, hand, ):
        self.root = Nature(hand)
        
    def build_tree(self, strategy):
        node = self.root
        start_round = node.round
        stack = []
        stack.extend(node.children)
        while stack:
            curr = stack.pop()
            if not curr.is_leaf:
                player = curr.hand.turn
                info_set = curr.hand.info_set(player)
                player_nodes = strategy[player]
                node = player_nodes.setdefault(info_set,
                    InfoSet(info_set, curr.hand.actions, curr.hand))
                hand = curr.hand
                turn = hand.turn
                children = {action:Node(hand.add(turn, action), start_round) for action in node.valid_actions()}
                curr.children = children
                stack.extend(children.values())

        return self.root
