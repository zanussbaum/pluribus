import numpy as np
import importlib
import sys
from itertools import permutations
from tqdm import tqdm
from collections import defaultdict
from pluribus.cfr.node import Node

class VanillaCFR:
    """An object to run Vanilla Counterfactual regret on Kuhn poker, or other games

    The expected value for player one in 2 player poker is ~ -.05
    This version of CFR assumes there are only two actions P for pass and
    B for bet. We assume that these are akin to checking and raising
    with no outstanding bet and folding and calling wtih an outstanding
    bet. Note that for multiplayer games, CFR is not guaranteed to 
    converge to a Nash or epsilon Nash Equilibrium.

    Attributes:
        num_players: An integer of players playing
        num_actions: An integer of actions
        actions: A list of strings of the allowed actions
        node_map: a dictionary of nodes of each information set
    """
    def __init__(self, json, **kwargs):
        """Initializes the Vanilla CFR

        Creates the object with specified number of players, actions
        and terminal states. For more than two players, you need
        to specify a new payoff function based on the terminal states

        Args:
            num_players: An integer of players playing
            num_actions: An integer of actions
            terminal: a list of strings of the terminal states in the game
        """
        self.num_players = json['num_players']
        self.num_actions = json['num_actions']
        self.num_raises = json['num_raises']
        self.num_rounds = json['num_rounds']
        self.num_cards = json['num_cards']
        self.state = json['state']
        if json['game'] == 'kuhn':
            if self.num_actions == 2:
                self.actions = ['P', 'B']
            else:
                self.actions = ['F', 'P', 'C', 'R']
        else:
            if json['game'] == 'leduc':
                self.actions = ['F', 'C', 'R']
                
        self.node_map = {}

        self.json = json
        self.state_json = {'num_players': json['num_players'], 
                        'num_actions': json['num_actions'], 
                        'num_rounds': json['num_rounds'],
                        'num_raises':json['num_raises'], 
                        'hand_eval':json['hand_eval'],
                        'raise_size':json['raise_size'],
                        'actions':self.actions}

    def train(self, cards, iterations):
        """Runs CFR and prints the calculated strategies
        
        Prints the average utility for each player at the
        end of training and also the optimal strategies

        Args:
            cards: array-like of ints denoting each card
            iterations: int for number of iterations to run
        """
        self.state_json['cards'] = cards
        for _ in tqdm(range(1, iterations+1), desc='Training'):
            np.random.shuffle(cards)
            prob = tuple(np.ones(self.num_players))
            hand = self.state(self.state_json)
            self.cfr(hand, prob)

        expected_utilities = self.expected_utility(cards)
        for player in range(self.num_players):
            print("expected utility for player {}: {}".format(
                player, expected_utilities[player]))
            player_info_sets = self.node_map[player]
            print('information set:\tstrategy:\t')
            for key in sorted(player_info_sets.keys(), key=lambda x: (len(x), x)):
                node = player_info_sets[key]
                strategy = node.avg_strategy()
                if self.json['game'] == 'kuhn':
                    if self.num_actions == 2:
                        print("{}:\t P: {} B: {}".format(key, strategy['P'], strategy['B']))
                    else:
                        print("{}:\t F: {} P: {} C: {} R: {}".format(
                            key, strategy['F'], strategy['P'], strategy['C'], strategy['R']))

                else:
                    print("{}:\t F: {} C: {} R: {}".format(key, strategy['F'], strategy['C'], strategy['R']))


    def cfr(self, hand, probability):    
        """Runs the VanillaCFR algorithm

        Calculates the regret for each information set
        based on each action.

        Args:
            player: int for which player is 'up'
            cards: array-like of ints of cards
            history: string of betting round(s)
            probability: tuple of probability for each player for 
                getting that information set

        Returns:
            utility: array-like of floats for the utility
                for the current node 
        """    
        if hand.is_terminal:
            utility = hand.payoff()
            return np.array(utility)

        player = hand.turn
        info_set = hand.info_set
        player_nodes = self.node_map.setdefault(player, {})
        node = player_nodes.setdefault(info_set, Node(self.actions))

        valid_actions = hand.valid_actions
        strategy = node.strategy(valid_actions, probability[player])
        
        utilities = {action:0 for action in valid_actions}

        node_util = np.zeros(self.num_players)
        
        for a in valid_actions:
            new_hand = hand.add(player, a)
            new_prob = tuple(prob if j != player else prob * strategy[a] for j, prob in enumerate(probability))
            returned_util = self.cfr(new_hand, new_prob)
            utilities[a] = returned_util[player]
            node_util += returned_util * strategy[a]
           
        opp_prob = 1
        for i, prob in enumerate(probability):
            if i != player:
                opp_prob *= prob
            
        for a in valid_actions:
            regret = utilities[a] - node_util[player]
            node.regret_sum[a] += regret * opp_prob

        return node_util

    def expected_utility(self, cards):
        """Calculates the expected utility from the average strategy

        Traverses every combination of cards dealt to calculate 
        the expected utility based on the probability of playing
        each action by each player. This only works for 2 player Kuhn
        poker currently

        Args:
            cards: array_like of ints of cards, where each 
                index corresponds to a player

        Returns:
            array_like: floats that correspond to each players expected
                utility
        """
        all_combos = [list(t) for t in set(permutations(cards, self.num_cards))]

        expected_utility = np.zeros(self.num_players)
        for card in tqdm(all_combos, desc='Calculating expected utility'):
            self.state_json['cards'] = card
            hand = self.state(self.state_json)
            expected_utility += self.traverse_tree(hand)

        return expected_utility/len(all_combos)


    def traverse_tree(self, hand):
        """Helper funtion that traverses the tree to calculate expected utility

        Calculates the strategy profile from the average strategy 
        and calculates the expected utility based on the probability of
        taking that action

        Args:
            history: str of betting history
            player: int for which player
            card: array_like of ints for that dealing of private cards

        Returns:
            util: array_like of floats for expected utility for this node
        """
        if hand.is_terminal:
            utility = hand.payoff()
            return np.array(utility)

        player = hand.turn
        info_set = hand.info_set
        player_nodes = self.node_map[player]
        node = player_nodes[info_set]

        strategy = node.avg_strategy()
        util = np.zeros(self.num_players)
        valid_actions = hand.valid_actions
        for a in self.actions:
            if a in valid_actions:
                new_hand = hand.add(player, a)
                util += self.traverse_tree(new_hand) * strategy[a]

        return util