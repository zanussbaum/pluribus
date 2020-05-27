#include "Trainer.hpp"


Trainer::Trainer(){
    mCards = {1,2,3};
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

Eigen::RowVectorXf Trainer::cfr(State state, std::vector<double> probs){
    if(state.isTerminal()){
        Eigen::VectorXf util = state.payoff();
        return util;
    }

    int player = state.mTurn;
    std::string infoSet = state.infoSet();
    
    auto search = mNodeMap[player].find(infoSet);
    if(search == mNodeMap[player].end()){
        mNodeMap[player].insert({infoSet, Node(2)});
    }

    Eigen::RowVectorXf strategy = mNodeMap[player].at(infoSet).getStrategy(probs[player]);

    Eigen::RowVectorXf utilities(state.mNumPlayers);
    utilities.setZero();

    Eigen::RowVectorXf nodeUtil(state.mNumPlayers);
    nodeUtil.setZero();

    std::vector<std::string> actions = {"P", "B"};
    Eigen::RowVectorXf returned;
    returned.setZero();
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
    float regret;
    for(int i=0; i<actions.size(); i++){
        regret = utilities[i] - nodeUtil[player];
        mNodeMap[player].at(infoSet).regretSum[i] += regret * opponentProb;
    }


    return nodeUtil;
};

Eigen::RowVectorXf Trainer::expectedUtility(){
    Eigen::RowVectorXf expectedUtility(2);
    expectedUtility.setZero();
    std::sort(mCards.begin(), mCards.end());
    int numPermutations = 0;
    do{
        State state(2, 1, mCards);
        expectedUtility += traverseTree(state);
        numPermutations += 1;
    }while(std::next_permutation(mCards.begin(), mCards.end()));

    return expectedUtility/numPermutations;
};

Eigen::RowVectorXf Trainer::traverseTree(State state){
    if(state.isTerminal()){
        Eigen::VectorXf util = state.payoff();
        return util;
    }

    int player = state.mTurn;
    std::string infoSet = state.infoSet();
    Eigen::RowVectorXf strategy = mNodeMap[player].at(infoSet).getAverageStrategy();

    Eigen::RowVectorXf expectedUtility(state.mNumPlayers);
    expectedUtility.setZero();

    std::vector<std::string> actions = {"P", "B"};
    for(int i=0; i<actions.size(); i++){
        expectedUtility += traverseTree(State(state, actions[i])) * strategy[i];
    }

    return expectedUtility;
}