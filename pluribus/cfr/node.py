import numpy as np
from pluribus.cfr.regret_min import RegretMin


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
        self.curr_strategy = np.zeros(num_actions)
        self.strategy_sum = np.zeros(num_actions)

    def strategy(self, actions, weight=1):
        """Calculates the new strategy based on regrets

        Gets the current strategy through regret matching
        Args:
            actions: boolean list of valid actions
            weight: float of probability that you are at that info set
        Returns:
            strategy: a numpy array of the current strategy
        """
        strat = np.maximum(self.regret_sum, 0)
        norm_sum = np.array(sum([prob for i, prob in enumerate(strat) if actions[i]]))
    
        if norm_sum > 0:
            strat = np.divide(strat, norm_sum, out=np.zeros_like(strat), where=np.array(actions))
        else:
            num_valid = sum(actions)
            strat= np.array([1/num_valid if action else 0 for action in actions])

        self.strategy_sum += strat * weight

        self.curr_strategy = strat

        return strat

    def __repr__(self):
        return 'info: {}\n strategy_sum: {}\n regret: {}\n strategy: {}\n'.format(
            self.info_set, self.strategy_sum, self.regret_sum, self.curr_strategy)

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