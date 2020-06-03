#include "Trainer.hpp"


Trainer::Trainer(){
    mCards = {1,2,3};
};

Trainer::Trainer(int numPlayers){
    mCards = {1,2,3};
    mNumPlayers = numPlayers;
};

Trainer::~Trainer(){
};

void Trainer::train(int iterations){
    std::random_device rd;
    std::mt19937 randEng(rd());
    for(int i=0; i<iterations; i++){
        std::shuffle(mCards.begin(), mCards.end(), randEng);
        State state(2, 1, mCards);
        std::vector<double> probs = {1,1};
        Trainer::cfr(state, probs);
    }
}

void Trainer::mccfrTrain(int iterations){
    std::random_device rd;
    std::mt19937 randEng(rd());
    for(int i=1; i<=iterations; i++){
        std::shuffle(mCards.begin(), mCards.end(), randEng);
        State state(2, 1, mCards);
        for(int player=0; player<mNumPlayers;player++){
            if(i % mStrategyInterval == 0){
                Trainer::updateStrategy(state, player);
            }
            if(i > mPruneThreshold){
                float prune = (float) rand()/RAND_MAX;
                if(prune < .05){
                    Trainer::mccfr(state, player);
                }
                else{
                    Trainer::mccfr(state, player, prune=true);
                }
            }
            else{
                Trainer::mccfr(state, player);
            }
        }
        if(i < mLCFRThreshold && i % mDiscountInterval == 0){
            float discount = (i/mDiscountInterval)/((i/mDiscountInterval) + 1);
            for(auto map: mNodeMap){
                std::unordered_map<std::string, Node> playerNodes = mNodeMap[map.first];
                for(auto keyValue: playerNodes){
                    // Node node = keyValue.second;
                    keyValue.second.regretSum *= discount;
                    keyValue.second.strategySum *= discount;
                }
            }
        }
    }
}

std::valarray<float> Trainer::cfr(State state, std::vector<double> probs){
    if(state.isTerminal()){
        std::valarray<float> util = state.payoff();
        return util;
    }

    int player = state.mTurn;
    std::string infoSet = state.infoSet();
    
    auto search = mNodeMap[player].find(infoSet);
    if(search == mNodeMap[player].end()){
        mNodeMap[player].insert({infoSet, Node(2)});
    }

    std::valarray<float> strategy = mNodeMap[player].at(infoSet).getStrategy(probs[player]);

    std::valarray<float> utilities(state.mNumPlayers);

    std::valarray<float> nodeUtil(state.mNumPlayers);

    std::vector<std::string> actions = {"P", "B"};
    std::valarray<float> returned;
    
    for(int i=0; i<actions.size(); i++){
        std::vector<double> newProbs = probs;
        newProbs[player] *= strategy[i]; 
        returned = cfr(State(state, actions[i]), newProbs);
        utilities[i] = returned[player];
        nodeUtil += returned * strategy[i];
    }

    double opponentProb = 1;
    for(int i=0; i<probs.size(); i++){
        if(i != player){
            opponentProb*= probs[i];
        }
    }
    float regret = 0.0;
    for(int i=0; i<actions.size(); i++){
        regret = utilities[i] - nodeUtil[player];
        mNodeMap[player].at(infoSet).regretSum[i] += regret * opponentProb;
    }


    return nodeUtil;
};

std::valarray<float> Trainer::mccfr(State state, int player, bool prune){
    if(state.isTerminal()){
        std::valarray<float> util = state.payoff();
        return util;
    }

    int currentPlayer = state.mTurn;

    if(currentPlayer == player){
        std::string infoSet = state.infoSet();
        auto search = mNodeMap[player].find(infoSet);
        if(search == mNodeMap[player].end()){
            mNodeMap[player].insert({infoSet, Node(state.mNumPlayers)});
        }
        // Node node = mNodeMap[player].at(infoSet);

        std::valarray<float> strategy = mNodeMap[player].at(infoSet).getStrategy();

        std::valarray<float> utilities(state.mNumPlayers);

        std::valarray<float> nodeUtil;

        std::vector<std::string> actions = {"P", "B"};
        std::valarray<float> returned;
        float regret = 0.0;

        if(prune){
            std::set<int> explored;
            for(int i=0; i<actions.size(); i++){
                if(mNodeMap[player].at(infoSet).regretSum[i] > mRegretMinimum){
                    returned = mccfr(State(state, actions[i]), player, prune);
                    utilities[i] = returned[player];
                    nodeUtil += returned * strategy[i];
                    explored.insert(i);
                }
            }
            for(int i=0; i<actions.size(); i++){
                auto search = explored.find(i);
                if(search != explored.end()){
                    regret = utilities[i] - nodeUtil[currentPlayer];
                    mNodeMap[player].at(infoSet).regretSum[i] += regret;
                }
            }
        }
        else{
            for(int i=0; i<actions.size(); i++){
                returned = mccfr(State(state, actions[i]), player, prune);
                utilities[i] = returned[player];
                nodeUtil += returned * strategy[i]; 
            }
            for(int i=0; i<actions.size(); i++){
                regret = utilities[i] - nodeUtil[currentPlayer];
                mNodeMap[player].at(infoSet).regretSum[i] += regret;
            }  
        }

        return nodeUtil;

    }
    else{
        std::string infoSet = state.infoSet();
        auto search = mNodeMap[player].find(infoSet);
        if(search == mNodeMap[player].end()){
            mNodeMap[player].insert({infoSet, Node(state.mNumPlayers)});
        }
        // Node node = mNodeMap[player].at(infoSet);
        std::valarray<float> strategy = mNodeMap[player].at(infoSet).getStrategy();
        std::vector<std::string> actions = {"P", "B"};

        std::random_device rd;
        std::mt19937 gen(rd());
        std::discrete_distribution<int> random_choice(std::begin(strategy), std::end(strategy));
        auto action = random_choice(gen);
        return mccfr(State(state, actions[action]), player, prune);
    }
};

void Trainer::updateStrategy(State state, int player){
    if(state.isTerminal()){
        return;
    }
    int currentPlayer = state.mTurn;

    if(currentPlayer == player){
        std::string infoSet = state.infoSet();
        auto search = mNodeMap[player].find(infoSet);
        if(search == mNodeMap[player].end()){
            mNodeMap[player].insert({infoSet, Node(state.mNumPlayers)});
        }
        // Node node = mNodeMap[player].at(infoSet);
        std::valarray<float> strategy = mNodeMap[player].at(infoSet).getStrategy();
        std::vector<std::string> actions = {"P", "B"};

        std::random_device rd;
        std::mt19937 gen(rd());
        std::discrete_distribution<int> random_choice(std::begin(strategy), std::end(strategy));
        auto action = random_choice(gen);

        mNodeMap[player].at(infoSet).strategySum[action] += 1;
        updateStrategy(State(state, actions[action]), player);
    }
    else{
        std::vector<std::string> actions = {"P", "B"};
        for(int i=0; i<actions.size(); i++){
            updateStrategy(State(state, actions[i]), player);
        }
    }
}

std::valarray<float> Trainer::expectedUtility(){
    std::valarray<float> expectedUtility(2);

    std::sort(mCards.begin(), mCards.end());
    int numPermutations = 0;
    do{
        State state(2, 1, mCards);
        expectedUtility += traverseTree(state);
        numPermutations += 1;
    }while(std::next_permutation(mCards.begin(), mCards.end()));

    return expectedUtility/numPermutations;
};

std::valarray<float> Trainer::traverseTree(State state){
    if(state.isTerminal()){
        std::valarray<float> util = state.payoff();
        return util;
    }

    int player = state.mTurn;
    std::string infoSet = state.infoSet();
    std::valarray<float> strategy = mNodeMap[player].at(infoSet).getAverageStrategy();

    std::valarray<float> expectedUtility(state.mNumPlayers);

    std::vector<std::string> actions = {"P", "B"};
    for(int i=0; i<actions.size(); i++){
        expectedUtility += traverseTree(State(state, actions[i])) * strategy[i];
    }

    return expectedUtility;
}