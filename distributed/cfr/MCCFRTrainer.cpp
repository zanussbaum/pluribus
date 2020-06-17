#include "MCCFRTrainer.hpp"


MCCFRTrainer::MCCFRTrainer(){
    mCards = {1,2,3};
};

MCCFRTrainer::MCCFRTrainer(int numPlayers){
    mCards = {1,2,3,1,2,3};
    mNumPlayers = numPlayers;

    std::random_device mRd;
    std::mt19937 mActionEng(mRd());
}

MCCFRTrainer::~MCCFRTrainer(){
};

void MCCFRTrainer::train(int iterations){
    std::random_device rd;
    std::mt19937 randEng(rd());
    for(int i=1; i<=iterations; i++){
        if(i%1000 == 0){
            std::cout << "\nIteration "<< i;
        }
        std::shuffle(mCards.begin(), mCards.end(), randEng);
        State state(mNumPlayers, 2, mCards, 2);
        for(int player=0; player<mNumPlayers;player++){
            if(i % mStrategyInterval == 0){
                MCCFRTrainer::updateStrategy(state, player);
            }
            if(i > mPruneThreshold){
                float prune = (float) rand()/RAND_MAX;
                if(prune < .05){
                    MCCFRTrainer::mccfr(state, player);
                }
                else{
                    MCCFRTrainer::mccfr(state, player, true);
                }
            }
            else{
                MCCFRTrainer::mccfr(state, player);
            }
        }
        if(i < mLCFRThreshold && i % mDiscountInterval == 0){
            float discount = (i/mDiscountInterval)/((i/mDiscountInterval) + 1.);
            for(auto map: mNodeMap){
                std::unordered_map<std::string, InfoNode> playerNodes = mNodeMap[map.first];
                for(auto keyValue: playerNodes){
                    auto validActions = mValidActionsMap[keyValue.first];
                    for(auto action: validActions){
                        keyValue.second.regretSum.at(action) *= discount;
                        keyValue.second.strategySum.at(action) *= discount;
                    }
                }
            }
        }
    }
}

std::valarray<float> MCCFRTrainer::mccfr(State state, int player, bool prune){
    if(state.isTerminal()){
        std::valarray<float> util = state.payoff();
        return util;
    }

    int currentPlayer = state.mTurn;

    if(currentPlayer == player){
        std::string infoSet = state.infoSet();
        auto search = mNodeMap[currentPlayer].find(infoSet);
        if(search == mNodeMap[currentPlayer].end()){
            std::vector<std::string> validActions = state.validActions();
            mNodeMap[currentPlayer].insert({infoSet, InfoNode(validActions)});
            mValidActionsMap[infoSet] = validActions;
        }

        std::vector<std::string> validActions = mValidActionsMap[infoSet];
        std::unordered_map<std::string, double> strategy = mNodeMap[currentPlayer].at(infoSet).getStrategy(validActions);

        std::unordered_map<std::string, double> utilities;

        std::valarray<float> nodeUtil(state.mNumPlayers);

        
        std::valarray<float> returned;
        float regret = 0.0;

        if(prune){
            std::set<std::string> explored;
            for(auto action: validActions){
                if(mNodeMap[currentPlayer].at(infoSet).regretSum.at(action) > mRegretMinimum){
                    returned = mccfr(State(state, action), player, prune);
                    utilities[action] = returned[currentPlayer];
                    nodeUtil += returned * strategy.at(action);
                    explored.insert(action);
                }
            }
            for(auto action: validActions){
                auto search = explored.find(action);
                if(search != explored.end()){
                    regret = utilities.at(action) - nodeUtil[currentPlayer];
                    mNodeMap[currentPlayer].at(infoSet).regretSum.at(action) += regret;
                }
            }
        }
        else{
            for(auto action: validActions){
                returned = mccfr(State(state, action), player, prune);
                utilities[action] = returned[currentPlayer];
                nodeUtil += returned * strategy.at(action); 
            }
            for(auto action: validActions){
                regret = utilities.at(action) - nodeUtil[currentPlayer];
                mNodeMap[currentPlayer].at(infoSet).regretSum.at(action) += regret;
            }  
        }
        return nodeUtil;
    }
    else{
        std::string infoSet = state.infoSet();
        auto search = mNodeMap[currentPlayer].find(infoSet);
        if(search == mNodeMap[currentPlayer].end()){
            std::vector<std::string> validActions = state.validActions();
            mNodeMap[currentPlayer].insert({infoSet, InfoNode(validActions)});
            mValidActionsMap[infoSet] = validActions;
        }
        std::vector<std::string> validActions = mValidActionsMap[infoSet];
        std::unordered_map<std::string, double> strategy = mNodeMap[currentPlayer].at(infoSet).getStrategy(validActions);

        std::vector<std::string> actions;
        std::vector<double> probabilities;
        for(auto map: strategy){
            actions.push_back(map.first);
            probabilities.push_back(map.second);
        }
        std::discrete_distribution<int> random_choice(probabilities.begin(), probabilities.end());
        auto action = random_choice(mActionEng);
        return mccfr(State(state, actions[action]), player, prune);
    }
};

void MCCFRTrainer::updateStrategy(State state, int player){
    if(state.isTerminal()){
        return;
    }
    int currentPlayer = state.mTurn;

    if(currentPlayer == player){
        std::string infoSet = state.infoSet();
        auto search = mNodeMap[currentPlayer].find(infoSet);
        if(search == mNodeMap[currentPlayer].end()){
            std::vector<std::string> validActions = state.validActions();
            mNodeMap[currentPlayer].insert({infoSet, InfoNode(validActions)});
            mValidActionsMap[infoSet] = validActions;
        }
        std::vector<std::string> validActions = mValidActionsMap[infoSet];
        std::unordered_map<std::string, double> strategy = mNodeMap[currentPlayer].at(infoSet).getStrategy(validActions);

        std::vector<std::string> actions;
        std::vector<double> probabilities;
        for(auto map: strategy){
            actions.push_back(map.first);
            probabilities.push_back(map.second);
        }
        std::discrete_distribution<int> random_choice(probabilities.begin(), probabilities.end());
        auto action = random_choice(mActionEng);

        mNodeMap[currentPlayer].at(infoSet).strategySum.at(actions[action]) += 1;
        updateStrategy(State(state, actions[action]), player);
    }
    else{
        std::string infoSet = state.infoSet();
        auto search = mValidActionsMap.find(infoSet);
        if(search == mValidActionsMap.end()){
            std::vector<std::string> validActions = state.validActions();
            mNodeMap[currentPlayer].insert({infoSet, InfoNode(validActions)});
            mValidActionsMap[infoSet] = validActions;
        }
        std::vector<std::string> validActions = mValidActionsMap[infoSet];
        for(auto action: validActions){
            updateStrategy(State(state, action), player);
        }
    }
}

std::valarray<float> MCCFRTrainer::expectedUtility(){
    std::valarray<float> expectedUtility(mNumPlayers);

    std::sort(mCards.begin(), mCards.end());
    int numPermutations = 0;
    do{
        State state(mNumPlayers, 2, mCards, 2);
        expectedUtility += traverseTree(state);
        numPermutations += 1;
    }while(std::next_permutation(mCards.begin(), mCards.end()));

    return expectedUtility/numPermutations;
};

std::valarray<float> MCCFRTrainer::traverseTree(State state){
    if(state.isTerminal()){
        std::valarray<float> util = state.payoff();
        return util;
    }

    int player = state.mTurn;
    std::string infoSet = state.infoSet();
    std::vector<std::string> validActions = mValidActionsMap[infoSet];
    std::unordered_map<std::string, double> strategy = mNodeMap[player].at(infoSet).getAverageStrategy();

    std::valarray<float> expectedUtility(mNumPlayers);

    for(auto action: validActions){
        expectedUtility += traverseTree(State(state, action)) * strategy.at(action);
    }

    return expectedUtility;
}