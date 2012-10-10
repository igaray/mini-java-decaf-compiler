#!/usr/bin/python2

import sys
from scanner import *
from tokens  import *
from errors  import LexicalError

def pretty_print_error_message(input_filepath, exc):
    input_file = open(input_filepath, 'r')
    line       = exc.line
    col        = exc.col
    print exc
    print "In line %s:%s" % (line, col)
    i = 0
    line_str = ""
    while (i < line):
        line_str = input_file.readline()
        i += 1
    if len(line_str) > 0 and line_str[-1] == "\n":
        print line_str,
    else:
        print line_str
    i = 1
    while (i < col):
        sys.stdout.write("-")
        i += 1
    print "^"
    input_file.close()

def usage():
    usage_str = """
    Usage:
        scanner INPUTFILE [OUTPUTFILE]

    """
    print usage_str


def run_scanner(input_filepath, output_filepath = None):
    try:
        if (output_filepath != None):
            output_file = open(output_filepath, 'w')
            sys.stdout  = output_file
    except IOError as ioe:
        print "Error: no such file."
        sys.exit()

    scanner = Scanner(input_filepath)
    while True:
        try:
            token = scanner.get_token()
            if token.type == TK_EOF:
                break
        except LexicalError as le:
            pretty_print_error_message(input_filepath, le)
            sys.exit()
        print token    

    if (output_filepath != None):
        output_file.close()

if __name__ == "__main__":
    argv_len = len(sys.argv)
    if not ((argv_len == 3) or (argv_len == 2)):
        usage()
        sys.exit()

    input_filepath = sys.argv[1]

    if (argv_len == 3):
        output_filepath = sys.argv[2]
        run_scanner(input_filepath, output_filepath)
    else:
        run_scanner(input_filepath)
