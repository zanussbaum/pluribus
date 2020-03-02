class Player:
    def __init__(self, player_number):
        self.player_number = player_number
        self.chips = 10

    def get_card(self, card):
        self.card = card

    def bet(self):
        self.chips -= 1

    def win(self, amount):
        self.chips += amount

    def action(self):
        action = int(input("Fold (0) Check (1) or Bet (2)? "))
        return action

    def __lt__(self, player):
        return self.card < player.card

    def __repr__(self):
        return 'Player: {} Card: {}'.format(self.player_number, self.card)