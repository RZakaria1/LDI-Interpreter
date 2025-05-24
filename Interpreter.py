import sys

# Token types used throughout the lexer and parser.
(
    NUMBER, BOOL, STRING, IDENTIFIER,  # Data types and variables
    PLUS, MINUS, STAR, SLASH,          # Arithmetic operators
    EQEQ, NEQ, LT, GT, LTE, GTE,       # Comparison operators
    AND, OR, NOT, ASSIGN, PRINT,       # Logical operators, assignment, print
    LPAREN, RPAREN,                    # Brackets for grouping
    EOF                                # End of file/input marker
) = (
    'NUMBER', 'BOOL', 'STRING', 'IDENTIFIER',
    'PLUS', 'MINUS', 'STAR', 'SLASH',
    'EQEQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE',
    'AND', 'OR', 'NOT', 'ASSIGN', 'PRINT',
    'LPAREN', 'RPAREN',
    'EOF'
)

# Token class to represent each token with a type and optional value
class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)})'

# Lexer class: converts raw input string into a sequence of tokens
class Lexer:
    def __init__(self, text):
        self.text = text                    # Full input program as text
        self.pos = 0                        # Current position in text
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        # Move one character forward in the input
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        # Skip spaces, tabs, and newlines
        while self.current_char and self.current_char.isspace():
            self.advance()

    def match(self, string):
        # Check if upcoming characters match a specific string (used for operators like ==)
        return self.text[self.pos:self.pos + len(string)] == string

    def string(self):
        # Parse a string literal wrapped in double quotes
        result = ''
        self.advance()  # Skip opening quote
        while self.current_char and self.current_char != '"':
            result += self.current_char
            self.advance()
        self.advance()  # Skip closing quote
        return Token(STRING, result)

    def identifier(self):
        # Parse variable names and keywords (like true, false, and, or, print)
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        result_lower = result.lower()
        # Return appropriate keyword token or identifier
        if result_lower == 'true':
            return Token(BOOL, True)
        elif result_lower == 'false':
            return Token(BOOL, False)
        elif result_lower == 'and':
            return Token(AND)
        elif result_lower == 'or':
            return Token(OR)
        elif result_lower == 'not':
            return Token(NOT)
        elif result_lower == 'print':
            return Token(PRINT)
        else:
            return Token(IDENTIFIER, result)

    def number(self):
        # Parse a number literal (integer or float)
        num_str = ''
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            num_str += self.current_char
            self.advance()
        return Token(NUMBER, float(num_str))

    def get_next_token(self):
        # Main method: returns the next token from input
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # Handle string literals
            if self.current_char == '"':
                return self.string()

            # Handle numbers
            if self.current_char.isdigit():
                return self.number()

            # Handle variable names and keywords
            if self.current_char.isalpha():
                return self.identifier()

            # Handle comparison operators (==, !=, <=, >=)
            if self.match('=='):
                self.advance(); self.advance(); return Token(EQEQ)
            if self.match('!='):
                self.advance(); self.advance(); return Token(NEQ)
            if self.match('<='):
                self.advance(); self.advance(); return Token(LTE)
            if self.match('>='):
                self.advance(); self.advance(); return Token(GTE)

            # Handle single-character tokens
            if self.current_char == '=':
                self.advance(); return Token(ASSIGN)
            if self.current_char == '+':
                self.advance(); return Token(PLUS)
            if self.current_char == '-':
                self.advance(); return Token(MINUS)
            if self.current_char == '*':
                self.advance(); return Token(STAR)
            if self.current_char == '/':
                self.advance(); return Token(SLASH)
            if self.current_char == '(':
                self.advance(); return Token(LPAREN)
            if self.current_char == ')':
                self.advance(); return Token(RPAREN)
            if self.current_char == '<':
                self.advance(); return Token(LT)
            if self.current_char == '>':
                self.advance(); return Token(GT)

            # Raise error for anything unrecognized
            raise Exception(f'Invalid character: {self.current_char}')
        
        # Return end-of-file token when no characters are left
        return Token(EOF)


# AST nodes
class Num:
    def __init__(self, token):
        self.value = token.value

class Bool:
    def __init__(self, token):
        self.value = token.value

class Str:
    def __init__(self, token):
        self.value = token.value

class Var:
    def __init__(self, token):
        self.name = token.value

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Assign:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class Print:
    def __init__(self, expr):
        self.expr = expr

# The Parser takes tokens from the lexer and builds the AST

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()  # Start with the first token

    def eat(self, token_type):
        # Consume the current token if it matches the expected type
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f'Expected {token_type}, got {self.current_token.type}')

    def factor(self):
        # Handles literals, variables, unary operations, and parentheses
        token = self.current_token
        if token.type == NUMBER:
            self.eat(NUMBER)
            return Num(token)
        elif token.type == BOOL:
            self.eat(BOOL)
            return Bool(token)
        elif token.type == STRING:
            self.eat(STRING)
            return Str(token)
        elif token.type == IDENTIFIER:
            self.eat(IDENTIFIER)
            return Var(token)
        elif token.type == MINUS:
            self.eat(MINUS)
            return UnaryOp(token, self.factor())
        elif token.type == NOT:
            self.eat(NOT)
            return UnaryOp(token, self.factor())
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        raise Exception("Invalid factor")

    def term(self):
        # Handles multiplication and division
        node = self.factor()
        while self.current_token.type in (STAR, SLASH):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.factor())
        return node

    def arith_expr(self):
        # Handles addition and subtraction
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.term())
        return node

    def comparison_expr(self):
        # Handles comparison operators (==, !=, <, >, <=, >=)
        node = self.arith_expr()
        while self.current_token.type in (EQEQ, NEQ, LT, GT, LTE, GTE):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.arith_expr())
        return node

    def logical_expr(self):
        # Handles logical operators (and, or)
        node = self.comparison_expr()
        while self.current_token.type in (AND, OR):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.comparison_expr())
        return node

    def statement(self):
        # Handles assignment and print, or an expression
        if self.current_token.type == IDENTIFIER:
            var_token = self.current_token
            self.eat(IDENTIFIER)
            self.eat(ASSIGN)
            expr = self.expr()
            return Assign(var_token.value, expr)
        elif self.current_token.type == PRINT:
            self.eat(PRINT)
            expr = self.expr()
            return Print(expr)
        else:
            return self.expr()

    def expr(self):
        # Start parsing from logical expressions
        return self.logical_expr()


# Interpreter class: walks the AST and executes code
class Interpreter:
    def __init__(self):
        self.env = {}  # Variable environment (a dictionary to store variable values)

    def visit(self, node):
        # Handle literal values
        if isinstance(node, Num): return node.value
        if isinstance(node, Bool): return node.value
        if isinstance(node, Str): return node.value

        # Handle variable access
        if isinstance(node, Var):
            if node.name not in self.env:
                raise Exception(f'Undefined variable: {node.name}')
            return self.env[node.name]

        # Handle unary operations (e.g., -x, not x)
        if isinstance(node, UnaryOp):
            val = self.visit(node.expr)
            if node.op.type == MINUS:
                return -val
            if node.op.type == NOT:
                return not val

        # Handle binary operations (e.g., +, -, ==, <, and)
        if isinstance(node, BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            if node.op.type == PLUS:
                # Supports string concatenation as well
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            if node.op.type == MINUS: return left - right
            if node.op.type == STAR: return left * right
            if node.op.type == SLASH: return left / right
            if node.op.type == EQEQ: return left == right
            if node.op.type == NEQ: return left != right
            if node.op.type == LT: return left < right
            if node.op.type == GT: return left > right
            if node.op.type == LTE: return left <= right
            if node.op.type == GTE: return left >= right
            if node.op.type == AND: return left and right
            if node.op.type == OR: return left or right

        # Handle variable assignment (e.g., x = 5)
        if isinstance(node, Assign):
            value = self.visit(node.expr)        # Evaluate the expression on the right-hand side
            self.env[node.name] = value          # Store it in the environment
            return None

        # Handle print statement
        if isinstance(node, Print):
            value = self.visit(node.expr)        # Evaluate the expression
            print(value)                         # Output the result
            return None

        # Handle unknown node types
        raise Exception(f'Unknown node: {node}')


# Entry point to run a program from a file
def main(filename):
    interpreter = Interpreter()  # Create an interpreter instance

    with open(filename) as f:
        lines = f.readlines()  # Read all lines from the file

        for line in lines:
            if not line.strip(): continue  # Skip empty lines

            lexer = Lexer(line)            # Turn line into tokens
            parser = Parser(lexer)         # Parse tokens into an AST
            tree = parser.statement()      # Get the statement node
            interpreter.visit(tree)        # Evaluate the AST

# Main block to handle command-line arguments
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python Interpreter.py <source_file>")
    else:
        main(sys.argv[1])

