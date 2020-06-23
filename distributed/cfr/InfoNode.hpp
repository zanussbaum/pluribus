#include <valarray>
#include <unordered_map>
#include <string>
#include <vector>
#include <boost/serialization/serialization.hpp>
#include <boost/serialization/unordered_map.hpp>
#include <boost/serialization/string.hpp>
#include <set>

class InfoNode{
    public:
        friend class boost::serialization::access;
        InfoNode();
        InfoNode(std::set<std::string> validActions);
        ~InfoNode();

        std::unordered_map<std::string, double> getAverageStrategy();
        std::unordered_map<std::string, double> getStrategy(std::set<std::string> validActions);

        std::unordered_map<std::string, double> regretSum;
        std::unordered_map<std::string, double> strategySum;

        template<class Archive>
        void serialize(Archive & ar, const unsigned int version){
            ar & regretSum;
            ar & strategySum;
        };

    private:
        std::unordered_map<std::string, double> strategy;
        std::set<std::string> mValidActions;
};