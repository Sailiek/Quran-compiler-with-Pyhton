from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from quran_widgets_common import QuranWidgetBase
import requests

class SearchWidget(QuranWidgetBase):
    def __init__(self):
        super().__init__()
        
        # Input field for entering the verse
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter Quran verse in English")

        # Button to check the verse
        self.check_button = QPushButton("Check Verse")
        self.check_button.clicked.connect(self.check_verse)

        # Add widgets to the main layout at the beginning
        self.layout.insertWidget(0, self.input_field)
        self.layout.insertWidget(1, self.check_button)
        self.layout.addLayout(self.nav_layout)
        self.layout.addLayout(self.audio_layout)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.background_label, 0, Qt.AlignCenter)

        # Set size constraints
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

    def show_error(self, message):
        """Display error message using QMessageBox"""
        QMessageBox.warning(self, "Error", message)

    def check_verse(self):
        entered_verse = self.input_field.text().strip()
        if not self.load_quran_data():
            return

        try:
            # Find the verse
            for chapter in self.quran_data:
                for verse in chapter["verses"]:
                    if verse["translation"].strip().lower() == entered_verse.lower():
                        self.current_chapter = chapter
                        self.current_verse = verse
                        self.display_verse()
                        return

            # If no match is found
            self.result_label.setText("Verse not found.")
            self.play_button.setEnabled(False)
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
        except Exception as e:
            self.show_error(f"Error reading JSON file: {e}")
            self.play_button.setEnabled(False)

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
            api_results=api_results
        )
        self.result_label.setText(formatted_text)

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
