def isToken(obj):
    return isinstance(obj, Token)

class Token(object):
    def __init__(self):
        self.lexeme = ""
        self.line   = 1
        self.col    = 0
        self.type   = 0
        self.value  = None

    def append(self, ch):
        self.lexeme += ch

    def __str__(self):
        return "%d:%d\t- %s :: %s" % (self.line, self.col, self.type, self.lexeme)

class TokenType(object):
    def __init__(self, id, name):
        self.id   = id
        self.name = name

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return self.name

    def __repr__(self):
        return "TokenType(%d,%s)" % (self.id, self.name)

TK_IDENTIFIER      = TokenType( 0, "<TK_IDENTIFIER>     ")
TK_INT_LITERAL     = TokenType( 1, "<TK_INT_LITERAL>    ")
TK_CHAR_LITERAL    = TokenType( 2, "<TK_CHAR_LITERAL>   ")
TK_STRING_LITERAL  = TokenType( 3, "<TK_STRING_LITERAL> ")
TK_BOOLEAN         = TokenType( 4, "<TK_BOOLEAN>        ")
TK_CHAR            = TokenType( 5, "<TK_CHAR>           ")
TK_CLASS           = TokenType( 6, "<TK_CLASS>          ")
TK_CLASSDEF        = TokenType( 7, "<TK_CLASSDEF>       ")
TK_ELSE            = TokenType( 8, "<TK_ELSE>           ")
TK_EXTENDS         = TokenType( 9, "<TK_EXTENDS>        ")
TK_FALSE           = TokenType(10, "<TK_FALSE>          ")
TK_FOR             = TokenType(11, "<TK_FOR>            ")
TK_IF              = TokenType(12, "<TK_IF>             ")
TK_INT             = TokenType(13, "<TK_INT>            ")
TK_NEW             = TokenType(14, "<TK_NEW>            ")
TK_NULL            = TokenType(15, "<TK_NULL>           ")
TK_RETURN          = TokenType(16, "<TK_RETURN>         ")
TK_STRING          = TokenType(17, "<TK_STRING>         ")
TK_SUPER           = TokenType(18, "<TK_SUPER>          ")
TK_THIS            = TokenType(19, "<TK_THIS>           ")
TK_TRUE            = TokenType(20, "<TK_TRUE>           ")
TK_VOID            = TokenType(21, "<TK_VOID>           ")
TK_WHILE           = TokenType(22, "<TK_WHILE>          ")
TK_BRACE_OPEN      = TokenType(23, "<TK_BRACE_OPEN>     ")
TK_BRACE_CLOSE     = TokenType(24, "<TK_BRACE_CLOSE>    ")
TK_PAREN_OPEN      = TokenType(25, "<TK_PAREN_OPEN>     ")
TK_PAREN_CLOSE     = TokenType(26, "<TK_PAREN_CLOSE>    ")
TK_PERIOD          = TokenType(27, "<TK_PERIOD>         ")
TK_COMMA           = TokenType(28, "<TK_COMMA>          ")
TK_SEMICOLON       = TokenType(29, "<TK_SEMICOLON>      ")
TK_ASSIGNMENT      = TokenType(30, "<TK_ASSIGNMENT>     ")
TK_ADD             = TokenType(31, "<TK_ADD>            ")
TK_SUB             = TokenType(32, "<TK_SUB>            ")
TK_MUL             = TokenType(33, "<TK_MUL>            ")
TK_DIV             = TokenType(34, "<TK_DIV>            ")
TK_MOD             = TokenType(35, "<TK_MOD>            ")
TK_LT              = TokenType(36, "<TK_LT>             ")
TK_GT              = TokenType(37, "<TK_GT>             ")
TK_LTEQ            = TokenType(38, "<TK_LTEQ>           ")
TK_GTEQ            = TokenType(39, "<TK_GTEQ>           ")
TK_EQUALS          = TokenType(40, "<TK_EQUALS>         ")
TK_NOTEQUALS       = TokenType(41, "<TK_NOTEQUALS>      ")
TK_NOT             = TokenType(42, "<TK_NOT>            ")
TK_AND             = TokenType(43, "<TK_AND>            ")
TK_OR              = TokenType(44, "<TK_OR>             ")
TK_EOF             = TokenType(45, "<TK_EOF>            ")
LAMBDA             = TokenType(-1, "LAMBDA              ")

RESERVED_WORDS = {
      "boolean"     : TK_BOOLEAN
    , "char"        : TK_CHAR
    , "class"       : TK_CLASS
    , "classDef"    : TK_CLASSDEF
    , "else"        : TK_ELSE
    , "extends"     : TK_EXTENDS
    , "false"       : TK_FALSE
    , "for"         : TK_FOR
    , "if"          : TK_IF
    , "int"         : TK_INT
    , "new"         : TK_NEW
    , "null"        : TK_NULL
    , "return"      : TK_RETURN
    , "String"      : TK_STRING
    , "super"       : TK_SUPER
    , "this"        : TK_THIS
    , "true"        : TK_TRUE
    , "void"        : TK_VOID
    , "while"       : TK_WHILE
    }

FORBIDDEN_WORDS = frozenset(
    [ 'abstract'
    , 'break'
    , 'byte'
    , 'byte'
    , 'byvalue'
    , 'case'
    , 'cast'
    , 'catch'
    , 'const'
    , 'continue'
    , 'default'
    , 'do'
    , 'double'
    , 'final'
    , 'finally'
    , 'float'
    , 'future'
    , 'generic'
    , 'goto'
    , 'implements'
    , 'import'
    , 'inner'
    , 'instanceof'
    , 'interface'
    , 'long'
    , 'long'
    , 'native'
    , 'none'
    , 'operator'
    , 'outer'
    , 'package'
    , 'private'
    , 'protected'
    , 'public'
    , 'rest'
    , 'short'
    , 'short'
    , 'static'
    , 'switch'
    , 'synchronized'
    , 'throw'
    , 'throws'
    , 'transient'
    , 'try'
    , 'var'
    , 'volatile'
    ])

