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

    def action(self, raised=False):
        valid = False
        if raised:
            
            while not valid:
                try:
                    action = int(input('Player: {} Fold (0) or Call (1)? '.format(self.player_number)))
                    if isinstance(action, int):
                        valid = True

                except:
                    print('please enter a valid action')
        else: 
            while not valid:
                try:
                    action = int(input("Player: {} Fold (0) Check (1) or Bet (2)? ".format(self.player_number)))
                    if isinstance(action, int):
                            valid = True
                except:
                    print('please enter a valid action')
        return action

    def __lt__(self, player):
        return self.card < player.card

    def __repr__(self):
        return 'Player: {} Card: {}'.format(self.player_number, self.card)