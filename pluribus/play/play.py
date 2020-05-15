import pickle
import random
import sys
import os
import numpy as np
from pluribus.search.search import NestedSearch
from pluribus.cfr.mccfr import MonteCarloCFR
from pluribus.game.card import Card
from pluribus.game.hand_eval import leduc_eval
from pluribus.game.state import LeducState


class Game:
    def __init__(self):
        self.cards = [Card(12, 1), Card(13, 1), Card(14, 1), Card(12, 2), Card(13, 2), Card(14, 2)]
        self.human = True
        settings = {'num_players':2, 'num_actions':3, 'hand_eval': leduc_eval,
            'num_rounds':2, 'num_raises':2, 'raise_size':[2,4],
            'num_cards': 3, 'game': 'leduc', 'state': LeducState
        }

        self.mccfr = MonteCarloCFR(settings)
        try:
            with open('pluribus/blueprint/leduc_strat.p', 'rb') as f:
                blueprint = pickle.load(f)

            self.mccfr.node_map = blueprint

        except:
            print('\n\n{}\nNo blueprint strategy was found.\n\
                \nCreating a new one\n{}\n\n'.format('*'*100, '*'*100)) 
           
            self.mccfr.train(self.cards, 10000)

            
            with open('pluribus/blueprint/leduc_strat.p', 'wb') as f:
                pickle.dump(self.mccfr.node_map, f)

        self.state_json = self.mccfr.state_json
        self.state_json['cards'] = self.cards

    def _handle_action(self):
        valid = False
        if self.human:
            while not valid:
                try:
                    opp_action = input("\nPlay an action (Fold, Call, Raise): ")
                    if opp_action in set(['F', 'C', 'R']):
                        if opp_action == 'R':
                            amount = input("How much would you like to raise? ")
                            if amount.isdigit():
                                opp_action = amount + opp_action
                                valid = True
                        else:
                            valid = True
                    else:
                        raise ValueError
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    print('please enter a valid action (F, C, R)')

        else:
            info_set = self.search.info_set
            node = self.search.strategy[self.search.turn]
            strategy = node[info_set].curr_strategy
            actions = list(strategy.keys())
            prob = list(strategy.values())

            opp_action = random.choices(actions, weights=prob)[0]

        return opp_action

    def start_game(self):
        print('\nshuffling cards\n')
        np.random.shuffle(self.cards)
        print("Cards are {}".format(self.cards))
        state = LeducState(self.state_json)
        self.search = NestedSearch(self.mccfr, state, 1)

    def state(self):
        if not self.search.terminal:
            return self.search.turn

        return -1

    def user_action(self, action):
        self.search.opponent_turn(action)

    def pluribus_action(self):
        action = self.search.traverser_turn()
        return action


if __name__ == '__main__':
    Game().play()
       