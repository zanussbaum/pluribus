import numpy as np
from node import Node
from itertools import permutations

class VanillaCFR:
    """An object to run Vanilla Counterfactual regret on Kuhn poker, or other games

    This currently doesn't support multiplayer Kuhn poker
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
        __custom_payoff: a method to determine different payoffs (only used for multiplayer)
        terminal: a list of strings of the terminal states in the game
        node_map: a dictionary of nodes of each information set
    """
    def __init__(self, num_players, num_actions, **kwargs):
        """Initializes the Vanilla CFR

        Creates the object with specified number of players, actions
        and terminal states. For more than two players, you need
        to specify a new payoff function based on the terminal states

        Args:
            num_players: An integer of players playing
            num_actions: An integer of actions
            terminal: a list of strings of the terminal states in the game
        """
        self.num_players = num_players
        self.num_actions = num_actions
        
        if 'actions' not in kwargs:
            self.actions = [i for i in range(num_actions)]
        else:
            self.actions = kwargs['actions']
        if 'payoff' in kwargs:
            self.__custom_payoff = kwargs['payoff']

        if 'terminal' in kwargs:
            self.terminal = kwargs['terminal']
        self.node_map = {}

    def train(self, cards, iterations):
        """Runs CFR and prints the calculated strategies
        
        Prints the average utility for each player at the
        end of training and also the optimal strategies

        Args:
            cards: array-like of ints denoting each card
            iterations: int for number of iterations to run
        """
        player_utils = np.zeros(self.num_players)
        for _ in range(iterations):
            if _ % 1000 == 0:
                print("Iteration {}/{}".format(_, iterations))
            np.random.shuffle(cards)
            prob = tuple(np.ones(self.num_players))
            player_utils += self.cfr(0, cards, "", prob)

        
        expected_utilities = self.expected_utility(cards)
        for player in range(self.num_players):
            print("expected utility for player {}: {}".format(
                player, expected_utilities[player]))
            player_info_sets = self.node_map[player]
            print('information set:\tstrategy:\t')
            for key in sorted(player_info_sets.keys(), key=lambda x: (len(x), x)):
                node = player_info_sets[key]
                strategy = node.get_avg_strategy()
                print("{}:\t P: {} B: {}".format(key, strategy[0], strategy[1]))


    def __payoff(self, history, cards):
        """Calculates the payoff for 2 player Kuhn poker

        Standard payoff for 2 player Kuhn poker
        based on the cards and history.

        Args:
            history: string of betting round(s)
            cards: array-like of ints of cards

        Returns:
            utilities: array-like of utilities for each player
        """
        winner = np.argmax(cards[:self.num_players])
        if history == "PBP":
            return [-1, 1]
        elif history == "BP":
            return [1, -1]
        if history == "PP":
            utilities = [1 if i == winner else -1 for i in range(self.num_players)]
            return utilities
        if history in ["BB", "PBB"]:
            utilities = [2 if i == winner else -2 for i in range(self.num_players)]
            return utilities

    
    def payoff(self, history, cards):
        """Function that calls the payoff function

        If there is no payoff passed through when the object
        is created, it will default to the 2 player Kuhn poker payoff

        Args:
            history: string of betting round(s)
            cards: array-like of ints of cards

        Returns:
            utilities: array-like of utilities for each player
        """
        try:
            return self.__custom_payoff(self, history, cards)
        except:
            return self.__payoff(history, cards)

    
    def cfr(self, player, cards, history, probability):    
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
        if history in self.terminal:
            utility = self.payoff(history, cards)
            return np.array(utility)

        info_set = str(cards[player]) + '|' + history
        player_nodes = self.node_map.setdefault(player, {})
        node = player_nodes.setdefault(info_set, 
                            Node(info_set, self.num_actions))

        strategy = node.get_strategy(probability[player])
        utilities = np.zeros(self.num_actions)
        next_player = (player + 1) % self.num_players

        node_util = np.zeros(self.num_players)
        for i, action in enumerate(self.actions):
            next_history = history + action
            new_prob = tuple(prob if j != player else prob * strategy[i] for j, prob in enumerate(probability))
            returned_util = self.cfr(next_player, cards, next_history, new_prob)
            utilities[i] = returned_util[player]
            node_util += returned_util * strategy[i]
           

        opp_prob = 1
        for i, prob in enumerate(probability):
            if i != player:
                opp_prob *= prob
            
        for i, action in enumerate(self.actions):
            regret = utilities[i] - node_util[player]
            node.regret_sum[i] += regret * opp_prob

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
        all_combos = [np.array(t) for t in set(permutations(cards))]

        expected_utility = np.zeros(self.num_players)
        for card in all_combos:
            history = ''
            expected_utility += self.traverse_tree(history, 0, card)

        return expected_utility/len(all_combos)

    def traverse_tree(self, history, player, card):
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
        if history in self.terminal:
            utility = self.payoff(history, card)
            return np.array(utility)

        info_set = str(card[player]) + '|' + history
        player_nodes = self.node_map[player]
        node = player_nodes[info_set]

        strategy = node.get_avg_strategy()
        next_player = (player + 1) % self.num_players
        util = np.zeros(self.num_players)
        for i, action in enumerate(self.actions):
            next_history = history + action
            util += self.traverse_tree(next_history, next_player, card) * strategy[i]

        return util