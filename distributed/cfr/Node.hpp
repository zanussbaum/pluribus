#include <valarray>
#include <unordered_map>
#include <string>
#include <vector>

class Node{
    public:
        Node(int numActions);
        ~Node();
        std::valarray<float> getAverageStrategy();
        std::valarray<float> getStrategy(float weight);
        std::valarray<float> getStrategy();
        std::valarray<float> regretSum;
        std::valarray<float> strategySum;
        int mNumActions;

    private:
        std::valarray<float> strategy;
};