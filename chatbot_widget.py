# File: chatbot_widget.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
import requests  # To make HTTP requests to the Flask API
import json

class ChatbotWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create the layout
        self.layout = QVBoxLayout(self)

        # Input field for entering the query (e.g., "give me ayas about the moon")
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Ask about a Quranic verse...")

        # Define button style
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
        
        # Button to send the query to the model
        self.ask_button = QPushButton("Ask", self)
        self.ask_button.clicked.connect(self.ask_model)
        self.ask_button.setStyleSheet(button_style)

        # Label to display the response from the model
        self.response_label = QLabel(self)

        # Add widgets to the layout
        self.layout.addWidget(self.input_field)
        self.layout.addWidget(self.ask_button)
        self.layout.addWidget(self.response_label)

    def ask_model(self):
        # Get the user's input query
        user_input = self.input_field.text().strip()

        if not user_input:
            self.response_label.setText("Please enter a valid query.")
            return

        try:
            # Define the JSON body with query and max_results
            payload = {
                "query": user_input,  # The query entered by the user
                "max_results": 4      # Set the max number of results you want (e.g., 4)
            }

            # Send the POST request to the Flask API
            response = requests.post("http://127.0.0.1:5000/search", json=payload)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the response as JSON
                data = response.json()

                # Check if the response contains results
                if 'results' in data and data['results']:
                    result_text = ""
                    for idx, result in enumerate(data['results']):
                        # Format the result information as needed
                        result_text += (f"Aya {idx + 1}:\n"
                                        f"Arabic: {result.get('arabic_text', 'No Arabic text available')}\n"
                                        f"English: {result.get('english_text', 'No English text available')}\n"
                                        f"Description: {result.get('description1', 'No description available')}\n"
                                        f"Chapter: {result.get('chapter', 'No chapter info')}, "
                                        f"Verse: {result.get('verse', 'No verse info')}\n"
                                        f"Similarity Score: {result.get('similarity_score', 'N/A')}\n\n")
                    
                    # Display the result in the response_label
                    self.response_label.setText(result_text)
                else:
                    self.response_label.setText("No results found.")

            else:
                self.response_label.setText(f"Error: {response.status_code} - {response.text}")

        except Exception as e:
            self.response_label.setText(f"Error occurred: {e}")
