#include <vector>
#include <string>
#include <iostream>
#include <algorithm>
#include <numeric>
#include <valarray>
#ifndef STATE_HPP
#define STATE_HPP
class State{
    public:
        State(int numPlayers, int numRound, std::vector<int> cards);
        State(const State &state, std::string action);
        ~State();
        std::string infoSet();
        bool isTerminal();
        std::valarray<float> payoff();
        

        std::vector<int> mCards;
        std::vector<int> mBets;
        int mTurn;
        std::vector<std::vector<std::string> > mHistory;
        int mNumPlayers;

    private:
        bool allCalledOrFolded();
        std::vector<bool> mIn;
        int mTotalRounds;
        int mRound;
};
    
#endif