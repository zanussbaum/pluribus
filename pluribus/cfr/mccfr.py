import numpy as np
from itertools import permutations
from vanilla_cfr import VanillaCFR
from node import InfoSet
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
        self.action_mapping = {'P':0, 'B':1}
        self.reverse_mapping = {0:'P', 1:'B'}

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
                if t % self.strategy_interval == 0:
                    self.update_strategy('', player, cards)
                if t > self.prune_threshold:
                    will_prune = np.random.random()
                    if will_prune < .05:
                        self.mccfr(cards, '', player)
                    else:
                        self.mccfr(cards, '', player, prune=True)
                else:
                    self.mccfr(cards, '', player)

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
                strategy = node.get_avg_strategy()
                print("{}:\t P: {} B: {}".format(key, strategy[0], strategy[1]))


    def mccfr(self, cards, history, player, prune=False):
        """Main function that runs the MonteCarloCFR

        Args:
            cards: array-like of ints denoting each card
            history: str of public betting history
            player: int of which player we are traversing with
            prune: boolean of whether to prune or not

        Returns:
            array_like: float of expected utilities
        """
        curr_player = self.which_player(history)
        if history in self.terminal:
            utility = self.payoff(history, cards)
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
            info_set = str(cards[player]) + '|' + history
            player_nodes = self.node_map.setdefault(player, {})
            node = player_nodes.setdefault(info_set, InfoSet(info_set, self.num_actions, player))

            strategy = node.get_strategy()
            valid_actions = self.get_valid_actions(history)

            expected_value = np.zeros(self.num_players)
            utilities = np.zeros(self.num_actions)
            if prune:
                explored = set()

            for action in valid_actions:
                mapping = self.action_mapping[action]
                if prune:
                    if node.regret_sum[mapping] > self.regret_minimum:
                        next_history = next_history = history + action
                        calculated_util  = self.mccfr(cards, next_history, player, prune=True)
                        utilities[mapping] = calculated_util[player]
                        expected_value += calculated_util * strategy[mapping]
                        explored.add(action)
                else:
                    next_history = history + action
                    calculated_util  = self.mccfr(cards, next_history, player)
                    utilities[mapping] = calculated_util[player]
                    expected_value += calculated_util * strategy[mapping]
            
            for action in valid_actions:
                mapping = self.action_mapping[action]
                if prune:
                    if action in explored:
                        regret = utilities[mapping] - expected_value[player]
                        node.regret_sum[mapping] += regret
                else:
                    regret = utilities[mapping] - expected_value[player]
                    node.regret_sum[mapping] += regret

            return expected_value

        else:
            info_set = str(cards[curr_player]) + '|' + history
            player_nodes = self.node_map.setdefault(curr_player, {})
            node = player_nodes.setdefault(info_set, InfoSet(info_set, self.num_actions, curr_player))

            strategy = node.get_strategy()
            choice = np.random.choice(self.num_actions, p=strategy)
            action = self.reverse_mapping[choice]
            next_history = history + action
            return self.mccfr(cards, next_history, player, prune=prune)


    def update_strategy(self, history, player, cards):
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
        betting_round = history.rfind('\n')
        if history in self.terminal or betting_round != -1:
            return

        elif self.which_player(history) == player:
            info_set = str(cards[player]) + '|' + history
            player_nodes = self.node_map.setdefault(player, {})
            node = player_nodes.setdefault(info_set, InfoSet(info_set, self.num_actions, player))

            strategy = node.get_strategy()
            choice = np.random.choice(self.num_actions, p=strategy)
            node.strategy_sum[choice] += 1
            action = self.reverse_mapping[choice]
            next_history = history + action
            self.update_strategy(next_history, player, cards)

        else:
            valid_actions = self.get_valid_actions(history)
            for action in valid_actions:
                next_history = history + action
                self.update_strategy(next_history, player, cards)

    
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
        actions = self.get_valid_actions(history)
        mappings = [self.action_mapping[key] for key in actions]
        valid_actions = [True if key in mappings else False for key in range(self.num_actions)]
        for i, valid in enumerate(valid_actions):
            if valid:
                action = self.reverse_mapping[i]
                next_history = history + action
                util += self.traverse_tree(next_history, next_player, card) * strategy[i]

        return util


    def get_valid_actions(self, history):
        """Gets the valid actions for the current round

        Args:
            history: str of public betting history
        """
        current_round = history.rfind('\n')
        outstanding_bet = history[current_round:].find('B')

        if outstanding_bet != -1:
            if history[current_round:].count('R') > self.num_raises:
                return ['P', 'B']
            return ['P', 'B']
        return ['P', 'B']


    def which_player(self, history):
        """Which player's turn it is

        Args:
            history: str of public betting history

        Returns:
            int: which player's turn it is
        """
        num_rounds = history.count('\n')
        hist_len = len(history) - num_rounds
        
        return hist_len % self.num_players
        

    def is_not_in(self, history, player):
        #TODO implement this
        actions_per_round = history.split('\n')
        player_actions = set()
        
        for each_round in actions_per_round:
            for action in each_round[player::self.num_players]:
                player_actions.add(action)


        return True if 'F' in player_actions else False

    def is_terminal(self, history):
        end = history.rfind('\n')
        last_round = end if end != -1 else 0

        current_round = history[last_round:]
        num_folded = current_round.count('F')

        if num_folded == self.num_players - 1:
            return True

        num_rounds = history.count('\n')
        
        #if we are in the last round
        if num_rounds == self.num_betting_rounds - 1:
            outstanding_bet = current_round.rfind('R')
            # if there's no outstanding bet
            if outstanding_bet == -1:
                num_checked = current_round.count('P')
                # if everyone has either checked or folded
                if num_checked + num_folded == self.num_players:
                    return True
                return False

            else:
                num_called = current_round.count('C')
                # if everyone has either called or folded
                if num_called + num_folded == self.num_players - 1:
                    return True
                return False
        return False
        

    def is_chance(self, history):
        #TODO implement this
        current_round = history.rfind('\n')
        start = current_round if current_round != -1 else 0
        if history[start:].count('P') == self.num_players:
            return True

        
        outstanding_bet = history[start+1:].rfind('B')
        if outstanding_bet != -1:
            did_call = history[outstanding_bet+1:].count('B')
            # if everyone else folded or called after the bet 
            folded = history[start+1:].count('P')
            if did_call + folded == self.num_players - 1:
                return True
            return False

        return False



            
