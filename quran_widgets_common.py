from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                    QLabel, QScrollArea, QSizePolicy, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
import json

class QuranWidgetBase(QWidget):
    def __init__(self):
        super().__init__()
        
        # Define reciters
        self.reciters = [
            {"id": 1, "name": "Mishary Rashid Al-Afasy", "picture": "afassy.jpg", "api_type": "default"},
            {"id": 2, "name": "Abu Bakr Al-Shatri", "picture": "Abu Bakr Al-Shatri.jpg", "api_type": "default"},
            {"id": 3, "name": "Nasser Al Qatami", "picture": "Nasser Al Qatami.jpg", "api_type": "default"},
            {"id": 4, "name": "Ahmed Ibn Ali Al-Ajamy", "picture": "Ahmed_ibn_Ali_al-Ajamy.jpg", "api_type": "everyayah", 
             "api_url": "https://everyayah.com/data/Ahmed_ibn_Ali_al-Ajamy_128kbps_ketaballah.net/"},
            {"id": 5, "name": "Yasser Ad-Dussaryi", "picture": "Yasser_Ad-Dussaryi.png", "api_type": "everyayah",
             "api_url": "https://everyayah.com/data/Yasser_Ad-Dussary_128kbps/"},
            {"id": 6, "name": "Saood Ash-Shuraym", "picture": "Saood_ash-Shuraym.jpg", "api_type": "everyayah",
             "api_url": "https://everyayah.com/data/Saood_ash-Shuraym_128kbps/"}
        ]
        
        # Initialize common attributes
        self.quran_data = None
        self.current_chapter = None
        self.current_verse = None
        
        # Create the main layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Create scroll area for results
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(400)
        
        # Result label
        self.result_label = QLabel()
        self.result_label.setFont(QFont("Traditional Arabic", 12))
        self.result_label.setWordWrap(True)
        self.result_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.result_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create container for result label
        result_container = QWidget()
        result_container_layout = QVBoxLayout(result_container)
        result_container_layout.addWidget(self.result_label)
        result_container_layout.addStretch()
        
        self.scroll_area.setWidget(result_container)
        
        # Navigation buttons layout
        self.nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("← Previous Verse")
        self.next_button = QPushButton("Next Verse →")
        self.prev_button.clicked.connect(self.show_previous_verse)
        self.next_button.clicked.connect(self.show_next_verse)
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.nav_layout.addWidget(self.prev_button)
        self.nav_layout.addWidget(self.next_button)
        
        # Audio control layout
        self.audio_layout = QHBoxLayout()
        
        # Reciter selection combo box
        self.reciter_combo = QComboBox()
        for reciter in self.reciters:
            self.reciter_combo.addItem(reciter["name"])
        self.reciter_combo.currentIndexChanged.connect(self.on_reciter_changed)
        
        # Play button
        self.play_button = QPushButton("Play Recitation")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.play_recitation)
        
        # Control button
        self.control_button = QPushButton("Stop")
        self.control_button.clicked.connect(self.toggle_playback)
        self.control_button.hide()
        
        self.audio_layout.addWidget(self.reciter_combo)
        self.audio_layout.addWidget(self.play_button)
        self.audio_layout.addWidget(self.control_button)
        
        # Background image label for reciter
        self.background_label = QLabel()
        self.background_label.setAlignment(Qt.AlignCenter)
        self.update_reciter_image()
        self.background_label.hide()
        self.background_label.setMaximumSize(200, 200)
        
        # Media player for audio
        self.media_player = QMediaPlayer()
        self.media_player.stateChanged.connect(self.handle_state_changed)

    def load_quran_data(self):
        """Load Quran data from JSON file"""
        if self.quran_data is None:
            try:
                with open('quran_ar_eng.json', 'r', encoding='utf-8') as f:
                    self.quran_data = json.load(f)
                return True
            except Exception as e:
                self.show_error(f"Error loading Quran data: {str(e)}")
                return False
        return True

    def get_audio_url(self):
        """Get the audio URL for the current verse"""
        if not self.current_chapter or not self.current_verse:
            return None
            
        try:
            current_reciter = self.reciters[self.reciter_combo.currentIndex()]
            
            if current_reciter["api_type"] == "default":
                return f"https://quranaudio.pages.dev/{current_reciter['id']}/{self.current_chapter['id']}_{self.current_verse['id']}.mp3"
            else:
                padded_surah = str(self.current_chapter['id']).zfill(3)
                padded_verse = str(self.current_verse['id']).zfill(3)
                return f"{current_reciter['api_url']}{padded_surah}{padded_verse}.mp3"
        except Exception as e:
            self.show_error(f"Failed to construct audio URL: {e}")
            return None

    def play_recitation(self):
        """Play the current verse's recitation"""
        audio_url = self.get_audio_url()
        if audio_url:
            self.media_player.stop()
            self.media_player.setMedia(QMediaContent(QUrl(audio_url)))
            self.media_player.play()
            self.control_button.show()
            self.background_label.show()
            self.play_button.setEnabled(False)
        else:
            self.show_error("Audio URL not found")

    def toggle_playback(self):
        """Toggle between play and pause states"""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.control_button.setText("Start")
        else:
            self.media_player.play()
            self.control_button.setText("Stop")

    def handle_state_changed(self, state):
        """Handle media player state changes"""
        if state == QMediaPlayer.StoppedState:
            self.control_button.hide()
            self.background_label.hide()
            self.play_button.setEnabled(True)

    def on_reciter_changed(self, index):
        """Handle reciter change event"""
        self.update_reciter_image()
        if self.current_chapter and self.current_verse and self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_recitation()

    def update_reciter_image(self):
        """Update the reciter's image"""
        current_reciter = self.reciters[self.reciter_combo.currentIndex()]
        pixmap = QPixmap(current_reciter["picture"])
        scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.background_label.setPixmap(scaled_pixmap)

    def format_verse_display(self, chapter, verse, include_tafsir=False, api_results=None, vf=None, skuld_output=None, similar_verses=None):
        """Format verse display with HTML"""
        formatted_text = f"""
        <div style='margin: 10px;'>
            <h3>Found Verse:</h3>
            <p><b>Chapter:</b> {chapter['name']} ({chapter['translation']})</p>
            <p><b>Chapter ID:</b> {chapter['id']}</p>
            <p><b>Type:</b> {chapter['type'].capitalize()}</p>
            <p><b>Total Verses:</b> {chapter['total_verses']}</p>
            <p><b>Verse Number:</b> {verse['id']}</p>
            <hr>
            <p><b>Arabic Text:</b><br>{verse['text']}</p>
            <p><b>Translation:</b><br>{verse['translation']}</p>
            <p><b>Traduction:</b><br>{vf}</p>
        """
        if include_tafsir:
            formatted_text += f"""
            <p><b>Meaning:</b><br>{verse['tafsir']}</p>
            """
        if api_results:
            formatted_text += "<hr><h3>Similar Verses:</h3>"
            for result in api_results:
                formatted_text += f"""
                <div style="margin: 10px; border: 1px solid #ccc; padding: 10px;">
                    <p><b>Chapter:</b> {result['chapter']}</p>
                    <p><b>Verse:</b> {result['verse']}</p>
                    <p><b>Arabic Text:</b><br>{result['arabic_text']}</p>
                    <p><b>English Text:</b><br>{result['english_text']}</p>
                    <p><b>Similarity Score:</b> {result['similarity_score']:.2f}</p>
                </div>
                """
        if skuld_output:
            formatted_text += f"""
            <hr>
            <h3>Lexical and Syntactic Analysis (Skuld):</h3>
            <p>{skuld_output.replace('\n', '<br>')}</p>
            """
            if "Error" in skuld_output and similar_verses:
                formatted_text += f"""
                <hr>
                <h3>Similar Verses (Error in Skuld Analysis):</h3>
                <ul>
                """
                for similar in similar_verses:
                    formatted_text += f"""
                    <li>Surah: {similar['surah_name']} (No. {similar['surah_number']}), 
                    Verse {similar['verse_number']}: {similar['verse_text']} (Similarity: {similar['similarity_score']:.2f})</li>
                    """
                formatted_text += "</ul>"

        formatted_text += "</div>"
        return formatted_text

    def show_error(self, message):
        """Display error message - to be implemented by subclasses"""
        raise NotImplementedError

    def show_previous_verse(self):
        """Show previous verse - to be implemented by subclasses"""
        raise NotImplementedError

    def show_next_verse(self):
        """Show next verse - to be implemented by subclasses"""
        raise NotImplementedError
