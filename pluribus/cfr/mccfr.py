import numpy as np
from itertools import permutations
from pluribus.cfr.vanilla_cfr import VanillaCFR
from pluribus.cfr.node import InfoSet
from pluribus.kuhn.game import Hand
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
    
    def __init__(self, num_players, num_actions, num_betting_rounds, num_raises, **kwargs):
        """initializes the object

        See object attributes for params
        """
        super().__init__(num_players, num_actions, **kwargs)
        self.num_betting_rounds = num_betting_rounds
        self.num_raises = num_raises
        self.regret_minimum = -300000
        self.strategy_interval = 100
        self.prune_threshold = 200
        self.discount_interval = 10
        self.lcfr_threshold = 400
        if self.num_actions == 2:
            self.reverse_mapping = {0:'P', 1:'B'}
        else:
            self.reverse_mapping = {0:'F', 1:'P', 2:'C', 3:'R'}

    def train(self, cards, iterations):
        """Runs MonteCarloCFR and prints the calculated strategies
        
        Prints the average utility for each player at the
        end of training and also the optimal strategies

        Args:
            cards: array-like of ints denoting each card
            iterations: int for number of iterations to run
        """
        for t in range(1, iterations+1):
            if t % 1000 == 0:
                print('Iteration {}/{}'.format(t, iterations))
            np.random.shuffle(cards)
            for player in range(self.num_players):
                hand = Hand(self.num_players, self.num_betting_rounds, cards, self.num_actions)
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
                        node.regret_sum *= discount
                        node.strategy_sum *= discount

        expected_utilities = self.expected_utility(cards)
        for player in range(self.num_players):
            print("expected utility for player {}: {}".format(
                player, expected_utilities[player]))
            player_info_sets = self.node_map[player]
            print('information set:\tstrategy:\t')
            for key in sorted(player_info_sets.keys(), key=lambda x: (len(x), x)):
                node = player_info_sets[key]
                strategy = node.avg_strategy()
                if self.num_actions == 2:
                    print("{}:\t P: {} B: {}".format(key, strategy[0], strategy[1]))
                else:
                    print("{}:\t F: {} P: {} C: {} R: {}".format(
                        key, strategy[0], strategy[1], strategy[2], strategy[3]))


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
        curr_player = hand.which_player()
        if hand.is_terminal():
            utility = hand.payoff()
            return np.array(utility)

        #TODO what do we do here?
        # elif self.is_not_in(history, player):
        #     next_history = history + '-'
        #     return self.mccfr(cards, next_history, player)

        # elif self.is_chance(history):
        #     next_history = history + '\n'
        #     #TODO sample cards to deal, then traverse
        #     return self.mccfr(cards, next_history, player)
        
        elif curr_player == player:
            info_set = hand.info_set(player)
            player_nodes = self.node_map.setdefault(player, {})
            node = player_nodes.setdefault(info_set, 
                            InfoSet(info_set, self.num_actions, player))

            valid_actions = hand.valid_actions()
            actions_to_sum = [True if a in valid_actions else False for a in self.actions]
            strategy = node.strategy(actions_to_sum)

            expected_value = np.zeros(self.num_players)
            utilities = np.zeros(self.num_actions)
            if prune:
                explored = set()

            for action, i in self.actions_mapping.items():
                if action in valid_actions:
                    if prune:
                        if node.regret_sum[i] > self.regret_minimum:
                            new_hand = hand.add(player, action)
                            calculated_util  = self.mccfr(player, new_hand, prune=True)
                            utilities[i] = calculated_util[player]
                            expected_value += calculated_util * strategy[i]
                            explored.add(action)
                    else:
                        new_hand = hand.add(player, action)
                        calculated_util  = self.mccfr(player, new_hand)
                        utilities[i] = calculated_util[player]
                        expected_value += calculated_util * strategy[i]
            
            for action, i in self.actions_mapping.items():
                if action in valid_actions:
                    if prune:
                        if action in explored:
                            regret = utilities[i] - expected_value[player]
                            node.regret_sum[i] += regret
                    else:
                        regret = utilities[i] - expected_value[player]
                        node.regret_sum[i] += regret

            return expected_value

        else:
            info_set = hand.info_set(curr_player)
            player_nodes = self.node_map.setdefault(curr_player, {})
            node = player_nodes.setdefault(info_set, 
                            InfoSet(info_set, self.num_actions, curr_player))

            valid_actions = hand.valid_actions()
            actions_to_sum = [True if a in valid_actions else False for a in self.actions]
            strategy = node.strategy(actions_to_sum)
            choice = np.random.choice(self.num_actions, p=strategy)
            action = self.reverse_mapping[choice]
            new_hand = hand.add(curr_player, action)
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

        #TODO add if hand is after first round
        curr_player = hand.which_player()
        if hand.is_terminal():
            return

        elif curr_player == player:
            info_set = hand.info_set(player)
            player_nodes = self.node_map.setdefault(player, {})
            node = player_nodes.setdefault(info_set, 
                            InfoSet(info_set, self.num_actions, player))

            valid_actions = hand.valid_actions()
            actions_to_sum = [True if a in valid_actions else False for a in self.actions]
            strategy = node.strategy(actions_to_sum)

            choice = np.random.choice(self.num_actions, p=strategy)
            node.strategy_sum[choice] += 1
            action = self.reverse_mapping[choice]
            new_hand = hand.add(player, action)
            self.update_strategy(player, new_hand)

        else:
            valid_actions = hand.valid_actions()
            for action, i in self.actions_mapping.items():
                if action in valid_actions:
                    new_hand = hand.add(curr_player, action)
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
        all_combos = [np.array(t) for t in set(permutations(cards))]

        expected_utility = np.zeros(self.num_players)
        for card in all_combos:
            hand = Hand(self.num_players, 1, card, self.num_actions)
            expected_utility += self.traverse_tree(0, hand)

        return expected_utility/len(all_combos)


    def traverse_tree(self, player, hand):
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

        info_set = hand.info_set(player)
        player_nodes = self.node_map.setdefault(player, {})
        node = player_nodes.setdefault(info_set, 
                            InfoSet(info_set, self.num_actions, player))

        strategy = node.avg_strategy()
        next_player = (player + 1) % self.num_players
        util = np.zeros(self.num_players)
        valid_actions = hand.valid_actions()
        for action, i in self.actions_mapping.items():
            if action in valid_actions:
                new_hand = hand.add(player, action)
                util += self.traverse_tree(next_player, new_hand) * strategy[i]

        return util



            
