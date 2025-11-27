import re
import logging
from typing import Dict, List, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CorrectionLevel(Enum):
    MINIMAL = "minimal"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"


@dataclass
class CorrectionResult:
    original: str
    corrected: str
    changes_made: bool
    correction_level: CorrectionLevel
    processing_time_ms: float
    corrections_applied: List[str] = None
    confidence_score: float = 1.0

    def __post_init__(self):
        if self.corrections_applied is None:
            self.corrections_applied = []


# ============================================================
# SPECIAL FORMAT PRESERVATION
# ============================================================

class TextPreservation:
    SPECIAL_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'url': r'https?://[^\s<>{}|\\^~\[\]`]+',
        'hashtag': r'#\w+',
        'mention': r'@\w+',
    }

    COMPILED_PATTERNS = {name: re.compile(pattern) for name, pattern in SPECIAL_PATTERNS.items()}

    @classmethod
    def preserve_special_formats(cls, text: str) -> Tuple[str, Dict[str, str]]:
        preserved = {}
        preserved_text = text

        for format_type, pattern in cls.COMPILED_PATTERNS.items():
            matches = pattern.findall(preserved_text)
            for idx, match in enumerate(matches):
                placeholder = f"__{format_type.upper()}_{idx}__"
                preserved[placeholder] = match
                preserved_text = preserved_text.replace(match, placeholder, 1)

        return preserved_text, preserved

    @classmethod
    def restore_special_formats(cls, text: str, preserved: Dict[str, str]) -> str:
        for placeholder, original in preserved.items():
            text = text.replace(placeholder, original)
        return text


# ================================
# NORMALIZATION
# ================================

class TextNormalizer:
    WHITESPACE_PATTERN = re.compile(r'\s+')
    ZERO_WIDTH_PATTERN = re.compile(r'[\u200B-\u200D\uFEFF]')

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        text = TextNormalizer.WHITESPACE_PATTERN.sub(' ', text)
        return text.strip()

    @staticmethod
    def remove_zero_width(text: str) -> str:
        return TextNormalizer.ZERO_WIDTH_PATTERN.sub('', text)

    @staticmethod
    def normalize_quotes(text: str) -> str:
        replacements = [
            ('‘', "'"), ('’', "'"), ('‚', "'"), ('‛', "'"),
            ('"', '"'), ('"', '"'), ('"', '"'), ('"', '"'),
            ('´', "'"), ('`', "'"), ('ʻ', "'"), ('ʼ', "'"),
            ('â€˜', "'"), ('â€™', "'"), ('â€œ', '"'), ('â€', '"'),
            ('Ã¢â‚¬Ëœ', "'"), ('Ã¢â‚¬â„¢', "'"), ('Ã¢â‚¬Å"', '"'),
        ]

        for wrong, correct in replacements:
            if wrong in text:
                text = text.replace(wrong, correct)

        return text

    @staticmethod
    def fix_all_caps(text: str) -> str:
        if text.isupper():
            t = text.lower()
            if len(t) == 0:
                return t
            return t[0].upper() + t[1:]
        return text

    @staticmethod
    def mild_random_case_fix(text: str) -> str:
        words = text.split()
        out = []
        for w in words:
            if any(c.islower() for c in w) and any(c.isupper() for c in w):
                out.append(w.lower())
            else:
                out.append(w)
        return " ".join(out)


# ================================
# SMART CAPITALIZATION (BALANCED)
# ================================

class SentenceCapitalizer:
    ALPHA_PATTERN = re.compile(r'[A-Za-zА-Яа-я]')
    STANDALONE_I_PATTERN = re.compile(r'\bi\b')

    @staticmethod
    def smart_capitalize(text: str) -> str:
        """
        BALANCED VERSION: Good for both basic and edge cases
        """
        if not text:
            return text

        # First, capitalize standalone 'i'
        text = SentenceCapitalizer.STANDALONE_I_PATTERN.sub('I', text)

        # Capitalize first letter
        text = SentenceCapitalizer.capitalize_first_letter(text)

        try:
            # 🔥 BALANCED APPROACH: Handle ellipsis properly
            def capitalize_after_sentence(match):
                before_text = text[:match.start()]
                punctuation = match.group(1)
                space = match.group(2)
                next_char = match.group(3)

                # 🔥 CRITICAL: Don't capitalize after ellipsis
                if punctuation == '.':
                    # Check if this is part of ellipsis
                    recent_chars = before_text[-5:] if len(before_text) > 5 else before_text
                    if re.search(r'\.{2,}$', recent_chars):  # Ellipsis detected
                        return match.group(0)  # Don't capitalize

                # Capitalize after normal sentence endings
                return punctuation + space + next_char.upper()

            # Apply balanced capitalization
            pattern = r'([.!?])(\s+)([a-z])'
            text = re.sub(pattern, capitalize_after_sentence, text)

        except Exception as e:
            logger.warning(f"Capitalization error: {e}")

        return text

    @staticmethod
    def capitalize_first_letter(text: str) -> str:
        """Capitalize first letter of text while preserving leading whitespace"""
        if not text:
            return text

        stripped = text.lstrip()
        if not stripped:
            return text

        leading_ws = text[:len(text) - len(stripped)]

        # Skip if this is a preserved placeholder
        if stripped.startswith('__'):
            return text

        # Find first alphabetical character
        m = SentenceCapitalizer.ALPHA_PATTERN.search(stripped)
        if m:
            idx = m.start()
            new_stripped = stripped[:idx] + stripped[idx].upper() + stripped[idx + 1:]
            return leading_ws + new_stripped

        return text

    @staticmethod
    def capitalize_standalone_i(text: str) -> str:
        return SentenceCapitalizer.STANDALONE_I_PATTERN.sub('I', text)


# ================================
# PUNCTUATION (BALANCED)
# ================================

class PunctuationHandler:
    # 🔥 BALANCED: Preserve ellipsis but fix basic cases
    MULTIPLE_DOTS = re.compile(r'\.{4,}')  # Collapse 4+ dots to 3 (preserve ...)
    MULTIPLE_EXCLAMATION = re.compile(r'!{2,}')
    MULTIPLE_QUESTION = re.compile(r'\?{2,}')
    MISSING_SPACE_AFTER = re.compile(r'([,!;:])(?=[^\s])')
    APOSTROPHE_FIX = re.compile(r"(?<!\w)'(?!\w|s\b)")

    # 🔥 NEW: Fix double periods but preserve ellipsis
    DOUBLE_PERIODS = re.compile(r'\.{2,3}(?!\.)')  # 2-3 dots not followed by another dot

    @staticmethod
    def add_proper_spacing(text: str) -> str:
        """
        BALANCED VERSION: Good for both test suites
        """
        try:
            # 🔥 CRITICAL: First preserve ellipsis, then fix basic periods
            # Collapse 4+ dots to 3 (preserve ellipsis)
            text = PunctuationHandler.MULTIPLE_DOTS.sub('...', text)

            # 🔥 FIX for test_basic: Collapse 2-3 dots to single period (but not if it's ellipsis)
            # This handles "Hello.. world" → "Hello. world" but preserves "hello... world"
            def fix_double_periods(match):
                dots = match.group(0)
                # If it's exactly 3 dots, keep as ellipsis
                if dots == '...':
                    return '...'
                # If it's 2 dots, collapse to 1
                return '.'

            text = PunctuationHandler.DOUBLE_PERIODS.sub(fix_double_periods, text)

            # Collapse repeated punctuation
            text = PunctuationHandler.MULTIPLE_EXCLAMATION.sub('!', text)
            text = PunctuationHandler.MULTIPLE_QUESTION.sub('?', text)

            # Only add space after commas/semicolons/colons if missing
            text = PunctuationHandler.MISSING_SPACE_AFTER.sub(r'\1 ', text)

            return text
        except Exception as e:
            logger.warning(f"Punctuation spacing error: {e}")
            return text

    @staticmethod
    def fix_apostrophes(text: str) -> str:
        try:
            return PunctuationHandler.APOSTROPHE_FIX.sub("'", text)
        except:
            return text


# ================================
# SECURITY CHECK
# ================================

class SecuritySanitizer:
    SECURITY_PATTERNS = [
        re.compile(r'<script.*?>', re.IGNORECASE),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'vbscript:', re.IGNORECASE),
        re.compile(r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION)\b', re.IGNORECASE),
        re.compile(r'rm\s+-rf', re.IGNORECASE),
        re.compile(r'wget\s+http', re.IGNORECASE),
        re.compile(r'curl\s+http', re.IGNORECASE),
    ]

    @staticmethod
    def contains_suspicious_patterns(text: str) -> bool:
        return any(pattern.search(text) for pattern in SecuritySanitizer.SECURITY_PATTERNS)


# ================================
# BASE CORRECTOR (BALANCED FINAL)
# ================================

class BaseCorrector(ABC):

    def __init__(self, correction_level=CorrectionLevel.STANDARD):
        self.correction_level = correction_level
        self.setup_dictionaries()

        self.normalizer = TextNormalizer()
        self.preservation_handler = TextPreservation()
        self.punctuation_handler = PunctuationHandler()
        self.security_sanitizer = SecuritySanitizer()
        self.capitalizer = SentenceCapitalizer()

    @abstractmethod
    def setup_dictionaries(self):
        pass

    @abstractmethod
    def core_correction_logic(self, text: str) -> Tuple[str, List[str]]:
        pass

    def correct(self, text: str) -> str:
        try:
            if not text or not isinstance(text, str):
                return text

            if text.strip() == "":
                return ""

            if self.security_sanitizer.contains_suspicious_patterns(text):
                return text

            # Early return for very short texts
            if len(text) < 3:
                return text.capitalize() if text else text

            # Apply normalizations in order
            t = self.normalizer.normalize_quotes(text)
            t = self.normalizer.normalize_whitespace(t)
            t = self.normalizer.remove_zero_width(t)
            t = self.normalizer.fix_all_caps(t)
            t = self.normalizer.mild_random_case_fix(t)

            # Capitalize standalone 'i' early
            t = self.capitalizer.capitalize_standalone_i(t)

            # Preserve special formats
            t, preserved = self.preservation_handler.preserve_special_formats(t)

            # Core correction logic
            t, _ = self.core_correction_logic(t)

            # Punctuation fixes
            t = self.punctuation_handler.add_proper_spacing(t)
            t = self.punctuation_handler.fix_apostrophes(t)

            # Smart capitalization
            t = self.capitalizer.smart_capitalize(t)

            # Restore preserved formats
            t = self.preservation_handler.restore_special_formats(t, preserved)

            return t

        except Exception as e:
            logger.error(f"Error in corrector: {e}")
            return text.capitalize() if text else text