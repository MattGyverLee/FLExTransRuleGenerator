from __future__ import annotations
from enum import Enum
from typing import Optional
from flextrans_rule_generator.model.constituent_with_features import ConstituentWithFeatures
from flextrans_rule_generator.model.rule_constituent import RuleConstituent
from flextrans_rule_generator.model.category import Category
from flextrans_rule_generator.model.affix import Affix, AffixType
from flextrans_rule_generator.model import strings


class HeadValue(Enum):
    YES = "yes"
    NO = "no"


class Word(ConstituentWithFeatures):
    def __init__(self):
        super().__init__()
        self.affixes: list[Affix] = []
        self.id: str = ""
        self.category: str = ""
        self.head: HeadValue = HeadValue.NO
        self.category_constituent: Category = Category(self.category)

    def delete_category(self) -> None:
        self.category = ""
        self.category_constituent = Category("")

    def insert_category(self, cat: str) -> None:
        self.category = cat
        if self.category_constituent is not None:
            self.category_constituent.name = cat
        else:
            self.category_constituent = Category(cat)

    def delete_affix_at(self, index: int) -> None:
        if index < 0 or index >= len(self.affixes):
            return
        del self.affixes[index]

    def insert_affix_at(self, affix: Affix, index: int) -> None:
        if index < 0 or (index > len(self.affixes) and len(self.affixes) > 0):
            return
        self.affixes.insert(index, affix)

    def insert_new_affix_at(self, affix_type: AffixType, index: int) -> None:
        if index < 0 or (index > len(self.affixes) and len(self.affixes) > 0):
            return
        new_affix = Affix()
        new_affix.type = affix_type
        self.affixes.insert(index, new_affix)

    def swap_position_of_affixes(self, index: int, other_index: int) -> None:
        if index < 0 or index >= len(self.affixes):
            return
        if other_index < 0 or other_index >= len(self.affixes):
            return
        self.affixes[index], self.affixes[other_index] = self.affixes[other_index], self.affixes[index]

    def find_constituent(self, identifier: int) -> Optional[RuleConstituent]:
        if self.identifier == identifier:
            return self
        constituent = self.category_constituent.find_constituent(identifier)
        if constituent is not None:
            return constituent
        constituent = self._find_constituent_in_features(identifier)
        if constituent is not None:
            return constituent
        for affix in self.affixes:
            constituent = affix.find_constituent(identifier)
            if constituent is not None:
                return constituent
        return None

    def produce_html(self) -> str:
        parts = ["<li>"]
        parts.append(self.produce_span("tf-nc", "w"))
        parts.append(strings.WORD)
        if self.head == HeadValue.YES:
            parts.append("(")
            parts.append('<span style="font-style:italic; font-size:smaller">')
            parts.append(strings.HEAD)
            parts.append("</span>")
            parts.append(")")
        if self.id:
            parts.append('<span class="index">')
            parts.append(self.id)
            parts.append("</span></span>\n")
        if self.category or self.features or self.affixes:
            parts.append("<ul>\n")
            if self.category:
                parts.append(self.category_constituent.produce_html())
            parts.append(self._produce_html_for_features())
            for affix in self.affixes:
                parts.append(affix.produce_html())
            parts.append("</ul>\n")
        parts.append("</li>")
        return "".join(parts)

    def duplicate(self) -> Word:
        new_word = Word()
        new_word.id = self.id
        new_word.category = self.category
        new_word.category_constituent = self.category_constituent.duplicate()
        new_word.head = self.head
        for affix in self.affixes:
            new_word.affixes.append(affix.duplicate())
        new_word.features = self._duplicate_features()
        return new_word
