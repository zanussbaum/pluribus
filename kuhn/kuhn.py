import numpy as np
from player import Player

    
class Kuhn:
    def __init__(self, betting_rounds, verbose=False, **args):
        self.pot = 0
        self.num_players = 3
        self.players = [Player(i) for i in range(self.num_players)]
        self.verbose = verbose
        self.betting_rounds = betting_rounds

    def __deal(self):
        cards = np.random.choice(5, 3, replace=False)
        for i in range(self.num_players):
            self.players[i].get_card(cards[i])

        self.leftover = set([i for i in range(5)]) - set(cards)

        if self.verbose:
            for player in range(self.num_players):
                print("player {} has card {}".format(player, cards[player]))

            print("the leftover cards are {}".format(self.leftover))

    def __raised(self, player):
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
                    self.pot += 1

            i += 1

        return raised_actions

                
    def __play_hand(self):
        players = self.players 

        actions = []
        self.folded_players = set()

        for _ in range(self.betting_rounds):
            current_round = []
            for i in range(len(players)):
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
                    current_round.append(self.__raised(i))
                    break
            
            actions.append(current_round)
            if len(self.folded_players) == self.num_players - 1:
                        if self.verbose:
                            print("player {} won {} chips. Everyone else folded".format(set([0,1,2]) - self.folded_players, self.pot))
                            print(actions)
                        return


        still_playing = [player for player in players if player.player_number not in self.folded_players]
        winner = max(still_playing)
        if self.verbose:
            print(actions)
            print(still_playing)
            print("the winner is {}. They won {} chips".format(winner, self.pot))

        return actions
        
            

    def play(self):
        if self.verbose:
            print('Staring game, each player antes 1')
        self.pot += self.num_players

        self.__deal()
        self.__play_hand()


if __name__ == '__main__':
    Kuhn(1, verbose=True).play()






