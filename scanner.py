from tokens import *
from states import *
from errors import *
import os, re

class Scanner(object):
    _whitespace = frozenset([ " ", "\n", "\r", "\t" ])

    def __init__(self, file_path, system_classes = ""):
        self._cursor              = 0
        self._line                = 1
        self._col                 = 0
        self._state               = ST_INITIAL
        self._current_token       = Token()
        self._current_char        = ""
        self._file_path           = file_path
        self._file                = open(self._file_path, "r")
        self._cursor              = -1
        self._file_data           = system_classes + self._file.read()
        self._one_sep             = False
        self._maybe_start_comment = False
        self._prev_token          = None
        self._is_string           = False
        self._remove_comments()

    def __del__(self):
        self._file.close()

    def _replacer(self, match):
        st = match.group()
        spl = st.split("\n")
        res = []
        for spl_st in spl:
            res.append(" "*len(spl_st))
        return "\n".join(res)

    def _remove_comments(self):
        regex = re.compile("(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?", re.DOTALL | re.MULTILINE)
        tmp = regex.sub(self._replacer, self._file_data)
        self._file_data = tmp

    def _real_next_char(self):
        self._cursor += 1
        if self._cursor >= len(self._file_data):
            return ""
        return self._file_data[self._cursor]

    def _next_char(self):
        ch = self._real_next_char()
        if len(ch) == 0:
            return ""
        self._col += 1

        if self._is_string:
            return ch

        if ch in self._whitespace and not self._one_sep:
            self._one_sep = True
            if ch == "\n":
                self._line += 1
                self._col   = 0
            return " "

        # eat whitespace
        while ch in self._whitespace:
            if ch == "\n":
                self._line += 1
                self._col = 0
            ch = self._real_next_char()
            if len(ch) == 0:
                return ""
            self._col += 1

        if ch == "/":
            if self._cursor+1 < len(self._file_data):
                if self._file_data[self._cursor+1] == "*":
                    raise LexicalError(self._line, self._col-1, "Comentario no cerrado.")
        if ch == "*":
            if self._cursor+1 < len(self._file_data):
                if self._file_data[self._cursor+1] == "/":
                    raise LexicalError(self._line, self._col-1, "Comentario que no ha sido abierto.")

        self._one_sep = False

        return ch

    def current_token(self):
        return self._current_token

    def get_token(self):
        self._state         = ST_INITIAL
        self._current_token = Token()

        if len(self._current_char) == 0:
            self._current_char = self._next_char()

        self._current_token._line = self._line
        if self._col > 0:
            self._current_token._col = self._col-1

        # si a esta altura el current_char es "" entonces estamos en EOF
        if len(self._current_char) == 0:
            # TODO: cambiar por un set_type()
            self._current_token._type = TK_EOF
            self._current_token._lexeme = "EOF"
            self._prev_token = self._current_token
            return self._current_token

        if self._current_char == " ":
            self._current_char = self._next_char()
            if len(self._current_char) == 0:
                # TODO: cambiar por un set_type()
                self._current_token._type = TK_EOF
                self._current_token._lexeme = "EOF"
                self._prev_token = self._current_token
                return self._current_token
            self._prev_token = None

        self._state = self._state.proc(self._current_char,
                                       self._line,
                                       self._col - len(self._current_token.lexeme()) - 1)

        self._is_string = False
        if self._current_char == "\"":
            self._is_string = True

        # main FSM loop
        while self._state != None:
            if len(self._current_char) == 0:
                self._current_token._type = TK_EOF
                self._current_token._lexeme = "EOF"
                self._prev_token = self._current_token
                return self._current_token

            self._current_token.append(self._current_char)
            self._current_token._type = self._state.get_token_type()
            self._current_char = self._next_char()

            if self._current_char == "\"" and self._is_string:
                self._is_string = False

            # execute the state procedure
            self._state = self._state.proc(self._current_char,
                                           self._line,
                                           self._col-len(self._current_token.lexeme())-1)
        # end main FSM loop

        if self._current_token.lexeme() in RESERVED_WORDS.keys():
            self._current_token._type = RESERVED_WORDS[self._current_token.lexeme()]
        if self._current_token.lexeme() in FORBIDDEN_WORDS:
            raise LexicalError(self, "Palabra prohibida: " + self._current_token.lexeme())

        if (self._prev_token != None):
            prev_token_type = self._prev_token.type()
            error_condition = ((  prev_token_type == TK_INT_LITERAL
                               or prev_token_type == TK_CHAR_LITERAL
                               or prev_token_type == TK_STRING_LITERAL
                               ) and self._current_token.type() == TK_IDENTIFIER)
            if (error_condition):
                if   (prev_token_type == TK_INT_LITERAL):
                    raise LexicalError(self, "Entero mal formado.")
                elif (prev_token_type == TK_CHAR_LITERAL):
                    raise LexicalError(self, "Literal de caracter seguido por un identificador.")
                elif (prev_token_type == TK_STRING_LITERAL):
                    raise LexicalError(self, "Literal de string seguido por un identificador.")
                else:
                    print "prev", self._prev_token.type()
                    print "curr", self._current_token.type()
                    print prev_token_type            == TK_INT_LITERAL
                    print prev_token_type            == TK_CHAR_LITERAL
                    print prev_token_type            == TK_STRING_LITERAL
                    print self._current_token.type() == TK_IDENTIFIER
                    raise LexicalError(self, "Error desconocido.")
        self._prev_token = self._current_token
        return self._current_token
