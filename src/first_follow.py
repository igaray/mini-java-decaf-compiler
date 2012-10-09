from tokens import *

primitive_types                   = set([TK_BOOLEAN, TK_CHAR, TK_INT, TK_STRING])
void_type                         = set([TK_VOID])
identifiers                       = set([TK_IDENTIFIER])
method_types                      = primitive_types | void_type | identifiers
literals                          = set([TK_NULL, TK_TRUE, TK_FALSE, TK_INT_LITERAL, TK_CHAR_LITERAL, TK_STRING_LITERAL])
if_for_while                      = set([TK_IF, TK_FOR, TK_WHILE])
operators                         = set([])
unary_operators                   = set([TK_ADD, TK_SUB, TK_NOT])

first_actual_args                 = set([TK_PAREN_OPEN])
first_block                       = set([TK_BRACE_OPEN])

first_classdef_start              = set([TK_CLASSDEF])
first_classdef_ctor_rest          = set([TK_PAREN_OPEN])
first_classdef_method             = method_types

first_class                       = set([TK_CLASS])
first_class_ctor_rest             = set([TK_PAREN_OPEN])
first_class_method                = method_types
first_class_method_rest           = set([TK_PAREN_OPEN])
first_class_start                 = set([TK_CLASS])
first_class_var_declaration_list  = set([TK_COMMA, TK_SEMICOLON])

first_primitive_type              = primitive_types
first_primitive_type_void         = primitive_types | void_type

first_primary                     = identifiers | literals | set([TK_PAREN_OPEN, TK_NEW, TK_SUPER, TK_THIS])
first_expression                  = unary_operators | first_primary
first_expr_list                   = first_expression

first_formal_arg_list             = primitive_types | identifiers

first_literal                     = literals

first_logical_expr                = unary_operators | first_primary
first_simple_statement            = first_logical_expr | set([TK_SEMICOLON, TK_RETURN, TK_BRACE_OPEN])
first_closed_statement            = first_simple_statement | if_for_while 
first_open_statement              = if_for_while
first_statement                   = first_closed_statement

follow_classdef_body_rest         = set([TK_BRACE_CLOSE]) # | follow_classdef_ctor_rest
follow_classdef_ctor_or_method    = follow_classdef_body_rest
follow_classdef_ctor_rest         = follow_classdef_ctor_or_method
follow_classdef_method_rest       = follow_classdef_body_rest | follow_classdef_ctor_or_method
follow_classdef_methods           = follow_classdef_method_rest

follow_class_start                = set([TK_EOF])
follow_class_start_rest           = follow_class_start
follow_class_body_rest            = set([TK_BRACE_CLOSE]) # | follow_class_var_declaration_list

first_class_body_rest             = identifiers | void_type | primitive_types | set([TK_BRACE_CLOSE])
follow_class_ctor_or_method       = first_class_body_rest
follow_class_ctor_rest            = follow_class_ctor_or_method

follow_class_field_ctor_or_method = follow_class_body_rest
follow_class_field_or_method      = follow_class_field_ctor_or_method
follow_class_method_rest          = follow_class_body_rest | follow_class_field_or_method
follow_class_var_declaration_list = follow_class_field_or_method
follow_class_methods              = follow_class_method_rest

follow_super                      = set([TK_BRACE_OPEN])
first_super                       = set([TK_EXTENDS]) | follow_super

follow_formal_arg_list            = set([TK_PAREN_CLOSE])
follow_formal_arg_list_rest       = follow_formal_arg_list

follow_assignment_expr            = set([TK_SEMICOLON, TK_PAREN_CLOSE, TK_COMMA])
follow_logical_expr               = set([TK_SEMICOLON, TK_PAREN_CLOSE, TK_ASSIGNMENT, TK_COMMA])
follow_logical_expr_rest          = follow_logical_expr
follow_logical_or_expr_rest       = first_expression | follow_logical_expr
first_logical_or_expr_rest        = set([TK_OR]) | follow_logical_or_expr_rest
follow_logical_and_expr_rest      = first_logical_or_expr_rest
first_logical_and_expr_rest       = set([TK_AND]) | follow_logical_and_expr_rest
follow_equality_expr              = first_logical_and_expr_rest
follow_equality_expr_rest         = follow_equality_expr
first_equality_expr_rest          = set([TK_EQUALS, TK_NOTEQUALS]) | follow_equality_expr_rest
follow_relational_expr            = first_equality_expr_rest
follow_relational_expr_rest       = follow_relational_expr
first_relational_expr_rest        = set([TK_LT, TK_GT, TK_LTEQ, TK_GTEQ]) | follow_relational_expr
follow_term_expr                  = first_relational_expr_rest
follow_term_expr_rest             = follow_term_expr
first_term_expr_rest              = set([TK_ADD, TK_SUB]) | follow_term_expr_rest
follow_factor_expr                = first_term_expr_rest
follow_factor_expr_rest           = follow_factor_expr
first_factor_expr_rest            = set([TK_MUL, TK_DIV, TK_MOD]) | follow_factor_expr_rest
follow_unary_expr                 = first_factor_expr_rest
follow_primary                    = follow_unary_expr
follow_primary_rest               = follow_primary
follow_primary_rest_id            = first_primary
follow_primary_rest_this          = first_primary
follow_expr_list_rest             = set([TK_PAREN_CLOSE])

follow_statements                 = set([TK_BRACE_CLOSE])

