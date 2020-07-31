import sys
import numpy as np

from tqdm import tqdm
from hand_eval import kuhn_eval
from state import State
from node import Node
from card import Card

def learn(iterations, node_map, action_map):
    num_players = len(node_map)
    cards = [Card(14, 1), Card(13, 1), Card(12, 1)]
    for i in tqdm(range(iterations), desc="Learning"):
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


if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            num_players = int(sys.argv[1])
        except ValueError:
            raise ValueError("Must pass an int for number of players")
    else:
        num_players = 2

    node_map = {i: {} for i in range(num_players)}
    action_map = {i: {} for i in range(num_players)}
    learn(10000, node_map, action_map) 
