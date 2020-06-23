#include <iostream>
#include <valarray>
#include <fstream>
#include <filesystem>
#include "Pluribus.hpp"
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>


int main(){
    std::cout << "Running Pluribus\n";
    Pluribus train(2);
    if(!std::filesystem::exists("blueprint")){
         auto t1 = std::chrono::high_resolution_clock::now();
        train.train(1000);
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

        std::ofstream ofs("blueprint");
        boost::archive::text_oarchive oa(ofs);
        oa << train;
    }
    else{
        std::ifstream ifs("blueprint");
        boost::archive::text_iarchive ia(ifs);
        ia >> train;
        std::cout << "loaded blueprint";
    } 
   
    return 0;
}