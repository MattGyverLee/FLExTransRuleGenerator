from __future__ import annotations
from enum import Enum
from typing import Optional
from flextrans_rule_generator.model.constituent_with_features import ConstituentWithFeatures
from flextrans_rule_generator.model.rule_constituent import RuleConstituent
from flextrans_rule_generator.model import strings


class AffixType(Enum):
    PREFIX = "prefix"
    SUFFIX = "suffix"


class Affix(ConstituentWithFeatures):
    def __init__(self):
        super().__init__()
        self.type: AffixType = AffixType.SUFFIX

    def find_constituent(self, identifier: int) -> Optional[RuleConstituent]:
        if self.identifier == identifier:
            return self
        return self._find_constituent_in_features(identifier)

    def produce_html(self) -> str:
        type_str = strings.PREFIX if self.type == AffixType.PREFIX else strings.SUFFIX
        result = "<li>" + self.produce_span("tf-nc affix", "a") + type_str + "</span>"
        if self.features:
            result += "<ul>" + self._produce_html_for_features() + "</ul>"
        result += "</li>\n"
        return result

    def duplicate(self) -> Affix:
        new_affix = Affix()
        new_affix.type = self.type
        new_affix.features = self._duplicate_features()
        return new_affix
