from __future__ import annotations
from enum import Enum
from typing import Optional
from flextrans_rule_generator.model.rule_constituent import RuleConstituent
from flextrans_rule_generator.model.word import Word, HeadValue
from flextrans_rule_generator.model import strings


class PhraseType(Enum):
    SOURCE = "source"
    TARGET = "target"


class Phrase(RuleConstituent):
    def __init__(self):
        super().__init__()
        self.words: list[Word] = []
        self.type: PhraseType = PhraseType.SOURCE

    def delete_word_at(self, index: int) -> None:
        if index < 0 or index >= len(self.words):
            return
        del self.words[index]

    def insert_new_word_at(self, index: int) -> None:
        if index < 0 or index >= len(self.words):
            return
        new_word = Word()
        new_word.id = str(len(self.words) + 1)
        self.words.insert(index, new_word)

    def insert_word_at(self, word: Word, index: int) -> None:
        if index < 0 or index >= len(self.words):
            return
        self.words.insert(index, word)

    def swap_position_of_words(self, index: int, other_index: int) -> None:
        if index < 0 or index >= len(self.words):
            return
        if other_index < 0 or other_index >= len(self.words):
            return
        self.words[index], self.words[other_index] = self.words[other_index], self.words[index]

    def mark_word_as_head(self, word: Word) -> None:
        index = self.words.index(word) if word in self.words else -1
        if index < 0 or index >= len(self.words):
            return
        for w in self.words:
            if w == word:
                w.head = HeadValue.YES
            else:
                w.head = HeadValue.NO

    def produce_html(self) -> str:
        parts = ["<li>"]
        parts.append(self.produce_span("tf-nc", "p"))
        parts.append(strings.PHRASE)
        parts.append('<span class="language">')
        if self.type == PhraseType.SOURCE:
            parts.append(strings.SRC)
        else:
            parts.append(strings.TGT)
        parts.append("</span></span>\n")
        parts.append("<ul>")
        for word in self.words:
            parts.append(word.produce_html())
        parts.append("</ul>")
        parts.append("</li>")
        return "".join(parts)

    def find_constituent(self, identifier: int) -> Optional[RuleConstituent]:
        if self.identifier == identifier:
            return self
        for word in self.words:
            constituent = word.find_constituent(identifier)
            if constituent is not None:
                return constituent
        return None

    def duplicate(self) -> Phrase:
        new_phrase = Phrase()
        for word in self.words:
            new_phrase.words.append(word.duplicate())
        return new_phrase
