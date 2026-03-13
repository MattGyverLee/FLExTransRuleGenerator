from __future__ import annotations
from flextrans_rule_generator.model.rule import FLExTransRule
from flextrans_rule_generator.model.disjoint_feature_set import DisjointFeatureSet


class FLExTransRuleGenerator:
    def __init__(self):
        self.rules: list[FLExTransRule] = []
        self.overwrite_rules: bool = False
        self.disjoint_feature_sets: list[DisjointFeatureSet] = []
