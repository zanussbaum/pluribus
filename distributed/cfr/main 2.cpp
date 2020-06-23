#include <iostream>
#include <valarray>
#include "MCCFRTrainer.hpp"

int main(){
    std::cout << "Running MCCFR on Leduc HoldEm";

    MCCFRTrainer train(2);
    auto t1 = std::chrono::high_resolution_clock::now();
    train.train(100000);
    auto t2 = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>( t2 - t1 ).count();
    

    for(auto map: train.mNodeMap){
        std::cout << "\nplayer " << map.first << "\n";
        for(auto infoSet: map.second){
            auto strat = infoSet.second.getAverageStrategy();
            std::cout << "\n" + infoSet.first + "\n";
            for(auto prob: strat){
                std::cout << prob.first << "\t";
                std::cout << prob.second << "\n";
            }
        }
    }
    std::valarray<float> expectedUtility = train.expectedUtility();

    for(int i=0; i<expectedUtility.size(); i++){
        std::cout << "\nPlayer " << i << " utility \n";
        std::cout << expectedUtility[i] << "\n";
    }

    std::cout <<"duration "<< duration/pow(10, 6) <<"\n";


    return 0;
}