from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QComboBox
from PyQt5.QtCore import Qt
from quran_widgets_common import QuranWidgetBase
from verseSugge import QuranVerseMatcher
import requests
from engine import lexical, syntax_lines
import settings
from test_skuld import translate_aya
from maining import analyzeee
import settings
from interface import analyze_input
from logger import logevent
from test_skuld import skuld


from typing import Optional, Dict, List
import logging

class SearchWidget(QuranWidgetBase):
    def __init__(self):
        super().__init__()
        logevent('Starting app\n')

        # Input field for entering the verse
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter Quran verse")

        # Dropdown for language selection (English or Arabic)
        self.language_selector = QComboBox()
        self.language_selector.addItem("English")
        self.language_selector.addItem("Arabic")

        # Button to check the verse
        self.check_button = QPushButton("Check Verse")
        self.check_button.clicked.connect(self.check_verse)

        # Add widgets to the main layout
        self.layout.insertWidget(0, self.input_field)
        self.layout.insertWidget(1, self.language_selector)
        self.layout.insertWidget(2, self.check_button)
        self.layout.addLayout(self.nav_layout)
        self.layout.addLayout(self.audio_layout)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.background_label, 0, Qt.AlignCenter)

        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize state
        
        self.setup_connections()

    
    def reset_states(self):
        settings.lex_state = {"output": ""}
        settings.syn_state = {"output": ""}


    
    def setup_connections(self):
        """Set up signal/slot connections"""
        self.input_field.textChanged.connect(self.on_input_changed)

    def on_input_changed(self, text: str):
        """Enable/disable check button based on input"""
        self.check_button.setEnabled(bool(text.strip()))

    def show_error(self, message: str, title: str = "Error"):
        """Display error message using QMessageBox"""
        self.logger.error(message)
        QMessageBox.warning(self, title, message)

    def check_verse(self):
        """Check the entered verse against the Quran database"""
        entered_verse = self.input_field.text().strip()
        selected_language = self.language_selector.currentText()
        
        # Clear previous results
        self.result_label.clear()
        self.reset_states()

        # Disable the button while processing to prevent multiple clicks
        self.check_button.setEnabled(False)
        
        if not entered_verse:
            self.show_error("Please enter a verse to search")
            self.check_button.setEnabled(True)  # Re-enable the button after error
            return

        if not self.load_quran_data():
            self.show_error("Failed to load Quran data")
            self.check_button.setEnabled(True)  # Re-enable the button after error
            return

        try:
            # Find the verse based on the selected language
            if selected_language == "English":
                try:
                    skuld_output, errors = skuld(entered_verse)  
                    formatted_text = self.format_verse_display(
                        chapter=self.current_chapter,
                        verse=self.current_verse,
                        include_tafsir=True,
                        api_results=None,
                        vf=None,
                        skuld_output=skuld_output  
                    )
                    self.result_label.setText(formatted_text)
                    
                    self.find_similar_verses(entered_verse)
                        
                    
                except Exception as e:
                    self.show_error(f"Error in lexical/syntactic analysis: {e}")
                

                for chapter in self.quran_data:
                    for verse in chapter["verses"]:
                        # Match the English translastion
                        if verse["translation"].strip().lower() == entered_verse.lower():
                            self.vf = translate_aya(entered_verse)
                            self.current_chapter = chapter
                            self.current_verse = verse
                            self.display_verse()
                            self.check_button.setEnabled(True)  # Re-enable after processing
                            return
                # If no match is found
                
                self.check_button.setEnabled(True)

            elif selected_language == "Arabic":
                results = analyzeee(entered_verse)
                self.display_analysis_results(results)
                self.check_button.setEnabled(True)  # Re-enable after processing
                return

        except Exception as e:
            self.show_error(f"Error during analysis: {e}")
            self.check_button.setEnabled(True)  # Re-enable after error
            # Handle cases where there's no exact match or use ML model
            if self.find_exact_match(entered_verse):
                return
            self.find_similar_verses(entered_verse)
            
        except Exception as e:
            self.logger.exception("Error during verse search")
            self.show_error(f"An error occurred while searching: {str(e)}")
            self.check_button.setEnabled(True)  # Re-enable after error

    def display_analysis_results(self, results):
        """Display the results in the UI"""
        if "error" in results:
            self.show_error(f"Error during analysis: {results['error']}")
        else:
            # Format Lexical, Syntactic, and Semantic outputs for Arabic and English
            lexical_output = f"Lexical Analysis: {results['lexical']['output']}\nError: {results['lexical']['is_error']}"
            syntactic_output = f"Syntactic Analysis: {results['syntactic']['output']}\nError: {results['syntactic']['is_error']}"
            semantic_output = f"Semantic Analysis: {results['semantic']['output']}\nError: {results['semantic']['is_error']}"

            # Update the UI with analysis results (Arabic or English based on input)
            self.result_label.setText(f"{lexical_output}\n\n{syntactic_output}\n\n{semantic_output}")

            # You can also add a separator or style to distinguish between English and Arabic results
            # For example:
            # self.result_label.setText(f"{lexical_output}\n\n{syntactic_output}\n\n{semantic_output}\n\n-- Arabic Analysis --")

    def find_exact_match(self, entered_verse: str) -> bool:
        """Find exact match for the entered verse"""
        for chapter in self.quran_data:
            for verse in chapter["verses"]:
                if verse["translation"].strip().lower() == entered_verse.lower():
                    self.current_chapter = chapter
                    self.current_verse = verse
                    self.display_verse()
                    return True
        return False

    def find_similar_verses(self, entered_verse: str):
        """Use ML model to find similar verses"""
        try:
            matcher = QuranVerseMatcher('quran_ar_eng.json')
            results = matcher.find_verse_match(entered_verse)
            
            if results['matches']:
                self.display_matches(results)
            else:
                self.show_error("No matching verses found", "Search Results")
                
        except Exception as e:
            self.logger.exception("Error in ML matching")
            raise Exception(f"Error in verse matching: {str(e)}")

    def display_matches(self, results: Dict):
        """Display the matching verses found"""
        matches_text = "Similar verses found:\n\n"
        for match in results['matches']:
            matches_text += (
                f"Surah: {match['surah_name']} (No. {match['surah_number']})\n"
                f"Verse {match['verse_number']}\n"
                f"Similarity: {match['similarity_score']:.2f}\n"
                f"Text: {match['verse_text']}\n\n"
            )
        
        self.result_label.setText(matches_text)
        self.play_button.setEnabled(True)

    def fetch_api_results(self, query: str) -> List:
        """Fetch results from the API"""
        try:
            response = requests.post(
                "http://127.0.0.1:5000/analyze_verse",
                json={"query": query},
                timeout=5  # Add timeout
            )
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            self.show_error(f"Failed to connect to the API: {str(e)}")
            return []

    def display_verse(self):
        """Display the current verse along with API results"""
        if not self.current_chapter or not self.current_verse:
            return

        # Fetch API results
        api_results = self.fetch_api_results(self.current_verse['translation'])
        skuld_output = None
        similar_verses = None

        try:
            # Try Skuld analysis
            skuld_output, errors = skuld(self.current_verse['translation'])
        except Exception as e:
            # Capture Skuld errors and find similar verses
            skuld_output = f"Error in Skuld analysis: {str(e)}"
            similar_verses = self.find_similar_verses(self.current_verse['translation'])

        # Format and display the verse with all relevant information
        formatted_text = self.format_verse_display(
            chapter=self.current_chapter, 
            verse=self.current_verse, 
            include_tafsir=True, 
            api_results=api_results,
            vf=self.vf,
            skuld_output=skuld_output,
            similar_verses=similar_verses
        )
        self.result_label.setText(formatted_text)

        # Display lexical and syntactic analysis output if available
        output = settings.lex_state.get("output", "")  # From lexical function
        syntax_output = settings.syn_state.get("output", "")  # From syntax_lines function
        if output or syntax_output:
            self.result_label.setText(formatted_text + "<br><br>" + output + "<br>" + syntax_output)

        # Enable audio controls
        self.play_button.setEnabled(True)

        # Update UI state
        self.update_ui_state()

    def update_ui_state(self):
        """Update UI elements based on current state"""
        self.play_button.setEnabled(True)
        
        # Update navigation buttons
        is_first_verse = self.is_first_verse()
        is_last_verse = self.is_last_verse()
        
        self.prev_button.setEnabled(not is_first_verse)
        self.next_button.setEnabled(not is_last_verse)

    def is_first_verse(self) -> bool:
        """Check if current verse is the first verse overall"""
        return (self.current_chapter["id"] == 1 and 
                self.current_verse["id"] == 1)

    def is_last_verse(self) -> bool:
        """Check if current verse is the last verse overall"""
        return (self.current_chapter["id"] == len(self.quran_data) and 
                self.current_verse["id"] == self.current_chapter["total_verses"])

    def show_previous_verse(self):
        """Navigate to the previous verse"""
        if not self.current_chapter or not self.current_verse:
            return

        try:
            if self.current_verse["id"] > 1:
                # Previous verse in same chapter
                self.current_verse = self.current_chapter["verses"][self.current_verse["id"] - 2]
            elif self.current_chapter["id"] > 1:
                # Last verse of previous chapter
                prev_chapter = next(
                    (chapter for chapter in self.quran_data 
                     if chapter["id"] == self.current_chapter["id"] - 1),
                    None
                )
                if prev_chapter:
                    self.current_chapter = prev_chapter
                    self.current_verse = prev_chapter["verses"][-1]
            else:
                QMessageBox.information(self, "Navigation", "This is the first verse in the Quran")
                return

            self.display_verse()
            
        except Exception as e:
            self.logger.exception("Error navigating to previous verse")
            self.show_error(f"Navigation error: {str(e)}")

    def show_next_verse(self):
        """Navigate to the next verse"""
        if not self.current_chapter or not self.current_verse:
            return

        try:
            if self.current_verse["id"] < self.current_chapter["total_verses"]:
                # Next verse in same chapter
                self.current_verse = self.current_chapter["verses"][self.current_verse["id"]]
            elif self.current_chapter["id"] < len(self.quran_data):
                # First verse of next chapter
                next_chapter = next(
                    (chapter for chapter in self.quran_data 
                     if chapter["id"] == self.current_chapter["id"] + 1),
                    None
                )
                if next_chapter:
                    self.current_chapter = next_chapter
                    self.current_verse = next_chapter["verses"][0]
            else:
                QMessageBox.information(self, "Navigation", "This is the last verse in the Quran")
                return

            self.display_verse()
            
        except Exception as e:
            self.logger.exception("Error navigating to next verse")
            self.show_error(f"Navigation error: {str(e)}")