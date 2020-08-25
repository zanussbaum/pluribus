import numpy as np

from itertools import permutations


def best_response(state, fixed, node_map, action_map, br_map, prob):
    if state.terminal:
        util = state.utility()
        return util * prob

    current_player = state.turn
    info_set = state.info_set()
    valid_actions = action_map[current_player][info_set]
    if current_player == fixed:
        br = {action: best_response(state.take(action, deep=True), fixed,
              node_map, action_map, br_map, prob) for action in valid_actions}
        br_map[current_player][info_set] = {action: 0
                                            for action in valid_actions}
        best_action, best_value = max(br.items(),
                                      key=lambda x: x[1][current_player])
        br_map[current_player][info_set][best_action] = 1
        return best_value

    else:
        strat = node_map[current_player][info_set].avg_strategy()
        ev = [best_response(state.take(action, deep=True), fixed, node_map,
              action_map, br_map, prob * strat[action])
              for action in valid_actions]
        return np.array(ev).sum(axis=0)


def traverse(state, action_map, node_map, br_map, player):
    if state.terminal:
        util = state.utility()
        return util

    info_set = state.info_set()
    if state.turn == player:
        strategy = br_map[state.turn][info_set]
    else:
        strategy = node_map[state.turn][info_set]

    util = np.zeros(len(node_map))
    valid_actions = action_map[state.turn][info_set]
    for action in valid_actions:
        new_hand = state.take(action, deep=True)
        util += traverse(new_hand, action_map, node_map,
                         br_map, player) * strategy[action]

    return util


def exploitability(cards, num_cards, node_map, action_map):
    if len(cards) > 4:
        from leduc.state import Leduc as State
        from leduc.hand_eval import leduc_eval as eval
    else:
        from leduc.state import State
        from leduc.hand_eval import kuhn_eval as eval

    all_combos = [list(t) for t in set(permutations(cards, num_cards))]

    num_players = len(node_map)
    br_map = {i: {} for i in range(num_players)}
    for combo in all_combos:
        state = State(combo, num_players, eval)
        for player in range(num_players):
            best_response(state, player, node_map, action_map, br_map, 1.)
    converged_strat = {p: {k: v.avg_strategy() for k,
                       v in node_map[p].items()} for p in node_map}

    exploitability = np.zeros(num_players)
    for combo in all_combos:
        state = State(combo, num_players, eval)
        for player in range(num_players):
            exploitability[player] += traverse(state, action_map, converged_strat,
                                               br_map, player)[player]
    print(exploitability)
    return exploitability.sum()/len(all_combos)
