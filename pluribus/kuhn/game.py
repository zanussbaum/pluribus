import numpy as np 
from itertools import permutations
from copy import deepcopy

class Hand:
    """Game/hand rules class inspired from https://github.com/tansey/pycfr

    This class makes it easier to calculate the expected utilities for 
    a variable number of players

    Attributes:
        num_players: int number of players
        num_rounds: int number of max betting rounds
        cards: n-d array of ints for card ordering this hand
        players_in: list of bool for which players are still in 
        bets: list of ints for how much each player has bet
        _history: 2d array/list of str for public betting history
        round: int for which round it is
    """
    def __init__(self, num_players, num_rounds, cards):
        """Initializes the class

        Args:
            num_players: int number of players
            num_rounds: int number of max betting rounds
            cards: n-d array of ints for card ordering this hand
        """
        self.players_in = [True] * num_players
        self.bets = [1] * num_players
        self.cards = cards
        self._history = [[] for _ in range(num_rounds)]
        self.round = 0
        self.num_rounds = num_rounds
        self.num_players = num_players

    def __repr__(self):
        return str(self.history)

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        """Ability to deep copy this object
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def bet(self, player, amount=1):
        """Increment the amount a player has bet by 'amount'"

        Args:
            player: int which player has bet
            amount: int how much they have bet
        """
        self.bets[player] += amount

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, a):
        self._history = a

    def add(self, player, action):
        """Adds a new action to the history and returns a new hand

        Args:
            player: int which player is making that action
            action: str of which action they are taking

        Returns:
            new_hand: a modified Hand object
        """
        new_hand = deepcopy(self)
        new_hand.history[new_hand.round].append(action)
        if action == 'F':
            new_hand.players_in[player] = False

        elif action == 'B' or action == 'R' or action == 'C':
            new_hand.bet(player)

        elif action == 'P':
            if new_hand.outstanding_bet():
                new_hand.players_in[player] = False

        new_hand.handle_round()
        return new_hand

    def info_set(self, player):
        """Gets the info set the player is currently in

        Args:
            player: int which player is currently playing 

        Returns:
            info_set: a str of the information set
        """
        card = self.cards[player]
        info_set = str(card) + " || " + str(self.history)

        return info_set

    def is_terminal(self):
        """Checks to see if a hand is in a terminal state

        Returns:
            bool: if the hand is in a terminal state
        """
        if self.players_in.count(True) == 1:
            return True
        
        if self.round < self.num_rounds:
            return False
    
        min_actions = self.players_in.count(True)
        actions_in_round = len(self.history[-1])

        if actions_in_round >= min_actions and self.all_called_or_folded():
            return True
        
        return False

    def all_called_or_folded(self):
        """Checks to see if there are no outstanding bets

        Returns:
            bool: true if everyone has called or folded
        """
        max_bet = max(self.bets)

        for i, still_in in enumerate(self.players_in):
            if still_in and self.bets[i] < max_bet:
                return False
        return True
    
    def outstanding_bet(self):
        """Returns whether there is an outstanding bet or not

        Returns:
            bool: true if not everyone has folded or called
        """
        return not self.all_called_or_folded()

    def handle_round(self):
        """Helper function to determine if the round has ended

        This function checks to see that the minimum number of
        actions has occurred and that there are no outstanding bets.
        If this is true, then the round has ended and is incremented.
        """
        min_actions = self.players_in.count(True)
        actions_in_round = len(self.history[self.round])

        if actions_in_round >= min_actions and self.all_called_or_folded():
            self.round += 1

    def payoff(self):
        """Calculates the payoff of a terminal state

        This function assumes that there can be ties

        Returns:
            list: list of floats of payoffs for each player
        """
        if self.players_in.count(True) == 1:
            winners = [i for i, _ in enumerate(self.players_in) if self.players_in[i]]
        else:
            winners = []
            high_card = -1
            for i, card in enumerate(self.cards[:-1]):
                if self.players_in[i]:
                    if len(winners) == 0 or card > high_card:
                        winners = [i]
                        high_card = card
                    elif card == high_card:
                        winners.append(i)

        pot = sum(self.bets)
        payoff = pot / len(winners)
        payoffs = [-bet for bet in self.bets]

        for w in winners:
            payoffs[w] += payoff

        return payoffs

    def which_player(self):
        current_round = self.history[-1]
        return len(current_round) % self.num_players

    def valid_actions(self):
        # TODO
        return ['P', 'B']
        """
        def get_valid_actions(self, history):
        Gets the valid actions for the current round

        Args:
            history: str of public betting history
        
        current_round = history.rfind('\n')
        outstanding_bet = history[current_round:].find('B')

        if outstanding_bet != -1:
            if history[current_round:].count('R') > self.num_raises:
                return ['P', 'B']
            return ['P', 'B']
        return ['P', 'B']
        """
        raise NotImplementedError('TODO')
        



if __name__ == '__main__':
    h = Hand(2, 1, [1,2,3])
    print(h.history)
    h.add(0, 'P')
    print(h.history)
    print(h.info_set(0))
    h.add(1, 'B')
    print(h.history)
    h.add(0, 'B')
    print(h.history)
    print(h.payoff())