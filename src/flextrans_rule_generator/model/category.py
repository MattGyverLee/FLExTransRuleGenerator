from __future__ import annotations
from typing import Optional
from flextrans_rule_generator.model.rule_constituent import RuleConstituent
from flextrans_rule_generator.model import strings


class Category(RuleConstituent):
    def __init__(self, name: str = ""):
        super().__init__()
        self.name: str = name

    def find_constituent(self, identifier: int) -> Optional[RuleConstituent]:
        if self.identifier == identifier:
            return self
        return None

    def produce_html(self) -> str:
        return (
            "<li>"
            + self.produce_span("tf-nc category", "c")
            + f"{strings.CAT}:{self.name}"
            + "</span></li>\n"
        )

    def duplicate(self) -> Category:
        return Category(self.name)
