import json
import numpy as np


from leduc.vanilla import learn, expected_utility
from leduc.hand_eval import kuhn_eval
from leduc.card import Card


def test_expected_utility():
    num_players = 2
    node_map = {i: {} for i in range(num_players)}
    action_map = {i: {} for i in range(num_players)}
    learn(10000, node_map, action_map)

    cards = [Card(14, 1), Card(13, 1), Card(12, 1)]
    util = expected_utility(cards, 3, 2, kuhn_eval, node_map, action_map)

    print(util)
    print(json.dumps(action_map, indent=4))
    print(node_map)

    assert util.sum() == 0
    assert np.isclose(np.abs(util[0]), np.abs(util[1])), f"Util was {util}"
    assert np.abs(util).sum() > 0, f"Util was {util}"

