"""
correctors/contextual_corrector.py

Contextual spelling correction for commonly confused words.
Handles: their/there/they're, your/you're, its/it's, etc.
"""

import re
from typing import List, Tuple


class ContextualCorrector:
    """
    Fixes contextually confused homophones based on grammar patterns.
    """

    def __init__(self):
        self.setup_patterns()

    def setup_patterns(self):
        """Define patterns for contextual corrections"""

        # Words that typically follow "you're" (verbs, adjectives, adverbs)
        self.youre_indicators = [
            'going', 'welcome', 'right', 'wrong', 'awesome', 'amazing',
            'beautiful', 'crazy', 'doing', 'getting', 'being', 'looking',
            'feeling', 'thinking', 'saying', 'making', 'having', 'coming',
            'leaving', 'running', 'walking', 'talking', 'working', 'playing',
            'here', 'there', 'sure', 'not', 'so', 'very', 'really', 'quite',
            'about', 'probably', 'definitely', 'certainly', 'likely'
        ]

        # Words that typically follow "your" (nouns, possessive contexts)
        self.your_indicators = [
            'car', 'house', 'book', 'phone', 'computer', 'dog', 'cat',
            'friend', 'family', 'mother', 'father', 'brother', 'sister',
            'name', 'email', 'address', 'time', 'money', 'job', 'life',
            'idea', 'problem', 'question', 'answer', 'work', 'home',
            'room', 'bed', 'desk', 'chair', 'table', 'own', 'turn',
            'head', 'eyes', 'hand', 'body', 'mind', 'heart', 'soul'
        ]

        # Words that follow "they're" (verbs, adjectives, adverbs)
        self.theyre_indicators = [
            'going', 'coming', 'here', 'there', 'not', 'so', 'very',
            'happy', 'sad', 'angry', 'excited', 'ready', 'doing',
            'making', 'having', 'being', 'getting', 'saying', 'thinking',
            'working', 'playing', 'running', 'walking', 'talking',
            'right', 'wrong', 'sure', 'fine', 'okay', 'great', 'good',
            'bad', 'amazing', 'awesome', 'beautiful', 'crazy'
        ]

        # Words that follow "their" (nouns)
        self.their_indicators = [
            'car', 'house', 'dog', 'cat', 'friend', 'family', 'children',
            'parents', 'room', 'home', 'work', 'job', 'life', 'time',
            'money', 'idea', 'problem', 'question', 'answer', 'name',
            'phone', 'computer', 'book', 'own', 'turn', 'way', 'place',
            'head', 'eyes', 'hands', 'body', 'minds', 'hearts'
        ]

        # Compile regex patterns for efficiency
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for better performance"""

        # YOUR/YOU'RE patterns
        self.your_pattern = re.compile(
            r'\b(your|you\'?re)\s+(\w+)',
            re.IGNORECASE
        )

        # THEIR/THERE/THEY'RE patterns
        self.their_pattern = re.compile(
            r'\b(their|there|they\'?re)\s+(\w+)',
            re.IGNORECASE
        )

        # ITS/IT'S patterns
        self.its_pattern = re.compile(
            r'\b(its|it\'?s)\s+(\w+)',
            re.IGNORECASE
        )

    def correct_your_youre(self, text: str) -> str:
        """
        Fix your/you're confusion based on following word.

        Rules:
        - "your" + verb/adjective/adverb → "you're"
        - "you're" + noun → "your"
        - Special cases: "your welcome" → "you're welcome"
        """

        def replacement(match):
            current_word = match.group(1).lower()
            next_word = match.group(2).lower()

            # Preserve original capitalization
            was_capitalized = match.group(1)[0].isupper()

            # Check if next word indicates "you're" usage
            if next_word in self.youre_indicators:
                correct = "you're"
            # Check if next word indicates "your" usage
            elif next_word in self.your_indicators:
                correct = "your"
            # Default: keep as is if unsure
            else:
                # If current is "your" and next word ends in 'ing' → probably "you're going"
                if current_word in ['your', 'youre'] and next_word.endswith('ing'):
                    correct = "you're"
                # If next word is a noun (ends in common noun suffixes)
                elif next_word.endswith(('tion', 'ness', 'ment', 'ity', 'er', 'or', 'ist')):
                    correct = "your"
                else:
                    return match.group(0)  # Keep original

            # Apply original capitalization
            if was_capitalized:
                correct = correct.capitalize()

            return f"{correct} {match.group(2)}"

        return self.your_pattern.sub(replacement, text)

    def correct_their_there_theyre(self, text: str) -> str:
        """
        Fix their/there/they're confusion.

        Rules:
        - "their" + noun (possessive)
        - "there" + is/are/was/were (existential)
        - "there" + location prepositions (by, in, at, on)
        - "they're" + verb/adjective/adverb (contraction of "they are")
        """

        def replacement(match):
            current_word = match.group(1).lower()
            next_word = match.group(2).lower()

            was_capitalized = match.group(1)[0].isupper()

            # "there is/are/was/were" OR location words → always "there"
            if next_word in ['is', 'are', 'was', 'were', 'will', 'would', 'should', 'by', 'in', 'at', 'on']:
                correct = "there"
            # Check for "they're" indicators (verbs, adjectives)
            elif next_word in self.theyre_indicators or next_word.endswith('ing'):
                correct = "they're"
            # Check for "their" indicators (nouns)
            elif next_word in self.their_indicators:
                correct = "their"
            # Default heuristic
            else:
                # If next word is likely a verb → "they're"
                if next_word.endswith(('ing', 'ed')) or next_word in ['happy', 'sad', 'ready', 'here', 'not']:
                    correct = "they're"
                # Likely a noun → "their"
                else:
                    correct = "their"

            if was_capitalized:
                correct = correct.capitalize()

            return f"{correct} {match.group(2)}"

        return self.their_pattern.sub(replacement, text)

    def correct_its_its(self, text: str) -> str:
        """
        Fix its/it's confusion.

        Rules:
        - "it's" = "it is" or "it has" (contraction)
        - "its" = possessive
        """

        def replacement(match):
            current_word = match.group(1).lower()
            next_word = match.group(2).lower()

            was_capitalized = match.group(1)[0].isupper()

            # "it's" before verbs/adjectives (it is/has)
            if next_word in ['a', 'the', 'not', 'been', 'going', 'time', 'okay', 'fine', 'good', 'bad']:
                correct = "it's"
            # "its" before nouns (possessive)
            else:
                correct = "its"

            if was_capitalized:
                correct = correct.capitalize()

            return f"{correct} {match.group(2)}"

        return self.its_pattern.sub(replacement, text)

    def correct(self, text: str) -> str:
        """
        Apply all contextual corrections to text.
        Order matters: process from most to least ambiguous.
        """
        if not text or not isinstance(text, str):
            return text

        # Apply corrections in sequence
        text = self.correct_your_youre(text)
        text = self.correct_their_there_theyre(text)
        text = self.correct_its_its(text)

        return text