import numpy as np
import random
import argparse

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
        return 'info: {} strategy: {} regret: {}'.format(self.info_set, self.strategy, self.regret_sum)

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
        
        Prints the average utility for player 1 at the
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

        print('expected utility per player {}'.format(player_utils/iterations))
        print('information set:\tstrategy:\t')
        for key in sorted(self.node_map.keys(), key=lambda x: (len(x), x)):
            node = self.node_map[key]
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

        info_set = str(cards[player]) + history

        node = self.node_map.setdefault(info_set, 
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


        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Counterfactual Regret Minimization')
    parser.add_argument('-i', '--iterations', type=int, help='number of iterations to run for.')
    parser.add_argument('-c','--cfr', type=int, help='(0) Run regret min or Run CFR for (1): 2 players or (2): 3 players')

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
        
    else:
        parser.print_help()



            
