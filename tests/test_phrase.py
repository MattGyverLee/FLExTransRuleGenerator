import pytest
from flextrans_rule_generator.model.word import Word, HeadValue
from flextrans_rule_generator.model.phrase import Phrase, PhraseType
from flextrans_rule_generator.model.source import Source
from flextrans_rule_generator.model.target import Target
from flextrans_rule_generator.model.rule import FLExTransRule

class TestPhrase:
    def setup_method(self):
        self.rule = FLExTransRule()
        self.rule.name = "test rule"
        # Source words
        source_word1 = Word()
        source_word1.id = "Source 1"
        source_word1.category = "Noun"
        source_word1.head = HeadValue.YES
        source_word2 = Word()
        source_word2.id = "Source 2"
        source_word2.category = "Det"
        source_word2.head = HeadValue.NO
        self.rule.source.phrase.words.append(source_word1)
        self.rule.source.phrase.words.append(source_word2)
        # Target words
        target_word1 = Word()
        target_word1.id = "Target 1"
        target_word1.category = "Det"
        target_word1.head = HeadValue.NO
        target_word2 = Word()
        target_word2.id = "Target 2"
        target_word2.category = "Noun"
        target_word2.head = HeadValue.YES
        self.rule.target.phrase.words.append(target_word1)
        self.rule.target.phrase.words.append(target_word2)

    def test_delete_word_at(self):
        phrase = self.rule.source.phrase
        assert len(phrase.words) == 2
        phrase.delete_word_at(0)
        assert len(phrase.words) == 1
        assert phrase.words[0].id == "Source 2"
        phrase.delete_word_at(0)
        assert len(phrase.words) == 0
        # boundary: no-op
        phrase.delete_word_at(0)
        assert len(phrase.words) == 0

    def test_insert_new_word_at(self):
        phrase = self.rule.source.phrase
        phrase.insert_new_word_at(1)
        assert len(phrase.words) == 3
        assert phrase.words[1].id == "3"
        phrase.insert_new_word_at(0)
        assert len(phrase.words) == 4
        assert phrase.words[0].id == "4"

    def test_swap_position_of_words(self):
        phrase = self.rule.source.phrase
        phrase.swap_position_of_words(0, 1)
        assert phrase.words[0].id == "Source 2"
        assert phrase.words[1].id == "Source 1"
        # swap back
        phrase.swap_position_of_words(1, 0)
        assert phrase.words[0].id == "Source 1"
        assert phrase.words[1].id == "Source 2"
        # invalid indices
        phrase.swap_position_of_words(-1, 0)
        assert phrase.words[0].id == "Source 1"
        phrase.swap_position_of_words(0, 2)
        assert phrase.words[0].id == "Source 1"

    def test_mark_word_as_head(self):
        phrase = self.rule.source.phrase
        source_word2 = phrase.words[1]
        phrase.mark_word_as_head(source_word2)
        assert phrase.words[0].head == HeadValue.NO
        assert phrase.words[1].head == HeadValue.YES
