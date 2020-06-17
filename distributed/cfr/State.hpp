#include <vector>
#include <string>
#include <iostream>
#include <algorithm>
#include <numeric>
#include <valarray>
class State{
    public:
        State(int numPlayers, int numRound, std::vector<int> cards, int numRaises);
        State(const State &state, std::string action, bool search=false);
        ~State();
        std::string infoSet();
        bool isTerminal();
        std::valarray<float> payoff();
        std::vector<int> winners();
        bool allCalledOrFolded();
        std::vector<std::string> validActions();
        
        std::vector<int> mCards;
        std::vector<int> mBets;
        std::vector<std::vector<std::string>> mHistory;
        std::vector<bool> mIn;
        
        int mNumPlayers;
        int mTurn;
        
        int mTotalRounds;
        int mRound;
        int mRaises;
        int mRaisesSoFar;
};