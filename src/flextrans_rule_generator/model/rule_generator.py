from __future__ import annotations
from flextrans_rule_generator.model.rule import FLExTransRule


class FLExTransRuleGenerator:
    def __init__(self):
        self.rules: list[FLExTransRule] = []
