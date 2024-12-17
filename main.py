from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QApplication, QSizePolicy
from PyQt5.QtCore import Qt
import sys
from search_widget import SearchWidget
from chatbot_widget import ChatbotWidget
from quran_reader_widget import QuranReaderWidget  # Import the new widget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quran Application")
        
        # Set minimum size instead of fixed geometry
        self.setMinimumSize(800, 600)
        
        # Allow the window to be resized
        self.setWindowFlags(self.windowFlags() | Qt.Window)

        # Create the stacked widget to hold the different pages
        self.central_widget = QStackedWidget()
        self.central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Widgets for each page
        self.quran_reader = QuranReaderWidget()  # Use the new QuranReaderWidget
        self.search_widget = SearchWidget()
        self.chatbot_widget = ChatbotWidget()

        # Add the widgets to the stack
        self.central_widget.addWidget(self.quran_reader)
        self.central_widget.addWidget(self.search_widget)
        self.central_widget.addWidget(self.chatbot_widget)

        # Initialize the UI layout
        self.init_ui()

    def init_ui(self):
        # Main layout that will hold the sidebar and the content area
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)  # Add spacing between sidebar and content
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add margins around the entire layout

        # Create a vertical layout for the sidebar (navigation)
        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(5)  # Add spacing between buttons
        nav_layout.setContentsMargins(5, 5, 5, 5)  # Add margins around buttons

        # Add buttons for navigation
        read_button = QPushButton("Lecture du Coran")
        read_button.setMinimumHeight(40)  # Make buttons more clickable
        read_button.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.quran_reader))
        
        search_button = QPushButton("Recherche")
        search_button.setMinimumHeight(40)
        search_button.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.search_widget))
        
        chatbot_button = QPushButton("Chatbot")
        chatbot_button.setMinimumHeight(40)
        chatbot_button.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.chatbot_widget))

        # Add the buttons to the sidebar layout
        nav_layout.addWidget(read_button)
        nav_layout.addWidget(search_button)
        nav_layout.addWidget(chatbot_button)
        nav_layout.addStretch()  # Add stretch to push buttons to the top

        # Create a widget for the sidebar and set its layout
        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)
        nav_widget.setMinimumWidth(150)  # Set minimum width for sidebar
        nav_widget.setMaximumWidth(200)  # Set maximum width for sidebar

        # Create the content area to hold the stacked widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to maximize content space
        content_layout.addWidget(self.central_widget)

        # Add the sidebar (left) and content area (right) to the main layout
        main_layout.addWidget(nav_widget)
        main_layout.addWidget(content_widget)

        # Set the central widget for the main window
        container_widget = QWidget()
        container_widget.setLayout(main_layout)
        self.setCentralWidget(container_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
