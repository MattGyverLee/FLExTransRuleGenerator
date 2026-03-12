import pytest
from flextrans_rule_generator.model.word import Word, HeadValue
from flextrans_rule_generator.model.affix import Affix, AffixType
from flextrans_rule_generator.model.feature import Feature

class TestWord:
    def setup_method(self):
        self.word = Word()
        self.word.id = "Source 1"
        self.word.category = "Noun"
        self.word.category_constituent.name = "Noun"
        self.word.head = HeadValue.YES

    def test_delete_category(self):
        self.word.delete_category()
        assert self.word.category == ""
        assert self.word.category_constituent.name == ""

    def test_insert_category(self):
        self.word.delete_category()
        self.word.insert_category("verb")
        assert self.word.category == "verb"
        assert self.word.category_constituent.name == "verb"

    def test_delete_affix_at(self):
        self._create_two_affixes()
        assert len(self.word.affixes) == 2
        self.word.delete_affix_at(0)
        assert len(self.word.affixes) == 1
        assert self.word.affixes[0].type == AffixType.SUFFIX
        self.word.delete_affix_at(0)
        assert len(self.word.affixes) == 0
        # boundary: no-op on empty
        self.word.delete_affix_at(0)
        assert len(self.word.affixes) == 0

    def test_insert_new_affix_at(self):
        self.word.insert_new_affix_at(AffixType.PREFIX, 0)
        assert len(self.word.affixes) == 1
        assert self.word.affixes[0].type == AffixType.PREFIX
        self.word.insert_new_affix_at(AffixType.SUFFIX, 0)
        assert len(self.word.affixes) == 2
        assert self.word.affixes[0].type == AffixType.SUFFIX
        assert self.word.affixes[1].type == AffixType.PREFIX
        self.word.insert_new_affix_at(AffixType.SUFFIX, 2)
        assert len(self.word.affixes) == 3
        assert self.word.affixes[2].type == AffixType.SUFFIX

    def test_insert_affix_at(self):
        affix1 = Affix()
        affix1.type = AffixType.PREFIX
        self.word.insert_affix_at(affix1, 0)
        assert len(self.word.affixes) == 1
        assert self.word.affixes[0].type == AffixType.PREFIX
        affix2 = Affix()
        affix2.type = AffixType.SUFFIX
        self.word.insert_affix_at(affix2, 0)
        assert len(self.word.affixes) == 2
        assert self.word.affixes[0].type == AffixType.SUFFIX
        assert self.word.affixes[1].type == AffixType.PREFIX

    def test_delete_feature(self):
        feat1 = self.word.insert_new_feature("gender", "alpha")
        feat2 = self.word.insert_new_feature("number", "beta")
        assert len(self.word.features) == 2
        self.word.delete_feature(feat1)
        assert len(self.word.features) == 1
        assert self.word.features[0].label == "number"
        self.word.delete_feature(feat2)
        assert len(self.word.features) == 0

    def test_swap_position_of_affixes(self):
        self._create_two_affixes()
        assert self.word.affixes[0].type == AffixType.PREFIX
        assert self.word.affixes[1].type == AffixType.SUFFIX
        self.word.swap_position_of_affixes(0, 1)
        assert self.word.affixes[0].type == AffixType.SUFFIX
        assert self.word.affixes[1].type == AffixType.PREFIX
        # swap back
        self.word.swap_position_of_affixes(1, 0)
        assert self.word.affixes[0].type == AffixType.PREFIX
        assert self.word.affixes[1].type == AffixType.SUFFIX
        # invalid indices - no change
        self.word.swap_position_of_affixes(-1, 0)
        assert self.word.affixes[0].type == AffixType.PREFIX
        self.word.swap_position_of_affixes(0, 2)
        assert self.word.affixes[0].type == AffixType.PREFIX

    def _create_two_affixes(self):
        affix1 = Affix()
        affix1.type = AffixType.PREFIX
        self.word.affixes.append(affix1)
        affix2 = Affix()
        affix2.type = AffixType.SUFFIX
        self.word.affixes.append(affix2)
