from __future__ import annotations
from flextrans_rule_generator.model.rule_constituent import RuleConstituent
from flextrans_rule_generator.model.source import Source
from flextrans_rule_generator.model.target import Target
from flextrans_rule_generator.model import strings


class FLExTransRule(RuleConstituent):
    def __init__(self):
        super().__init__()
        self.source: Source = Source()
        self.target: Target = Target()
        self.name: str = ""

    def duplicate(self) -> FLExTransRule:
        new_rule = FLExTransRule()
        new_rule.name = self.name
        new_rule.source = self.source.duplicate()
        new_rule.target = self.target.duplicate()
        return new_rule

    def __str__(self) -> str:
        if self.name:
            return self.name
        return strings.NAME_MISSING
