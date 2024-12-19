import json
import numpy as np
import pandas as pd
import re
import unicodedata

# Arabic text processing libraries
import pyarabic.araby as araby
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher

class QuranVerseMatcher:
    def __init__(self, quran_data_path):
        """
        Initialize Quran verse matcher
        
        :param quran_data_path: Path to Quran JSON
        """
        # Load Quran data
        with open(quran_data_path, 'r', encoding='utf-8') as file:
            self.quran_data = json.load(file)
        
        # Prepare data for ML
        self.prepare_training_data()
        
        # Train the model
        self.train_model()
    
    def remove_diacritics(self, text):
        """
        Remove Arabic diacritics safely
        
        :param text: Input text
        :return: Text without diacritics
        """
        if not text:
            return ""
        
        # Remove specific Arabic diacritical marks
        diacritics = '\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652'
        return ''.join(char for char in text if char not in diacritics)
    
    def preprocess_arabic_text(self, text):
        """
        Preprocess Arabic text for matching
        
        :param text: Input Arabic text
        :return: Preprocessed text
        """
        # Handle None or empty input
        if not text:
            return ""
        
        # Remove diacritics
        text = self.remove_diacritics(text)
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # Normalize Arabic characters
        text = unicodedata.normalize('NFKD', text)
        
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def prepare_training_data(self):
        """
        Prepare verses for machine learning training
        """
        # Collect verses and their metadata
        verses_arabic = []
        verses_translations = []
        surah_numbers = []
        verse_numbers = []
        surah_names = []
        
        for surah in self.quran_data:
            surah_id = surah.get('id', 0)
            surah_name = surah.get('name', f'Surah {surah_id}')
            
            for verse in surah.get('verses', []):
                # Preprocess Arabic text
                processed_arabic = self.preprocess_arabic_text(verse.get('text', ''))
                
                verses_arabic.append(processed_arabic)
                verses_translations.append(verse.get('translation', ''))
                surah_numbers.append(surah_id)
                verse_numbers.append(verse.get('id', 0))
                surah_names.append(surah_name)
        
        # Create DataFrame
        self.verse_df = pd.DataFrame({
            'verse_arabic': verses_arabic,
            'verse_translation': verses_translations,
            'surah_number': surah_numbers,
            'verse_number': verse_numbers,
            'surah_name': surah_names
        })
    
    def train_model(self):
        """
        Train vectorizers for Arabic and English
        """
        # Arabic Vectorizer
        self.arabic_vectorizer = TfidfVectorizer(
            stop_words=None,
            ngram_range=(1, 3)  # Expanded n-gram range
        )
        arabic_vectors = self.arabic_vectorizer.fit_transform(
            self.verse_df['verse_arabic']
        )
        
        # English Vectorizer
        self.english_vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 3)  # Expanded n-gram range
        )
        english_vectors = self.english_vectorizer.fit_transform(
            self.verse_df['verse_translation']
        )
        
        # Compute similarity matrices
        self.arabic_similarity_matrix = cosine_similarity(arabic_vectors)
        self.english_similarity_matrix = cosine_similarity(english_vectors)
    
    def detect_language(self, text):
        """
        Detect if input is Arabic or English
        
        :param text: Input text
        :return: Language ('arabic' or 'english')
        """
        # Check for Arabic characters
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        total_chars = len(text)
        
        # If more than 50% Arabic characters, consider it Arabic
        return 'arabic' if arabic_chars / total_chars > 0.5 else 'english'
    
    def calculate_string_similarity(self, str1, str2):
        """
        Calculate string similarity using multiple methods
        
        :param str1: First string
        :param str2: Second string
        :return: Similarity score
        """
        # Use SequenceMatcher for basic string similarity
        seq_matcher = SequenceMatcher(None, str1, str2)
        sequence_similarity = seq_matcher.ratio()
        
        # Additional similarity metrics
        word_overlap = len(set(str1.split()) & set(str2.split())) / max(len(str1.split()), len(str2.split()))
        
        # Combine different similarity metrics
        combined_similarity = (sequence_similarity + word_overlap) / 2
        
        return combined_similarity
    
    def find_verse_match(self, user_input, top_k=3, similarity_threshold=0.3):
        """
        Find most similar verses to user input with enhanced matching
        
        :param user_input: Text entered by the user
        :param top_k: Number of top matches to return
        :param similarity_threshold: Minimum similarity to consider a match
        :return: Matching verse information
        """
        # Detect language
        language = self.detect_language(user_input)
        
        # Preprocess input
        if language == 'arabic':
            processed_input = self.preprocess_arabic_text(user_input)
            vectorizer = self.arabic_vectorizer
            verse_column = 'verse_arabic'
            result_column = 'verse_translation'
        else:
            processed_input = user_input
            vectorizer = self.english_vectorizer
            verse_column = 'verse_translation'
            result_column = 'verse_translation'
        
        # Vectorize input
        input_vector = vectorizer.transform([processed_input])
        
        # Compute similarity with all verses
        cosine_similarities = cosine_similarity(
            input_vector, 
            vectorizer.transform(self.verse_df[verse_column])
        )[0]
        
        # Calculate additional text similarity
        text_similarities = [
            self.calculate_string_similarity(processed_input, verse) 
            for verse in self.verse_df[verse_column]
        ]
        
        # Combined similarity score (weighted average)
        combined_similarities = (
            0.7 * cosine_similarities + 
            0.3 * np.array(text_similarities)
        )
        
        # Get top matching indices
        top_indices = combined_similarities.argsort()[-top_k:][::-1]
        
        # Prepare results
        matches = []
        for idx in top_indices:
            # Only include matches above threshold
            if combined_similarities[idx] > similarity_threshold:
                matches.append({
                    'verse_text': self.verse_df.loc[idx, result_column],
                    'surah_number': self.verse_df.loc[idx, 'surah_number'],
                    'verse_number': self.verse_df.loc[idx, 'verse_number'],
                    'surah_name': self.verse_df.loc[idx, 'surah_name'],
                    'similarity_score': combined_similarities[idx]
                })
        
        return {
            'matches': matches,
            'input_text': user_input,
            'detected_language': language
        }
