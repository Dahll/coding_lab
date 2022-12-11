#include <iostream>
#include <cstdlib>
#include <set>

int main()
{

    int max;
    int min;
    int max_turn;
    int actual_turn;

    std::cin >> min >> max >> max_turn;
    
    while (true)
    {
        std::cin >> actual_turn;
    
        while (true)
        {
            int move = rand() % (max - min) + min;
    
            std::set<int> histo {};
            if(histo.find(move) == histo.end())
            {
                histo.insert(move);
                std::cout << move << std::endl;
                break;
            }
        }
    }
    
    return 0;
}
