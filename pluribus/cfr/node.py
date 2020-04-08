import numpy as np
from regret_min import RegretMin


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
        strategy = np.maximum(self.regret_sum, 0)
        norm_sum = np.sum(strategy)

        if norm_sum > 0:
            strategy /= norm_sum
        else:
            strategy = np.ones(self.actions)/self.actions

        self.strategy_sum += strategy * weight

        self.strategy = strategy

        return strategy

    def __repr__(self):
        return 'info: {} strategy_sum: {} regret: {} strategy: {}'.format(
            self.info_set, self.strategy_sum, self.regret_sum, self.strategy)

    def __eq__(self, value):
        return self.info_set == value.info_set


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


    def get_strategy(self, actions=None):
        """Calculates the strategy given a player's regrets

        This function is similar to the Node class get_strategy
        function except that we don't add the probabilities of each action
        to the strategy_sum like we do in Node since we are running a 
        Monte Carlo process
        """
        strategy = np.maximum(self.regret_sum, 0)
        if actions is not None:
            # if we are here, we just want to get the conditional probability that we play that prob
            # this is the case where the opponent is traversing
            norm_sum = np.array(sum([prob for i, prob in enumerate(strategy) if actions[i]]))
            if norm_sum > 0:
                strategy = np.divide(strategy, norm_sum, out=np.zeros_like(strategy), where=actions==True)
            else:
                num_valid = sum(actions)
                strategy = np.array([1/num_valid if action else 0 for action in actions])

            return strategy

        norm_sum = np.sum(strategy)

        if norm_sum > 0:
            strategy /= norm_sum
        else:
            strategy = np.ones(self.actions)/self.actions

        self.strategy = strategy
    
        return strategy