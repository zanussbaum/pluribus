import numpy as np

from copy import copy, deepcopy


class Player:
    def __init__(self):
        self.bets = 1
        self.folded = False
        self.raised = False

    def __repr__(self):
        return f"B: {self.bets} F: {self.folded}"

    def __eq__(self, other):
        return self.bets == other.bets

    def __gt__(self, other):
        return self.bets > other.bets

    def __add__(self, other):
        return self.bets + other.bets

    def __radd__(self, other):
        return self.bets + other

class State:
    def __init__(self, cards, num_players, num_rounds, hand_eval):
        self.num_players = num_players
        self.num_rounds = num_rounds
        self.eval = hand_eval
        self.cards = cards
        self.players = [Player() for _ in range(num_players)]
        self.history = [[] for _ in range(num_rounds)]
        self.round = 0
        self.turn = 0
        self.terminal = False
        self.num_raises = 0

    def __repr__(self):
        return f"{self.history}\nTurn: {self.turn}\nPlayers: {self.players}"

    def __copy__(self):
        new_state = State(self.cards, self.num_players, self.num_rounds, self.eval)
        new_state.players = deepcopy(self.players)
        new_state.history = deepcopy(self.history)
        new_state.turn = self.turn
        new_state.num_raises = self.num_raises
        new_state.terminal = self.terminal
        new_state.round = self.round

        return new_state

    def info_set(self):
        hole_card = self.cards[self.turn]

        info_set = f"{hole_card} || {self.history}"
        return info_set

    def take(self, action, deep=False):
        if deep is True:
            new_state = copy(self)
        else:
            new_state = self

        new_state.history[self.round].append(action)

        if action == 'F':
            new_state.players[new_state.turn].folded = True

        elif 'R' in action:
            bet_amount = int(action[:-1])
            new_state.players[new_state.turn].bets += bet_amount
            new_state.players[new_state.turn].raised = True

        else:
            curr_player = new_state.players[new_state.turn]
            any_raised = any([p > curr_player for p in self.players])
            call_size = max(self.players).bets - curr_player.bets
            new_state.players[new_state.turn].bets += call_size

        new_state.terminal = new_state.is_terminal()

        new_state.turn = (new_state.turn + 1) % new_state.num_players

        while new_state.players[new_state.turn].folded:
            new_state.turn += 1

        return new_state

    def is_terminal(self):
        num_folded = sum([p.folded for p in self.players])

        if num_folded == self.num_players - 1:
            return True

        num_actions = len(self.history[self.round])
        min_actions = self.num_players - num_folded

        max_bet = max([p for p in self.players if p.folded is False],
                        key=lambda k: k.bets)

        end_round = True
        for player in self.players:
            if not player.folded:
                if player < max_bet:
                   end_round = False

        if num_actions >= min_actions and end_round:
            if self.round == self.num_rounds - 1:
                return True
            else:
                self.round += 1

        return False

    def utility(self):
        if sum([p.folded for p in self.players]) == 1:
            winners = [i for i, _ in enumerate(self.players) if self.players[i].folded == False]

        else:
            board_cards = self.cards[self.num_players:self.num_players+self.round-1]
            players_in = [i for i, p in enumerate(self.players) if p.folded == False]
            hand_scores = [self.eval(self.cards[i], board_cards) for i in players_in]
            winners = []
            high_score = -1
            for i, score in enumerate(hand_scores):
                if self.players[i].folded == False:
                    if len(winners) == 0 or score > high_score:
                        winners = [i]
                        high_score = score
                    elif score == high_score:
                        winners.append(i)

        pot = sum(self.players)
        payoff = pot / len(winners)
        payoffs = [-p.bets for p in self.players]

        self.winners = winners
        for w in winners:
            payoffs[w] += payoff

        return np.array(payoffs)

    def valid_actions(self):
        any_raises = any([p.raised for p in self.players])
        already_raised = self.players[self.turn].raised
        if any_raises:
            return ['F', 'C']

        return ['F', 'C', '1R']
