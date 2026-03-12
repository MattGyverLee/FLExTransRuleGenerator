from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from flextrans_rule_generator.flex_model.flex_feature import FLExFeature

class FLExFeatureValue:
    def __init__(self):
        self.abbreviation: str = ""
        self.feature: FLExFeature | None = None
    def __str__(self) -> str:
        result = ""
        if self.feature is not None:
            result += self.feature.name + " : "
        result += self.abbreviation
        return result
