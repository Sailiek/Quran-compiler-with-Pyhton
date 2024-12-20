import settings
from interface import analyze_input
from logger import logevent

def analyzeee(input_text):
    logevent('Starting app\n')

    # Initialize settings
    settings.init()

    # Analyze input
    results = analyze_input(input_text)

    # Return the formatted results for display in GUI
    return results

