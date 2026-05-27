#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int PARTITION(vector<int>& A, int p, int r) {
    int x = A[r - 1];
    int i = (p - 1);

    for (int j = p; j <= (r - 1); ++j) {
        if (A[j - 1] <= x) {
            i = (i + 1);
            swap(A[i - 1], A[j - 1]);
        }
    }

    swap(A[(i + 1) - 1], A[r - 1]);
    return (i + 1);
}

void QUICKSORT(vector<int>& A, int p, int r) {
    if (p < r) {
        int q = PARTITION(A, p, r);
        QUICKSORT(A, p, (q - 1));
        QUICKSORT(A, (q + 1), r);
    }
}

int main() {
    vector<int> A = {10, 7, 8, 9, 1, 5};

    // same note: p = 1, r = size
    QUICKSORT(A, 1, A.size());

    cout << "Sorted array: ";
    for (int x : A) {
        cout << x << " ";
    }
    cout << endl;

    return 0;
}