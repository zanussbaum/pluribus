import numpy as np
from player import Player

 
class Kuhn:
    def __init__(self, betting_rounds, num_cards, verbose=False,**args):
        self.pot = 0
        self.num_players = 3
        self.players = [Player(i) for i in range(self.num_players)]
        self.verbose = verbose
        self.betting_rounds = betting_rounds
        self.num_cards = num_cards
        self.mapping = {'fold': [1, -1, -1, -1], 
                        'check': [-1, 1, -1, -1], 
                        'call': [-1, -1, 1, -1], 
                        'raise': [-1, -1, -1, 1],
                        'out': [0, 0, 0, 0]
                    }

    def _deal(self):
        cards = np.random.choice(self.num_cards, self.num_players, replace=False)
        for i in range(self.num_players):
            self.players[i].get_card(cards[i])

        self.leftover = set([i for i in range(self.num_cards)]) - set(cards)

        if self.verbose:
            for player in range(self.num_players):
                print("player {} has card {}".format(player, cards[player]))

            print("the leftover cards are {}".format(self.leftover))

    def _raised(self, player, last_bet=1):
        i = 1
        players = self.players
        raised_actions = []
        while i < self.num_players:
            curr_player = (player + self.num_players + i) % self.num_players
            if len(self.folded_players) == self.num_players - 1:
                return raised_actions
            if curr_player not in self.folded_players:
                raised_actions.append(players[curr_player].action(True))
                if raised_actions[-1] == 'fold':
                    self.folded_players.add(curr_player)
                if raised_actions[-1] == 'call':
                    if curr_player in self.raised_players or curr_player in self.called_players:
                        bet = last_bet - 1
                    else:
                        bet = last_bet
                        self.called_players.add(curr_player)
                    
                    self.pot += bet
            else:
                raised_actions.append('out')
            i += 1

        return raised_actions

                
    def _play_hand(self):
        players = self.players 

        actions = []
        self.folded_players = set()
        
        for r in range(self.betting_rounds):
            current_round = []
            self.raised_players = set()
            self.called_players = set()
            if self.verbose:
                print("current round: {} chips: {}".format(r, self.pot))
            for i in range(len(players)):
                if i not in self.folded_players:
                    if len(self.folded_players) == self.num_players - 1:
                            if self.verbose:
                                print("player {} won {} chips. Everyone else folded".format(i, self.pot))
                                print(current_round)
                            return
                    curr_action = players[i].action()
                    current_round.append(curr_action)
                    try:
                        did_raise = current_round[-1] == 'raise'
                        did_fold = current_round[-1] == 'fold'
                        
                        if did_fold:
                            self.folded_players.add(i)
                        
                    except:
                        did_raise = False
                    if did_raise:
                        self.pot += 1
                        self.raised_players.add(i)
                        current_round.append(self._raised(i, 1))
                        break
                else:
                    current_round.append('out')
            actions.append(current_round)
            if len(self.folded_players) == self.num_players - 1:
                        if self.verbose:
                            print("player {} won {} chips. Everyone else folded".format(set([0,1,2]) - self.folded_players, self.pot))
                            print(actions)
                        return
        if self.verbose:
            print(actions)

        return actions
        
    def _showdown(self):
        still_playing = [player for player in self.players if player.player_number not in self.folded_players]
        winner = max(still_playing)
        if self.verbose:
            print(still_playing)
            print("the winner is {}. They won {} chips".format(winner, self.pot))

    def play(self):
        self.pot += self.num_players
        if self.verbose:
            print('Staring game, each player antes 1')
            print('The pot is {}'.format(self.pot))
        

        self._deal()
        actions = self._play_hand()
        self._showdown()

        for player in self.players:
            print(self.represent(actions, player.card, player.player_number))

    def represent(self, actions, card, player_number):
        representation = []

        for r in actions:
            for action in r:
                if isinstance(action, list):
                    for response in action:
                        mapping = self.mapping[response]
                        representation.append(mapping)
                else:
                    mapping = self.mapping[action]
                    representation.append(mapping)

        representation = np.array(representation).reshape(-1)
        size = representation.shape[0]
        flattened = np.zeros(23)
        flattened[:size] = representation
        flattened[-3] = self.pot / 6
        flattened[-2] = player_number
        flattened[-1] = card
        return flattened


class ExtendedKuhn(Kuhn):
    def _deal(self):
        choices = [i for i in range(0, 10)] * 2
        cards = np.random.choice(choices, self.num_players, replace=False)
        for i in range(self.num_players):
            self.players[i].get_card(cards[i])

        res = list(map(lambda x: choices.remove(x) if x in choices else None, cards))

        common_card = np.random.choice(list(choices),1)
        choices.remove(common_card)
        self.leftover = choices
        self.common_card = common_card[0]
        if self.verbose:
            for player in range(self.num_players):
                print("player {} has card {}".format(player, cards[player]))

            print("the leftover cards are {}".format(self.leftover))
            print("the common card is {}".format(self.common_card))

    def _raised(self, player, last_bet=1, last_raiser=None):
        i = 1
        players = self.players
        raised_actions = []
        while i < self.num_players:
            curr_player = (player + self.num_players + i) % self.num_players
            if len(self.folded_players) == self.num_players - 1:
                return raised_actions
            if curr_player not in self.folded_players:
                raised_actions.append(players[curr_player].action(True, extended=True))
                if raised_actions[-1] == 'fold':
                    self.folded_players.add(curr_player)
                if raised_actions[-1] == 'call':
                    self.pot += last_bet
                    self.called_players.add(curr_player)
                if raised_actions[-1] == 'raise':
                    self.pot += last_bet + 1
                    self.raised_players.add(curr_player)
                    actions = super()._raised(curr_player, 2)
                    raised_actions.append(actions)
                    return raised_actions
            i += 1

        return raised_actions

    def _showdown(self):
        still_playing = [player for player in self.players if player.player_number not in self.folded_players]

        for player in still_playing:
            if player.card == self.common_card:
                print("player {} won with a pair! They won {} chips".format(player, self.pot))
                return

        high_card_player = max(still_playing)


        ties = sum(player.card == high_card_player.card for player in still_playing)

        if ties > 1:
            winners = [p for p in still_playing if p.card == high_card_player.card]

            print('there was a tie. {} and {} split the pot of {}'.format(winners[0], winners[1], self.pot))


        print("player {} won with high card. They won {} chips".format(high_card_player, self.pot))

    def represent(self, actions, card, player_number):
        rounds = []

        for r in actions:
            curr_round = []
            for action in r:
                if isinstance(action, list):
                    for response in action:
                        if isinstance(response, list):
                            for raised in response:
                                mapping = self.mapping[raised]
                                curr_round.append(mapping)
                        else:
                            mapping = self.mapping[response]
                            curr_round.append(mapping)
                else:
                    mapping = self.mapping[action]
                    curr_round.append(mapping)
            rounds.append(np.array(curr_round).flatten())
        
        first_round_length = len(rounds[0])
        second_round_length = len(rounds[1])

        max_betting_length = 28

        flattened = np.zeros(59)
        flattened[:first_round_length] = rounds[0]
        flattened[max_betting_length:max_betting_length+second_round_length] = rounds[1]
        flattened[-3] = self.pot / 15
        flattened[-2] = player_number
        flattened[-1] = card
        return flattened


        


if __name__ == '__main__':
    # Kuhn(1, 5, verbose=True).play()
    ExtendedKuhn(2, 10, verbose=True).play()






