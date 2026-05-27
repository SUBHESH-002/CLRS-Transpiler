import sys
sys.path.append("o:/PROJECTS/Transpiler/v2")
import transpiler

code = """
for i = 1 to 10
    print(i)
end
"""

try:
    print("Python Translation:")
    print(transpiler.translate(code, "Python"))
    print("\nC++ Translation:")
    print(transpiler.translate(code, "C++"))
    print("\nTest Passed!")
except Exception as e:
    print("Error:", e)
