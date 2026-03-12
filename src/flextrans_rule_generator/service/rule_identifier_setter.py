from flextrans_rule_generator.model.rule import FLExTransRule
from flextrans_rule_generator.model.phrase import Phrase
from flextrans_rule_generator.model.word import Word
from flextrans_rule_generator.model.feature import Feature
from flextrans_rule_generator.model.affix import Affix


class RuleIdentifierAndParentSetter:
    def __init__(self):
        self.current_identifier: int = 0

    def set_identifiers_and_parents(self, rule: FLExTransRule):
        self.current_identifier = 0
        self._set_phrase_identifiers(rule.source.phrase)
        self._set_phrase_identifiers(rule.target.phrase)
        rule.source.phrase.parent = rule
        rule.target.phrase.parent = rule

    def _set_phrase_identifiers(self, phrase: Phrase):
        self.current_identifier += 1
        phrase.identifier = self.current_identifier
        for word in phrase.words:
            self.current_identifier += 1
            word.identifier = self.current_identifier
            word.parent = phrase
            self.current_identifier += 1
            word.category_constituent.identifier = self.current_identifier
            word.category_constituent.parent = word
            self._set_feature_identifiers(word.features, word)
            for affix in word.affixes:
                self.current_identifier += 1
                affix.identifier = self.current_identifier
                affix.parent = word
                self._set_feature_identifiers(affix.features, affix)

    def _set_feature_identifiers(self, features: list, parent):
        for feature in features:
            self.current_identifier += 1
            feature.identifier = self.current_identifier
            feature.parent = parent
