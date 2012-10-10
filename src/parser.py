from scanner        import Scanner
from tokens         import *
from first_follow   import *
from errors         import SyntacticError, SemanticError

#import mj.mjprimary as mjp
#import mj.mjclass   as mjc
#from   mj.mjts  import mjTS

class Parser(object):
    def __init__(self,  path, debug = False, system_classes = ""):
        self._debug = debug
        if (self.debug):
            self.log       = open('DEBUG.log', 'w')
        else:
            self.log       = None
        self.current_token = None
        self.scanner       = Scanner(path, system_classes)

    def parse(self, st = None):
        self.update_token()
        return self.start()

    def update_token(self):
        self.current_token = self._scanner.get_token()
        #print(self.current_token)

    def match_token(self, tokentype):
        return self.current_token.type == tokentype

    def token_in(self, first):
        return (self.current_token.type in first)

    def DEBUG(self, msg):
        if (self.debug):
            self.log.write(msg + "\n")
            #print(msg)
            if (msg in ["ERROR", "SYNTAX OK"]):
                self.log.flush()
                self.log.close()

    ##################################################################
    def start(self, st = None):
        self.DEBUG("> start")
        self.classdef_start()
        self.class_start()
        self.DEBUG("< start")
        self.DEBUG("SYNTAX OK")

    def classdef_start(self, st = None):
        self.DEBUG("> classdef_start")
        self.classdef()
        self.classdef_start_rest()
        self.DEBUG("< classdef_start")

    def classdef_start_rest(self, st = None):
        self.DEBUG("> classdef_start_rest")
        if (self.token_in(first_classdef_start)):
            self.classdef_start()
        else:
            pass
        self.DEBUG("< classdef_start_rest")

    def classdef(self, st = None):
        self.DEBUG("> classdef")
        if not (self.match_token(TK_CLASSDEF)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected: classDef got "
            errormsg += self.current_token().lexeme()
            errormsg += ".\nYou must have at least one class defined by the classDef keyword."
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_CLASSDEF")
        self.update_token()
        if not (self.match_token(TK_IDENTIFIER)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected an identifier got " + self.current_token().lexeme()
            errormsg += ".\nYou must declare your class with a valid identifier."
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_IDENTIFIER")
        self.update_token()
        if (self.token_in(first_super)):
            self.superr()
        self.classdef_body()
        self.DEBUG("< classdef")

    def classdef_body(self, st = None):
        self.DEBUG("> classdef_body")
        if not (self.match_token(TK_BRACE_OPEN)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected an { got: " + self.current_token().lexeme()
            errormsg += ".\nThe class declaration must have a body, starting with an opening brace."
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_BRACE_OPEN")
        self.update_token()
        self.classdef_body_rest()
        if not (self.match_token(TK_BRACE_CLOSE)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected an } got: " + self.current_token().lexeme()
            errormsg += ".\nYou must close the classDef body with a closing brace."
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_BRACE_CLOSE")
        self.update_token()
        self.DEBUG("< classdef_body")

    def classdef_body_rest(self, st = None):
        self.DEBUG("> classdef_body_rest")
        if (self.match_token(TK_IDENTIFIER)):
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.classdef_ctor_or_method()
        elif (self.token_in(first_primitive_type_void)):
            self.DEBUG("p classdef_method_rest")
            self.update_token()
            if not (self.match_token(TK_IDENTIFIER)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected an identifier got " + self.current_token().lexeme()
                errormsg += ".\nIt seems you are defining a method.\n"
                errormsg += "You must provide a valid identifier for the method name."
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.classdef_method_rest()
        else:
            pass
        self.DEBUG("< classdef_body_rest")

    def classdef_ctor_or_method(self, st = None):
        self.DEBUG("> classdef_ctor_or_method")
        if (self.match_token(TK_IDENTIFIER)):
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.classdef_method_rest()
        elif (self.token_in(first_classdef_ctor_rest)):
            self.classdef_ctor_rest()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected an identifier or the beginning of a list of formal arguments, got " 
            errormsg += self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< classdef_ctor_or_method")

    def classdef_ctor_rest(self, st = None):
        self.DEBUG("> classdef_ctor_rest")
        self.formal_args()
        if not (self.match_token(TK_SEMICOLON)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected an ; got " + self.current_token().lexeme()
            errormsg += ".\nYou must terminate the declaration of a constructor with ;"
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_SEMICOLON")
        self.update_token()
        self.classdef_body_rest()        
        self.DEBUG("< classdef_ctor_rest")

    def classdef_method_rest(self, st = None):
        #classdef_method_rest ::= formal_args TK_SEMICOLON classdef_methods
        self.DEBUG("> classdef_method_rest")
        self.formal_args()
        if not (self.match_token(TK_SEMICOLON)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected an ; got " + self.current_token().lexeme()
            errormsg += ".\nYou must terminate a method declaration in with a semicolon."
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_SEMICOLON")
        self.update_token()
        self.classdef_methods()
        self.DEBUG("< classdef_method_rest")

    def classdef_methods(self, st = None):
        self.DEBUG("> classdef_methods")
        if (self.token_in(first_classdef_method)):
            #classdef_methods ::= classdef_method classdef_methods
            self.classdef_method()
            self.classdef_methods()
        elif (self.token_in(follow_classdef_methods)):
            #classdef_methods ::= LAMBDA
            pass
        else:
            DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected: a classDef method type, got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< classdef_methods")

    def classdef_method(self, st = None):
        #classdef_method ::= method_type TK_IDENTIFIER formal_args TK_SEMICOLON
        self.DEBUG("> classdef_method")
        self.method_type()
        if not (self.match_token(TK_IDENTIFIER)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected: identifier got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_IDENTIFIER")
        self.update_token()
        self.formal_args()
        if not (self.match_token(TK_SEMICOLON)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected: ; got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_SEMICOLON")
        self.update_token()
        self.DEBUG("< classdef_method")

    def class_start(self, st = None):
        #class_start ::= classs class_start_rest
        self.DEBUG("> class_start")
        self.classs()
        self.class_start_rest()
        self.DEBUG("< class_start")

    def class_start_rest(self, st = None):
        self.DEBUG("> class_start_rest")
        if (self.token_in(first_class)):
            #class_start_rest ::= classs class_start_rest    
            self.classs()
            self.class_start_rest()
        elif (self.token_in(follow_class_start_rest)):
            #class_start_rest ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< class_start_rest")

    def classs(self, st = None):
        #classs ::= TK_CLASS TK_IDENTIFIER superr class_body
        self.DEBUG("> classs")
        if not (self.match_token(TK_CLASS)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected class keyword got " 
            errormsg += str(self.current_token().type()) #.lexeme()
            errormsg += ".\nYou must have at least one class defined by the class keyword."
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_CLASS")
        self.update_token()
        if not (self.match_token(TK_IDENTIFIER)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected: identifier got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_IDENTIFIER")
        self.update_token()
        self.superr()
        self.class_body()
        self.DEBUG("< classs")

    def class_body(self, st = None):
        #class_body ::= TK_BRACE_OPEN class_body_rest TK_BRACE_CLOSE
        self.DEBUG("> class_body")
        if not (self.match_token(TK_BRACE_OPEN)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected: { got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_BRACE_OPEN")
        self.update_token()
        self.class_body_rest()
        if not (self.match_token(TK_BRACE_CLOSE)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected: } got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_BRACE_CLOSE")
        self.update_token()
        self.DEBUG("< class_body")

    def class_body_rest(self, st = None):
        self.DEBUG("> class_body_rest")
        if (self.match_token(TK_IDENTIFIER)):
            #class_body_rest ::= TK_IDENTIFIER class_field_ctor_or_method
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.class_field_ctor_or_method()
        elif (self.match_token(TK_VOID)):
            #class_body_rest ::= TK_VOID TK_IDENTIFIER class_method_rest
            self.DEBUG("m TK_VOID")
            self.update_token()
            if not (self.match_token(TK_IDENTIFIER)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: identifier got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_IDENTIFIER")
            self.class_method_rest()
        elif (self.token_in(first_primitive_type)):
            #class_body_rest ::= primitive_type TK_IDENTIFIER class_field_or_method
            self.primitive_type()
            if not (self.match_token(TK_IDENTIFIER)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: identifier got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.class_field_or_method()
        elif (self.token_in(follow_class_body_rest)):
            #class_body_rest ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< class_body_rest")

    def class_field_ctor_or_method(self, st = None):
        self.DEBUG("> class_field_ctor_or_method")
        if (self.match_token(TK_IDENTIFIER)):
            #class_field_ctor_or_method ::= TK_IDENTIFIER class_field_or_method
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.class_field_or_method()
        elif (self.token_in(first_class_ctor_rest)):
            #class_field_ctor_or_method ::= class_ctor_rest
            self.class_ctor_rest()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< class_field_ctor_or_method")

    def class_field_or_method(self, st = None):
        self.DEBUG("> class_field_or_method")
        if (self.token_in(first_class_var_declaration_list)):
            #class_field_or_method ::= class_var_declaration_list
            self.class_var_declaration_list()
        elif (self.token_in(first_class_method_rest)):
            #class_field_or_method ::= class_method_rest
            self.class_method_rest()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< class_field_or_method")

    def class_var_declaration_list(self, st = None):
        self.DEBUG("> class_var_declaration_list")
        if (self.match_token(TK_COMMA)):
            #class_var_declaration_list ::= TK_COMMA TK_IDENTIFIER class_var_declaration_list
            self.DEBUG("m TK_COMMA")
            self.update_token()
            if not (self.match_token(TK_IDENTIFIER)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: identifier got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.class_var_declaration_list()
        elif (self.match_token(TK_SEMICOLON)):
            #class_var_declaration_list ::= TK_SEMICOLON class_body_rest
            self.DEBUG("m TK_SEMICOLON")
            self.update_token()
            self.class_body_rest()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< class_var_declaration_list")

    def class_method_rest(self, st = None):
        #class_method_rest ::= formal_args block class_methods
        self.DEBUG("> class_method_rest")
        self.formal_args()
        self.block()
        self.class_methods()
        self.DEBUG("< class_method_rest")

    def class_methods(self, st = None):
        self.DEBUG("> class_methods")
        if (self.token_in(first_class_method)):
            #class_methods ::= class_method class_methods
            self.class_method()
            self.class_methods()
        elif (self.token_in(follow_class_methods)):
            #class_methods ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< class_methods")

    def class_method(self, st = None):
        #class_method ::= method_type TK_IDENTIFIER formal_args block
        self.DEBUG("> class_method")
        self.method_type()
        if not (self.match_token(TK_IDENTIFIER)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected: identifier got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_IDENTIFIER")
        self.update_token()
        self.formal_args()
        self.block()
        self.DEBUG("< class_method")

    def class_ctor_rest(self, st = None):
        #class_ctor_rest ::= formal_args block class_ctor_or_method
        self.DEBUG("> class_ctor_rest")
        self.formal_args()
        self.block()
        self.class_ctor_or_method()
        self.DEBUG("< class_ctor_rest")

    def class_ctor_or_method(self, st = None):
        self.DEBUG("> class_ctor_or_method")
        if (self.match_token(TK_IDENTIFIER)):
            #class_ctor_or_method ::= TK_IDENTIFIER class_ctor_or_method_rest
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.class_ctor_or_method_rest()
        elif (self.token_in(first_primitive_type_void)):
            #class_ctor_or_method ::= primitive_type_void TK_IDENTIFIER class_method_rest 
            self.update_token()
            if not (self.match_token(TK_IDENTIFIER)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: identifier got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.update_token()
            self.class_method_rest()
        elif (self.token_in(follow_class_ctor_or_method)):
            #class_ctor_or_method ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< class_ctor_or_method")

    def class_ctor_or_method_rest(self, st = None):
        self.DEBUG("> class_ctor_or_method_rest")
        if (self.match_token(TK_IDENTIFIER)):
            #class_ctor_or_method_rest ::= TK_IDENTIFIER class_method_rest
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.class_method_rest()
        elif (self.token_in(first_class_ctor_rest)):
            #class_ctor_or_method_rest ::= class_ctor_rest
            self.class_ctor_rest()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< class_ctor_or_method_rest")

    def superr(self, st = None):
        self.DEBUG("> superr")
        if (self.match_token(TK_EXTENDS)):
            #superr ::= TK_EXTENDS TK_IDENTIFIER
            self.DEBUG("m TK_EXTENDS")
            self.update_token()
            if not (self.match_token(TK_IDENTIFIER)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: identifier got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
        elif (self.token_in(follow_super)):
            #superr ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< superr")

    def formal_args(self, st = None):
        #formal_args ::= TK_PAREN_OPEN formal_args_rest
        self.DEBUG("> formal_args")
        if not (self.match_token(TK_PAREN_OPEN)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected: ( got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_PAREN_OPEN")
        self.update_token()
        self.formal_args_rest()
        self.DEBUG("< formal_args")

    def formal_args_rest(self, st = None):
        self.DEBUG("> formal_args_rest")
        if (self.match_token(TK_PAREN_CLOSE)):
            #formal_args_rest ::= TK_PAREN_CLOSE
            self.DEBUG("m TK_PAREN_CLOSE")
            self.update_token()
        elif (self.token_in(first_formal_arg_list)):
            #formal_args_rest ::= formal_arg_list TK_PAREN_CLOSE
            self.formal_arg_list()
            if not (self.match_token(TK_PAREN_CLOSE)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ) got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_CLOSE")
            self.update_token()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< formal_args_rest")

    def formal_arg_list(self, st = None):
        #formal_arg_list ::= formal_arg formal_arg_list_rest
        self.DEBUG("> formal_arg_list")
        self.formal_arg()
        self.formal_arg_list_rest()
        self.DEBUG("< formal_arg_list")

    def formal_arg_list_rest(self, st = None):
        self.DEBUG("> formal_arg_list_rest")
        if (self.match_token(TK_COMMA)):
            #formal_arg_list_rest ::= TK_COMMA formal_arg formal_arg_list_rest
            self.DEBUG("m TK_COMMA")
            self.update_token()
            self.formal_arg()
            self.formal_arg_list_rest()
        elif (self.token_in(follow_formal_arg_list_rest)):
            #formal_arg_list_rest ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< formal_arg_list_rest")

    def formal_arg(self, st = None):
        #formal_arg ::= typee TK_IDENTIFIER
        self.DEBUG("> formal_arg")
        self.typee()
        if not (self.match_token(TK_IDENTIFIER)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected: identifier got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_IDENTIFIER")
        self.update_token()
        self.DEBUG("< formal_arg")

    def method_type(self, st = None):
        #method_type ::= TK_VOID
        #method_type ::= typee
        self.DEBUG("> method_type")
        if not (self.token_in([TK_BOOLEAN, TK_CHAR, TK_INT, TK_STRING, TK_IDENTIFIER, TK_VOID])):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected a method type, got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m method type")
        self.update_token()
        self.DEBUG("< method_type")

    def typee(self, st = None):
        #typee ::= TK_IDENTIFIER
        #typee ::= primitive_type
        self.DEBUG("> typee")
        if not (self.token_in([TK_BOOLEAN, TK_CHAR, TK_INT, TK_STRING, TK_IDENTIFIER])):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected a type, got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m type")
        self.update_token()
        self.DEBUG("< typee")

    def primitive_type_void(self, st = None):
        #primitive_type_void ::= void
        #primitive_type_void ::= primitive_type
        self.DEBUG("> primitive_type_void")
        if not (self.token_in([TK_BOOLEAN, TK_CHAR, TK_INT, TK_STRING, TK_VOID])):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected a primitive type or void, got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m primitive type or void")
        self.update_token()
        self.DEBUG("< primitive_type_void")

    def primitive_type(self, st = None):
        #primitive_type ::= TK_BOOLEAN
        #primitive_type ::= TK_CHAR
        #primitive_type ::= TK_INT
        #primitive_type ::= TK_STRING
        self.DEBUG("> primitive_type")
        if not (self.token_in([TK_BOOLEAN, TK_CHAR, TK_INT, TK_STRING])):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected a primitive type got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m primitive type")
        self.update_token()
        self.DEBUG("< primitive_type")

    def block(self, st = None):
        #block ::= TK_BRACE_OPEN statements TK_BRACE_CLOSE
        self.DEBUG("> block")
        if not (self.match_token(TK_BRACE_OPEN)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected: { got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_BRACE_OPEN")
        self.update_token()
        self.statements()
        if not (self.match_token(TK_BRACE_CLOSE)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected: } got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_BRACE_CLOSE")
        self.update_token()
        self.DEBUG("< block")

    def statements(self, st = None):
        self.DEBUG("> statements")
        if (self.token_in(first_statement)):
            #statements ::= statement statements
            self.statement()
            self.statements()
        elif (self.token_in(follow_statements)):
            #statements ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< statements")

    def statement(self, st = None):
        self.DEBUG("> statement")
        if (self.token_in(first_closed_statement)):
            #statement ::= closed_statement
            self.closed_statement()
        elif (self.first_open_statement):
            #statement ::= open_statement
            self.open_statement()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< statement")

    def open_statement(self, st = None):
        self.DEBUG("> open_statement")
        if (self.match_token(TK_IF)):
            self.DEBUG("m TK_IF")
            self.update_token()
            if not (self.match_token(TK_PAREN_OPEN)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ( got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_OPEN")
            self.update_token()
            self.expression()
            if not (self.match_token(TK_PAREN_CLOSE)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ) got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_CLOSE")
            self.update_token()
            if (self.token_in(first_closed_statement)):
                #open_statement ::= TK_IF    TK_PAREN_OPEN expression TK_PAREN_CLOSE closed_statement TK_ELSE open_statement
                self.closed_statement()
                if not (self.match_token(TK_ELSE)):
                    self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                    errormsg = "Expected: ) got " + self.current_token().lexeme()
                    raise SyntacticError(self, errormsg)
                self.open_statement()
            elif (self.token_in(first_statement)):
                #open_statement ::= TK_IF    TK_PAREN_OPEN expression TK_PAREN_CLOSE statement
                self.statement()
            else:
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected:  got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
        elif (self.match_token(TK_FOR)):
            #open_statement ::= TK_FOR   TK_PAREN_OPEN expression TK_SEMICOLON expression TK_SEMICOLON expression TK_PAREN_CLOSE open_statement
            self.DEBUG("m TK_FOR")
            self.update_token()
            if not (self.match_token(TK_PAREN_OPEN)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ( got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_OPEN")
            self.update_token()
            self.expression()
            if not (self.match_token(TK_SEMICOLON)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ; got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_SEMICOLON")
            self.update_token()
            self.expression()
            if not (self.match_token(TK_SEMICOLON)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ; got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_SEMICOLON")
            self.update_token()
            self.expression()
            if not (self.match_token(TK_PAREN_CLOSE)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ) got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_CLOSE")
            self.update_token()
            self.open_statement()
        elif (self.match_token(TK_WHILE)):
            #open_statement ::= TK_WHILE TK_PAREN_OPEN expression TK_PAREN_CLOSE open_statement
            self.DEBUG("m TK_WHILE")
            self.update_token()
            if not (self.match_token(TK_PAREN_OPEN)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ( got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_OPEN")
            self.update_token()
            self.expression()
            if not (self.match_token(TK_PAREN_CLOSE)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ) got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_CLOSE")
            self.update_token()
            self.open_statement()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< open_statement")

    def closed_statement(self, st = None):
        self.DEBUG("> closed_statement")
        if (self.match_token(TK_IF)):
            #closed_statement ::= TK_IF    TK_PAREN_OPEN expression TK_PAREN_CLOSE closed_statement TK_ELSE closed_statement
            self.DEBUG("m TK_IF")
            self.update_token()
            if not (self.match_token(TK_PAREN_OPEN)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ( got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_OPEN")
            self.update_token()
            self.expression()
            if not (self.match_token(TK_PAREN_CLOSE)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ) got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_CLOSE")
            self.update_token()
            self.closed_statement()
            if not (self.match_token(TK_ELSE)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: else keyword got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_ELSE")
            self.update_token()
            self.closed_statement()
        elif (self.match_token(TK_FOR)):
            #closed_statement ::= TK_FOR   TK_PAREN_OPEN expression TK_SEMICOLON expression TK_SEMICOLON expression TK_PAREN_CLOSE closed_statement
            self.DEBUG("m TK_FOR")
            self.update_token()
            if not (self.match_token(TK_PAREN_OPEN)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ( got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_OPEN")
            self.update_token()
            self.expression()
            if not (self.match_token(TK_SEMICOLON)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ; got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_SEMICOLON")
            self.update_token()
            self.expression()
            if not (self.match_token(TK_SEMICOLON)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ; got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_SEMICOLON")
            self.update_token()
            self.expression()
            if not (self.match_token(TK_PAREN_CLOSE)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ) got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_CLOSE")
            self.update_token()
            self.closed_statement()
        elif (self.match_token(TK_WHILE)):
            #closed_statement ::= TK_WHILE TK_PAREN_OPEN expression TK_PAREN_CLOSE closed_statement
            self.DEBUG("m TK_WHILE")
            self.update_token()
            if not (self.match_token(TK_PAREN_OPEN)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ( got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_OPEN")
            self.update_token()
            self.expression()
            if not (self.match_token(TK_PAREN_CLOSE)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ) got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_CLOSE")
            self.update_token()
            self.closed_statement()
        elif (self.token_in(first_simple_statement)):
            #closed_statement ::= simple_statement
            self.simple_statement()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< closed_statement")

    def simple_statement(self, st = None):
        self.DEBUG("> simple_statement")
        if (self.match_token(TK_SEMICOLON)):
            #simple_statement ::= TK_SEMICOLON
            self.DEBUG("m TK_SEMICOLON")
            self.update_token()
        elif (self.match_token(TK_RETURN)):
            #simple_statement ::= TK_RETURN statement_return_rest
            self.DEBUG("m TK_RETURN")
            self.update_token()
            self.statement_return_rest()
        elif (self.token_in(first_block)):
            #simple_statement ::= block
            self.block()
        elif (self.token_in(first_expression)):
            #simple_statement ::= expression
            self.expression()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< simple_statement")

    def statement_return_rest(self, st = None):
        self.DEBUG("> statement_return_rest")
        if (self.match_token(TK_SEMICOLON)):
            #statement_return_rest ::= TK_SEMICOLON
            self.DEBUG("m TK_SEMICOLON")
            self.update_token()
        elif (self.token_in(first_expression)):
            #statement_return_rest ::= expression TK_SEMICOLON
            self.expression()
            if not (self.match_token(TK_SEMICOLON)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ; got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_SEMICOLON")
            self.update_token()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< statement_return_rest")

    def expression(self, st = None):
        #expression ::= assignment_expr
        self.DEBUG("> expression")
        self.logical_expr()
        self.assignment_expr()
        self.DEBUG("< expression")

    def assignment_expr(self, st = None):
        self.DEBUG("> assignment_expr")
        if (self.match_token(TK_ASSIGNMENT)):
            #assignment_expr ::= TK_ASSIGNMENT expression
            self.DEBUG("m TK_ASSIGNMENT")
            self.update_token()
            self.expression()
        elif (self.token_in(follow_assignment_expr)):
            #assignment_expr ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< assignment_expr")

    def logical_expr(self, st = None):
        #logical_expr ::= logical_or_expr logical_expr_rest
        self.DEBUG("> logical_expr")
        self.logical_or_expr()
        self.logical_expr_rest()
        self.DEBUG("< logical_expr")

    def logical_expr_rest(self, st = None):
        self.DEBUG("> logical_expr_rest")
        if (self.token_in(first_logical_expr)):
            #logical_expr_rest ::= logical_expr
            self.logical_expr()
        elif (self.token_in(follow_logical_expr_rest)):
            #logical_expr_rest ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< logical_expr_rest")

    def logical_or_expr(self, st = None):
        #logical_or_expr ::= logical_and_expr logical_or_expr_rest
        self.DEBUG("> logical_or_expr")
        self.logical_and_expr()
        self.logical_or_expr_rest()
        self.DEBUG("< logical_or_expr")

    def logical_or_expr_rest(self, st = None):
        self.DEBUG("> logical_or_expr_rest")
        if (self.match_token(TK_OR)):
            #logical_or_expr_rest ::= TK_OR logical_or_expr
            self.DEBUG("m TK_OR")
            self.update_token()
            self.logical_or_expr()
        elif (self.token_in(follow_logical_or_expr_rest)):
            #logical_or_expr_rest ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< logical_or_expr_rest")

    def logical_and_expr(self, st = None):
        #logical_and_expr ::= equality_expr logical_and_expr_rest
        self.DEBUG("> logical_and_expr")
        self.equality_expr()
        self.logical_and_expr_rest()
        self.DEBUG("< logical_and_expr")

    def logical_and_expr_rest(self, st = None):
        self.DEBUG("> logical_and_expr_rest")
        if (self.match_token(TK_AND)):
            #logical_and_expr_rest ::= TK_AND logical_and_expr
            self.DEBUG("m TK_AND")
            self.update_token()
            self.logical_and_expr()
        elif (self.token_in(follow_logical_and_expr_rest)):
            #logical_and_expr_rest ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme()) 
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< logical_and_expr_rest")

    def equality_expr(self, st = None):
        #equality_expr ::= relational_expr equality_expr_rest
        self.DEBUG("> equality_expr")
        self.relational_expr()
        self.equality_expr_rest()
        self.DEBUG("< equality_expr")

    def equality_expr_rest(self, st = None):
        self.DEBUG("> equality_expr_rest")
        if (self.match_token(TK_EQUALS)):
            #equality_expr_rest ::= TK_EQUALS    equality_expr
            self.DEBUG("m TK_EQUALS")
            self.update_token()
            self.equality_expr()
        elif (self.match_token(TK_NOTEQUALS)):
            #equality_expr_rest ::= TK_NOTEQUALS equality_expr
            self.DEBUG("m TK_NOTEQUALS")
            self.update_token()
            self.equality_expr()
        elif (self.token_in(follow_equality_expr_rest)):
            #equality_expr_rest ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< equality_expr_rest")

    def relational_expr(self, st = None):
        #relational_expr ::= term_expr relational_expr_rest
        self.DEBUG("> relational_expr")
        self.term_expr()
        self.relational_expr_rest()
        self.DEBUG("< relational_expr")

    def relational_expr_rest(self, st = None):
        self.DEBUG("> relational_expr_rest")
        if (self.match_token(TK_LT)):
            #relational_expr_rest ::= TK_LT   relational_expr
            self.DEBUG("m TK_LT")
            self.update_token()
            self.relational_expr()
        elif (self.match_token(TK_GT)):
            #relational_expr_rest ::= TK_GT   relational_expr
            self.DEBUG("m TK_GT")
            self.update_token()
            self.relational_expr()
        elif (self.match_token(TK_LTEQ)):
            #relational_expr_rest ::= TK_LTEQ relational_expr
            self.DEBUG("m TK_LTEQ")
            self.update_token()
            self.relational_expr()
        elif (self.match_token(TK_GTEQ)):
            #relational_expr_rest ::= TK_GTEQ relational_expr
            self.DEBUG("m TK_GTEQ")
            self.update_token()
            self.relational_expr()
        elif (self.token_in(follow_relational_expr_rest)):
            #relational_expr_rest ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< relational_expr_rest")

    def term_expr(self, st = None):
        #term_expr ::= factor_expr term_expr_rest
        self.DEBUG("> term_expr")
        self.factor_expr()
        self.term_expr_rest()
        self.DEBUG("< term_expr")

    def term_expr_rest(self, st = None):
        self.DEBUG("> term_expr_rest")
        if (self.match_token(TK_ADD)):
            #term_expr_rest ::= TK_ADD term_expr
            self.DEBUG("m TK_ADD")
            self.update_token()
            self.term_expr()
        elif (self.match_token(TK_SUB)):
            #term_expr_rest ::= TK_SUB term_expr
            self.DEBUG("m TK_SUB")
            self.update_token()
            self.term_expr()
        elif (self.token_in(follow_term_expr_rest)):
            #term_expr_rest ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< term_expr_rest")

    def factor_expr(self, st = None):
        #factor_expr ::= unary_expr factor_expr_rest
        self.DEBUG("> factor_expr")
        self.unary_expr()
        self.factor_expr_rest()
        self.DEBUG("< factor_expr")

    def factor_expr_rest(self, st = None):
        self.DEBUG("> factor_expr_rest")
        if (self.match_token(TK_MUL)):
            #factor_expr_rest ::= TK_MUL factor_expr
            self.DEBUG("m TK_MUL")
            self.update_token()
            self.factor_expr()
        elif (self.match_token(TK_DIV)):
            #factor_expr_rest ::= TK_DIV factor_expr
            self.DEBUG("m TK_DIV")
            self.update_token()
            self.factor_expr()
        elif (self.match_token(TK_MOD)):
            #factor_expr_rest ::= TK_MOD factor_expr
            self.DEBUG("m TK_MOD")
            self.update_token()
            self.factor_expr()
        elif (self.token_in(follow_factor_expr_rest)):
            pass
            #factor_expr_rest ::= LAMBDA
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< factor_expr_rest")

    def unary_expr(self, st = None):
        self.DEBUG("> unary_expr")
        if (self.match_token(TK_ADD)):
            #unary_expr ::= TK_ADD unary_expr
            self.DEBUG("m TK_ADD")
            self.update_token()
            self.unary_expr()
        elif (self.match_token(TK_SUB)):
            #unary_expr ::= TK_SUB unary_expr
            self.DEBUG("m TK_SUB")
            self.update_token()
            self.unary_expr()
        elif (self.match_token(TK_NOT)):
            #unary_expr ::= TK_NOT unary_expr
            self.DEBUG("m TK_NOT")
            self.update_token()
            self.unary_expr()
        elif (self.token_in(first_primary)):
            #unary_expr ::= primary
            self.primary()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< unary_expr")

    def primary(self, st = None):
        self.DEBUG("> primary")
        if (self.token_in(first_literal)):
            #primary ::= literal primary_rest
            self.literal()
            self.primary_rest()
        elif (self.match_token(TK_PAREN_OPEN)):
            #primary ::= TK_PAREN_OPEN expression TK_PAREN_CLOSE primary_rest
            self.DEBUG("m TK_PAREN_OPEN")
            self.update_token()
            self.expression()
            if not (self.match_token(TK_PAREN_CLOSE)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ) got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_CLOSE")
            self.update_token()
            self.primary_rest()
        elif (self.match_token(TK_NEW)):
            #primary ::= TK_NEW TK_IDENTIFIER actual_args primary_rest
            self.DEBUG("m TK_NEW")
            self.update_token()
            if not (self.match_token(TK_IDENTIFIER)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: identifier got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.actual_args()
            self.primary_rest()
        elif (self.match_token(TK_SUPER)):
            #primary ::= TK_SUPER TK_PERIOD TK_IDENTIFIER actual_args primary_rest
            self.DEBUG("m TK_SUPER")
            self.update_token()
            if not (self.match_token(TK_PERIOD)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: . got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PERIOD")
            self.update_token()
            if not (self.match_token(TK_IDENTIFIER)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: identifier got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.actual_args()
            self.primary_rest()
        elif (self.match_token(TK_THIS)):
            #primary ::= TK_THIS primary_rest_this primary_rest
            self.DEBUG("m TK_THIS")
            self.update_token()
            self.primary_rest_this()
            self.primary_rest()
        elif (self.match_token(TK_IDENTIFIER)):
            #primary ::= TK_IDENTIFIER primary_rest_id primary_rest
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.primary_rest_id()
            self.primary_rest()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< primary")

    def primary_rest(self, st = None):
        self.DEBUG("> primary_rest")
        if (self.match_token(TK_PERIOD )):
            #primary_rest ::= TK_PERIOD TK_IDENTIFIER actual_args
            self.DEBUG("m TK_PERIOD")
            self.update_token()
            if not (self.match_token(TK_IDENTIFIER)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: identifier got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.actual_args()
            self.primary_rest()
        elif (self.token_in(follow_primary_rest)):
            #primary_rest ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< primary_rest")

    def primary_rest_this(self, st = None):
        self.DEBUG("> primary_rest_this")
        if (self.match_token(TK_PERIOD )):
            #primary_rest_this ::= TK_PERIOD TK_IDENTIFIER
            self.DEBUG("m TK_PERIOD")
            self.update_token()
            if not (self.match_token(TK_IDENTIFIER)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: identifier got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_IDENTIFIER")
            self.update_token()
            self.primary_rest_id()
        # TODO
        # see primary_rest_id for why this is commented out

        #elif (self.token_in(follow_primary_rest_this)):
        #    #primary_rest_this ::= LAMBDA
        #    pass
        #else:
        #    self.DEBUG("ERROR CT: " + self.current_token().lexeme())
        #    errormsg = "Expected:  got " + self.current_token().lexeme()
        #    raise SyntacticError(self, errormsg)
        self.DEBUG("< primary_rest_this")

    def primary_rest_id(self, st = None):
        self.DEBUG("> primary_rest_id")
        if (self.token_in(first_actual_args)):
            #primary_rest_id ::= actual_args
            self.actual_args()
        # TODO
        # commenting out this because follow_primary_rest_id seems to be wrong
        # if you have id = id, it enters primary_rest_id and doesn't recognize = 
        # as belonging to the follow set for primary

        #elif (self.token_in(follow_primary_rest_id)):
        #    #primary_rest_id ::= LAMBDA
        #    pass
        #else:
        #    self.DEBUG("ERROR CT: " + self.current_token().lexeme())
        #    errormsg = "Expected:  got " + self.current_token().lexeme()
        #    raise SyntacticError(self, errormsg)
        self.DEBUG("< primary_rest_id")

    def literal(self, st = None):
        #literal ::= TK_NULL
        #literal ::= TK_TRUE
        #literal ::= TK_FALSE
        #literal ::= TK_INT_LITERAL
        #literal ::= TK_CHAR_LITERAL
        #literal ::= TK_STRING_LITERAL
        self.DEBUG("> literal")
        if not (self.token_in([TK_NULL, TK_TRUE, TK_FALSE, TK_INT_LITERAL, TK_CHAR_LITERAL, TK_STRING_LITERAL])):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected a literal value, got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m LITERAL")
        self.update_token()
        self.DEBUG("< literal")

    def actual_args(self, st = None):
        #actual_args ::= TK_PAREN_OPEN actual_args_rest
        self.DEBUG("> actual_args")
        if not (self.match_token(TK_PAREN_OPEN)):
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected: ) got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("m TK_PAREN_OPEN")
        self.update_token()
        self.actual_args_rest()
        self.DEBUG("< actual_args")

    def actual_args_rest(self, st = None):
        self.DEBUG("> actual_args_rest")
        if (self.match_token(TK_PAREN_CLOSE)):
            #actual_args_rest ::= TK_PAREN_CLOSE
            self.DEBUG("m TK_PAREN_CLOSE")
            self.update_token()
        elif (self.token_in(first_expr_list)):
            #actual_args_rest ::= expr_list TK_PAREN_CLOSE
            self.DEBUG("p expr_list")
            self.expr_list()
            if not (self.match_token(TK_PAREN_CLOSE)):
                self.DEBUG("ERROR CT: " + self.current_token().lexeme())
                errormsg = "Expected: ) got " + self.current_token().lexeme()
                raise SyntacticError(self, errormsg)
            self.DEBUG("m TK_PAREN_CLOSE")
            self.update_token()
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< actual_args_rest")

    def expr_list(self, st = None):
        #expr_list ::= expression expr_list_rest
        self.DEBUG("> expr_list")
        self.expression()
        self.expr_list_rest()
        self.DEBUG("< expr_list")

    def expr_list_rest(self, st = None):
        self.DEBUG("> expr_list_rest")
        if (self.match_token(TK_COMMA)):
            #expr_list_rest ::= TK_COMMA expr_list
            self.DEBUG("m TK_COMMA")
            self.update_token()
            self.expr_list()
        elif (self.token_in(follow_expr_list_rest)):
            #expr_list_rest ::= LAMBDA
            pass
        else:
            self.DEBUG("ERROR CT: " + self.current_token().lexeme())
            errormsg = "Expected:  got " + self.current_token().lexeme()
            raise SyntacticError(self, errormsg)
        self.DEBUG("< expr_list_rest")

