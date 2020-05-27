#include "Node.hpp"

Node::Node(int numActions){
    regretSum.resize(numActions);
    regretSum.setZero();

    strategySum.resize(numActions);
    strategySum.setZero();

    strategy.resize(numActions);
    strategy.setZero();

    mNumActions = numActions;
};

Node::~Node(){
};

Eigen::RowVectorXf Node::getAverageStrategy(){
    float normSum = 0;
    Eigen::RowVectorXf avgStrategy(mNumActions);
    avgStrategy.setZero();

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

Eigen::RowVectorXf Node::getStrategy(float weight){
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
    