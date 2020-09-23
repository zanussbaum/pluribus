import sys
import json
import numpy as np

from itertools import permutations
from tqdm import tqdm
from leduc.best_response import exploitability
from leduc.node import MNode as Node
from leduc.card import Card
from leduc.hand_eval import leduc_eval
from leduc.util import expected_utility

STRAT_INTERVAL = 100
PRUNE_THRESH = 200
DISCOUNT = 10
LCFR_INTERVAL = 400
REGRET_MIN = -300000


def learn(iterations, cards, num_cards, node_map, action_map):
    if len(cards) > 4:
        from leduc.state import Leduc as State
        from leduc.hand_eval import leduc_eval as eval
    else:
        from leduc.state import State
        from leduc.hand_eval import kuhn_eval as eval

    all_combos = [list(t) for t in set(permutations(cards, num_cards))]
    num_players = len(node_map)
    for i in tqdm(range(1, iterations + 1), desc="learning"):
        card = np.random.choice(len(all_combos))
        for player in range(num_players):
            state = State(all_combos[card], num_players, eval)
            if i % STRAT_INTERVAL == 0:
                update_strategy(player, state, node_map, action_map)

            if i > PRUNE_THRESH:
                chance = np.random.rand()
                if chance < .05:
                    accumulate_regrets(player, state, node_map, action_map)
                else:
                    accumulate_regrets(player, state, node_map, action_map,
                                       prune=True)
            else:
                accumulate_regrets(player, state, node_map, action_map)

        if i < LCFR_INTERVAL and i % DISCOUNT == 0:
            discounted = (i/DISCOUNT)/(i/(DISCOUNT) + 1)
            for player in node_map:
                player_nodes = node_map[player]
                for key, node in player_nodes.items():
                    node.regret_sum = {key: value * discounted for
                                       key, value in node.regret_sum.items()}
                    node.strategy_sum = {key: value * discounted for
                                         key, value in node.strategy_sum.items()}


def update_strategy(traverser, state, node_map, action_map):
    if state.terminal:
        return

    turn = state.turn
    info_set = state.info_set()

    if info_set not in action_map[turn]:
        action_map[turn][info_set] = state.valid_actions()

    valid_actions = action_map[turn][info_set]

    if info_set not in node_map[turn]:
        node_map[turn][info_set] = Node(valid_actions)

    node = node_map[turn][info_set]
    strategy = node.strategy()

    if turn == traverser:
        actions = list(strategy.keys())
        probs = list(strategy.values())
        random_action = actions[np.random.choice(len(actions), p=probs)]
        node.strategy_sum[random_action] += 1
        new_state = state.take(random_action, deep=True)

        update_strategy(traverser, new_state, node_map, action_map)

    else:
        for action in valid_actions:
            new_state = state.take(action, deep=True)
            update_strategy(traverser, new_state, node_map, action_map)


def accumulate_regrets(traverser, state, node_map, action_map, prune=False):
    if state.terminal:
        util = state.utility()
        return util

    turn = state.turn
    info_set = state.info_set()

    if info_set not in action_map[turn]:
        action_map[turn][info_set] = state.valid_actions()

    valid_actions = action_map[turn][info_set]

    if info_set not in node_map[turn]:
        node_map[turn][info_set] = Node(valid_actions)

    node = node_map[turn][info_set]
    strategy = node.strategy()

    if turn == traverser:
        util = {a: 0 for a in valid_actions}
        node_util = np.zeros(len(node_map))
        explored = set(valid_actions)

        for action in valid_actions:
            if prune is True and node.regret_sum[action] <= REGRET_MIN:
                explored.remove(action)
            else:
                new_state = state.take(action, deep=True)
                returned = accumulate_regrets(traverser, new_state, node_map,
                                              action_map, prune=prune)

                util[action] = returned[turn]
                node_util += returned * strategy[action]

        for action in explored:
            regret = util[action] - node_util[turn]
            node.regret_sum[action] += regret

        return node_util

    else:
        actions = list(strategy.keys())
        probs = list(strategy.values())
        random_action = actions[np.random.choice(len(actions), p=probs)]
        new_state = state.take(random_action, deep=True)
        return accumulate_regrets(traverser, new_state, node_map, action_map,
                                  prune=prune)


if __name__ == '__main__':
    num_players = 2
    node_map = {i: {} for i in range(num_players)}
    action_map = {i: {} for i in range(num_players)}
    cards = [Card(14, 1), Card(13, 1), Card(12, 1), Card(14, 2), Card(13, 2), Card(12, 2)]
    learn(50000, cards, 3, node_map, action_map)
    exploit = exploitability(cards, 3, node_map, action_map)
    print(exploit)

    for player in node_map:
        print(f"Player {player}")
        print('Number of info sets', len(node_map[player]))
        for info_set, node in node_map[player].items():
            avg_strat = node.avg_strategy()
            print(f"{info_set}: {avg_strat}")
        

    util = expected_utility(cards, 3, 2, node_map, action_map)
    print(util)
