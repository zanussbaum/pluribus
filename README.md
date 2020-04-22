## This repo will hold an implementation of pure Python implementation of Pluribus, Facebook's No-Limit 6-player Hold 'Em Poker Bot.

[Kuhn Poker](https://en.wikipedia.org/wiki/Kuhn_poker) 
============
Kuhn poker is a simplified game of poker where each player is given one card from a set of 3 cards. The third card is set aside. High card wins. We implement a variation of Kuhn poker where the three cards are chose from a set of 5 cards for three players. 


Implementation of Pluribus
===================================
- [X] Implement Kuhn Poker 
- [X] Monte Carlo Counterfactual Regret Minimization
    * Samples action in game tree rather than traversing entire game tree
    * One player is traverser on each iteration
    * Linear CFR in early iterations
    - [x] Two player Kuhn MCCFR
    - [x] Three player Kuhn MCCFR
    - [x] Three player Leduc MCCFR

- [ ] Depth Limited Search
    * Plays blueprint strategy in the first betting round
        * Doesn't need to use informal abstraction since the number of decision points are small
    * After the first betting round, real time search is conducted
    * Real-time search considers k=4 different strategies (all modifications of blueprint strategies)
        * How did they calculate these different modifications?  
    * Use MCCFR like before if early in the game or subgame is large
    * Else, use vector-based form of Linear CFR

- [ ] Implement Poker Abstraction
    * Action Abstraction
        * What are the different situations? Talks about there being between 1 and 14 different bets it considers
    * Information Abstraction
        * Treat similar hands with the same strategy
        * How do we determine what hands are similar? By card? By win probability? 

