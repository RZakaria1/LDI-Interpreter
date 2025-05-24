import sys
import re

# Token types
NUMBER, PLUS, MINUS, STAR, SLASH, LPAREN, RPAREN, EOF = (
    'NUMBER', 'PLUS', 'MINUS', 'STAR', 'SLASH', 'LPAREN', 'RPAREN', 'EOF'
)

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

# Lexer
class Lexer:
    def __init__(self, text):
        self.text = text.replace('\n', '')
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

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
            if self.current_char.isdigit() or self.current_char == '.':
                return self.number()
            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')
            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')
            if self.current_char == '*':
                self.advance()
                return Token(STAR, '*')
            if self.current_char == '/':
                self.advance()
                return Token(SLASH, '/')
            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')
            raise Exception(f'Invalid character: {self.current_char}')
        return Token(EOF)

# AST nodes
class Num:
    def __init__(self, token):
        self.value = token.value

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

# Parser (Recursive Descent)
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()
    
    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        token = self.current_token
        if token.type == NUMBER:
            self.eat(NUMBER)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            return BinOp(Num(Token(NUMBER, 0)), Token(MINUS, '-'), self.factor())
        else:
            self.error()

    def term(self):
        node = self.factor()
        while self.current_token.type in (STAR, SLASH):
            token = self.current_token
            if token.type == STAR:
                self.eat(STAR)
            elif token.type == SLASH:
                self.eat(SLASH)
            node = BinOp(node, token, self.factor())
        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)
            node = BinOp(node, token, self.term())
        return node

# Interpreter
class Interpreter:
    def visit(self, node):
        if isinstance(node, Num):
            return node.value
        elif isinstance(node, BinOp):
            if node.op.type == PLUS:
                return self.visit(node.left) + self.visit(node.right)
            elif node.op.type == MINUS:
                return self.visit(node.left) - self.visit(node.right)
            elif node.op.type == STAR:
                return self.visit(node.left) * self.visit(node.right)
            elif node.op.type == SLASH:
                return self.visit(node.left) / self.visit(node.right)

def main(filename):
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            lexer = Lexer(line)
            parser = Parser(lexer)
            tree = parser.expr()
            interpreter = Interpreter()
            result = interpreter.visit(tree)
            print(f"{line.strip()} = {result}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python interpreter.py <source_file>")
    else:
        main(sys.argv[1])
