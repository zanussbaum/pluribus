import numpy as np
from player import Player


# implement folding correctly and cards 
    
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
                print("player {} has card {}".format(player+1, cards[player]))

            print("the leftover cards are {}".format(self.leftover))

    def play_cards(self):
        folded = np.array([0 for i in range(self.num_players)])

        for i in range(self.num_players):
            action = self.players[i].action()
            if not action:
                folded[i] = 1
                if sum(folded) == 2:
                    player = np.where(folded == 0)[0][0]
                    print("everyone else folded\nplayer {} wins {} chips".format(player, self.pot))
                    return
            elif action == 1:
                continue
            else:
                self.pot += 1
                self.players[i].bet()

        winner = max(self.players)

        print("player {} won with card {}".format(winner.player_number, winner.card))
        print("they won {} chips".format(self.pot))

        self.players[i].win(self.pot)
        


    def play(self):
        print('Staring game, each player antes 1')
        self.pot += self.num_players
        print(self.pot)

        self.deal(verbose=True)
        self.play_cards()


if __name__ == '__main__':
    Kuhn().play()






