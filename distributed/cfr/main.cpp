#include <iostream>
#include <valarray>
#include "Trainer.hpp"

int main(){
    std::cout << "Running Vanilla CFR";

    Trainer train;
    auto t1 = std::chrono::high_resolution_clock::now();
    train.train(10000);
    auto t2 = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>( t2 - t1 ).count();
    std::cout <<"duration "<< duration/pow(10, 6) <<"\n";

    for(auto map: train.mNodeMap){
        std::cout << "\nplayer " << map.first << "\n";
        for(auto infoSet: map.second){
            auto strat = infoSet.second.getAverageStrategy();
            std::cout << "\n" + infoSet.first + "\n";
            for(auto prob: strat){
                std::cout << prob << "\t";
            }
        }
    }
    std::valarray<float> expectedUtility = train.expectedUtility();

    for(int i=0; i<expectedUtility.size(); i++){
        std::cout << "\nPlayer " << i << " utility \n";
        std::cout << expectedUtility[i] << "\n";
    }
    std::cout <<"duration "<< duration/pow(10, 6) <<"\n";

    std::cout << "\nRunning MCCFR";
    
    Trainer train2(2);
    t1 = std::chrono::high_resolution_clock::now();
    train2.mccfrTrain(10000);
    t2 = std::chrono::high_resolution_clock::now();
    duration = std::chrono::duration_cast<std::chrono::microseconds>( t2 - t1 ).count();
    

    for(auto map: train2.mNodeMap){
        std::cout << "\nplayer " << map.first << "\n";
        for(auto infoSet: map.second){
            auto strat = infoSet.second.getAverageStrategy();
            std::cout << "\n" + infoSet.first + "\n";
            for(auto prob: strat){
                std::cout << prob << "\t";
            }
        }
    }
    expectedUtility = train2.expectedUtility();

    for(int i=0; i<expectedUtility.size(); i++){
        std::cout << "\nPlayer " << i << " utility \n";
        std::cout << expectedUtility[i] << "\n";
    }

    std::cout <<"duration "<< duration/pow(10, 6) <<"\n";


    return 0;
}