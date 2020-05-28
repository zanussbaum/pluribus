#include <valarray>

class Node{
    public:
        Node(int numActions);
        ~Node();
        std::valarray<float> getAverageStrategy();
        std::valarray<float> getStrategy(float weight);
        std::valarray<float> regretSum;
        int mNumActions;

    private:
        std::valarray<float> strategySum;
        std::valarray<float> strategy;
};