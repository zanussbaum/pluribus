import argparse
import numpy as np 
from regret_min import RegretMin
from vanilla_cfr import VanillaCFR
from mccfr import MonteCarloCFR


def three_player_payoff(self, history, cards):
    outstanding_bet = history.find('B')

    if outstanding_bet != -1:
        actions_after = history[outstanding_bet:]
        num_folds = actions_after.count('P')
        num_bets = history.count('B')

        utilities = [0 for i in range(self.num_players)]
        pot = self.num_players + num_bets
        
        for i in range(self.num_players):
            utilities[i] = -(sum([1 if action == 'B' else 0 for action in history[i::3]]) + 1)

        if num_folds == self.num_players  - 1:
            utilities[outstanding_bet] += pot
            return utilities

        left = [(pos+outstanding_bet)%self.num_players for pos, char in enumerate(history[outstanding_bet:]) if char != 'P']
        winner = np.argwhere(cards == max(cards[:self.num_players][left])).item()
        utilities[winner] += pot
        
        return utilities
        
    winner = np.argmax(cards[:self.num_players])

    return [-1 if i != winner else 2 for i in range(self.num_players)]


parser = argparse.ArgumentParser(description='Counterfactual Regret Minimization')
parser.add_argument('-i', '--iterations', type=int, help='number of iterations to run for.')
parser.add_argument('-c','--cfr', type=int, help='(0) Run regret min or Run CFR for (1): 2 players or (2): 3 players')
parser.add_argument('-r', '--rounds', default=1, type=int, help='Number of betting rounds')
parser.add_argument('-b', '--raises', default=1, type=int, help='Number of raises per round')
parser.add_argument('-m', '--mccfr', type=int, help='(1) Run MCCFR for two player kuhn poker or (2) 3 players')
args = parser.parse_args()

if args.cfr == 0: 
    print("Running regret minimization for RPS with strat [.4, .3, .3]")
    utilities = np.array([[[0, -1, 1], [1, 0, -1], [-1, 1, 0]], [[0, 1, -1], [-1, 0, 1], [1, -1, 0]]])
    minimization = RegretMin(3, utilities[0], np.array([.4, .3, .3]))
    minimization.train(args.iterations)
    print(minimization.get_avg_strategy())
elif args.cfr == 1:
    # kuhn poker 2 player 
    # 2 actions
    cards = [i for i in range(1, 4)]
    ACTIONS = ['P', 'B']
    TERMINAL = ["PP", "PBP", "PBB", "BP", "BB"]

    kuhn_regret = VanillaCFR(2, 2, terminal=TERMINAL, actions=ACTIONS)

    kuhn_regret.train(cards, args.iterations)
elif args.cfr == 2:
    cards = np.array([i for i in range(1, 5)])
    ACTIONS = ['P', 'B']
    TERMINAL = ["PPP", "PPBPP", "PPBPB", "PPBBP", "PPBBB", "PBPP",
            "PBPB", "PBBP", "PBBB", "BPP", "BPB", "BBP", "BBB"
        ]


    three_kuhn = VanillaCFR(3, 2, terminal=TERMINAL, actions=ACTIONS, payoff=three_player_payoff)

    three_kuhn.train(cards, args.iterations)

elif args.mccfr == 1:
    cards = [i for i in range(1, 4)]
    ACTIONS = ['P', 'B']
    TERMINAL = ["PP", "PBP", "PBB", "BP", "BB"]

    mccfr = MonteCarloCFR(2, 4, args.rounds, args.raises, terminal=TERMINAL, actions=ACTIONS)

    mccfr.train(cards, args.iterations)

elif args.mccfr == 2:
    cards = np.array([i for i in range(1, 5)])
    ACTIONS = ['P', 'B']
    TERMINAL = ["PPP", "PPBPP", "PPBPB", "PPBBP", "PPBBB", "PBPP",
            "PBPB", "PBBP", "PBBB", "BPP", "BPB", "BBP", "BBB"
        ]

    mccfr = MonteCarloCFR(3, 4, args.rounds, args.raises, terminal=TERMINAL, actions=ACTIONS, payoff=three_player_payoff)

    mccfr.train(cards, args.iterations)
    
else:
    parser.print_help()