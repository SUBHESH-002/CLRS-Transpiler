def QUICKSORT(A, p, r):
    if (p < r):
        q = PARTITION(A, p, r)
        QUICKSORT(A, p, (q - 1))
        QUICKSORT(A, (q + 1), r)

def PARTITION(A, p, r):
    x = A[r - 1]
    i = (p - 1)
    for j in range(p, ((r - 1)) + 1):
        if (A[j - 1] <= x):
            i = (i + 1)
            A[i - 1], A[j - 1] = A[j - 1], A[i - 1]
    A[(i + 1) - 1], A[r - 1] = A[r - 1], A[(i + 1) - 1]
    return (i + 1)

# Example run
A = [10, 7, 8, 9, 1, 5]

# NOTE: p = 1, r = length (because of your indexing style)
QUICKSORT(A, 1, len(A))

print("Sorted array:", A)