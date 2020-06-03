#include <string>
#include <unordered_map>
#include <algorithm>
#include <random>
#include <set>
#include "Node.hpp"
#include "State.hpp"

class Trainer{
    public:
        Trainer();
        Trainer(int numPlayers);
        ~Trainer();
        void train(int iterations);
        void mccfrTrain(int iterations);
        std::vector<int> mCards;
        std::unordered_map<int, std::unordered_map<std::string, Node>> mNodeMap;
        std::valarray<float> expectedUtility();

    private:
        std::valarray<float> cfr(State state, std::vector<double> probs);
        std::valarray<float> mccfr(State state, int player, bool prune=false);
        void updateStrategy(State state, int player);
        std::valarray<float> traverseTree(State state);

        int mNumPlayers;
        int mRegretMinimum = -300000;
        int mStrategyInterval = 100;
        int mPruneThreshold = 200;
        int mDiscountInterval = 100;
        int mLCFRThreshold = 400;
};