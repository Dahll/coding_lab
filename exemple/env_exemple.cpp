#include <iostream>
#include <cstdlib>


int main()
{
    int min = 1;
    int max = 10;
    int max_turn = 5;

    std::cout << min << std::endl;
    std::cout << max << std::endl;
    std::cout << max_turn << std::endl;


    int actual_turn = 0;
    int solution = rand() % (max - min) + min;
    int player_move = -1;

    // Send state
    std::cout << actual_turn << std::endl;
    // Send game result
    std::cout << "pending" << std::endl;

    while ( (actual_turn != max_turn))
    {
        //Get player move
        std::cin >> player_move;
        actual_turn += 1;

        if (player_move == solution)
        {
            std::cout << actual_turn << std::endl;
            std::cout << "win" << std::endl;
            return 0;
        }
    }
    std::cout << actual_turn << std::endl;
    std::cout << "loose" << std::endl;
    return 1;
}
