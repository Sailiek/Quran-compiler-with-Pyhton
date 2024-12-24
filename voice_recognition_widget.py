from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from voice import recognize_speech, find_closest_match, quranic_verses

class VoiceRecognitionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Voice Recognition")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arabic Typesetting", 24, QFont.Bold))
        layout.addWidget(title)

        # Instructions
        instructions = QLabel("Click the button below and recite a verse from Al-Fatiha in English")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setFont(QFont("Arabic Typesetting", 16))
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Record button
        self.record_button = QPushButton("Start Recording")
        self.record_button.setMinimumHeight(50)
        self.record_button.setFont(QFont("Arabic Typesetting", 16))
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #b79c6b;
                color: black;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #a68957;
            }
        """)
        self.record_button.clicked.connect(self.start_recording)
        layout.addWidget(self.record_button)

        # Results area
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setMinimumHeight(200)
        self.results_area.setFont(QFont("Arabic Typesetting", 14))
        layout.addWidget(self.results_area)

        layout.addStretch()
        self.setLayout(layout)

    def start_recording(self):
        self.record_button.setEnabled(False)
        self.record_button.setText("Recording...")
        self.results_area.setText("Listening...")
        
        # Get speech input
        spoken_text = recognize_speech()
        
        if spoken_text:
            verse_number, verse_text, confidence = find_closest_match(spoken_text, quranic_verses)
            if confidence > 50:
                result = f"You said: {spoken_text}\n\n"
                result += f"Matched Verse #{verse_number}:\n{verse_text}\n"
                result += f"Confidence: {confidence}%"
            else:
                result = f"You said: {spoken_text}\n\nSorry, I could not match your recitation to a verse."
        else:
            result = "Sorry, I could not understand the audio. Please try again."
        
        self.results_area.setText(result)
        self.record_button.setText("Start Recording")
        self.record_button.setEnabled(True)
