#include <string>
#include <unordered_map>
#include <algorithm>
#include <random>
#include <set>
#include "InfoNode.hpp"
#include "State.hpp"
#include <boost/serialization/serialization.hpp>
#include <boost/serialization/unordered_map.hpp>
#include <boost/serialization/string.hpp>
#include <boost/serialization/vector.hpp>
#include <boost/serialization/set.hpp>


class Pluribus{
    public:
        friend class boost::serialization::access;

        Pluribus(int numPlayers);
        ~Pluribus();
        void train(int iterations);
        std::vector<int> mCards;
        std::unordered_map<int, std::unordered_map<std::string, InfoNode>> mNodeMap;
        std::valarray<float> expectedUtility();

        std::valarray<float> subgameSolve(State state, int player, bool prune=false);
        void subgameUpdate(State state, int player);
        void search(int iterations);

        void play();
        void opponentTurn(std::string action);
        void pluribusTurn();
        void checkNewRound();

        template<class Archive>
        void serialize(Archive & ar, const unsigned int version){
            ar & mNodeMap;
            ar & mValidActionsMap;
        };

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

        //maybe change to set?
        std::unordered_map<std::string, std::set<std::string>> mValidActionsMap;
        std::unordered_map<std::string, std::string> mFrozenNodes;
        std::vector<std::string> mValidActions;

        State mCurrentState;
        int mPublicState;
};