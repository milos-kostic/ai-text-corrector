"""
correctors/grammar_corrector.py

Grammar correction with contextual spelling support.
"""

from .base_corrector import BaseCorrector
from .spelling_corrector import SpellingCorrector
from .contextual_corrector import ContextualCorrector
import re
from typing import Tuple, List


class GrammarCorrector(BaseCorrector):

    def setup_dictionaries(self):
        try:
            self.spelling_corrector = SpellingCorrector()
        except Exception:
            self.spelling_corrector = None

        # Initialize contextual corrector
        try:
            self.contextual_corrector = ContextualCorrector()
        except Exception:
            self.contextual_corrector = None

        # ========================================
        # CONTRACTIONS - EXPANDED
        # ========================================
        self.contractions = {
            'dont': "don't",
            'doesnt': "doesn't",
            'didnt': "didn't",
            'wont': "won't",
            'cant': "can't",
            'couldnt': "couldn't",
            'shouldnt': "shouldn't",
            'wouldnt': "wouldn't",
            'isnt': "isn't",
            'arent': "aren't",
            'wasnt': "wasn't",
            'werent': "weren't",
            'hasnt': "hasn't",
            'havent': "haven't",
            'hadnt': "hadn't",
            'im': "I'm",
            'youre': "you're",
            'hes': "he's",
            'shes': "she's",
            'its': "it's",
            'were': "we're",  # OVO JE PROBLEM - treba da se izbegne
            'theyre': "they're",
            'ive': "I've",
            'youve': "you've",
            'weve': "we've",
            'theyve': "they've",
            'ill': "I'll",
            'youll': "you'll",
            'hell': "he'll",
            'shell': "she'll",
            'well': "we'll",  # OVO JE PROBLEM - treba da se izbegne
            'theyll': "they'll",
            'id': "I'd",
        }

        # ========================================
        # IRREGULAR VERBS - EXPANDED
        # ========================================
        self.irregular_verbs = {
            'goed': 'went',
            'runned': 'ran',
            'eated': 'ate',
            'drinked': 'drank',
            'buyed': 'bought',
            'thinked': 'thought',
            'comed': 'came',
            'sayed': 'said',
            'maked': 'made',
            'taked': 'took',
            'gived': 'gave',
            'sended': 'sent',
            'finded': 'found',
            'knowed': 'knew',
            'writed': 'wrote',

            # Perfect tense
            'has ate': 'has eaten',
            'have ate': 'have eaten',
            'has went': 'has gone',
            'have went': 'have gone',
            'has ran': 'has run',
            'have ran': 'have run',
            'has came': 'has come',
            'have came': 'have come',
            'has wrote': 'has written',
            'have wrote': 'have written',

            # Negative past
            "didn't went": "didn't go",
            "didn't ate": "didn't eat",
            "didn't drank": "didn't drink",
            "didn't came": "didn't come",
            "didn't ran": "didn't run",
            "didn't saw": "didn't see",
            "didn't wrote": "didn't write",

            # Was/were constructions
            'was went': 'went',
            'was ate': 'ate',
            'was came': 'came',
            'were went': 'went',
        }

        # ========================================
        # VERB AGREEMENT - GREATLY EXPANDED
        # ========================================
        self.verb_agreements = {
            # Have/Has
            'he have': 'he has',
            'she have': 'she has',
            'it have': 'it has',
            'they has': 'they have',
            'we has': 'we have',
            'you has': 'you have',
            'i has': 'i have',

            # Do/Does
            'he do': 'he does',
            'she do': 'she does',
            'it do': 'it does',
            'they does': 'they do',
            'we does': 'we do',
            'you does': 'you do',

            # Go/Goes
            'he go': 'he goes',
            'she go': 'she goes',
            'it go': 'it goes',

            # Is/Are/Am
            'he are': 'he is',
            'she are': 'she is',
            'it are': 'it is',
            'they is': 'they are',
            'we is': 'we are',
            'you is': 'you are',
            'i is': 'i am',

            # Was/Were
            'i were': 'i was',  # OVO JE KLJUČNO - popravlja "i were" → "I was"
            'he were': 'he was',
            'she were': 'she was',
            'it were': 'it was',
            'we was': 'we were',
            'they was': 'they were',
            'you was': 'you were',

            # Don't/Doesn't
            'she dont': "she doesn't",
            'he dont': "he doesn't",
            'it dont': "it doesn't",
            "he don't": "he doesn't",
            "she don't": "she doesn't",
            "it don't": "it doesn't",
            "we doesn't": "we don't",
            "they doesn't": "they don't",
            "i doesn't": "i don't",
            "you doesn't": "you don't",

            # NEW - Demonstratives (this/that/these/those) - CRITICAL FIX
            'this are': 'this is',
            'that are': 'that is',
            'this were': 'this was',
            'that were': 'that was',
            'these is': 'these are',
            'those is': 'those are',
            'these was': 'these were',
            'those was': 'those were',
        }

        # ========================================
        # COMPOUND SUBJECT + VERB AGREEMENT
        # ========================================
        self.compound_subject_fixes = {
            'he and i was': 'he and i were',
            'she and i was': 'she and i were',
            'you and i was': 'you and i were',
            'they and i was': 'they and i were',
            'we and i was': 'we and i were',
            'he and she was': 'he and she were',
            'him and i was': 'he and i were',
            'her and i was': 'she and i were',

            # 🔥 FIX #2: "I and I" patterns (after pronoun correction "me and i" → "i and i")
            'i and i was': 'i and i were',
            'i and i is': 'i and i are',

            # 🔥 FIX #2: More compound patterns with "was"
            'me and you was': 'you and i were',
            'me and he was': 'he and i were',
            'me and she was': 'she and i were',
            'me and him was': 'he and i were',
            'me and her was': 'she and i were',
        }

        # ========================================
        # PRONOUN SUBJECT/OBJECT
        # ========================================
        self.pronoun_corrections = {
            'me am': 'i am',
            'me is': 'i am',
            'me was': 'i was',
            'me were': 'i was',
            'me have': 'i have',
            'me do': 'i do',
            'me go': 'i go',
            'me like': 'i like',
            'me want': 'i want',
            'me need': 'i need',
            'me think': 'i think',
            'me know': 'i know',
            'me understand': 'i understand',

            # 🔥 FIX #2: "me and [pronoun]" patterns
            'me and i': 'i and i',
            'me and you': 'you and i',
            'me and he': 'he and i',
            'me and she': 'she and i',
            'me and him': 'he and i',
            'me and her': 'she and i',
            'me and they': 'they and i',
            'me and we': 'we and i',

            # 🔥 FIX #2: Reverse order
            'i and me': 'i and i',
            'you and me': 'you and i',
            'he and me': 'he and i',
            'she and me': 'she and i',
            'him and me': 'he and i',
            'her and me': 'she and i',
            'they and me': 'they and i',
            'we and me': 'we and i',
        }

        # ========================================
        # ARTICLES - EXPANDED
        # ========================================
        self.article_corrections = {
            'a apple': 'an apple',
            'a orange': 'an orange',
            'a umbrella': 'an umbrella',
            'a hour': 'an hour',
            'a honest': 'an honest',
            'a interesting': 'an interesting',
            'a elephant': 'an elephant',
            'a eagle': 'an eagle',
            'a onion': 'an onion',
            'a octopus': 'an octopus',

            'an book': 'a book',
            'an house': 'a house',
            'an car': 'a car',
            'an dog': 'a dog',
            'an table': 'a table',
            'an university': 'a university',
            'an user': 'a user',
            'an european': 'a european',
            'an one': 'a one',
        }

        # ========================================
        # WORD ORDER - EXPANDED
        # ========================================
        self.word_order_rules = {
            'i tomorrow will': 'i will tomorrow',
            'always he': 'he always',
            'never i': 'i never',
            'often she': 'she often',
            'sometimes they': 'they sometimes',
            'always we': 'we always',
            'usually he': 'he usually',
            'yesterday i go': 'yesterday i went',  # 🔥 FIX #3: Keep "yesterday" at start

            # Question word order fixes
            'why she dont': 'why doesn\'t she',
            'why she doesn\'t': 'why doesn\'t she',
            'why he dont': 'why doesn\'t he',
            'why he doesn\'t': 'why doesn\'t he',
            'why they doesnt': 'why don\'t they',
            'why they doesn\'t': 'why don\'t they',
        }

        # ========================================
        # PREPOSITIONS - EXPANDED
        # ========================================
        self.preposition_rules = {
            'arrived to': 'arrived at',
            'listen me': 'listen to me',
            'wait to': 'wait for',
            'discuss about': 'discuss',
            'married with': 'married to',
            'different than': 'different from',
            'depend of': 'depend on',
        }

        # ========================================
        # COMMON PHRASES - EXPANDED
        # NOTE: Removed "their"->"there" and "your"->"you're"
        # These are now handled by contextual_corrector
        # ========================================
        self.common_phrases = {
            "it's me": "it's I",
            "me and him": "he and I",
            "me and her": "she and I",
            "him and me": "he and I",
            "her and me": "she and I",
            "me and you": "you and I",

            "more better": "better",
            "most easiest": "easiest",
            "more faster": "faster",
            "most biggest": "biggest",

            "could of": "could have",
            "should of": "should have",
            "would of": "would have",
            "must of": "must have",
            "might of": "might have",

            "alot": "a lot",
            "incase": "in case",
            "atleast": "at least",
            "aswell": "as well",
        }

        # ========================================
        # NEW - Common adjectives that need article before noun
        # ========================================
        self.common_adjectives = {
            'bad', 'good', 'great', 'big', 'small', 'new', 'old', 'nice',
            'beautiful', 'ugly', 'happy', 'sad', 'fast', 'slow', 'hot', 'cold',
            'long', 'short', 'high', 'low', 'strong', 'weak', 'clean', 'dirty',
            'easy', 'hard', 'simple', 'complex', 'true', 'false', 'correct', 'wrong',
            'real', 'fake', 'rich', 'poor', 'young', 'wise', 'foolish', 'brave',
            'smart', 'stupid', 'funny', 'serious', 'important', 'dangerous', 'safe'
        }

        self._compile_combined_patterns()

    def _compile_combined_patterns(self):
        try:
            # Contractions pattern - IZBACUJEMO 'were' i 'well' iz kontrakcija
            contractions_without_problems = {k: v for k, v in self.contractions.items()
                                           if k not in ['were', 'well']}
            self.contractions_pattern = re.compile(
                r'\b(' + '|'.join(map(re.escape, contractions_without_problems.keys())) + r')\b',
                re.IGNORECASE
            )

            # 🔥 FIX #2: Recompile pronoun pattern with new entries
            self.pronoun_pattern = re.compile(
                r'\b(' + '|'.join(map(re.escape, self.pronoun_corrections.keys())) + r')\b',
                re.IGNORECASE
            )

            # 🔥 FIX #2: Recompile compound subject pattern with new entries
            self.compound_subject_pattern = re.compile(
                r'\b(' + '|'.join(map(re.escape, self.compound_subject_fixes.keys())) + r')\b',
                re.IGNORECASE
            )

            self.combined_verb_pattern = re.compile(
                r'\b(' + '|'.join(map(re.escape, self.verb_agreements.keys())) + r')\b',
                re.IGNORECASE
            )
            self.combined_irregular_pattern = re.compile(
                r'\b(' + '|'.join(map(re.escape, self.irregular_verbs.keys())) + r')\b',
                re.IGNORECASE
            )
            self.combined_word_order_pattern = re.compile(
                r'\b(' + '|'.join(map(re.escape, self.word_order_rules.keys())) + r')\b',
                re.IGNORECASE
            )
            self.combined_preposition_pattern = re.compile(
                r'\b(' + '|'.join(map(re.escape, self.preposition_rules.keys())) + r')\b',
                re.IGNORECASE
            )
        except Exception:
            pass

    def correct_contractions(self, text: str) -> str:
        """Fix missing apostrophes in contractions - POBOLJŠANA VERZIJA"""

        def replacement(match):
            word = match.group().lower()

            # 🔥 FIX: Sprečava "were" → "we're" grešku
            if word == 'were':
                return match.group()  # Vrati original "were"

            # 🔥 NOVI FIX: Sprečava "well" → "we'll" grešku
            if word == 'well':
                return match.group()  # Vrati original "well"

            correct = self.contractions.get(word, word)

            # 🔥 POBOLJŠANJE: Uvek kapitalizuj "I" u kontrakcijama
            if correct.lower().startswith("i"):
                correct = correct.replace('i', 'I')

                # Poseban slučaj za kontrakcije u sredini rečenice
                if match.group()[0].islower() and not match.group()[0].isupper():
                    # Ovo je "i'm" u sredini - kapitalizuj samo "I"
                    correct = 'I' + correct[1:]

            # Preserve original casing for first character
            elif match.group()[0].isupper():
                correct = correct.capitalize()

            return correct

        return self.contractions_pattern.sub(replacement, text)

    def prevent_well_correction(self, text: str) -> str:
        """
        Sprečava korekciju 'well' → 'we'll' koja je pogrešna.
        """
        # Koristimo regex da zamenimo 'We'll' nazad u 'Well' kada je na početku rečenice
        text = re.sub(r'^We\'ll\b', 'Well', text)
        text = re.sub(r'\. We\'ll\b', '. Well', text)
        text = re.sub(r'\! We\'ll\b', '! Well', text)
        text = re.sub(r'\? We\'ll\b', '? Well', text)
        text = re.sub(r'\, We\'ll\b', ', Well', text)
        return text

    def fix_overcorrection_articles(self, text: str) -> str:
        """
        Popravlja preterano dodavanje članova ispred pridjeva.
        """
        # Uklanja 'a/an' ispred pridjeva koji ne trebaju član
        overcorrections = {
            'a young': 'young',
            'an young': 'young',
            'a old': 'old',
            'an old': 'old',
            'a big': 'big',
            'an big': 'big',
            'a small': 'small',
            'an small': 'small',
            'a rich': 'rich',
            'an rich': 'rich',
            'a poor': 'poor',
            'an poor': 'poor',
        }

        for wrong, correct in overcorrections.items():
            text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text, flags=re.IGNORECASE)

        return text

    def correct_pronouns(self, text: str) -> str:
        """Fix subject pronoun errors like 'me am' -> 'i am' and 'me and i' -> 'i and i'"""

        def replacement(match):
            phrase = match.group().lower()
            correct = self.pronoun_corrections.get(phrase, phrase)

            # Always capitalize I
            if correct.startswith('i '):
                correct = 'I' + correct[1:]

            # Handle "I and I" pattern
            if 'i and i' in correct:
                correct = correct.replace('i and i', 'I and I')

            return correct

        return self.pronoun_pattern.sub(replacement, text)

    def correct_common_phrases(self, text: str) -> str:
        for wrong, correct in self.common_phrases.items():
            text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text, flags=re.IGNORECASE)
        return text

    def correct_articles(self, text):
        words = text.split()
        out = []
        i = 0
        while i < len(words):
            if i < len(words) - 1:
                p = f"{words[i]} {words[i + 1]}".lower()
                if p in self.article_corrections:
                    out.extend(self.article_corrections[p].split())
                    i += 2
                    continue
            out.append(words[i])
            i += 1
        return ' '.join(out)

    def add_missing_articles(self, text: str) -> str:
        """
        Add missing indefinite article 'a/an' before adjective + noun patterns.
        POBOLJŠANA VERZIJA: Sprečava dodavanje člana ispred pridjeva koji ne trebaju.
        """
        words = text.split()
        result = []
        i = 0

        while i < len(words):
            result.append(words[i])

            # Check if current word is a form of "be" verb
            if i < len(words) - 2 and words[i].lower() in ['is', 'was', 'are', 'were']:
                next_word = words[i + 1].lower()
                word_after = words[i + 2] if i + 2 < len(words) else None

                # Check if pattern is: be_verb + adjective + noun (without article)
                if next_word in self.common_adjectives and word_after:
                    # Don't add article if one already exists
                    if next_word not in ['a', 'an', 'the']:
                        # Check if word after adjective looks like a singular noun
                        # (simple heuristic: doesn't end in 's' for plural, not a verb form)
                        if not word_after.lower().endswith(('s', 'ing', 'ed', 'ly')):
                            # 🔥 POBOLJŠANJE: Proveri da li je pridjev već deo fraze
                            # Sprečava "was young" → "was a young" grešku
                            common_adjective_phrases = {
                                'young', 'old', 'big', 'small', 'rich', 'poor'
                            }

                            if next_word not in common_adjective_phrases:
                                # Determine a vs an
                                if next_word[0] in 'aeiou':
                                    result.append('an')
                                else:
                                    result.append('a')

            i += 1

        return ' '.join(result)

    def apply_pattern_replacement(self, text, mapping, pattern):
        def repl(m):
            result = mapping.get(m.group().lower(), m.group())
            # Always capitalize standalone "I"
            result = re.sub(r'\bi\b', 'I', result)
            return result

        return pattern.sub(repl, text)

    def core_correction_logic(self, text: str) -> Tuple[str, List[str]]:
        corrected = text
        changes = []

        # 1. Spelling corrections
        if self.spelling_corrector:
            tmp = self.spelling_corrector.correct_spelling(corrected)
            if tmp != corrected:
                changes.append("spelling")
            corrected = tmp

        # 2. CONTEXTUAL SPELLING (before contractions!)
        if self.contextual_corrector:
            tmp = self.contextual_corrector.correct(corrected)
            if tmp != corrected:
                changes.append("contextual spelling")
            corrected = tmp

        # 3. Contractions (high priority) - POBOLJŠANO
        tmp = self.correct_contractions(corrected)
        if tmp != corrected:
            changes.append("contractions")
        corrected = tmp

        # 🔥 NOVI FIX: Sprečava 'well' → 'we'll' grešku
        tmp = self.prevent_well_correction(corrected)
        if tmp != corrected:
            changes.append("prevent well overcorrection")
        corrected = tmp

        # 4. 🔥 FIX #2: Pronoun corrections (BEFORE compound subjects)
        # This converts "me and i" -> "i and i" first
        tmp = self.correct_pronouns(corrected)
        if tmp != corrected:
            changes.append("pronouns")
        corrected = tmp

        # 5. Verb agreement
        tmp = self.apply_pattern_replacement(corrected, self.verb_agreements, self.combined_verb_pattern)
        if tmp != corrected:
            changes.append("verb agreement")
        corrected = tmp

        # 6. Irregular verbs
        tmp = self.apply_pattern_replacement(corrected, self.irregular_verbs, self.combined_irregular_pattern)
        if tmp != corrected:
            changes.append("irregular verb")
        corrected = tmp

        # 7. Common phrases (includes "me and him" → "he and I")
        tmp = self.correct_common_phrases(corrected)
        if tmp != corrected:
            changes.append("common phrase")
        corrected = tmp

        # 8. 🔥 FIX #2: Compound subject + verb agreement (AFTER pronouns)
        # Now "i and i was" becomes "i and i were"
        tmp = self.apply_pattern_replacement(corrected, self.compound_subject_fixes, self.compound_subject_pattern)
        if tmp != corrected:
            changes.append("compound subject")
        corrected = tmp

        # 9. Articles (a/an corrections)
        tmp = self.correct_articles(corrected)
        if tmp != corrected:
            changes.append("article")
        corrected = tmp

        # 10. Add missing articles before adjective + noun
        tmp = self.add_missing_articles(corrected)
        if tmp != corrected:
            changes.append("missing article")
        corrected = tmp

        # 🔥 NOVI FIX: Popravlja preterano dodavanje članova
        tmp = self.fix_overcorrection_articles(corrected)
        if tmp != corrected:
            changes.append("fix article overcorrection")
        corrected = tmp

        # 11. Word order (includes question fixes)
        tmp = self.apply_pattern_replacement(corrected, self.word_order_rules, self.combined_word_order_pattern)
        if tmp != corrected:
            changes.append("word order")
        corrected = tmp

        # 12. Prepositions
        tmp = self.apply_pattern_replacement(corrected, self.preposition_rules, self.combined_preposition_pattern)
        if tmp != corrected:
            changes.append("preposition")
        corrected = tmp

        return corrected, changes

    def correct(self, text: str, safe_mode: bool = True) -> str:
        """
        Enhanced with optional safe mode for production.
        """
        # Existing correction logic...
        corrected = super().correct(text)

        # 🔥 SAFETY LAYER: Apply safe mode if enabled (default: True)
        # Za sada samo vratimo corrected, kasnije ćemo dodati SafeMode
        # if safe_mode:
        #     corrected = SafeMode.apply_safe_mode(corrected, text)

        return corrected