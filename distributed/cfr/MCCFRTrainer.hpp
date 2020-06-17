#include <string>
#include <unordered_map>
#include <algorithm>
#include <random>
#include <set>
#include "InfoNode.hpp"
#include "State.hpp"

class MCCFRTrainer{
    public:
        MCCFRTrainer();
        MCCFRTrainer(int numPlayers);
        ~MCCFRTrainer();
        void train(int iterations);
        std::vector<int> mCards;
        std::unordered_map<int, std::unordered_map<std::string, InfoNode>> mNodeMap;
        std::valarray<float> expectedUtility();

    private:
        std::valarray<float> mccfr(State state, int player, bool prune=false);
        void updateStrategy(State state, int player);
        std::valarray<float> traverseTree(State state);

        int mNumPlayers;
        int mRegretMinimum = -300000;
        int mStrategyInterval = 100;
        int mPruneThreshold = 200;
        int mDiscountInterval = 100;
        int mLCFRThreshold = 400;
        std::random_device mRd;
        std::mt19937 mActionEng;

        std::unordered_map<std::string, std::vector<std::string>> mValidActionsMap;
        std::vector<std::string> mValidActions;
};