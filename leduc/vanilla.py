import sys
import json
import numpy as np

from itertools import permutations
from tqdm import tqdm
from leduc.hand_eval import kuhn_eval
from leduc.state import State
from leduc.node import Node
from leduc.card import Card


def learn(iterations, node_map, action_map):
    num_players = len(node_map)
    cards = [Card(14 - i, 1) for i in range(num_players + 1)]
    for i in tqdm(range(iterations), desc="learning"):
        np.random.shuffle(cards)
        for player in range(num_players):
            state = State(cards, num_players, 1, kuhn_eval)
            probs = np.ones(num_players)
            accumulate_regrets(state, node_map, action_map, probs)


def accumulate_regrets(state, node_map, action_map, probs):
    if state.terminal:
        util = state.utility()
        return util

    info_set = state.info_set()

    if info_set not in action_map[state.turn]:
        action_map[state.turn][info_set] = state.valid_actions()

    valid_actions = action_map[state.turn][info_set]

    if info_set not in node_map[state.turn]:
        node_map[state.turn][info_set] = Node(valid_actions)

    node = node_map[state.turn][info_set]

    strategy = node.strategy(probs[state.turn])

    util = {a: 0 for a in valid_actions}
    node_util = np.zeros(len(node_map))
    for action in valid_actions:
        new_prob = [p if i != state.turn else p*strategy[action]
                    for i, p in enumerate(probs)]
        new_state = state.take(action, deep=True)
        returned = accumulate_regrets(new_state, node_map,
                                      action_map, new_prob)

        util[action] = returned[state.turn]
        node_util += returned * strategy[action]

    reach_prob = 1
    for p, prob in enumerate(probs):
        if p != state.turn:
            reach_prob *= prob

    for action in valid_actions:
        regret = util[action] - node_util[state.turn]
        node.regret_sum[action] += regret * reach_prob

    return node_util


def expected_utility(cards, num_cards, num_players, eval, node_map, action_map):
    cards = sorted(cards)
    all_combos = [list(t) for t in set(permutations(cards, num_cards))]

    expected_utility = np.zeros(num_players)
    for card in tqdm(all_combos, desc='calculating expected utility'):
        hand = State(card, num_players, 1, eval)
        expected_utility += traverse_tree(hand, node_map, action_map)

    return expected_utility/len(all_combos)


def traverse_tree(hand, node_map, action_map):
    if hand.is_terminal():
        utility = hand.utility()
        return np.array(utility)

    info_set = hand.info_set()
    node = node_map[hand.turn][info_set]

    strategy = node.avg_strategy()
    util = np.zeros(len(node_map))
    valid_actions = action_map[hand.turn][info_set]
    for action in valid_actions:
        new_hand = hand.take(action, deep=True)
        util += traverse_tree(new_hand, node_map, action_map) * strategy[action]

    return util


if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            num_players = int(sys.argv[1])
        except ValueError:
            raise ValueError("must pass an int for number of players")
    else:
        num_players = 2

    node_map = {i: {} for i in range(num_players)}
    action_map = {i: {} for i in range(num_players)}
    learn(10000, node_map, action_map)

    cards = [Card(14, 1), Card(13, 1), Card(12, 1)]
    util = expected_utility(cards, 2, 2, kuhn_eval, node_map, action_map)
    print(util)
    print(node_map)
    print(json.dumps(action_map, indent=4))
