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
    def __init__(self, json):
        """Initializes the class

        Args:
            num_players: int number of players
            num_rounds: int number of max betting rounds
            cards: n-d array of ints for card ordering this hand
        """
        self.players_in = [True] * json['num_players']
        self.bets = [1] * json['num_players']
        self.raises = [False] * json['num_players']
        self.cards = json['cards']
        self._history = [[] for _ in range(json['num_rounds'])]
        self.round = 0
        self.turn = 0
        self.num_rounds = json['num_rounds']
        self.num_players = json['num_players']
        self.num_actions = json['num_actions']
        self.num_raises = json['num_raises']
        self.eval = json['hand_eval']
        self.raise_size = json['raise_size']

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

    def bet(self, player):
        """Increment the amount a player has bet by 'amount'"

        Args:
            player: int which player has bet
            amount: int how much they have bet
        """
        self.bets[player] += self.raise_size[self.round]

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
            if action == 'R' or action == 'B':
                new_hand.raises[player] = True

        elif action == 'P':
            if new_hand.outstanding_bet():
                new_hand.players_in[player] = False

        elif action == '-':
            assert self.players_in[player] == False

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
        if self.round > 0:
            board_cards = self.cards[self.num_players]
            info_set = str(card) + " || " + str(board_cards) + ' || ' + str(self.history)

        else:
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

    def is_chance(self):
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
            if self.round == self.num_rounds:
                # we are at a terminal state
                return
            player = 0
        else:
            player = (self.turn + 1) % self.num_players

        while not self.players_in[player]:
            player = (player + 1) % self.num_players

        self.turn = player

    def payoff(self):
        """Calculates the payoff of a terminal state

        This function assumes that there can be ties

        Returns:
            list: list of floats of payoffs for each player
        """
        if self.players_in.count(True) == 1:
            winners = [i for i, _ in enumerate(self.players_in) if self.players_in[i]]
        else:
            board_cards = self.cards[self.num_players:self.num_players+self.round-1]
            hand_scores = [self.eval(self.cards[i], board_cards) for i in range(self.num_players)]
            winners = []
            high_score = -1
            for i, score in enumerate(hand_scores):
                if self.players_in[i]:
                    if len(winners) == 0 or score > high_score:
                        winners = [i]
                        high_score = score
                    elif score == high_score:
                        winners.append(i)

        pot = sum(self.bets)
        payoff = pot / len(winners)
        payoffs = [-bet for bet in self.bets]

        for w in winners:
            payoffs[w] += payoff

        return payoffs

    def which_player(self):
        return self.turn

    def valid_actions(self):
        if self.num_actions == 2:
            return set(['P', 'B'])

        if self.outstanding_bet():
            num_raised = self.raises.count(True)
            if num_raised < self.num_raises:
                return set(['F', 'C', 'R'])
            else:
                return set(['F', 'C'])
        return set(['P', 'R'])
