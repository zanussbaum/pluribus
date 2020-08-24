import json
import numpy as np


from leduc.vanilla import learn, expected_utility
from leduc.hand_eval import kuhn_eval
from leduc.card import Card


def test_expected_utility():
    num_players = 2
    node_map = {i: {} for i in range(num_players)}
    action_map = {i: {} for i in range(num_players)}
    cards = [Card(14, 1), Card(13, 1), Card(12, 1)]
    learn(10000, cards, 2, node_map, action_map)

    util = expected_utility(cards, 2, 2, kuhn_eval, node_map, action_map)

    print(util)
    print(json.dumps(action_map, indent=4))
    print(node_map)

    assert util.sum() == 0
    assert np.isclose(np.abs(util[0]), np.abs(util[1])), f"Util was {util}"
    assert np.abs(util).sum() > 0, f"Util was {util}"
    assert abs(util[1] - 1/18) <= .01, f"Util not converging {util}"


def test_expected_utility_three_player():
    num_players = 3 
    node_map = {i: {} for i in range(num_players)}
    action_map = {i: {} for i in range(num_players)}
    cards = [Card(14, 1), Card(13, 1), Card(12, 1), Card(11, 1)]
    learn(10000, cards, 3, node_map, action_map)

    util = expected_utility(cards, 3, 3, kuhn_eval, node_map, action_map)

    print(util)
    print(json.dumps(action_map, indent=4))
    print(node_map)

    assert abs(util.sum()) <= 0.0001, f"Something weird, not a zero sum game"
    assert np.abs(util).sum() > 0, f"Util was {util}"
