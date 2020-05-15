import numpy as np
import multiprocessing as mp
from leduc.cfr.regret_min import RegretMin


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
    def __init__(self, actions):
        self.actions = set(actions)
        self.regret_sum = {action:0 for action in actions}
        self.curr_strategy = {action:0 for action in actions}
        self.strategy_sum = {action:0 for action in actions}

    def strategy(self, actions, weight=1):
        """Calculates the new strategy based on regrets

        Gets the current strategy through regret matching
        Args:
            actions: boolean list of valid actions
            weight: float of probability that you are at that info set
        Returns:
            strategy: a numpy array of the current strategy
        """
        m = max
        s = sum
        strat = {action:m(value, 0) for action, value in self.regret_sum.items()}
        norm_sum = s([strat[key] for key in strat if key in actions])
    
        if norm_sum > 0:
            strat = {key:(strat[key]/norm_sum if key in actions else 0) for key in actions}
        else:
            num_valid = len(actions)
            strat = {key:(1/num_valid if key in actions else 0) for key, value in strat.items()}

        self.strategy_sum = {key: value + strat[key] * weight for key, value in self.strategy_sum.items()}

        return strat

    def avg_strategy(self):
        avg_strategy = {action:0 for action in self.actions}
        norm_sum = sum([value for key, value in self.strategy_sum.items()])

        if norm_sum > 0:
            avg_strategy = dict((key, self.strategy_sum[key]/norm_sum) for key in self.strategy_sum.keys())
        else:
            avg_strategy = dict((key, 1/len(self.actions)) for key in self.strategy_sum.keys())

        self.curr_strategy = avg_strategy
        
        return avg_strategy

    def __repr__(self):
        return 'info: {}\n strategy_sum: {}\n regret: {}\n strategy: {}\n'.format(
            self.info_set, self.strategy_sum, self.regret_sum, self.curr_strategy)


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
    def __init__(self, actions):
        super().__init__(actions)
        self.is_frozen = False
        self.actions = set(actions) | set(("1", "2", "3", "4"))
        self.regret_sum = {action:0 for action in self.actions}
        self.curr_strategy = {action:0 for action in self.actions}
        self.strategy_sum = {action:0 for action in self.actions}

    def strategy(self, actions, weight=1):
        """Calculates the new strategy based on regrets

        Gets the current strategy through regret matching
        Args:
            actions: boolean list of valid actions
            weight: float of probability that you are at that info set
        Returns:
            strategy: a numpy array of the current strategy
        """
        difference = actions - self.actions
        for a in difference:
            self.add_action(a)
        
        m = max
        s = sum
        strat = {action:m(value, 0) for action, value in self.regret_sum.items()}
        norm_sum = s([strat[key] for key in strat if key in actions])
    
        if norm_sum > 0:
            strat = {key:(strat[key]/norm_sum if key in actions else 0) for key in actions}
        else:
            num_valid = len(actions)
            strat = {key:(1/num_valid if key in actions else 0) for key, value in strat.items()}

        return strat

    def avg_strategy(self):
        norm_sum = sum([value for key, value in self.strategy_sum.items()])

        if norm_sum > 0:
            avg_strategy = dict((key, self.strategy_sum[key]/norm_sum) for key in self.strategy_sum.keys() if not key.isdigit())
        else:
            valid_actions = sum([1 for k in self.actions if not k.isdigit()])
            avg_strategy = dict((key, 1/valid_actions) for key in self.strategy_sum.keys() if not key.isdigit())

        self.curr_strategy = avg_strategy
        
        return avg_strategy

    def add_action(self, action):
        self.actions.add(action)
        self.regret_sum[action] = 0
        self.strategy_sum[action] = 0
        self.curr_strategy[action] = 0

    def clear(self):
        self.regret_sum = {action:0 for action in self.actions}
        self.strategy_sum = {action:0 for action in self.actions}