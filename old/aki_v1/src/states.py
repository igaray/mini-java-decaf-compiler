import string

from tokens import *
from errors import *

class State(object):

    def __init__(self, desc, next_chk_list, acc, tok_type):
        self.description = desc
        # [ (next_state, loop, lambda_check), ... ]
        # Each element of the next_chk_list is a 3-tuple representing
        # a transition.
        # The first element is the next state of the FMS if the 
        # transition is fired. 
        # The second element is a boolean value 'loop', which is true
        # if the transition loops into the same state.
        # The third element is a lambda function, which is called to 
        # ascertain whether the transtion should fire.
        self.next_state = next_chk_list
        self.accepts    = acc
        self.token_type = tok_type
    
    def check(self, ch):
        for (next, loop, chk) in self.next_state:
            if (chk != None):
                if (chk(ch) and next != None):
                    return next
                elif (chk(ch) and loop):
                    return self
                elif chk(ch):
                    raise Exception("Bad state.")
        return None

    def proc(self, ch, line, col):
        if (len(ch) == 0 and not self.accepts):
            raise LexicalError(line, col, "Unknown token.")

        if (len(ch) == 0):
            return None

        next_state = self.check(ch)

        # if the state we are in is accepting, and the next state is none
        # then the next state is none
        # if the next state is not none
        # then the next state is the next state
        # in any other case, something bad happened
        if not ((self.accepts and next_state == None) or (next_state != None)):
            raise LexicalError(line, col, "Unrecognized token.")
        return next_state

    def get_token_type(self):
        return self.token_type

# Transition checks
_check_identifier           = lambda c: c in string.ascii_letters + "_"
_check_identifier_rest      = lambda c: c in string.ascii_letters + string.digits + "_"
_check_int                  = lambda c: c in string.digits[1:]
_check_int_rest             = lambda c: c in string.digits
_check_char                 = lambda c: (c in string.printable and c != "\\" and c != "\'")
_check_string_char          = lambda c: (c in string.printable and c != "\\" and c != "\"" and c != "\n")
_check_char_quote           = lambda c: c == "\'"
_check_escaped_char_start   = lambda c: c == "\\"
_check_escaped_char_end     = lambda c: c in "\\\'\"n"
_check_string_quote         = lambda c: c == "\""
_check_zero                 = lambda c: c == "0"
_check_period               = lambda c: c == "."
_check_comma                = lambda c: c == ","
_check_semicolon            = lambda c: c == ";"
_check_brace_open           = lambda c: c == "{"
_check_brace_close          = lambda c: c == "}"
_check_paren_open           = lambda c: c == "("
_check_paren_close          = lambda c: c == ")"
_check_equals               = lambda c: c == "="
_check_colon                = lambda c: c == ":"
_check_question             = lambda c: c == "?"
_check_circumflex           = lambda c: c == "^"
_check_tilde                = lambda c: c == "~"
_check_add                  = lambda c: c == "+"
_check_sub                  = lambda c: c == "-"
_check_mul                  = lambda c: c == "*"
_check_div                  = lambda c: c == "/"
_check_mod                  = lambda c: c == "%"
_check_not                  = lambda c: c == "!"
_check_amp                  = lambda c: c == "&"
_check_pipe                 = lambda c: c == "|"
_check_lt                   = lambda c: c == "<"
_check_gt                   = lambda c: c == ">"

# States
ST_IDENTIFIER               = State("ST_IDENTIFIER", 
                                    [ (None, True, _check_identifier_rest) ], 
                                    True, 
                                    TK_IDENTIFIER)

ST_ZERO_LITERAL             = State("ST_ZERO_LITERAL", 
                                    [], 
                                    True, 
                                    TK_INT_LITERAL)

ST_INT_LITERAL              = State("ST_INT_LITERAL", 
                                    [ (None, True, _check_int_rest) ], 
                                    True, 
                                    TK_INT_LITERAL)

ST_CHAR_QUOTE_END           = State("ST_CHAR_QUOTE_END", 
                                    [], 
                                    True, 
                                    TK_CHAR_LITERAL)

ST_CHAR_END                 = State("ST_CHAR_END",     
                                    [ (ST_CHAR_QUOTE_END, False, _check_char_quote) ], 
                                    False, 
                                    None)

ST_ESCAPED_CHAR             = State("ST_ESCAPED_CHAR", 
                                    [ (ST_CHAR_END,       False, _check_escaped_char_end) ], 
                                    False, 
                                    None)

ST_CHAR_QUOTE               = State("ST_CHAR_QUOTE",   
                                    [ (ST_CHAR_END,       False, _check_char)
                                    , (ST_ESCAPED_CHAR,   False, _check_escaped_char_start)
                                    ], 
                                    False, 
                                    None)

ST_STRING_END               = State("ST_STRING_END", 
                                    [], 
                                    True, 
                                    TK_STRING_LITERAL)

ST_STRING_START             = State("ST_STRING_START", 
                                    [], 
                                    False, 
                                    None) 

ST_ESCAPED_CHAR             = State("ST_ESCAPED_CHAR", 
                                    [ (ST_STRING_START, False, _check_escaped_char_end) ], 
                                    False, 
                                    None)
# Hack
ST_STRING_START.next_state  =       [ (None,              True,  _check_string_char)
                                    , (ST_ESCAPED_CHAR,   False, _check_escaped_char_start)
                                    , (ST_STRING_END,     False, _check_string_quote)
                                    ]

ST_PERIOD                   = State("ST_PERIOD", 
                                    [], 
                                    True, 
                                    TK_PERIOD)

ST_COMMA                    = State("ST_COMMA", 
                                    [], 
                                    True, 
                                    TK_COMMA)

ST_SEMICOLON                = State("ST_SEMICOLON", 
                                    [], 
                                    True, 
                                    TK_SEMICOLON)

ST_BRACE_OPEN               = State("ST_BRACE_OPEN", 
                                    [], 
                                    True, 
                                    TK_BRACE_OPEN)

ST_BRACE_CLOSE              = State("ST_BRACE_CLOSE", 
                                    [], 
                                    True, 
                                    TK_BRACE_CLOSE)

ST_PAREN_OPEN               = State("ST_PAREN_OPEN", 
                                    [], 
                                    True, 
                                    TK_PAREN_OPEN)

ST_PAREN_CLOSE              = State("ST_PAREN_CLOSE", 
                                    [], 
                                    True, 
                                    TK_PAREN_CLOSE)

ST_EQUALS                   = State("ST_EQUALS", 
                                    [], 
                                    True, 
                                    TK_EQUALS)

ST_ASSIGNMENT               = State("ST_ASSIGNMENT", 
                                    [ (ST_EQUALS, False, _check_equals) ], 
                                    True, 
                                    TK_ASSIGNMENT)

ST_FORBIDDEN_OP1            = State("ST_FORBIDDEN_OP1", 
                                    [], 
                                    True, 
                                    TK_FOP)

ST_ADD                      = State("ST_ADD", 
                                    [ (ST_FORBIDDEN_OP1, False, _check_add) ], 
                                    True, 
                                    TK_ADD)

ST_SUB                      = State("ST_SUB", 
                                    [ (ST_FORBIDDEN_OP1, False, _check_sub) ], 
                                    True, 
                                    TK_SUB)

ST_MUL                      = State("ST_MUL", 
                                    [], 
                                    True, 
                                    TK_MUL)

ST_DIV                      = State("ST_DIV", 
                                    [], 
                                    True, 
                                    TK_DIV)

ST_MOD                      = State("ST_MOD", 
                                    [ (ST_FORBIDDEN_OP1, False, _check_equals) ], 
                                    True, 
                                    TK_MOD)

ST_NOTEQUALS                = State("ST_NOTEQUALS", 
                                    [], 
                                    True, 
                                    TK_NOTEQUALS)

ST_NOT                      = State("ST_NOT", 
                                    [ (ST_NOTEQUALS, False, _check_equals) ], 
                                    True, 
                                    TK_NOT)

ST_AND_END                  = State("ST_AND_END", 
                                    [], 
                                    True, 
                                    TK_AND)

ST_AND                      = State("ST_AND", 
                                    [ (ST_AND_END, False, _check_amp) ], 
                                    False, 
                                    None)

ST_OR_END                   = State("ST_OR_END", 
                                    [], 
                                    True, 
                                    TK_OR)
ST_OR                       = State("ST_OR", 
                                    [ (ST_OR_END, False, _check_pipe) ], 
                                    False, 
                                    None)

ST_LTEQ                     = State("ST_LTEQ", 
                                    [], 
                                    True, 
                                    TK_LTEQ)
ST_FORBIDDEN_OP2            = State("ST_FORBIDDEN_OP2", 
                                    [ (ST_FORBIDDEN_OP1, False, _check_equals) ], 
                                    True, 
                                    TK_FOP)

ST_LT                       = State("ST_LT", 
                                    [ (ST_LTEQ,          False, _check_equals) 
                                    , (ST_FORBIDDEN_OP2, False, _check_lt)
                                    ], 
                                    True, 
                                    TK_LT)

ST_GTEQ                     = State("ST_GTEQ", 
                                    [], 
                                    True, 
                                    TK_GTEQ)

ST_FORBIDDEN_OP4            = State("ST_FORBIDDEN_OP4", 
                                    [ (ST_FORBIDDEN_OP1, False, _check_equals) ], 
                                    True, 
                                    TK_FOP)

ST_FORBIDDEN_OP3            = State("ST_FORBIDDEN_OP3", 
                                    [ (ST_FORBIDDEN_OP1, False, _check_equals) 
                                    , (ST_FORBIDDEN_OP4, False, _check_gt)
                                    ], 
                                    True, 
                                    TK_FOP)

ST_GT                       = State("ST_GT",
                                    [ (ST_GTEQ,          False, _check_equals)
                                    , (ST_FORBIDDEN_OP3, False, _check_gt)
                                    ], 
                                    True, 
                                    TK_GT)

ST_FORBIDDEN_OP5            = State("ST_FORBIDDEN_OP5", 
                                    [ (ST_FORBIDDEN_OP1, False, _check_equals) ], 
                                    True, 
                                    TK_FOP)

ST_INITIAL                  = State("ST_INITIAL",
                                    [ (ST_IDENTIFIER,       False, _check_identifier)
                                    , (ST_ZERO_LITERAL,     False, _check_zero)
                                    , (ST_INT_LITERAL,      False, _check_int)
                                    , (ST_CHAR_QUOTE,       False, _check_char_quote)
                                    , (ST_STRING_START,     False, _check_string_quote)
                                    , (ST_PERIOD,           False, _check_period)
                                    , (ST_COMMA,            False, _check_comma)
                                    , (ST_SEMICOLON,        False, _check_semicolon)
                                    , (ST_BRACE_OPEN,       False, _check_brace_open)
                                    , (ST_BRACE_CLOSE,      False, _check_brace_close)
                                    , (ST_PAREN_OPEN,       False, _check_paren_open)
                                    , (ST_PAREN_CLOSE,      False, _check_paren_close)
                                    , (ST_ASSIGNMENT,       False, _check_equals)
                                    , (ST_ADD,              False, _check_add)
                                    , (ST_SUB,              False, _check_sub)
                                    , (ST_MUL,              False, _check_mul)
                                    , (ST_DIV,              False, _check_div)
                                    , (ST_MOD,              False, _check_mod)

                                    , (ST_NOT,              False, _check_not)
                                    , (ST_AND,              False, _check_amp)
                                    , (ST_OR,               False, _check_pipe)
                                    , (ST_LT,               False, _check_lt)
                                    , (ST_GT,               False, _check_gt)

                                    , (ST_FORBIDDEN_OP1,    False, _check_colon)
                                    , (ST_FORBIDDEN_OP1,    False, _check_question)
                                    , (ST_FORBIDDEN_OP1,    False, _check_tilde)
                                    , (ST_FORBIDDEN_OP5,    False, _check_circumflex)
                                    ],
                                    False,
                                    None)
