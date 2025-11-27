"""
correctors/spelling_corrector.py

Basic spelling correction - does NOT handle contextual homophones.
Contextual words (their/your) are handled by contextual_corrector.py
"""

from .base_corrector import BaseCorrector
import re
from typing import Tuple, List


class SpellingCorrector(BaseCorrector):

    def setup_dictionaries(self):
        self.spelling_rules = {
            # Original rules
            "teh": "the",
            "adress": "address",
            "recieve": "receive",
            "occurence": "occurrence",
            "accomodate": "accommodate",
            "definately": "definitely",
            "seperate": "separate",
            "wich": "which",
            "becuase": "because",
            "alot": "a lot",
            "truely": "truly",
            "goverment": "government",
            "enviroment": "environment",
            "untill": "until",
            "wiches": "which",

            # NEW - Missing words that caused test failures
            "beleive": "believe",
            "beleve": "believe",
            "corect": "correct",
            "correkt": "correct",
            "terrble": "terrible",
            "terrable": "terrible",

            # BONUS - Additional common misspellings
            "awsome": "awesome",
            "freind": "friend",
            "occured": "occurred",
            "reccomend": "recommend",
            "necesary": "necessary",
            "tommorow": "tomorrow",
            "succesful": "successful",
            "embarass": "embarrass",
            "occassion": "occasion",
            "persue": "pursue",
            "arguement": "argument",
            "wierd": "weird",
            "foriegn": "foreign",
            "heighth": "height",
            "greatful": "grateful",
            "concious": "conscious",
            "posession": "possession",
            "cemetary": "cemetery",
            "millenium": "millennium",

            # REMOVED: "their": "there" - now handled by contextual_corrector
            # REMOVED: "your": "you're" - now handled by contextual_corrector
        }

        all_wrong = '|'.join(re.escape(w) for w in self.spelling_rules.keys())
        self.combined_spelling_pattern = re.compile(r'\b(' + all_wrong + r')\b', re.IGNORECASE)

    def correct_spelling(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return text

        def replacement(match):
            word = match.group()
            wrong = word.lower()
            correct = self.spelling_rules.get(wrong, word)

            # Preserve original casing
            if word.isupper():
                return correct.upper()
            if word[0].isupper():
                return correct.capitalize()
            return correct

        try:
            return self.combined_spelling_pattern.sub(replacement, text)
        except Exception:
            return text

    def core_correction_logic(self, text: str) -> Tuple[str, List[str]]:
        corrected = self.correct_spelling(text)
        changes = []
        if corrected != text:
            changes.append("Applied spelling corrections")
        return corrected, changes