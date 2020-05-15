import random
from copy import deepcopy
from leduc.cfr.mccfr import MonteCarloCFR
from leduc.game.tree import Subgame
class NestedSearch:
    # we need to figure out a way to 'freeze' infosets for actions that have already occured
    # basically we don't want to calculate new strategy for that action just everything after
    # again if we are passing things make sure we copy everything
    # 
    # we need to figure out a way to speed up subgame solving
    def __init__(self, mccfr, hand, traverser, verbose=1):
        self.game_state = hand
        self.public_state = hand
        self.mccfr = mccfr
        self.strategy = mccfr.node_map
        self.leduc = traverser
        self.cards = deepcopy(hand.cards)
        self.blueprint = deepcopy(mccfr.node_map)
        self.verbose = verbose

    @property
    def turn(self):
        return self.game_state.turn

    @property
    def action(self):
        return self.game_state.valid_actions

    @property
    def terminal(self):
        return self.game_state.is_terminal

    @property
    def info_set(self):
        return self.game_state.info_set

    @property
    def payoff(self):
        return self.game_state.payoff()

    def search(self):
        subgame = Subgame(self.public_state)
        tree = subgame.build_tree(self.strategy)
        strat = self.strategy

        subgame_strategy = self.mccfr.subgame_solve(tree, strat, 1000)

        for player in self.strategy:
            strat = self.strategy[player]
            for key in subgame_strategy[player]:
                if key not in strat:
                    strat[key] = subgame_strategy[player][key]
                else:
                    strat[key].strategy_sum = {k:value + subgame_strategy[player][key].strategy_sum[k] for k, value in strat[key].strategy_sum.items()}

    def opponent_turn(self, action):
        player = self.turn
        info_set = self.game_state.info_set
        node = self.strategy[player][info_set]
        
        amount = None
        if len(action) > 1:
            amount = int(action[:-1])

        if action not in node.curr_strategy.keys() and amount != self.public_state.raise_size[self.public_state.round]:
            self.public_state.actions.add(action)
            public_state = self.public_state.public_state
            for state, node in self.strategy[player].items():
                if public_state in state:
                    node.add_action(action)

            self.search()

        if self.verbose:
            print("player {} played {}".format(player, action), flush=True)

        self.game_state = self.game_state.add(player, action)

    def traverser_turn(self):
        info_set = self.game_state.info_set
        player_nodes = self.strategy[self.leduc]
        node = player_nodes[info_set]
        valid_actions = self.game_state.valid_actions
        strategy = node.strategy(valid_actions)
        actions = list(strategy.keys())
        prob = list(strategy.values())

        action = random.choices(actions, weights=prob)[0]
        if self.verbose:
            print("leduc played {}".format(action))

        self.game_state = self.game_state.add(self.leduc, action)
        player_nodes[info_set].is_frozen = True

        return action

    def check_new_round(self):
        if self.terminal:
            if self.verbose:
                print("The game has ended")
                payoffs = self.game_state.payoff()
                if len(self.game_state.winners) > 1:
                    print("There was a tie. pot split: {}".format(payoffs))

                else:
                    print("Player {} won. They won {}".format(self.game_state.winners, max(payoffs)))
            
            return True

        if self.game_state.round > self.public_state.round:
            if self.verbose:
                print("New round. The current state of the game is {}".format(self.game_state.public_state))
            self.public_state = self.game_state
            self.search()
            return True

        return False