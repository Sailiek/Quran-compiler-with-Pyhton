from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QComboBox
from PyQt5.QtCore import Qt
from quran_widgets_common import QuranWidgetBase
import requests
from engine import lexical, syntax_lines
import settings
from test_skuld import translate_aya
from maining import analyzeee
import settings
from interface import analyze_input
from logger import logevent



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

        # Set size constraints
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        
    def reset_states(self):
        settings.lex_state = {"output": ""}
        settings.syn_state = {"output": ""}


    def show_error(self, message):
        """Display error message using QMessageBox"""
        QMessageBox.warning(self, "Error", message)

    def check_verse(self):
        entered_verse = self.input_field.text().strip()
        selected_language = self.language_selector.currentText()
        self.result_label.clear()
        self.reset_states()
        if not self.load_quran_data():
            return

        try:
            # Find the verse based on the selected language
            if selected_language == "English":
                for chapter in self.quran_data:
                    for verse in chapter["verses"]:                        
                            # Match the English translation
                        if verse["translation"].strip().lower() == entered_verse.lower():
                            self.vf=translate_aya(entered_verse)
                            self.current_chapter = chapter
                            self.current_verse = verse
                            self.display_verse()
                            return
                        else:
                            self.result_label.setText("Verse not found.")
                            self.play_button.setEnabled(False)
                            self.prev_button.setEnabled(False)
                            self.next_button.setEnabled(False)
            elif selected_language == "Arabic":
                results = analyzeee(entered_verse)
                self.display_analysis_results(results)
                return
                # for chapter in self.quran_data:
                #     for verse in chapter["verses"]:                        
                #             # Match the English translation
                #         if verse["text"].strip().lower() == entered_verse.lower():
                #             self.vf=translate_aya(entered_verse)
                #             self.current_chapter = chapter
                #             self.current_verse = verse
                #             self.display_verse()
                #             return
            return

                        # If no match is found
            self.result_label.setText("Verse not found.")
            self.play_button.setEnabled(False)
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)

        except Exception as e:
            self.show_error(f"Error during analysis: {e}")
            self.play_button.setEnabled(False)
    
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

    def display_verse(self):
        """Display the current verse along with API results."""
        if not self.current_chapter or not self.current_verse:
            return

        # Prepare data for API request
        query = self.current_verse['translation']
        api_results = []

        try:
            # Call the API with the current verse translation
            response = requests.post(
                "http://127.0.0.1:5000/analyze_verse",  # Update with actual API URL if needed
                json={"query": query},
            )
            if response.status_code == 200:
                api_results = response.json().get("results", [])
            else:
                self.show_error(f"API Error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.show_error(f"Failed to connect to the API: {e}")

        # Format and display the verse along with API results
        formatted_text = self.format_verse_display(
            self.current_chapter, 
            self.current_verse, 
            include_tafsir=True, 
            api_results=api_results,
            vf=self.vf
        )
        self.result_label.setText(formatted_text)

        # Display lexical and syntactic analysis output
        output = settings.lex_state["output"]  # From lexical function
        syntax_output = settings.syn_state["output"]  # From syntax_lines function
        if output or syntax_output:
            self.result_label.setText(formatted_text + "\n\n" + output + "\n" + syntax_output)

        # Enable audio controls
        self.play_button.setEnabled(True)

        # Update navigation buttons
        is_first_verse_overall = self.current_chapter["id"] == 1 and self.current_verse["id"] == 1
        is_last_verse_overall = (
            self.current_chapter["id"] == len(self.quran_data) and 
            self.current_verse["id"] == self.current_chapter["total_verses"]
        )
        self.prev_button.setEnabled(not is_first_verse_overall)
        self.next_button.setEnabled(not is_last_verse_overall)

    def show_previous_verse(self):
        if not self.current_chapter or not self.current_verse:
            return

        if self.current_verse["id"] > 1:
            # Previous verse in same chapter
            self.current_verse = self.current_chapter["verses"][self.current_verse["id"] - 2]
            self.display_verse()
        else:
            # Last verse of previous chapter
            if self.current_chapter["id"] > 1:
                for chapter in self.quran_data:
                    if chapter["id"] == self.current_chapter["id"] - 1:
                        self.current_chapter = chapter
                        self.current_verse = chapter["verses"][-1]
                        self.display_verse()
                        return
            else:
                QMessageBox.information(self, "Navigation", "This is the first verse in the Quran")

    def show_next_verse(self):
        if not self.current_chapter or not self.current_verse:
            return

        if self.current_verse["id"] < self.current_chapter["total_verses"]:
            # Next verse in same chapter
            self.current_verse = self.current_chapter["verses"][self.current_verse["id"]]
            self.display_verse()
        else:
            # First verse of next chapter
            if self.current_chapter["id"] < len(self.quran_data):
                for chapter in self.quran_data:
                    if chapter["id"] == self.current_chapter["id"] + 1:
                        self.current_chapter = chapter
                        self.current_verse = chapter["verses"][0]
                        self.display_verse()
                        return
            else:
                QMessageBox.information(self, "Navigation", "This is the last verse in the Quran")
