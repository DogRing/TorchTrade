#include "pch.h" // use pch.h in Visual Studio 2019
#include "MathLibrary.h"

void pred_period(const float per, const int d_len, bool ohlc, const int** x, int** y) {
	unsigned long target_p[2];
	int i, j;

	int high = ohlc ? 2 : 0;
	int low = ohlc ? 1 : 0;

	for (i = 0; i < d_len; i++) {
		target_p[0] = (unsigned long)(x[i][3] * (1 + per));
		target_p[1] = (unsigned long)(x[i][3] * (1 - per));

		for (j = i; j < d_len; j++) {
			if (target_p[0] < x[j][low]) {
				y[i][0] = j - i;
				break;
			}
			else if (target_p[1] > x[j][high]) {
				y[i][0] = i - j;
				break;
			}
		}
	}
}