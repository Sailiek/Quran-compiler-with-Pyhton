from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from quran_widgets_common import QuranWidgetBase
from verseSugge import QuranVerseMatcher
import requests
from typing import Optional, Dict, List
import logging

class SearchWidget(QuranWidgetBase):
    def __init__(self):
        super().__init__()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize state
        self.setup_ui()
        self.setup_layouts()
        self.setup_connections()

    def setup_ui(self):
        """Initialize and configure UI elements"""
        # Input field for entering the verse
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter Quran verse in English")
        self.input_field.returnPressed.connect(self.check_verse)  # Allow Enter key to trigger search

        # Button to check the verse
        self.check_button = QPushButton("Check Verse")
        self.check_button.setEnabled(False)  # Disable until text is entered
        
        # Set size constraints
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

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
        self.logger.error(message)
        QMessageBox.warning(self, title, message)

    def check_verse(self):
        """Check the entered verse against the Quran database"""
        entered_verse = self.input_field.text().strip()
        if not entered_verse:
            self.show_error("Please enter a verse to search")
            return

        if not self.load_quran_data():
            self.show_error("Failed to load Quran data")
            return

        try:
            # First try exact match
            if self.find_exact_match(entered_verse):
                return

            # If no exact match, use ML model
            self.find_similar_verses(entered_verse)
            
        except Exception as e:
            self.logger.exception("Error during verse search")
            self.show_error(f"An error occurred while searching: {str(e)}")
            self.play_button.setEnabled(False)

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

        # Format and display the verse
        formatted_text = self.format_verse_display(
            self.current_chapter, 
            self.current_verse, 
            include_tafsir=True, 
            api_results=api_results
        )
        self.result_label.setText(formatted_text)

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