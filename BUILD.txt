README - Custom Language Interpreter (Stages 1–4)

This interpreter was built in Python and implements a simple, dynamically typed language with support for arithmetic, boolean logic, string manipulation, and global variables.

✔ Stage 1: Arithmetic Expressions
- Supports +, -, *, / and parentheses
- Handles unary negation (e.g., -5)
- Example: (10 * 2) / (3 + 2)

✔ Stage 2: Boolean Logic
- Supports ==, !=, <, >, <=, >=
- Boolean operators: and, or, not
- Example: true and (5 > 3)

✔ Stage 3: String Handling
- Supports string literals with quotes
- Concatenation: "hello" + "world"
- Comparison: "foo" == "foo"

✔ Stage 4: Global Variables and Print
- Allows assigning and reusing variables
- Variables persist across multiple lines
- Built-in `print` command
- Example:
    x = 5
    x = x + 2
    print x

Stage 5 (if, while, input) is not implemented.

Files:
- Interpreter.py → main source code
- demo_stage1.txt → arithmetic examples
- demo_stage2.txt → boolean logic examples
- demo_stage3.txt → string handling examples
- demo_stage4.txt → variable and print examples

To run
-python Interpreter.py demo_stage4.txt, -python Interpreter.py demo_stage3.txt, python Interpreter.py demo_stage2.txt, python Interpreter.py demo_stage1.txt
