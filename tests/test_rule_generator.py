import pytest
from flextrans_rule_generator.model.rule_generator import FLExTransRuleGenerator
from flextrans_rule_generator.model.rule import FLExTransRule
from flextrans_rule_generator.model.word import Word, HeadValue
from flextrans_rule_generator.model.affix import Affix, AffixType
from flextrans_rule_generator.model.feature import Feature
from flextrans_rule_generator.model.phrase import PhraseType

class TestRuleGenerator:
    def test_new_operation(self):
        gen = FLExTransRuleGenerator()
        assert len(gen.rules) == 0

        rule = FLExTransRule()
        gen.rules.append(rule)
        assert len(gen.rules) == 1

        assert rule.source is not None
        assert rule.target is not None
        assert rule.source.phrase.type == PhraseType.SOURCE
        assert rule.target.phrase.type == PhraseType.TARGET

        word = Word()
        assert word.id == ""
        assert word.category == ""
        assert word.head == HeadValue.NO
        assert len(word.affixes) == 0
        assert len(word.features) == 0

        affix = Affix()
        assert affix.type == AffixType.SUFFIX
        assert len(affix.features) == 0

        feature = Feature()
        assert feature.match == ""
        assert feature.label == ""
