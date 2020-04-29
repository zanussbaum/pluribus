from pluribus.game.hand import PokerHand as Hand
from pluribus.game.hand_eval import leduc_eval
from pluribus.game.card import Card


class Node:
    def __init__(self, hand, start_round):
        self.hand = hand
        self.children = []
        self.is_leaf = hand.is_leaf(start_round)
        self.children = []

    def __repr__(self):
        return self.hand.__repr__()

class Subgame:
    def __init__(self, hand, traverser):
        self.root = Node(hand, hand.round)
        self.traverser = traverser
        

    def build_tree(self):
        node = self.root
        start_round = node.hand.round
        stack = [node]
        while stack:
            curr = stack.pop()
            if not curr.is_leaf:
                children = [Node(curr.hand.add(curr.hand.turn, action), start_round) for action in curr.hand.valid_actions()]
                stack.extend(children)


if __name__ == '__main__':
    cards = [Card(12, 1), Card(13, 1), Card(14, 1), Card(12, 2), Card(13, 2), Card(14, 2)]
    hand_json = {'num_players': 2, 
                        'num_actions': 3, 
                        'num_rounds': 2,
                        'num_raises':2, 
                        'hand_eval':leduc_eval,
                        'raise_size':[2, 4],
                        'cards': cards}

    hand = Hand(hand_json)

    subgame = Subgame(hand, 0)

    subgame.build_tree()
            


