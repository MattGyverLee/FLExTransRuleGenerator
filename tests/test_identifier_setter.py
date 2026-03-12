import pytest
from pathlib import Path

class TestRuleIdentifierAndParentSetter:
    def setup_method(self):
        from flextrans_rule_generator.service.xml_backend_provider import XmlBackEndProvider
        from flextrans_rule_generator.service.rule_identifier_setter import RuleIdentifierAndParentSetter
        self.provider = XmlBackEndProvider()
        self.setter = RuleIdentifierAndParentSetter()
        self.test_data = Path(__file__).parent / "test_data"

    def test_identifiers_ex1a(self):
        self.provider.load_data_from_file(str(self.test_data / "Ex1a_Def-Noun.xml"))
        rule = self.provider.rule_generator.rules[0]
        self.setter.set_identifiers_and_parents(rule)
        src = rule.source.phrase
        assert src.identifier == 1
        assert src.words[0].identifier == 2
        assert src.words[0].category_constituent.identifier == 3
        assert src.words[1].identifier == 4
        assert src.words[1].category_constituent.identifier == 5
        tgt = rule.target.phrase
        assert tgt.identifier == 6
        assert tgt.words[0].identifier == 7
        assert tgt.words[0].category_constituent.identifier == 8
        assert tgt.words[0].features[0].identifier == 9
        assert tgt.words[1].identifier == 10
        assert tgt.words[1].category_constituent.identifier == 11
        assert tgt.words[1].features[0].identifier == 12

    def test_identifiers_ex4b(self):
        self.provider.load_data_from_file(str(self.test_data / "Ex4b_Indef-Adj-Noun.xml"))
        rule = self.provider.rule_generator.rules[0]
        self.setter.set_identifiers_and_parents(rule)
        src = rule.source.phrase
        assert src.identifier == 1
        assert src.words[0].identifier == 2
        assert src.words[0].category_constituent.identifier == 3
        assert src.words[2].identifier == 6
        assert src.words[2].category_constituent.identifier == 7
        tgt = rule.target.phrase
        assert tgt.identifier == 8
        assert tgt.words[0].identifier == 9
        assert tgt.words[0].category_constituent.identifier == 10
        assert tgt.words[0].affixes[0].identifier == 11
        assert tgt.words[0].affixes[0].features[0].identifier == 12
        assert tgt.words[0].affixes[1].identifier == 13
        assert tgt.words[0].affixes[1].features[0].identifier == 14
        assert tgt.words[2].affixes[1].identifier == 24
        assert tgt.words[2].affixes[1].features[0].identifier == 25

    def test_parents_ex1a(self):
        self.provider.load_data_from_file(str(self.test_data / "Ex1a_Def-Noun.xml"))
        rule = self.provider.rule_generator.rules[0]
        self.setter.set_identifiers_and_parents(rule)
        src = rule.source.phrase
        assert src.parent is rule
        assert src.words[0].parent is src
        assert src.words[0].category_constituent.parent is src.words[0]
        tgt = rule.target.phrase
        assert tgt.parent is rule
        assert tgt.words[0].parent is tgt
        assert tgt.words[0].features[0].parent is tgt.words[0]

    def test_parents_ex4b(self):
        self.provider.load_data_from_file(str(self.test_data / "Ex4b_Indef-Adj-Noun.xml"))
        rule = self.provider.rule_generator.rules[0]
        self.setter.set_identifiers_and_parents(rule)
        tgt = rule.target.phrase
        assert tgt.words[0].affixes[0].parent is tgt.words[0]
        assert tgt.words[0].affixes[0].features[0].parent is tgt.words[0].affixes[0]
