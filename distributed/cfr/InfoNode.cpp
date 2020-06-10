#include "InfoNode.hpp"

InfoNode::InfoNode(std::vector<std::string> validActions){
    for(auto action: validActions){
        regretSum[action] = 0;
        strategySum[action] = 0;
        strategy[action] = 0;
    }
    mValidActions = validActions;
}

InfoNode::~InfoNode(){
};

std::unordered_map<std::string, double> InfoNode::getAverageStrategy(){
    float normSum = 0;
    std::unordered_map<std::string, double> avgStrategy;

    for(auto action: mValidActions){
        normSum += strategySum[action];
    }
    
    int numActions = mValidActions.size();
    for(auto action: mValidActions){
        if (normSum > 0){
            avgStrategy[action] = strategySum[action]/normSum;
        }
        else{
            avgStrategy[action] = 1.0/numActions;  
        }
        
    }

    return avgStrategy;
};

std::unordered_map<std::string, double> InfoNode::getStrategy(std::vector<std::string> validActions){
    float normSum = 0;

    for(auto action: validActions){
        strategy[action] = regretSum[action] > 0 ? regretSum[action]: 0;
        normSum += strategy[action];
    }

    int numActions = validActions.size();
    for(auto action: validActions){
        if (normSum > 0){
            strategy[action] /= normSum;
        }
        else{
            strategy[action] = 1.0/numActions;  
        }
    }

    return strategy;
};
    