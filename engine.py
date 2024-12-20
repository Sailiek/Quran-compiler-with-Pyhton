import ply.lex as lex
import ply.yacc as yacc
from mylex import tokens, t_ignore, t_DEF_N, t_NEG, t_PREP, t_CONJ, t_EMPH, t_CERT, t_DEM, t_REL, t_REM, t_INTG, t_VERB, t_UNDEF_N, t_PRON_PLURAL, t_PRON, t_SUB, t_DIVIDER, t_newline, t_error
from myyacc import p_surah, p_verse_n, p_verse, p_ns, p_vs, p_pp, p_sc, p_object, p_subject, p_adj, p_error
import settings
from logger import logevent, logeventinfo

def lexical(lines):
    # Ensure state is reset before analysis
    settings.init()
    logevent('Starting Lexical analysis...\n')
    settings.lex_state["output"] += "| LINE | COL |  TYPE  | TOKEN\n-------------------------------\n"
    logeventinfo("\n| LINE | COL |  TYPE  | TOKEN\n-------------------------------\n")

    # Create a new lexer instance for each analysis
    lexer = lex.lex()
    lexer.lineno = 1
    settings.lineno = 1
    lexer.input(lines)
    while 1:
        tok = lexer.token()        
        if not tok: break
        logeventinfo("|{2: <6}|{3: <5}|{1: <8}|{0: <9}\n".format(tok.value, tok.type, settings.lineno, tok.lexpos))
        settings.lex_state["output"] += "|{2: <6}|{3: <5}|{1: <8}|{0: <9}\n".format(tok.value, tok.type, settings.lineno, tok.lexpos)
        if (tok.type == 'DIVIDER'): 
            logeventinfo("-------------------------------\n")
            settings.lex_state["output"] += "-------------------------------"


def syntax_lines(lines):
    logevent('Starting syntactic and semantic analysis...\n')
    # Create a new parser instance for each analysis
    from myyacc import yacc
    local_parser = yacc.yacc(debug=True)
    res = local_parser.parse(lines, tracking=True, debug=False)
    print("parser result :\n", res)
    if(res != None):
        settings.syn_state["output"] += "parser result:\n" + res + "\n"
        logeventinfo("parser result:\n" + res + "\n")
