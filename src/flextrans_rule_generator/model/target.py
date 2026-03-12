from __future__ import annotations
from flextrans_rule_generator.model.phrase import Phrase, PhraseType


class Target:
    def __init__(self):
        self.phrase: Phrase = Phrase()
        self.phrase.type = PhraseType.TARGET

    def duplicate(self) -> Target:
        new_target = Target()
        new_target.phrase = self.phrase.duplicate()
        return new_target
