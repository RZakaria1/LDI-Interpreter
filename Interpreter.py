import sys

# Token types
(
    NUMBER, BOOL, PLUS, MINUS, STAR, SLASH, 
    LPAREN, RPAREN, EQEQ, NEQ, LT, GT, LTE, GTE,
    AND, OR, NOT, EOF
) = (
    'NUMBER', 'BOOL', 'PLUS', 'MINUS', 'STAR', 'SLASH',
    'LPAREN', 'RPAREN', 'EQEQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE',
    'AND', 'OR', 'NOT', 'EOF'
)

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)})'

# Lexer
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def match(self, string):
        return self.text[self.pos:self.pos + len(string)] == string

    def identifier(self):
        result = ''
        while self.current_char and (self.current_char.isalpha() or self.current_char.isdigit()):
            result += self.current_char
            self.advance()
        if result.lower() == 'true':
            return Token(BOOL, True)
        elif result.lower() == 'false':
            return Token(BOOL, False)
        elif result.lower() == 'and':
            return Token(AND)
        elif result.lower() == 'or':
            return Token(OR)
        elif result.lower() == 'not':
            return Token(NOT)
        else:
            raise Exception(f'Unknown identifier: {result}')

    def number(self):
        num_str = ''
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            num_str += self.current_char
            self.advance()
        return Token(NUMBER, float(num_str))

    def get_next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.number()
            if self.current_char.isalpha():
                return self.identifier()

            if self.match('=='):
                self.advance(); self.advance()
                return Token(EQEQ)
            if self.match('!='):
                self.advance(); self.advance()
                return Token(NEQ)
            if self.match('<='):
                self.advance(); self.advance()
                return Token(LTE)
            if self.match('>='):
                self.advance(); self.advance()
                return Token(GTE)

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

            raise Exception(f'Invalid character: {self.current_char}')
        return Token(EOF)

# AST nodes
class Num:
    def __init__(self, token): self.value = token.value

class Bool:
    def __init__(self, token): self.value = token.value

class BinOp:
    def __init__(self, left, op, right): self.left = left; self.op = op; self.right = right

class UnaryOp:
    def __init__(self, op, expr): self.op = op; self.expr = expr

# Parser
class Parser:
    def __init__(self, lexer): self.lexer = lexer; self.current_token = lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f'Expected {token_type}, got {self.current_token.type}')

    def factor(self):
        token = self.current_token
        if token.type == NUMBER:
            self.eat(NUMBER); return Num(token)
        elif token.type == BOOL:
            self.eat(BOOL); return Bool(token)
        elif token.type == MINUS:
            self.eat(MINUS); return UnaryOp(token, self.factor())
        elif token.type == NOT:
            self.eat(NOT); return UnaryOp(token, self.factor())
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        raise Exception("Invalid factor")

    def term(self):
        node = self.factor()
        while self.current_token.type in (STAR, SLASH):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.factor())
        return node

    def arith_expr(self):
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.term())
        return node

    def comparison_expr(self):
        node = self.arith_expr()
        while self.current_token.type in (EQEQ, NEQ, LT, GT, LTE, GTE):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.arith_expr())
        return node

    def logical_expr(self):
        node = self.comparison_expr()
        while self.current_token.type in (AND, OR):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.comparison_expr())
        return node

    def expr(self):
        return self.logical_expr()

# Interpreter
class Interpreter:
    def visit(self, node):
        if isinstance(node, Num): return node.value
        elif isinstance(node, Bool): return node.value
        elif isinstance(node, UnaryOp):
            val = self.visit(node.expr)
            if node.op.type == MINUS: return -val
            if node.op.type == NOT: return not val
        elif isinstance(node, BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            if node.op.type == PLUS: return left + right
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
        raise Exception(f'Unknown node: {node}')

# Run file
def main(filename):
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            if not line.strip(): continue
            lexer = Lexer(line)
            parser = Parser(lexer)
            tree = parser.expr()
            result = Interpreter().visit(tree)
            print(f"{line.strip()} = {result}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python Interpreter.py <source_file>")
    else:
        main(sys.argv[1])
