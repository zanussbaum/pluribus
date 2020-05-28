#include "Node.hpp"

Node::Node(int numActions){
    regretSum = std::valarray<float>(numActions);

    strategySum = std::valarray<float>(numActions);

    strategy = std::valarray<float>(numActions);

    mNumActions = numActions;
};

Node::~Node(){
};

std::valarray<float> Node::getAverageStrategy(){
    float normSum = 0;
    std::valarray<float> avgStrategy(mNumActions);

    for(int i=0; i < mNumActions; i++){
        normSum += strategySum[i];
    }

    for(int i=0; i < mNumActions; i++){
        if (normSum > 0){
            avgStrategy[i] = strategySum[i]/normSum;
        }
        else{
            avgStrategy[i] = 1.0/mNumActions;  
        }
        
    }

    return avgStrategy;
};

std::valarray<float> Node::getStrategy(float weight){
    float normSum = 0;

    for(int i=0; i < mNumActions; i++){
        strategy[i] = regretSum[i] > 0 ? regretSum[i]: 0;
        normSum += strategy[i];
    }

    for(int i=0; i < mNumActions; i++){
        if (normSum > 0){
            strategy[i] /= normSum;
        }
        else{
            strategy[i] = 1.0/mNumActions;  
        }
        strategySum[i] += strategy[i] * weight;
    }

    return strategy;
};
    