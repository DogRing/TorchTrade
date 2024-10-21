#include <stdio.h>

void pred_period(const float per, const int len, int*x, int*y)
{
    unsigned long upper,lower;
    for (int i=0;i<len;i++){
        upper = (unsigned long)(x[i] * (1+per));
        lower = (unsigned long)(x[i] * (1-per));

        for (int j=i;j<len;j++){
            if (upper < x[j]){
                y[i] = j-i;
                break;
            }
            else if (lower > x[j]){
                y[i] = i-j;
                break;
            }
        }
    }
}