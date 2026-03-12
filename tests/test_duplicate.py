import pytest
from flextrans_rule_generator.model.word import Word, HeadValue
from flextrans_rule_generator.model.affix import Affix, AffixType
from flextrans_rule_generator.model.feature import Feature
from flextrans_rule_generator.model.rule import FLExTransRule

class TestDuplicate:
    def setup_method(self):
        self.rule = FLExTransRule()
        self.rule.name = "test rule"
        source_word = Word()
        source_word.id = "1"
        source_word.category = "Noun"
        source_word.category_constituent.name = "Noun"
        source_word.head = HeadValue.YES
        self.rule.source.phrase.words.append(source_word)
        target_word = Word()
        target_word.id = "1"
        target_word.category = "Det"
        target_word.category_constituent.name = "Det"
        target_word.head = HeadValue.NO
        self.rule.target.phrase.words.append(target_word)

    def test_rule_duplicate(self):
        dup = self.rule.duplicate()
        assert dup.name == self.rule.name
        assert len(dup.source.phrase.words) == len(self.rule.source.phrase.words)
        assert len(dup.target.phrase.words) == len(self.rule.target.phrase.words)

    def test_word_duplicate(self):
        word = self.rule.source.phrase.words[0]
        word.insert_new_feature("gender", "alpha")
        affix = Affix()
        affix.type = AffixType.PREFIX
        word.affixes.append(affix)
        dup = word.duplicate()
        assert dup.id == word.id
        assert dup.category == word.category
        assert dup.category_constituent.name == word.category_constituent.name
        assert len(dup.affixes) == len(word.affixes)
        assert len(dup.features) == len(word.features)

    def test_affix_duplicate(self):
        affix = Affix()
        affix.type = AffixType.PREFIX
        affix.insert_new_feature("gender", "alpha")
        dup = affix.duplicate()
        assert dup.type == AffixType.PREFIX
        assert len(dup.features) == 1
        assert dup.features[0].label == "gender"
        assert dup.features[0].match == "alpha"
