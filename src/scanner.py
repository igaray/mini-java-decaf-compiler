from tokens import *
from states import *
from errors import *
import os, re

class Scanner(object):
    whitespace = frozenset([ " ", "\n", "\r", "\t" ])

    def __init__(self, file_path, system_classes = ""):
        self.cursor        = -1
        self.line          = 1
        self.col           = 0
        self.state         = ST_INITIAL
        self.prev_token    = None
        self.current_token = Token()
        self.current_char  = ""
        self.file_path     = file_path
        self.file          = open(file_path, "r")
        self.file_data     = system_classes + self.file.read()
        self.one_sep       = False
        self.is_string     = False
        self.remove_comments()

    def __del__(self):
        try:
            self.file.close()
        except:
            pass

    def replacer(self, match):
        st  = match.group()
        spl = st.split("\n")
        res = []
        for spl_st in spl:
            res.append(" "*len(spl_st))
        return "\n".join(res)

    def remove_comments(self):
        regex = re.compile("(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?", re.DOTALL | re.MULTILINE)
        tmp   = regex.sub(self.replacer, self.file_data)
        #print "REMOVING COMMENTS"
        #print "BEFORE"
        #print "-----"
        #print self._file_data
        #print "AFTER"
        #print tmp
        #print "-----"
        self.file_data = tmp

    def real_next_char(self):
        self.cursor += 1
        if (self.cursor >= len(self.file_data)):
            return ""
        return self.file_data[self.cursor]

    def next_char(self):
        ch = self.real_next_char()
        if (len(ch) == 0): 
            return ""
        self.col += 1

        # we are in 'literal string mode' and just returning each 
        # character encountered until we realize the literal string is 
        # closed.
        if self.is_string: 
            return ch

        if (ch in self.whitespace and not self.one_sep):
            self.one_sep = True
            # newline encountered, increment line count and reset column count
            if (ch == "\n"):
                self.line += 1
                self.col   = 0
            return " "

        # eat whitespace
        while ch in self.whitespace:
            # newline encountered, increment line count and reset column count
            if (ch == "\n"):
                self.line += 1
                self.col   = 0
            ch = self.real_next_char()
            if (len(ch) == 0): 
                return ""
            self.col += 1

        if (ch == "/"):
            if ((self.cursor + 1) < len(self._file_data)):
                if (self.file_data[self.cursor + 1] == "*"):
                    raise LexicalError(self.line, self.col - 1, "Unclosed comment.")

        # This checks for the occurrence of */ which might indicate an 
        # unopened comment.
        # However, the course professor indicated that */ should be 
        # read as TK_MUL followed by TK_DIV
        #if ch == "*":
        #    if ((self.cursor + 1) < len(self.file_data)):
        #        if (self._file_data[self.cursor + 1] == "/"):
        #            raise LexicalError(self.line, self.col - 1, "Unopened comment.")

        self.one_sep = False
        return ch

    def get_token(self):
        self._state         = ST_INITIAL
        self._current_token = Token()

        if ((len(self.current_char) == 0) or (self.current_char in self.whitespace)):
            self.current_char = self.next_char()

        # if current_char is "" then we are at EOF 
        if (len(self.current_char) == 0):
            self.current_token.type   = TK_EOF
            self.current_token.lexeme = "EOF"
            self.prev_token           = self.current_token
            return self.current_token

        # if current_char is " " then call next_char to consume whitespace
        if (self.current_char == " "):
            self.current_char = self.next_char()
            if (len(self._current_char) == 0):
                self.current_token.type   = TK_EOF
                self.current_token.lexeme = "EOF"
                self.prev_token           = self.current_token
                return self.current_token
            self.prev_token = None

        self.current_token.line = self.line
        self.current_token.col  = self.col

        self.state = self.state.proc(self.current_char, 
                                     self.line, 
                                     self.col - 1)

        # check whether we must enter 'literal string mode'
        self.is_string = False
        if (self.current_char == "\""):
            self.is_string = True

        # main FSM loop
        # the FSM implementation is ingenious but I dislike that the 
        # FSM logic is spread out between the scanner and state classes
        while self.state != None:
            if (len(self.current_char) == 0):
                self.current_token.type   = TK_EOF
                self.current_token.lexeme = "EOF"
                self.prev_token           = self.current_token
                return self.current_token

            self.current_token.append(self.current_char)
            self.current_token.type = self.state.get_token_type()
            self.current_char       = self.next_char()

            # check whether we must exit 'literal string mode'
            if (self.current_char == "\"" and self.is_string):
                self.is_string = False

            # execute the state procedure
            self.state = self.state.proc(self.current_char,
                                         self.line,
                                         self.col - len(self.current_token.lexeme) - 1)
        # end main FSM loop

        # check for identifiers in the reserved words set
        if (self.current_token.lexeme in RESERVED_WORDS.keys()):
            self.current_token.type = RESERVED_WORDS[self.current_token.lexeme]

        # check for identifiers in the forbidden words set
        if (self.current_token.lexeme in FORBIDDEN_WORDS):
            raise LexicalError(self.current_token.line, 
                               self.current_token.col, 
                               "Forbidden word: " + self.current_token.lexeme)

        # check for errors
        if (self.prev_token != None):
            prev_token_type = self.prev_token.type
            error_condition = ((  prev_token_type == TK_INT_LITERAL
                               or prev_token_type == TK_CHAR_LITERAL
                               or prev_token_type == TK_STRING_LITERAL
                               ) and self.current_token.type == TK_IDENTIFIER)
            if (error_condition):
                if   (prev_token_type == TK_INT_LITERAL):
                    raise LexicalError(self.line, 
                                       self.col - 1, 
                                       "Bad integer.")
                elif (prev_token_type == TK_CHAR_LITERAL):
                    raise LexicalError(self.line, 
                                       self.col - 1, 
                                       "Character literal followed by an identifier.")
                elif (prev_token_type == TK_STRING_LITERAL):
                    raise LexicalError(self.line, 
                                       self.col - 1, 
                                       "String literal followed by an identifier.")
                else:
                    raise LexicalError(self.line, 
                                       self.col - 1, 
                                       "Unknown error.")
        self.prev_token = self.current_token

        # Convert lexemes into values for literal values.
        if (self.current_token.type == TK_INT_LITERAL):
            self.current_token.value = int(self.current_token.lexeme)
        elif (self.current_token.type == TK_CHAR_LITERAL):
            if (self.current_token.lexeme[1] == '\\'):
                # literal character is escaped '\\', '\"', '\'', '\n', '\r', '\t'
                self.current_token.value = self.current_token.lexeme[2]
            else:
                self.current_token._value = self.current_token.lexeme[1]
        else:
            self.current_token.value = self.current_token.lexeme

        return self.current_token
