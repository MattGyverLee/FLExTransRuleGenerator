from __future__ import annotations
from typing import Optional
from flextrans_rule_generator.model.rule_constituent import RuleConstituent
from flextrans_rule_generator.model import strings


class Feature(RuleConstituent):
    def __init__(self):
        super().__init__()
        self.match: str = ""
        self.label: str = ""

    def find_constituent(self, identifier: int) -> Optional[RuleConstituent]:
        if self.identifier == identifier:
            return self
        return None

    def produce_html(self) -> str:
        if not self.label and not self.match:
            return ""
        label = self.label if self.label else strings.FEATURE_X
        match = self.match if self.match else strings.MATCH_X
        return (
            "<li>"
            + self.produce_span("tf-nc feature", "f")
            + f"{label}:{match}"
            + "</span></li>\n"
        )

    def duplicate(self) -> Feature:
        new_feature = Feature()
        new_feature.match = self.match
        new_feature.label = self.label
        return new_feature
