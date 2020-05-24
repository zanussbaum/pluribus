#include <string>
#include <unordered_map>
#include <algorithm>
#include <random>
#include "Node.hpp"
#include "State.hpp"

class Trainer{
    public:
        Trainer();
        ~Trainer();
        void train(int iterations);
        std::vector<int> mCards;
        std::unordered_map<int, std::unordered_map<std::string, Node>> mNodeMap;

    private:
        Eigen::RowVectorXf cfr(State state, std::vector<double> probs);
};