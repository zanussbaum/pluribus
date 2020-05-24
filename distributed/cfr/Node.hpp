#include <vector>
#include <eigen3/Eigen/Core>

class Node{
    public:
        Node(int numActions);
        ~Node();
        Eigen::RowVectorXf getAverageStrategy();
        Eigen::RowVectorXf getStrategy(float weight);
        Eigen::RowVectorXf regretSum;
        int mNumActions;

    private:
        
        Eigen::RowVectorXf strategySum;
        Eigen::RowVectorXf strategy;
};