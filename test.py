import transpiler

test_code = """
for i = 1 to n
    A[i] = i * 2
    
x = A[r]
i = p - 1
for j = p to r - 1
    if A[j] <= x
        i = i + 1
        k \u2190 A[i]
        A[i] <- A[j]
        A[j] = k
A[r] = A[i + 1]
"""

if __name__ == "__main__":
    print("--- Translating CLRS Code ---")
    print(test_code)
    print("--- Output Python Code ---")
    output = transpiler.translate(test_code)
    print(output)
