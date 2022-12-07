// C++ Code generated from Python Code: 
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <cmath>
#include <cassert>

using namespace std;

double predict(double CRIM, double ZN, double INDUS, double CHAS, double NOX, double RM, double AGE, double DIS, double RAD, double TAX, double PTRATIO, double B, double LSTAT) {
    if (RM <= 6.94) {
        if (LSTAT <= 14.4) {
            if (DIS <= 1.38) {
                return 45.58;
            } else {  // if DIS > 1.38
                return 22.9052;
            }
        } else {  // if LSTAT > 14.4
            if (CRIM <= 6.99) {
                return 17.1376;
            } else {  // if CRIM > 6.99
                return 11.9784;
            }
        }
    } else {  // if RM > 6.94
        if (RM <= 7.44) {
            if (NOX <= 0.66) {
                return 33.3488;
            } else {  // if NOX > 0.66
                return 14.4;
            }
        } else {  // if RM > 7.44
            if (PTRATIO <= 19.65) {
                return 45.8966;
            } else {  // if PTRATIO > 19.65
                return 21.9;
            }
        }
    }
}

int main() {
    cout << "Done" << endl;
    return 0;
}