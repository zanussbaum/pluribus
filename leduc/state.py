from copy import copy, deepcopy


class Player:
    def __init__(self):
        self.bets = 0
        self.folded = False

    def __repr__(self):
        return f"B: {self.bets} F: {self.folded}"

    def __eq__(self, other):
        return self.bets == other.bets

    def __gt__(self, other):
        return self.bets > other.bets

class State:
    def __init__(self, num_players, num_rounds):
        self.num_players = num_players
        self.num_rounds = num_rounds
        self.players = [Player() for _ in range(num_players)]
        self.history = [[] for _ in range(num_rounds)]
        self.round = 0
        self.turn = 0
        self.terminal = False

    def __repr__(self):
        return f"{self.history}\nTurn: {self.turn}\nPlayers: {self.players}"

    def __copy__(self):
        new_state = State(self.num_players, self.num_rounds)
        new_state.players = deepcopy(self.players)
        new_state.history = deepcopy(self.history)

        return new_state

    def take(self, action, deep=False):
        if deep is True:
            new_state = copy(self)
        else:
            new_state = self

        new_state.history[self.round].append(action)

        if action == 'F':
            self.players[self.turn].folded = True

        elif 'R' in action:
            bet_amount = int(action[:-1])
            self.players[self.turn].bets += bet_amount

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
