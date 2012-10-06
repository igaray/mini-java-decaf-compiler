import string

from tokens import *
from errors import *

class State(object):

    def __init__(self, next_chk_list, acc, tok_type):
        self._next_state = next_chk_list # [ ( sig_estado, loop, lambda_checkeo ) , ... ]
        self.accepts     = acc
        self._token_type = tok_type

    def check(self, ch):
        for (next, loop, chk) in self._next_state:
            if chk != None:
                if chk(ch) and next != None:
                    return next
                elif chk(ch) and loop:
                    return self
                elif chk(ch):
                    raise Exception("Estado mal definido.")
        return None

    def proc(self, ch, line = 0, col = 0):
        if len(ch) == 0 and not self.accepts:
            raise LexicalError(line,col)

        if len(ch) == 0:
            return None

        nst = self.check(ch)

        # si es aceptador y se termino lo buscado ent retorna todo bien
        if self.accepts and nst == None:
            return None
        elif nst != None:
            # si hay una transicion siguiente
            # ya sea porque no acepta o porque todavia queda algo del token por leer
            # retorna el estado por el que hay que seguir
            return nst
        # sino algo malo paso
        else:
            raise LexicalError(line, col)

    def get_token_type(self):
        return self._token_type

_check_identifier           = lambda c: c in string.ascii_letters+"_"
_check_identifier_rest      = lambda c: c in string.ascii_letters+string.digits+"_"
ST_IDENTIFIER               = State([ (None, True, _check_identifier_rest) ], True, TK_IDENTIFIER)

_check_zero                 = lambda c: c == "0"
ST_ZERO_LITERAL             = State([], True, TK_INT_LITERAL)

_check_int                  = lambda c: c in string.digits[1:]
_check_int_rest             = lambda c: c in string.digits
ST_INT_LITERAL              = State([ (None, True, _check_int_rest) ], True, TK_INT_LITERAL)

_check_char_quote           = lambda c: c == "\'"
_check_char                 = lambda c: (c in string.printable and c != "\\" and c != "\'")
_check_escaped_char_start   = lambda c: c == "\\"
_check_escaped_char_end     = lambda c: c in "\\\'\"n"
ST_CHAR_QUOTE_END           = State([], True, TK_CHAR_LITERAL)
ST_CHAR_END                 = State([ (ST_CHAR_QUOTE_END, False, _check_char_quote) ], False, None)
ST_ESCAPED_CHAR             = State([ (ST_CHAR_END,       False, _check_escaped_char_end) ], False, None)
ST_CHAR_QUOTE               = State([ (ST_CHAR_END,       False, _check_char)
                                    , (ST_ESCAPED_CHAR,   False, _check_escaped_char_start)
                                    ], False, None)

_check_string_quote         = lambda c: c == "\""
_check_string_char          = lambda c: (c in string.printable and c != "\\" and c != "\"" and c != "\n")
ST_STRING_END               = State([], True, TK_STRING_LITERAL)
ST_STRING_START             = State([], False, None) # Hack
ST_ESCAPED_CHAR             = State([ (ST_STRING_START, False, _check_escaped_char_end) ], False, None)
ST_STRING_START._next_state = [ (None, True, _check_string_char)
                              , (ST_ESCAPED_CHAR, False, _check_escaped_char_start)
                              , (ST_STRING_END, False, _check_string_quote)
                              ]

_check_period               = lambda c: c == "."
ST_PERIOD                   = State([], True, TK_PERIOD)

_check_comma                = lambda c: c == ","
ST_COMMA                    = State([], True, TK_COMMA)

_check_semicolon            = lambda c: c == ";"
ST_SEMICOLON                = State([], True, TK_SEMICOLON)

_check_brace_open           = lambda c: c == "{"
ST_BRACE_OPEN               = State([], True, TK_BRACE_OPEN)

_check_brace_close          = lambda c: c == "}"
ST_BRACE_CLOSE              = State([], True, TK_BRACE_CLOSE)

_check_paren_open           = lambda c: c == "("
ST_PAREN_OPEN               = State([], True, TK_PAREN_OPEN)

_check_paren_close          = lambda c: c == ")"
ST_PAREN_CLOSE              = State([], True, TK_PAREN_CLOSE)

_check_equals               = lambda c: c == "="
ST_EQUALS                   = State([                                   ], True, TK_EQUALS)
ST_ASSIGNMENT               = State([ (ST_EQUALS, False, _check_equals) ], True, TK_ASSIGNMENT)

_check_colon                = lambda c: c == ":"
_check_question             = lambda c: c == "?"
_check_circumflex           = lambda c: c == "^"
_check_tilde                = lambda c: c == "~"
ST_FORBIDDEN_OP1            = State([], False, None)

_check_add                  = lambda c: c == "+"
ST_ADD                      = State([ (ST_FORBIDDEN_OP1, False, _check_add) ], True, TK_ADD)

_check_sub                  = lambda c: c == "-"
ST_SUB                      = State([ (ST_FORBIDDEN_OP1, False, _check_sub) ], True, TK_SUB)

_check_mul                  = lambda c: c == "*"
ST_MUL                      = State([], True, TK_MUL)

_check_div                  = lambda c: c == "/"
ST_DIV                      = State([], True, TK_DIV)

_check_mod                  = lambda c: c == "%"
ST_MOD                      = State([ (ST_FORBIDDEN_OP1, False, _check_equals) ], True, TK_MOD)

_check_not                  = lambda c: c == "!"
ST_NOTEQUALS                = State([                                      ], True, TK_NOTEQUALS)
ST_NOT                      = State([ (ST_NOTEQUALS, False, _check_equals) ], True, TK_NOT)

_check_amp                  = lambda c: c == "&"
ST_AND_END                  = State([], True, TK_AND)
ST_AND                      = State([ (ST_AND_END, False, _check_amp) ], False, None)

_check_pipe                 = lambda c: c == "|"
ST_OR_END                   = State([], True, TK_OR)
ST_OR                       = State([ (ST_OR_END, False, _check_pipe) ], False, None)

_check_lt                   = lambda c: c == "<"
ST_LTEQ                     = State([], True, TK_LTEQ)
ST_FORBIDDEN_OP2            = State([ (ST_FORBIDDEN_OP1, False, _check_equals) ], False, None)
ST_LT                       = State([ (ST_LTEQ,          False, _check_equals) 
                                    , (ST_FORBIDDEN_OP2, False, _check_lt)
                                    ], True, TK_LT)

_check_gt                   = lambda c: c == ">"
ST_GTEQ                     = State([], True, TK_GTEQ)
ST_FORBIDDEN_OP4            = State([ (ST_FORBIDDEN_OP1, False, _check_equals) ], False, None)
ST_FORBIDDEN_OP3            = State([ (ST_FORBIDDEN_OP1, False, _check_equals) 
                                    , (ST_FORBIDDEN_OP4, False, _check_gt)
                                    ], False, None)
ST_GT                       = State([ (ST_GTEQ,          False, _check_equals)
                                    , (ST_FORBIDDEN_OP3, False, _check_gt)
                                    ], True, TK_GT)

ST_FORBIDDEN_OP5            = State([ (ST_FORBIDDEN_OP1, False, _check_equals) ], False, None)

ST_INITIAL                  = State([ (ST_IDENTIFIER,       False, _check_identifier)
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
