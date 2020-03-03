import numpy as np
from player import Player
from copy import deepcopy

    
class Kuhn:
    def __init__(self, **args):
        self.pot = 0
        self.num_players = 3
        self.players = [Player(i) for i in range(self.num_players)]

    def deal(self, verbose=False):
        cards = np.random.choice(5, 3, replace=False)
        for i in range(self.num_players):
            self.players[i].get_card(cards[i])

        self.leftover = set([i for i in range(5)]) - set(cards)

        if verbose:
            for player in range(self.num_players):
                print("player {} has card {}".format(player, cards[player]))

            print("the leftover cards are {}".format(self.leftover))

    def __folded(self, actions, players):
        folded = np.where(actions==0)[0]
        for out in folded[::-1]:
            players.pop(out)

    def __raised(self, actions, raiser, players):
        #make sure that the raiser stays in the game
        actions[players.index(raiser)] = 1
        for i, player in enumerate(players):
            if player != raiser and actions[i] != 0:
                actions[i] = self.players[player].action(raised=True)
                if actions[i]:
                    self.pot += 1

        self.__folded(actions, players)

    def __showdown(self, players):
        if len(players) == 1:
            print("everyone else folded\nplayer {} wins {} chips".format(players[0], self.pot))
            self.players[players[0]].win(self.pot)
            return
        winner = self.players[max(players, key=lambda k: self.players[k])]
        print("player {} won with card {}".format(winner.player_number, winner.card))
        print("they won {} chips".format(self.pot))

        winner.win(self.pot)

    def __betting_round(self, players):
        folded = np.array([0 for i in range(len(players))])
        actions = np.array([None for i in range(len(players))])
        for i, player in enumerate(players):
            actions[i] = self.players[player].action()
            if not actions[i]:
                folded[i] = True
                if sum(folded) == 2:
                    player = np.where(folded == 0)[0][0]
                    print("everyone else folded\nplayer {} wins {} chips".format(player, self.pot))
                    players = []
                    return
            elif actions[i] == 2:
                self.pot += 1
                self.__raised(actions, player, players)
                self.__showdown(players)
                return

        # if everyone calls, less than two people fold, or some combination
        # remove the people that have folded
        self.__folded(actions, players)
        self.__showdown(players)
                
    def play_hand(self):
        players = [i for i in range(self.num_players)]
        self.__betting_round(players)


    def play(self):
        print('Staring game, each player antes 1')
        self.pot += self.num_players
        print(self.pot)

        self.deal(verbose=True)
        self.play_hand()


if __name__ == '__main__':
    Kuhn().play()






