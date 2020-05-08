import numpy as np
from copy import deepcopy, copy

class State:
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
        self.raises = 0
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
        self.actions = json['actions']
        self.json = json

    def __repr__(self):
        return str(self.history)

    def __copy__(self):
        new_instance = State(self.json)
        new_instance.__dict__.update(self.__dict__)
        new_instance._history = deepcopy(self._history)
        new_instance.raises = deepcopy(self.raises)
        new_instance.bets = deepcopy(self.bets)
        new_instance.players_in = deepcopy(self.players_in)

        return new_instance

    def bet(self, player, amount):
        """Increment the amount a player has bet by 'amount'"

        Args:
            player: int which player has bet
            amount: int how much they have bet
        """
        self.bets[player] += amount

    @property
    def history(self):
        return self._history
     
    @property
    def public_state(self):
        if self.round > 0:
            board_cards = self.cards[self.num_players]
            public = "%s || %s" % (board_cards, self.history)

        else:
            public = "%s" % self.history

        return public

    @property
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

    @property
    def info_set(self):
        """Gets the info set the player is currently in

        Args:
            player: int which player is currently playing 

        Returns:
            info_set: a str of the information set
        """
        player = self.turn
        card = self.cards[player]
        if self.round > 0:
            # this will be a problem later on when there are more than one board cards
            board_cards = self.cards[self.num_players]
            info_set = "%s || %s || %s" %(card, board_cards, self.history)

        else:
            info_set = "%s || %s" %(card, self.history)

        return info_set

    @property
    def valid_actions(self): 
        num_raised = self.raises
        if num_raised < self.num_raises:
            valid = self.actions
            return set(valid)
        else:
            valid = [a for a in self.actions if 'R' not in a]
            return set(valid)

    def add(self, player, action, copy=True):
        """Adds a new action to the history and returns a new hand

        Args:
            player: int which player is making that action
            action: str of which action they are taking

        Returns:
            new_hand: a modified Hand object
        """
        if copy:
            new_hand = deepcopy(self)
        else: 
            new_hand = self

        if 'R' in action:
            if len(action) <= 1:
                action = str(self.raise_size[self.round]) + action

        new_hand.history[new_hand.round].append(action)
        if action == 'F':
            new_hand.players_in[player] = False

        elif action == 'B' or 'R' in action or action == 'C':
            if 'R' in action:
                raise_size = int(action[:-1])
                amount = max(self.bets) - self.bets[player] + raise_size

                new_hand.raises += 1

                new_hand.bet(player, amount)
                
                

            elif action == 'B':
                if not new_hand.all_called_or_folded():
                    amount = max(self.bets) - self.bets[player]
                    new_hand.bet(player, amount)
                else:
                    amount = max(self.bets) - self.bets[player] + self.raise_size[self.round]
                    new_hand.bet(player, amount)
                    new_hand.raises += True

            else:
                amount = max(self.bets) - self.bets[player]
                new_hand.bet(player, amount)

        elif action == 'P':
            if not new_hand.all_called_or_folded():
                new_hand.players_in[player] = False

        elif action == '-':
            assert self.players_in[player] == False

        new_hand.handle_round()
        return new_hand

    def is_leaf(self, round):
        min_actions = self.players_in.count(True)
        actions_in_round = len(self.history[round])

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
            self.raises = 0
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

        self.winners = winners
        for w in winners:
            payoffs[w] += payoff

        return payoffs

class LeducState(State):
    pass
