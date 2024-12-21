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


        
    def reset_states(self):
        settings.lex_state = {"output": ""}
        settings.syn_state = {"output": ""}


    def setup_layouts(self):
        """Set up the widget layouts"""
        # Create main layout if it doesn't exist
        if not hasattr(self, 'layout'):
            self.layout = QVBoxLayout()
            self.setLayout(self.layout)

        # Add widgets to the main layout
        self.layout.insertWidget(0, self.input_field)
        self.layout.insertWidget(1, self.check_button)
        
        # Add existing layouts if they exist
        if hasattr(self, 'nav_layout'):
            self.layout.addLayout(self.nav_layout)
        if hasattr(self, 'audio_layout'):
            self.layout.addLayout(self.audio_layout)
        if hasattr(self, 'scroll_area'):
            self.layout.addWidget(self.scroll_area)
        if hasattr(self, 'background_label'):
            self.layout.addWidget(self.background_label, 0, Qt.AlignCenter)

    def setup_connections(self):
        """Set up signal/slot connections"""
        self.check_button.clicked.connect(self.check_verse)
        self.input_field.textChanged.connect(self.on_input_changed)

    def on_input_changed(self, text: str):
        """Enable/disable check button based on input"""
        self.check_button.setEnabled(bool(text.strip()))

    def show_error(self, message: str, title: str = "Error"):
        """Display error message using QMessageBox"""
        # self.logger.error(message)
        QMessageBox.warning(self, title, message)

    def check_verse(self):
        """Check the entered verse against the Quran database"""
        entered_verse = self.input_field.text().strip()
        selected_language = self.language_selector.currentText()
        self.result_label.clear()
        self.reset_states()
        if not self.load_quran_data():
            self.show_error("Failed to load Quran data")
            return

        try:
            # Find the verse based on the selected language
            if selected_language == "English":
                skuld_output, errors = skuld(entered_verse)
                if errors:
                # If there are errors, display them in the terminal
                    print('\n'.join(errors))
                    
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
                            # self.result_label.setText("Verse not found.")
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

    def display_matches(self, results):
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

    def fetch_api_results(self, query: str):
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
            # self.logger.error(f"API request failed: {e}")
            self.show_error(f"Failed to connect to the API: {str(e)}")
            return []

    def display_verse(self):
        """Display the current verse along with API results"""
        if not self.current_chapter or not self.current_verse:
            return

        # Fetch API results
        api_results = self.fetch_api_results(self.current_verse['translation'])

        # Format and display the verse
        formatted_text = self.format_verse_display(
            self.current_chapter, 
            self.current_verse, 
            include_tafsir=True, 
            api_results=api_results,
            vf=self.vf
        )
        self.result_label.setText(formatted_text)

        #Display english lexical and syntactic analysis output
        try:
        # Pass the query to the `skuld` function
            skuld_output, errors = skuld(query)  
            formatted_skuld_output = f"""
            <h3>Lexical and Syntactic Analysis</h3>
            <p>{skuld_output.replace('\n', '<br>')}</p>
            """
            if errors:
                error_output = f"<h4>Errors:</h4><p>{'<br>'.join(errors)}</p>"
                # Append both the analysis and errors to the result label
                self.result_label.setText(self.result_label.text() + formatted_skuld_output + error_output)
            else:
                # Append only the analysis output
                self.result_label.setText(self.result_label.text() + formatted_skuld_output)
        except Exception as e:
            self.show_error(f"Error in lexical/syntactic analysis: {e}")
        
        # Display lexical and syntactic analysis output
        output = settings.lex_state["output"]  # From lexical function
        syntax_output = settings.syn_state["output"]  # From syntax_lines function
        if output or syntax_output:
            self.result_label.setText(formatted_text + "\n\n" + output + "\n" + syntax_output)

        # Enable audio controls
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