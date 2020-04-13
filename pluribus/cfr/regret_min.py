import numpy as np


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
        self.curr_strategy = np.zeros(num_actions)
        self.strategy_sum = np.zeros(num_actions)
        self.opponent_strategy = opponent_strategy
        self.utilities = utilities

    def strategy(self):
        """Calculates the new strategy based on regrets

        Gets the current strategy through regret matching

        Returns:
            strategy: a numpy array of the current strategy
        """
        self.curr_strategy = np.maximum(self.regret_sum, 0)
        norm_sum = np.sum(self.curr_strategy)

        if norm_sum > 0:
            self.curr_strategy /= norm_sum
        else:
            self.curr_strategy = np.ones(self.actions)/self.actions

        self.strategy_sum += self.curr_strategy

        return self.curr_strategy

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
            strategy = self.strategy()
            action = self.get_action(strategy)
            opponent_action = self.get_action(self.opponent_strategy)
            # compute action utilities
            action_utility = self.utilities[:, opponent_action]
            # accumulate action regrets
            self.regret_sum += action_utility - action_utility[action]

    def avg_strategy(self): 
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