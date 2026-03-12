import pytest
from pathlib import Path

class TestConstituentFinder:
    def setup_method(self):
        from flextrans_rule_generator.service.xml_backend_provider import XmlBackEndProvider
        from flextrans_rule_generator.service.constituent_finder import ConstituentFinder
        from flextrans_rule_generator.service.rule_identifier_setter import RuleIdentifierAndParentSetter
        self.provider = XmlBackEndProvider()
        self.finder = ConstituentFinder()
        self.setter = RuleIdentifierAndParentSetter()
        self.test_data = Path(__file__).parent / "test_data"

    def test_set_for_ex1a_def_noun(self):
        from flextrans_rule_generator.model.phrase import Phrase
        from flextrans_rule_generator.model.word import Word
        from flextrans_rule_generator.model.category import Category
        from flextrans_rule_generator.model.feature import Feature

        self.provider.load_data_from_file(str(self.test_data / "Ex1a_Def-Noun.xml"))
        rule = self.provider.rule_generator.rules[0]
        self.setter.set_identifiers_and_parents(rule)

        c = self.finder.find_constituent(rule, 1)
        assert isinstance(c, Phrase)
        c = self.finder.find_constituent(rule, 2)
        assert isinstance(c, Word)
        c = self.finder.find_constituent(rule, 3)
        assert isinstance(c, Category)
        assert c.name == "def"
        c = self.finder.find_constituent(rule, 4)
        assert isinstance(c, Word)
        c = self.finder.find_constituent(rule, 5)
        assert isinstance(c, Category)
        assert c.name == "n"
        c = self.finder.find_constituent(rule, 6)
        assert isinstance(c, Phrase)
        c = self.finder.find_constituent(rule, 7)
        assert isinstance(c, Word)
        c = self.finder.find_constituent(rule, 8)
        assert isinstance(c, Category)
        c = self.finder.find_constituent(rule, 9)
        assert isinstance(c, Feature)
        assert c.label == "gender"
        assert c.match == "α"
        c = self.finder.find_constituent(rule, 13)
        assert c is None

    def test_set_for_ex4b_indef_adj_noun(self):
        from flextrans_rule_generator.model.phrase import Phrase
        from flextrans_rule_generator.model.word import Word
        from flextrans_rule_generator.model.category import Category
        from flextrans_rule_generator.model.feature import Feature
        from flextrans_rule_generator.model.affix import Affix

        self.provider.load_data_from_file(str(self.test_data / "Ex4b_Indef-Adj-Noun.xml"))
        rule = self.provider.rule_generator.rules[0]
        self.setter.set_identifiers_and_parents(rule)

        c = self.finder.find_constituent(rule, 1)
        assert isinstance(c, Phrase)
        c = self.finder.find_constituent(rule, 3)
        assert isinstance(c, Category)
        assert c.name == "indef"
        c = self.finder.find_constituent(rule, 5)
        assert isinstance(c, Category)
        assert c.name == "adj"
        c = self.finder.find_constituent(rule, 11)
        assert isinstance(c, Affix)
        c = self.finder.find_constituent(rule, 12)
        assert isinstance(c, Feature)
        assert c.label == "gender"
        c = self.finder.find_constituent(rule, 26)
        assert c is None
