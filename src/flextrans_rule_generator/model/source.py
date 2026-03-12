from __future__ import annotations
from flextrans_rule_generator.model.phrase import Phrase, PhraseType


class Source:
    def __init__(self):
        self.phrase: Phrase = Phrase()
        self.phrase.type = PhraseType.SOURCE

    def duplicate(self) -> Source:
        new_source = Source()
        new_source.phrase = self.phrase.duplicate()
        return new_source
