import numpy as np
import random
from itertools import permutations
from pluribus.cfr.vanilla_cfr import VanillaCFR
from pluribus.cfr.node import InfoSet
from tqdm import tqdm

class MonteCarloCFR(VanillaCFR):
    """An object to run Monte Carlo Counter Factual Regret 

    Unlike VanillaCFR, Monte Carlo samples the actions of the opponent
    and of chance (called external sampling) by traversing as one player. This way, we don't need to 
    traverse the entire tree like we do in VanillaCFR. We are able to reach similar
    results with MonteCarloCFR in the same number iterations as VanillaCFR, but we touch
    fewer number of nodes than VanillaCFR. In this implementation, we also implement
    pruning for actions that have incredibly negative regret and linear discounting
    for the first part of running so that early actions, which tend to be worse, 
    don't dominate later on in the running of the simulation.


    Attributes:
        num_players: An integer of players playing
        num_actions: An integer of actions
        actions: A list of strings of the allowed actions
        __custom_payoff: a method to determine different payoffs (only used for multiplayer)
        terminal: a list of strings of the terminal states in the game
        node_map: a dictionary of nodes of each information set
        num_betting_rounds: int of number of betting rounds
        num_raises: int of max number of raises per round
        regret_minimum: int for the threshold to prune
        strategy_interval: int when to update the strategy sum
        prune_threshold: int for when to start pruning
        discount_interval: int for at n iterations, when to discount
        lcfr_threshold: int for when to discount
        action_mapping: dict of actions to int
        reverse_mapping: dict of ints to action
    """
    
    def __init__(self, json, **kwargs):
        """initializes the object

        See object attributes for params
        """
        super().__init__(json, **kwargs)
        self.regret_minimum = -300000
        self.strategy_interval = 100
        self.prune_threshold = 200
        self.discount_interval = 10
        self.lcfr_threshold = 400
        
    def train(self, cards, iterations):
        """Runs MonteCarloCFR and prints the calculated strategies
        
        Prints the average utility for each player at the
        end of training and also the optimal strategies

        Args:
            cards: array-like of ints denoting each card
            iterations: int for number of iterations to run
        """
        self.hand_json['cards'] = cards
        for t in tqdm(range(1, iterations+1), desc='Training'):
            np.random.shuffle(cards)
            for player in range(self.num_players):
                hand = self.hand(self.hand_json)
                if t % self.strategy_interval == 0:
                    self.update_strategy(player, hand)
                if t > self.prune_threshold:
                    will_prune = np.random.random()
                    if will_prune < .05:
                        self.mccfr(player, hand)
                    else:
                        self.mccfr(player, hand, prune=True)
                else:
                    self.mccfr(player, hand)

            if t < self.lcfr_threshold and t % self.discount_interval == 0:
                discount = (t/self.discount_interval)/(t/self.discount_interval+ 1)
                for player in range(self.num_players):
                    player_nodes = self.node_map[player]
                    for node in player_nodes.values():
                        node.regret_sum = {key:value * discount for key,value in node.regret_sum.items()}
                        node.strategy_sum = {key:value * discount for key,value in node.strategy_sum.items()}

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


    def mccfr(self, player, hand, prune=False):
        """Main function that runs the MonteCarloCFR

        Args:
            cards: array-like of ints denoting each card
            history: str of public betting history
            player: int of which player we are traversing with
            prune: boolean of whether to prune or not

        Returns:
            array_like: float of expected utilities
        """
        if hand.is_terminal():
            utility = hand.payoff()
            return np.array(utility)

        curr_player = hand.which_player()
        
        if curr_player == player:
            info_set = hand.info_set(player)
            player_nodes = self.node_map.setdefault(player, {})
            node = player_nodes.setdefault(info_set, 
                            InfoSet(info_set, self.actions, player))

            valid_actions = hand.valid_actions()
            strategy = node.strategy(valid_actions)

            expected_value = np.zeros(self.num_players)
            utilities = {action:0 for action in valid_actions}
            if prune:
                explored = set()

            for a in self.actions:
                if a in valid_actions:
                    if prune:
                        if node.regret_sum[a] > self.regret_minimum:
                            new_hand = hand.add(player, a)
                            calculated_util = self.mccfr(player, new_hand, prune=True)
                            utilities[a] = calculated_util[player]
                            expected_value += calculated_util * strategy[a]
                            explored.add(a)
                    else:
                        new_hand = hand.add(player, a)
                        calculated_util = self.mccfr(player, new_hand)
                        utilities[a] = calculated_util[player]
                        expected_value += calculated_util * strategy[a]
            
            for a in self.actions:
                if a in valid_actions:
                    if prune:
                        if a in explored:
                            regret = utilities[a] - expected_value[player]
                            node.regret_sum[a] += regret
                    else:
                        regret = utilities[a] - expected_value[player]
                        node.regret_sum[a] += regret

            return expected_value

        else:
            info_set = hand.info_set(curr_player)
            player_nodes = self.node_map.setdefault(curr_player, {})
            node = player_nodes.setdefault(info_set, 
                            InfoSet(info_set, self.actions, curr_player))

            valid_actions = hand.valid_actions()
            strategy = node.strategy(valid_actions)
            actions = list(strategy.keys())
            prob = list(strategy.values())
            random_action = random.choices(actions, weights=prob)[0]
            new_hand = hand.add(curr_player, random_action)
            return self.mccfr(player, new_hand, prune=prune)


    def update_strategy(self, player, hand):
        """After running for a fixed number of iterations, update the average
        strategies
        
        Since we are running a Monte Carlo process, we can't update
        the strategy sum after iteration. We run for a fixed number of iterations
        (strategy_interval) and then update the strategy so as to be sure that
        the regrets are up to date with the current strategy

        Args:
            history: str of public betting history
            player: int of which player we are updating
        """
        if hand.is_terminal():
            return
        
        curr_player = hand.which_player()
        if curr_player == player:
            info_set = hand.info_set(player)
            player_nodes = self.node_map.setdefault(player, {})
            node = player_nodes.setdefault(info_set, 
                            InfoSet(info_set, self.actions, player))

            valid_actions = hand.valid_actions()
            strategy = node.strategy(valid_actions)

            actions = list(strategy.keys())
            prob = list(strategy.values())
            random_action = random.choices(actions, weights=prob)[0]
            node.strategy_sum[random_action] += 1
            new_hand = hand.add(player, random_action)
            self.update_strategy(player, new_hand)

        else:
            valid_actions = hand.valid_actions()
            for a in self.actions:
                if a in valid_actions:
                    new_hand = hand.add(curr_player, a)
                    self.update_strategy(player, new_hand)

    
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
        for card in tqdm(all_combos):
            self.hand_json['cards'] = card
            hand = self.hand(self.hand_json)
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
        if hand.is_terminal():
            utility = hand.payoff()
            return np.array(utility)
        try:
            player = hand.which_player()
            info_set = hand.info_set(player)
            player_nodes = self.node_map[player]
            node = player_nodes[info_set]

            strategy = node.avg_strategy()
            util = np.zeros(self.num_players)
            valid_actions = hand.valid_actions()
            for a in self.actions:
                if a in valid_actions:
                    new_hand = hand.add(player, a)
                    util += self.traverse_tree(new_hand) * strategy[a]

            return util

        except:
            raise UserWarning("\nUnexplored information set: {}\
                \nYou may need to train for more iterations to reach all possible states".format(info_set))
            