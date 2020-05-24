#include "State.hpp"


State::State(int numPlayers, int numRounds, std::vector<int> cards): mTurn(0), mRound(0){
    mNumPlayers = numPlayers;
    mCards = cards;
    mBets.assign(numPlayers, 1);
    mTotalRounds = numRounds; 

    mHistory.push_back(std::vector<std::string>());
    mIn.assign(numPlayers, true);
};

State::State(const State &state, std::string action): mTurn(state.mTurn), mCards(state.mCards),
    mRound(state.mRound), mBets(state.mBets), mNumPlayers(state.mNumPlayers),
    mHistory(state.mHistory), mIn(state.mIn), mTotalRounds(state.mTotalRounds){
        std::string lastAction;
        if(!mHistory[mRound].empty()){
            lastAction = mHistory[mRound].back();
        }
        
        mHistory[mRound].push_back(action);

        
        if(action == "P"){
            if(lastAction == "B"){
                mIn[mTurn] = false;
            }
 
        }
        else if (action == "B"){
            mBets[mTurn] += 1;
        }

        mTurn = (mTurn + 1) % mNumPlayers;

        int minActions = std::count(mIn.begin(), mIn.end(), true);
        int actionsInRound = mHistory[mRound].size();

        if(minActions <= actionsInRound and allCalledOrFolded()){
            mRound += 1;
        }
}

State::~State(){
};

std::string State::infoSet(){
    int player = mTurn;
    int card = mCards[player];

    std::string infoSet = std::to_string(card) + " | ";

    for(const auto &chunk: mHistory){
        for(const auto &piece: chunk){
            infoSet += piece;
        }
        
    } 

    return infoSet;
};

bool State::isTerminal(){
    int playersIn = std::count(mIn.begin(), mIn.end(), true);
    if(playersIn == 1){
        return true;
    }

    else if(mRound < mTotalRounds){
        return false;
    }
    else{
        int minActions = playersIn;
        int actionsInRound = mHistory.back().size();

        if(minActions <= actionsInRound and allCalledOrFolded()){
            return true;
        }
        return false;
    }
};

bool State::allCalledOrFolded(){
    int maxBet = *std::max_element(mBets.begin(), mBets.end());

    for(int i=0; i< mIn.size(); i++){
        if(mIn[i] and mBets[i] < maxBet){
            return false;
        }
    }

    return true;
};

Eigen::RowVectorXf State::payoff(){
    int winner;
    int playersIn = std::count(mIn.begin(), mIn.end(), true);
    if(playersIn == 1){
        std::vector<bool>::iterator found = std::find(mIn.begin(), mIn.end(), true);
        try{
            if(found != mIn.end()){
                winner = found- mIn.begin();
            }
            else{
                throw std::logic_error("didn't find winner");
            }
        }
        
        catch(std::exception &ex){
            std::cout << "Something weird happened";
        }
    }
    else{
        try{
            auto found = std::distance(mCards.begin(),
                                    std::max_element(mCards.begin(), mCards.end()-1));
            if(found < 0){
                throw std::logic_error("didn't find winner");
            }
            winner = found;
        }
        catch(std::exception &ex){
            std::cout << "Something weird happened";
        }
        
    }

    int pot = std::accumulate(mBets.begin(), mBets.end(), 0);

    Eigen::VectorXf payoffs;
    payoffs.resize(mNumPlayers);
    for(int i=0; i<mBets.size(); i++){
        payoffs(i) = -mBets[i];
    }

    payoffs(winner) += pot;

    return payoffs;
};