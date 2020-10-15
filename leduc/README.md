# MCCFR and CFR for Kuhn Poker and Leduc Poker 

## Kuhn Poker 

[Kuhn Poker](https://en.wikipedia.org/wiki/Kuhn_poker) is a simplified version of poker. In the 2 player version, there are 3 cards (Ace, King, Queen). Each player has the option to Fold, Call, or Bet 1. If player 1 bets, then player 2 can either call or fold. High card wins.  3 player is similar in that a third card is added. See the Wikipedia link for a more in-depth description.

The NE expected value for player 1 is -1/18

Three player Kuhn Poker has a family of analytically found Nash Equilibriums, but it's not known if the family covers all Nash Equilibrium.

## Leduc Poker
[Leduc Poker](http://poker.cs.ualberta.ca/publications/UAI05.pdf) is a smaller variant of hold'em poker where each player is dealt one card. There consists of two betting roudns with max number of raises of 2 per round with raise size of 2 in the first round and 4 in the second round. After the first round, a community card is dealt and another round of betting ensues. Pairs beats high card.  

## CFR and MCCFR

Counterfactual Regret Minimization (CFR) is a self-play algorithm used to learn a strategy to a game by repeatedly playing a game and updating its strategy to improve how much it "regret" taking a decision at a each decision point. This strategy has been wildly successful for imperfect information games like poker. 

[CFR](https://www.quora.com/What-is-an-intuitive-explanation-of-counterfactual-regret-minimization) has been shown to converge to Nash Equilibrium strategy for 2 player zero-sum games. 

[Here](http://modelai.gettysburg.edu/2013/cfr/cfr.pdf) is a great resource for the curious reader.

MCCFR is a variant of CFR where instead of traversing the whole game tree, we will only sample actions so that we will traverse paths on the game tree that are more likely than others. This makes MCCFR a much efficient algorithm for large games.

## How To Use 

`python [vanilla.py|montey.py]` 
to run the CFR/MCCFR variant

`python search.py` to play a game of Leduc. 

CFR converges in around ~10,000 iterations.

MCCFR can converge in around ~10,000, but is more stable around ~20,000 iterations.

For Leduc, you need aorund 50,000 iterations. 