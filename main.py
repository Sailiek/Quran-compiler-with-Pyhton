import sys
import pygame
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QApplication, \
    QSizePolicy, QLabel, QFrame, QLineEdit, QTextEdit
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QColor, QFont, QIcon
from search_widget import SearchWidget
from chatbot_widget import ChatbotWidget
from quran_reader_widget import QuranReaderWidget


class OpeningWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Initialiser pygame pour le son
        pygame.mixer.init()

        # Jouer le son à l'ouverture
        self.play_sound()

        # Configuration de la fenêtre d'ouverture
        self.setWindowTitle("Page d'Ouverture")
        self.setWindowIcon(QIcon('icon.jpg'))  # Remplacez par le chemin de votre image
        self.setMinimumSize(800, 600)

        # Ajouter l'image à la fenêtre
        self.display_image()

        # Lancer la fenêtre principale après un délai
        QTimer.singleShot(3000, self.open_main_window)  # Attendre 3 secondes avant d'ouvrir la fenêtre principale

    def play_sound(self):
        """Jouer le son au démarrage"""
        pygame.mixer.music.load("1211.MP3")  # Assurez-vous que le fichier est dans le bon dossier
        pygame.mixer.music.play()

    def display_image(self):
        """Afficher l'image à l'ouverture"""
        image_label = QLabel(self)  # Créer un label pour l'image
        pixmap = QPixmap("image.jpg")  # Assurez-vous que le fichier image.jpg est dans le bon dossier
        image_label.setPixmap(pixmap)  # Définir l'image
        image_label.setAlignment(Qt.AlignCenter)  # Centrer l'image
        image_label.setScaledContents(True)  # Pour redimensionner l'image pour occuper toute la fenêtre

        # Créer une mise en page et ajouter l'image
        layout = QVBoxLayout()
        layout.addWidget(image_label)
        self.setLayout(layout)

    def open_main_window(self):
        """Ouvrir la fenêtre principale"""
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()  # Fermer la fenêtre d'ouverture


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quran Application")

        self.setWindowIcon(QIcon('icon.jpg'))  # Remplacez par le chemin de votre image




        # Configuration de la fenêtre principale
        self.setMinimumSize(800, 600)
        self.setWindowFlags(self.windowFlags() | Qt.Window)

        # Appliquer l'image de fond
        self.set_background_image()

        # Créer le widget central (QStackedWidget)
        self.central_widget = QStackedWidget()
        self.central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Widgets pour chaque page
        self.quran_reader = QuranReaderWidget()
        self.search_widget = SearchWidget()
        self.chatbot_widget = ChatbotWidget()

        # Ajouter les widgets au QStackedWidget
        self.central_widget.addWidget(self.quran_reader)
        self.central_widget.addWidget(self.search_widget)
        self.central_widget.addWidget(self.chatbot_widget)

        # Initialiser la mise en page de l'UI
        self.init_ui()

    def set_background_image(self):
        """Définir l'image de fond de la fenêtre principale"""
        pixmap = QPixmap("123.jpg")  # Assurez-vous que le fichier quran_background.png est dans le bon dossier
        palette = self.palette()
        palette.setBrush(QPalette.Background, QBrush(pixmap))  # Appliquer l'image de fond
        self.setPalette(palette)

    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        # Mise en page principale avec une barre latérale
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Mise en page de la barre latérale
        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(5)
        nav_layout.setContentsMargins(5, 5, 5, 5)

        # Ajouter les boutons de navigation
        read_button = QPushButton("Lecture du Coran")
        self.style_button(read_button)
        read_button.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.quran_reader))

        search_button = QPushButton("Recherche")
        self.style_button(search_button)
        search_button.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.search_widget))

        chatbot_button = QPushButton("Chatbot")
        self.style_button(chatbot_button)
        chatbot_button.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.chatbot_widget))

        # Ajouter les boutons au layout de la barre latérale
        nav_layout.addWidget(read_button)
        nav_layout.addWidget(search_button)
        nav_layout.addWidget(chatbot_button)
        nav_layout.addStretch()  # Ajouter un espace pour pousser les boutons vers le haut

        # Créer le widget pour la barre latérale
        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)
        nav_widget.setMinimumWidth(150)
        nav_widget.setMaximumWidth(200)
        nav_widget.setStyleSheet("background-color: #d1b88c;")  # Fond doré pour la sidebar

        # Créer un cadre pour la zone de contenu
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: white; border: 1px solid #b79c6b; border-radius: 10px;")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.addWidget(self.central_widget)

        # Ajouter la barre latérale et la zone de contenu à la mise en page
        main_layout.addWidget(nav_widget)
        main_layout.addWidget(content_frame)

        # Définir le widget central de la fenêtre principale
        container_widget = QWidget()
        container_widget.setLayout(main_layout)
        self.setCentralWidget(container_widget)

        # Appliquer les styles
        self.apply_styles()

    def style_button(self, button):
        """Appliquer un style uniforme aux boutons"""
        button.setMinimumHeight(40)
        button.setFont(QFont("Arabic Typesetting", 14))
        button.setStyleSheet("""
            QPushButton {
                background-color: #b79c6b;
                color: black;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #a68957;
            }
        """)

    def apply_styles(self):
        """Appliquer des styles aux widgets éditables uniquement."""
        self.setStyleSheet("""
            QLineEdit, QTextEdit {
                border: 2px solid #b79c6b;  /* Couleur et épaisseur du cadre */
                border-radius: 5px;         /* Coins arrondis */
                padding: 5px;               /* Espacement interne */
                background-color: white;    /* Couleur de fond */
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #a68957;  /* Couleur du cadre au focus */
                background-color: #fefbe9;  /* Fond légèrement différent */
            }
            QLabel {
                border: none;               /* Pas de cadre pour les labels */
                font-weight: bold;          /* Gras pour les titres */
                font-size: 16px;            /* Taille des titres */
                color: black;               /* Couleur du texte */
                padding: 0px;               /* Pas de padding pour les titres */
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    opening_window = OpeningWindow()
    opening_window.show()  # Afficher la fenêtre d'ouverture
    sys.exit(app.exec_())
