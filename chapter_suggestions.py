import json
from typing import Optional


class ChapterSuggestionModel:
    def __init__(self):
        self.chapter_names = []
        self.load_chapters()

    def load_chapters(self):
        """
        Load chapter data from the JSON file and populate chapter names.
        """
        try:
            with open('quran_ar_eng.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Extract all variants of chapter names
                for chapter in data:
                    self.chapter_names.extend([
                        chapter.get('transliteration', ""),  # Add a default value if key doesn't exist
                        chapter.get('translation', ""),
                        chapter.get('name', "")
                    ])
        except Exception as e:
            self.chapter_names = []

    def get_suggestion(self, prefix: str) -> Optional[str]:
        """
        Get the first chapter suggestion that matches the given prefix.
        """
        if not prefix:
            return None
        
        prefix = prefix.lower()
        for name in self.chapter_names:
            words = name.lower().split()
            if any(word.startswith(prefix) for word in words):
                return name
        
        return None

    def get_all_matches(self, prefix: str) -> list[str]:
        """
        Get all chapter names that match the given prefix.
        """
        if not prefix:
            return []
        
        prefix = prefix.lower()
        matches = []
        
        for name in self.chapter_names:
            words = name.lower().split()
            if any(word.startswith(prefix) for word in words):
                matches.append(name)
        
        return matches


if __name__ == "__main__":
    model = ChapterSuggestionModel()
    
    # Test get_suggestion method
    test_prefix = "al-b"  # Replace with your desired prefix
    suggestion = model.get_suggestion(test_prefix)
    print(f"Suggestion for '{test_prefix}': {suggestion}")
    
    # Test get_all_matches method
    all_matches = model.get_all_matches(test_prefix)
    print(f"All matches for '{test_prefix}': {all_matches}")
