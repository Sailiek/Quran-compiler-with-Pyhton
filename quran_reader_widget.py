from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLineEdit, 
                                    QPushButton, QLabel, QCompleter)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QKeyEvent
from quran_widgets_common import QuranWidgetBase
from chapter_suggestions import ChapterSuggestionModel
from test_skuld import translate_aya
from googletrans import Translator

class SuggestionLineEdit(QLineEdit):
    def __init__(self, suggestion_model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.suggestion_model = suggestion_model
        self.current_suggestion = None
        self.setPlaceholderText("Enter chapter ID or name")
        
        # Initialize completer
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.string_model = QStringListModel()
        self.completer.setModel(self.string_model)
        self.setCompleter(self.completer)
        
        self.textChanged.connect(self.on_text_changed)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Tab and self.current_suggestion:
            # Complete with suggestion on Tab press
            self.setText(self.current_suggestion)
            self.current_suggestion = None
            self.setPlaceholderText("Enter chapter ID or name")
        else:
            super().keyPressEvent(event)

    def on_text_changed(self, text: str):
        if not text:
            self.string_model.setStringList([])
            return
            
        # Get all matching suggestions
        matches = self.suggestion_model.get_all_matches(text)
        if matches:
            # Update completer model with matches
            self.string_model.setStringList(matches)
            self.current_suggestion = matches[0]
            # Show completion popup if there are matches
            self.completer.complete()
        else:
            self.current_suggestion = None
            self.string_model.setStringList([])

class QuranReaderWidget(QuranWidgetBase):
    def __init__(self):
        super().__init__()
        
        # Initialize suggestion model
        self.suggestion_model = ChapterSuggestionModel()
        
        # Create input fields layout
        input_layout = QHBoxLayout()
        
        # Chapter input field with suggestions
        chapter_layout = QVBoxLayout()
        chapter_label = QLabel("Chapter (ID or Name):")
        self.chapter_input = SuggestionLineEdit(self.suggestion_model)
        chapter_layout.addWidget(chapter_label)
        chapter_layout.addWidget(self.chapter_input)
        
        # Verse input field
        verse_layout = QVBoxLayout()
        verse_label = QLabel("Verse (Number or Text):")
        self.verse_input = QLineEdit()
        self.verse_input.setPlaceholderText("Enter verse number or text")
        verse_layout.addWidget(verse_label)
        verse_layout.addWidget(self.verse_input)
        
        # Add input layouts to horizontal layout
        input_layout.addLayout(chapter_layout)
        input_layout.addLayout(verse_layout)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Button style
        button_style = """
            QPushButton {
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f8f9fa;
            }
            QPushButton:hover {
                background-color: #e2e2e2;
                color: black;
                border-color: #cccccc;
            }
            QPushButton:disabled {
                background-color: #e9ecef;
                color: #6c757d;
                border-color: #dee2e6;
            }
        """
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_verse)
        self.search_button.setStyleSheet(button_style)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_inputs)
        self.clear_button.setStyleSheet(button_style)
        
        buttons_layout.addWidget(self.search_button)
        buttons_layout.addWidget(self.clear_button)
        
        # Add all widgets to main layout
        self.layout.insertLayout(0, input_layout)
        self.layout.insertLayout(1, buttons_layout)
        self.layout.addLayout(self.nav_layout)
        self.layout.addLayout(self.audio_layout)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.background_label, 0, Qt.AlignCenter)
        
        # Set minimum size
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

    def show_error(self, message):
        """Display error message in status label"""
        if not hasattr(self, 'status_label'):
            self.status_label = QLabel()
            self.status_label.setStyleSheet("color: red;")
            self.layout.insertWidget(2, self.status_label)
        self.status_label.setText(message)
        self.status_label.show()

    def show_loading(self, show=True):
        """Show/hide loading status"""
        if not hasattr(self, 'status_label'):
            self.status_label = QLabel()
            self.layout.insertWidget(2, self.status_label)
        if show:
            self.status_label.setText("Searching...")
            self.status_label.setStyleSheet("color: blue;")
            self.status_label.show()
        else:
            self.status_label.hide()

    def clear_inputs(self):
        """Clear all inputs and results"""
        self.chapter_input.clear()
        self.verse_input.clear()
        self.result_label.clear()
        if hasattr(self, 'status_label'):
            self.status_label.hide()
        self.play_button.setEnabled(False)
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.background_label.hide()
        self.control_button.hide()
        self.current_chapter = None
        self.current_verse = None

    def search_verse(self):
        # Validate inputs
        chapter_query = self.chapter_input.text().strip()
        verse_query = self.verse_input.text().strip()
        
        if not chapter_query:
            self.show_error("Please enter a chapter ID or name")
            return
            
        if not verse_query:
            self.show_error("Please enter a verse number or text")
            return
        
        # Show loading status
        self.show_loading(True)
        
        # Load Quran data
        if not self.load_quran_data():
            self.show_loading(False)
            return
            
        # Find chapter
        chapter = None
        try:
            # Try as chapter ID
            chapter_id = int(chapter_query)
            if chapter_id <= 0:
                self.show_error("Invalid chapter number: must be greater than 0")
              #  self.show_loading(False)
                return
            for ch in self.quran_data:
                if ch["id"] == chapter_id:
                    chapter = ch
                    break
        except ValueError:
            # Try as chapter name
            chapter_query_lower = chapter_query.lower()
            for ch in self.quran_data:
                if (ch["name"].lower() == chapter_query_lower or 
                    ch["transliteration"].lower() == chapter_query_lower or 
                    ch["translation"].lower() == chapter_query_lower):
                    chapter = ch
                    break
        
        if not chapter:
            self.show_error("Chapter not found")
            return
            
        # Find verse
        verse = None
        try:
            # Try as verse number
            verse_num = int(verse_query)
            if verse_num <= 0:
                self.show_error("Invalid verse number: must be greater than 0")
               # self.show_loading(False)
                return
            if verse_num > chapter["total_verses"]:
                self.show_error(f"Chapter {chapter['name']} ({chapter['translation']}) only has {chapter['total_verses']} verses")
                #self.show_loading(False)
                return
            verse = chapter["verses"][verse_num - 1]
        except ValueError:
            # Try as verse text
            verse_query_lower = verse_query.lower()
            for v in chapter["verses"]:
                if (v["text"].lower() == verse_query_lower or 
                    v["translation"].lower() == verse_query_lower):
                    verse = v
                    break
        
        if not verse:
            self.show_error("verse not found")
            return
        
        # Store current chapter and verse
        self.current_chapter = chapter
        self.current_verse = verse
            
        # Hide loading and status
        self.show_loading(False)
        if hasattr(self, 'status_label'):
            self.status_label.hide()
            
        self.display_verse()

    def display_verse(self):
        """Display the current verse"""
        if not self.current_chapter or not self.current_verse:
            return
        self.vf= translate_aya(self.current_verse['translation'])
        translator = Translator()
        self.es=translator.translate(self.current_verse['translation'], dest='es').text 
        # Format and display the verse
        formatted_text = self.format_verse_display(chapter=self.current_chapter, 
            verse=self.current_verse, 
            include_tafsir=True, 
            vf=self.vf,
            es=self.es
            )
        self.result_label.setText(formatted_text)
        
        # Enable audio controls
        self.play_button.setEnabled(True)
        
        # Update navigation buttons
        is_first_verse_overall = self.current_chapter['id'] == 1 and self.current_verse['id'] == 1
        is_last_verse_overall = (self.current_chapter['id'] == len(self.quran_data) and 
                               self.current_verse['id'] == self.current_chapter['total_verses'])
        
        self.prev_button.setEnabled(not is_first_verse_overall)
        self.next_button.setEnabled(not is_last_verse_overall)

    def show_previous_verse(self):
        if not self.current_chapter or not self.current_verse:
            return
            
        if self.current_verse['id'] > 1:
            # Previous verse in same chapter
            self.current_verse = self.current_chapter['verses'][self.current_verse['id'] - 2]
        else:
            # Last verse of previous chapter
            if self.current_chapter['id'] > 1:
                for chapter in self.quran_data:
                    if chapter['id'] == self.current_chapter['id'] - 1:
                        self.current_chapter = chapter
                        self.current_verse = chapter['verses'][-1]
                        break
            else:
                self.show_error("This is the first verse in the Quran")
                return
                
        self.display_verse()

    def show_next_verse(self):
        if not self.current_chapter or not self.current_verse:
            return
            
        if self.current_verse['id'] < self.current_chapter['total_verses']:
            # Next verse in same chapter
            self.current_verse = self.current_chapter['verses'][self.current_verse['id']]
        else:
            # First verse of next chapter
            if self.current_chapter['id'] < len(self.quran_data):
                for chapter in self.quran_data:
                    if chapter['id'] == self.current_chapter['id'] + 1:
                        self.current_chapter = chapter
                        self.current_verse = chapter['verses'][0]
                        break
            else:
                self.show_error("This is the last verse in the Quran")
                return
                
        self.display_verse()
