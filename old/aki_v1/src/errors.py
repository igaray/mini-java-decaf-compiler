class LexicalError(Exception):
    def __init__(self, line, col, msg):
        self.line    = line
        self.col     = col
        self.message = "LEXICAL ERROR: Line: %d, Col: %d :: %s" % (line, col, msg)

    def __str__(self):
        return self.message

class SyntacticError(Exception):
    def __init__(self, parser, msg = "Error de sintaxis."):
        self.line    = parser.current_token().line()
        self.col     = parser.current_token().col()
        self.message = "SYNTACTIC ERROR: Line: %d, Col: %d :: %s" % (self.line, self.col, msg)

    def __str__(self):
        return self.message

class SemanticError(Exception):
    def __init__(self, parser, msg = "Error semantico."):
        self.line    = parser.current_token().line()
        self.col     = parser.current_token().col()
        self.message = "SEMANTIC ERROR: Line: %d, Col: %d :: %s" % (line, col, msg)

