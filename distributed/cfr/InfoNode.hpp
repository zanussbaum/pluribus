#include <valarray>
#include <unordered_map>
#include <string>
#include <vector>

class InfoNode{
    public:
        InfoNode(std::vector<std::string> validActions);
        ~InfoNode();

        std::unordered_map<std::string, double> getAverageStrategy();
        std::unordered_map<std::string, double> getStrategy(std::vector<std::string> validActions);

        std::unordered_map<std::string, double> regretSum;
        std::unordered_map<std::string, double> strategySum;

    private:
        std::unordered_map<std::string, double> strategy;
        std::vector<std::string> mValidActions;
};