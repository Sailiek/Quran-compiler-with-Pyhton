import settings
from engine import lexical, syntax_lines

def analyze_input(input_text):
    # Reset analysis results
    settings.lex_state["output"] = ""
    settings.lex_state["is_error"] = False

    settings.syn_state["output"] = ""
    settings.syn_state["is_error"] = False

    settings.sem_state["output"] = ""
    settings.sem_state["is_error"] = False

    # Line number will be initialized in lexical()

    # Perform analysis
    lexical(input_text)
    syntax_lines(input_text)

    # Collect results
    results = {
        "lexical": {
            "output": settings.lex_state["output"],
            "is_error": settings.lex_state["is_error"]
        },
        "syntactic": {
            "output": settings.syn_state["output"],
            "is_error": settings.syn_state["is_error"]
        },
        "semantic": {
            "output": settings.sem_state["output"],
            "is_error": settings.sem_state["is_error"]
        }
    }
    return results
