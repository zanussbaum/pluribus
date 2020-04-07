import numpy as np
import random
import argparse
from itertools import permutations


class RegretMin:
    """A class that performs Regret Minimization

    Source code followed from tutorial from http://modelai.gettysburg.edu/2013/cfr/cfr.pdf.
    This is a good beginning to what regret minimization is.

    Attributes:
        num_actions: An integer of actions
        utilities: A Nd array of payoffs/utilies where N is the number of players
        opponent_strategy: A 1xN array where N is the number of actions
        regret_sum: a numpy array of accumulated regrets
        strategy: a numpy array of probability distributions for each strategy
        strategy_sum: a numpy array of counts for each time you play an action
    """
    def __init__(self, num_actions, utilities, opponent_strategy):
        """Initializes the RegretMin class

        Creates the object with specified number of actions,
        utilities, and an opponent strategy.
        Args:
            num_actions: An integer of actions
            utilities: A Nd array of payoffs/utilies where N is the number of players
            opponent_strategy: A 1xN array where N is the number of actions
        """
        self.actions = num_actions
        self.regret_sum = np.zeros(num_actions)
        self.strategy = np.zeros(num_actions)
        self.strategy_sum = np.zeros(num_actions)
        self.opponent_strategy = opponent_strategy
        self.utilities = utilities

    def get_strategy(self):
        """Calculates the new strategy based on regrets

        Gets the current strategy through regret matching

        Returns:
            strategy: a numpy array of the current strategy
        """
        self.strategy = np.maximum(self.regret_sum, 0)
        norm_sum = np.sum(self.strategy)

        if norm_sum > 0:
            self.strategy /= norm_sum
        else:
            self.strategy = np.ones(self.actions)/self.actions

        self.strategy_sum += self.strategy

        return self.strategy

    def get_action(self, strategy):
        """Chooses a random action based on a strategy

        Gets a random action according to the strategy
        distribution

        Args:
            strategy: a numpy array of probability distributions

        Returns:
            action: int for which action to choose
        """
        return np.random.choice(self.actions, p=strategy)


    def train(self, iterations):
        """Trains the regret matching algorithm

        Runs the regret matching algorithm for
        specified number of iterations. The longer
        you train, the better the predictions will be

        Args:
            iterations: int of how many iterations to run
        """
        for _ in range(iterations):
            # get regret-matched mixed strategy
            strategy = self.get_strategy()
            action = self.get_action(strategy)
            opponent_action = self.get_action(self.opponent_strategy)
            # compute action utilities
            action_utility = self.utilities[:, opponent_action]
            # accumulate action regrets
            self.regret_sum += action_utility - action_utility[action]

    def get_avg_strategy(self): 
        """Calculates the average strategy over all training iterations

        Altough the training runs for a number of iterations,
        the average strategy converges to a strategy that
        minimizes regret

        Returns:
            avg_strategy: a 1D array of an optimal strategy to minimize regret
        """
        avg_strategy = np.zeros(self.actions)
        norm_sum = np.sum(self.strategy_sum)

        if norm_sum > 0:
            avg_strategy = self.strategy_sum / norm_sum
        else:
            avg_strategy = np.ones(self.actions)/self.actions

        return avg_strategy


class Node(RegretMin):
    """A Node class that represents an information set

    When running CFR for poker, an information set
    is a state where all public knowledge (such as 
    betting history and public cards) and a player's private card
    is known. For example, player 1 is dealt a 4. Their information 
    set in the first round is '4'. However, if everyone checks except
    the last player, the first player's informaton set would be 
    '4PPB' in a simple Kuhn poker game.


    Attributes:
        info_set: string of which infoset we are in
        action: int of number of actions
        regret_sum: a numpy array of accumulated regrets
        strategy: a numpy array of probability distributions for each strategy
        strategy_sum: a numpy array of counts for each time you play an action
    """
    def __init__(self, info_set, num_actions):
        self.info_set = info_set
        self.actions = num_actions
        self.regret_sum = np.zeros(num_actions)
        self.strategy = np.zeros(num_actions)
        self.strategy_sum = np.zeros(num_actions)

    def get_strategy(self, weight=1):
        """Calculates the new strategy based on regrets

        Gets the current strategy through regret matching
        Args:
            weight: float of 
        Returns:
            strategy: a numpy array of the current strategy
        """
        self.strategy = np.maximum(self.regret_sum, 0)
        norm_sum = np.sum(self.strategy)

        if norm_sum > 0:
            self.strategy /= norm_sum
        else:
            self.strategy = np.ones(self.actions)/self.actions

        self.strategy_sum += self.strategy * weight

        return self.strategy

    def __repr__(self):
        return 'info: {} strategy_sum: {} regret: {}'.format(self.info_set, self.strategy_sum, self.regret_sum)

    def __eq__(self, value):
        return self.info_set == value.info_set

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
        """Main function that calls the payoff function

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

        TODO: Check to see if this works for 3player

        Args:
            cards: array_like of ints of cards, where each 
                index corresponds to a player

        Returns:
            array_like: floats that correspond to each players expected
                utility
        """
        all_combos = set(permutations(cards))

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


class InfoSet(Node):
    """An object that represents an Information Set node


    Attributes:
        info_set: string of which infoset we are in
        action: int of number of actions
        regret_sum: a numpy array of accumulated regrets
        strategy: a numpy array of probability distributions for each strategy
        strategy_sum: a numpy array of counts for each time you play an action
        player: which player this information set belongs to
    """
    def __init__(self, info_set, num_actions, player):
        super().__init__(info_set, num_actions)
        self.player = player


    def get_strategy(self):
        """Calculates the strategy given a player's regrets

        This function is similar to the Node class get_strategy
        function except that we don't add the probabilities of each action
        to the strategy_sum like we do in Node since we are running a 
        Monte Carlo process
        """
        self.strategy = np.maximum(self.regret_sum, 0)
        norm_sum = np.sum(self.strategy)

        if norm_sum > 0:
            self.strategy /= norm_sum
        else:
            self.strategy = np.ones(self.actions)/self.actions
    
        return self.strategy


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
                    self.update_strategy('', player)
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


    def update_strategy(self, history, player):
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

        elif self.is_players_turn(history, player):
            info_set = str(cards[player]) + '|' + history
            player_nodes = self.node_map.setdefault(player, {})
            node = player_nodes.setdefault(info_set, InfoSet(info_set, self.num_actions, player))

            strategy = node.get_strategy()
            choice = np.random.choice(self.num_actions, p=strategy)
            node.strategy_sum[choice] += 1
            action = self.reverse_mapping[choice]
            next_history = history + action
            self.update_strategy(next_history, player)

        else:
            valid_actions = self.get_valid_actions(history)
            for action in valid_actions:
                next_history = history + action
                self.update_strategy(next_history, player)


    def get_valid_actions(self, history):
        """Gets the valid actions for the current round

        Args:
            history: str of public betting history
        """
        current_round = history.rfind('\n')
        outstanding_bet = history[current_round:].find('R')

        if outstanding_bet != -1:
            if history[current_round:].count('R') > self.num_raises:
                return ['P', 'B']
            return ['P', 'B']
        return ['P', 'B']

    
    def is_players_turn(self, history, player):
        """Boolean if it's the player's turn

        Args:
            history: str of public betting history
            player: int which player it is

        Returns:
            boolean: if it's the player's turn
        """
        num_rounds = history.count('\n')
        hist_len = len(history) - num_rounds
        
        return hist_len % self.num_players == player

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
        #TODO implement this
        if self.is_chance(history):
            rounds = history.count('\n') + 1
            # if you're in the last betting round
            if rounds == self.num_betting_rounds:
                start = history.rfind('\n')
                start = start if start != -1 else 0
                folded = history[start+1:].count('-') + history[start:].count('F')
                # if everyone's folded but one player
                if folded == self.num_players - 1:
                    return True
                return False
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


        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Counterfactual Regret Minimization')
    parser.add_argument('-i', '--iterations', type=int, help='number of iterations to run for.')
    parser.add_argument('-c','--cfr', type=int, help='(0) Run regret min or Run CFR for (1): 2 players or (2): 3 players')
    parser.add_argument('-m', '--mccfr', type=int, help='(1) Run MCCFR for two player kuhn poker or (2) 3 players')
    args = parser.parse_args()

    if args.cfr == 0: 
        print("Running regret minimization for RPS with strat [.4, .3, .3]")
        utilities = np.array([[[0, -1, 1], [1, 0, -1], [-1, 1, 0]], [[0, 1, -1], [-1, 0, 1], [1, -1, 0]]])
        minimization = RegretMin(3, utilities[0], np.array([.4, .3, .3]))
        minimization.train(args.iterations)
        print(minimization.get_avg_strategy())
    elif args.cfr == 1:
        # kuhn poker 2 player 
        # 2 actions
        cards = [i for i in range(1, 4)]
        ACTIONS = ['P', 'B']
        TERMINAL = ["PP", "PBP", "PBB", "BP", "BB"]

        kuhn_regret = VanillaCFR(2, 2, terminal=TERMINAL, actions=ACTIONS)

        kuhn_regret.train(cards, args.iterations)
    elif args.cfr == 2:
        cards = np.array([i for i in range(1, 5)])
        ACTIONS = ['P', 'B']
        TERMINAL = ["PPP", "PPBPP", "PPBPB", "PPBBP", "PPBBB", "PBPP",
                "PBPB", "PBBP", "PBBB", "BPP", "BPB", "BBP", "BBB"
            ]

        def payoff(self, history, cards):
            outstanding_bet = history.find('B')

            if outstanding_bet != -1:
                actions_after = history[outstanding_bet:]
                num_folds = actions_after.count('P')
                num_bets = history.count('B')

                utilities = [0 for i in range(self.num_players)]
                pot = self.num_players + num_bets
                
                for i in  range(self.num_players):
                    utilities[i] = -(sum([1 if action == 'B' else 0 for action in history[i::3]]) + 1)

                if num_folds == self.num_players  - 1:
                    utilities[outstanding_bet] += pot
                    return utilities

                left = [(pos+outstanding_bet)%self.num_players for pos, char in enumerate(history[outstanding_bet:]) if char != 'P']
                winner = np.argwhere(cards == max(cards[:self.num_players][left])).item()
                utilities[winner] += pot
                
                return utilities
                
            winner = np.argmax(cards[:self.num_players])

            return [-1 if i != winner else 2 for i in range(self.num_players)]

        three_kuhn = VanillaCFR(3, 2, terminal=TERMINAL, actions=ACTIONS, payoff=payoff)

        three_kuhn.train(cards, args.iterations)

    elif args.mccfr == 1:
        cards = [i for i in range(1, 4)]
        ACTIONS = ['P', 'B']
        TERMINAL = ["PP", "PBP", "PBB", "BP", "BB"]

        mccfr = MonteCarloCFR(2, 2, 1, 1, terminal=TERMINAL, actions=ACTIONS)

        mccfr.train(cards, args.iterations)

    elif args.mccfr == 2:
        raise NotImplementedError('Not yet implemented for 3 player kuhn poker')
        
    else:
        parser.print_help()



            
