import sys
import numpy as np

from itertools import permutations
from tqdm import tqdm
from leduc.hand_eval import kuhn_eval
from leduc.state import State
from leduc.node import MNode as Node
from leduc.card import Card

STRAT_INTERVAL = 100
PRUNE_THRESH = 200
DISCOUNT = 10
LCFR_INTERVAL = 400
REGRET_MIN = -300000


def learn(iterations, node_map, action_map):
    num_players = len(node_map)
    cards = [Card(14, 1), Card(13, 1), Card(12, 1)]
    for i in tqdm(range(1, iterations + 1), desc="learning"):
        np.random.shuffle(cards)
        for player in range(num_players):
            state = State(cards, num_players, 1, kuhn_eval)
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
            discounted = (i/DISCOUNT)/(i/(DISCOUNT + 1))
            for player in node_map:
                player_nodes = node_map[player]
                for node in player_nodes.values():
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


def expected_utility(cards, num_cards, num_players,
                     eval, node_map, action_map):
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
