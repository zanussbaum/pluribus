#include "State.hpp"


State::State(int numPlayers, int numRounds, std::vector<int> cards, int numRaises): mTurn(0), mRound(0), mRaisesSoFar(0){
    mNumPlayers = numPlayers;
    mCards = cards;
    mBets.assign(numPlayers, 1);
    mTotalRounds = numRounds; 
    mRaises = numRaises;

    for(int i=0; i< numRounds; i++){
        mHistory.push_back(std::vector<std::string>());
    }
    
    mIn.assign(numPlayers, true);
};

State::State(const State &state, std::string action, bool search): mTurn(state.mTurn), mCards(state.mCards),
    mRound(state.mRound), mBets(state.mBets), mNumPlayers(state.mNumPlayers),
    mHistory(state.mHistory), mIn(state.mIn), mTotalRounds(state.mTotalRounds), 
    mRaises(state.mRaises), mRaisesSoFar(state.mRaisesSoFar){
        std::string lastAction = "EMPTY";
        if(!mHistory[mRound].empty()){
            lastAction = mHistory[mRound].back();
        }
        
        mHistory[mRound].push_back(action);

        if(action == "F"){
            mIn[mTurn] = false;
        }
        else if (action.find("R") != std::string::npos){
            int raiseSize = std::stoi(action.substr(0, action.size()-1));
            mBets[mTurn] += *std::max_element(mBets.begin(), mBets.end()) + raiseSize;
            mRaisesSoFar++;
        }
        else if(action == "C"){
            if(lastAction.find("R") != std::string::npos){
                int callSize = *std::max_element(mBets.begin(), mBets.end()) - mBets[mTurn];
                mBets[mTurn] += callSize;
            }
        }

        mTurn = (mTurn + 1) % mNumPlayers;

        int minActions = std::count(mIn.begin(), mIn.end(), true);
        int actionsInRound = mHistory[mRound].size();

        if(minActions <= actionsInRound and allCalledOrFolded()){
            mRound += 1;
            mRaisesSoFar = 0;
        }
}

State::~State(){
};

std::string State::infoSet(){
    int player = mTurn;
    int card = mCards[player];

    std::string infoSet = std::to_string(card) + " | ";

    if(mRound > 0){
        infoSet += std::to_string(mCards[mNumPlayers]) + " | ";
    } 
    for(const auto &chunk: mHistory){
        for(const auto &piece: chunk){
            infoSet += piece;
        }
        infoSet += "|";
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

std::valarray<float> State::payoff(){
    std::vector<int> winners;
    int playersIn = std::count(mIn.begin(), mIn.end(), true);
    if(playersIn == 1){
        std::vector<bool>::iterator found = std::find(mIn.begin(), mIn.end(), true);
        try{
            if(found != mIn.end()){
                int winner = found - mIn.begin();
                winners.push_back(winner);
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
        winners = State::winners();
    }

    int pot = std::accumulate(mBets.begin(), mBets.end(), 0)/winners.size();

    std::valarray<float> payoffs(mNumPlayers);
    for(int i=0; i<mBets.size(); i++){
        payoffs[i] = -mBets[i];
    }

    for(auto win: winners){
        payoffs[win] += pot;
    }
    

    return payoffs;
};

std::vector<int> State::winners(){
    std::vector<int> scores;
    int boardCard = mCards[mNumPlayers];
    for(int player=0; player<mNumPlayers; player++){
        if(mCards[player] == boardCard){
            int score = 5*4 + boardCard;
            scores.push_back(score);
        }
        else{
            int score = 4 * std::max(boardCard, mCards[player]) + std::min(boardCard, mCards[player]);
            scores.push_back(score);
        }
    }

    std::vector<int> winners;
    int high = -1;
    for(int i=0; i<scores.size();i++){
        if(winners.size() == 0 || scores[i] > high){
            winners = {i};
            high = scores[i];
        }
        else if(scores[i] == high){
            winners.push_back(i);
        } 
    }

    return winners;
}

std::vector<std::string> State::validActions(){
    std::vector<std::string> actions;
    actions.push_back("C");
    actions.push_back("F");
    if(mRaisesSoFar < mRaises){
        int raiseSize = mRound == 0 ? 2 : 4;
        actions.push_back(std::to_string(raiseSize) + "R");
    }
    return actions;
}
