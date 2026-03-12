from flextrans_rule_generator.model.rule import FLExTransRule
from flextrans_rule_generator.model.rule_constituent import RuleConstituent


class ConstituentFinder:
    def find_constituent(self, rule: FLExTransRule, identifier: int) -> RuleConstituent | None:
        if identifier < rule.target.phrase.identifier:
            constituent = rule.source.phrase.find_constituent(identifier)
            if constituent is not None:
                return constituent
        else:
            constituent = rule.target.phrase.find_constituent(identifier)
        return constituent
