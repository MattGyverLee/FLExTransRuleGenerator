import xml.etree.ElementTree as ET

from flextrans_rule_generator.model.rule_generator import FLExTransRuleGenerator
from flextrans_rule_generator.model.rule import FLExTransRule
from flextrans_rule_generator.model.source import Source
from flextrans_rule_generator.model.target import Target
from flextrans_rule_generator.model.phrase import Phrase, PhraseType
from flextrans_rule_generator.model.word import Word, HeadValue
from flextrans_rule_generator.model.affix import Affix, AffixType
from flextrans_rule_generator.model.feature import Feature
from flextrans_rule_generator.model.category import Category


class XmlBackEndProvider:
    def __init__(self):
        self.rule_generator: FLExTransRuleGenerator | None = None

    def load_data_from_file(self, file_name: str):
        tree = ET.parse(file_name)
        root = tree.getroot()

        gen = FLExTransRuleGenerator()

        rules_elem = root.find("FLExTransRules")
        if rules_elem is not None:
            for rule_elem in rules_elem.findall("FLExTransRule"):
                rule = FLExTransRule()
                rule.name = rule_elem.get("name", "")

                source_elem = rule_elem.find("Source")
                if source_elem is not None:
                    rule.source = self._parse_source(source_elem)

                target_elem = rule_elem.find("Target")
                if target_elem is not None:
                    rule.target = self._parse_target(target_elem)

                gen.rules.append(rule)

        self.rule_generator = gen

    def _parse_source(self, source_elem: ET.Element) -> Source:
        source = Source()
        phrase_elem = source_elem.find("Phrase")
        if phrase_elem is not None:
            source.phrase = self._parse_phrase(phrase_elem, PhraseType.SOURCE)
        return source

    def _parse_target(self, target_elem: ET.Element) -> Target:
        target = Target()
        phrase_elem = target_elem.find("Phrase")
        if phrase_elem is not None:
            target.phrase = self._parse_phrase(phrase_elem, PhraseType.TARGET)
        return target

    def _parse_phrase(self, phrase_elem: ET.Element, phrase_type: PhraseType) -> Phrase:
        phrase = Phrase()
        phrase.type = phrase_type
        words_elem = phrase_elem.find("Words")
        if words_elem is not None:
            for word_elem in words_elem.findall("Word"):
                word = self._parse_word(word_elem)
                phrase.words.append(word)
        return phrase

    def _parse_word(self, word_elem: ET.Element) -> Word:
        word = Word()
        word.category = word_elem.get("category", "")
        word.id = word_elem.get("id", "")
        head_str = word_elem.get("head", "")
        if head_str == "yes":
            word.head = HeadValue.YES
        else:
            word.head = HeadValue.NO
        word.category_constituent = Category(word.category)

        features_elem = word_elem.find("Features")
        if features_elem is not None:
            for feat_elem in features_elem.findall("Feature"):
                feat = Feature()
                feat.label = feat_elem.get("label", "")
                feat.match = feat_elem.get("match", "")
                word.features.append(feat)

        affixes_elem = word_elem.find("Affixes")
        if affixes_elem is not None:
            for affix_elem in affixes_elem.findall("Affix"):
                affix = self._parse_affix(affix_elem)
                word.affixes.append(affix)

        return word

    def _parse_affix(self, affix_elem: ET.Element) -> Affix:
        affix = Affix()
        type_str = affix_elem.get("type", "suffix")
        if type_str == "prefix":
            affix.type = AffixType.PREFIX
        else:
            affix.type = AffixType.SUFFIX

        features_elem = affix_elem.find("Features")
        if features_elem is not None:
            for feat_elem in features_elem.findall("Feature"):
                feat = Feature()
                feat.label = feat_elem.get("label", "")
                feat.match = feat_elem.get("match", "")
                affix.features.append(feat)

        return affix

    def save_data_to_file(self, file_name: str):
        if self.rule_generator is None:
            return

        lines = []
        lines.append('<?xml version="1.0" encoding="utf-8"?>')
        lines.append('<!DOCTYPE FLExTransRuleGenerator PUBLIC " -//XMLmind//DTD FLExTransRuleGenerator//EN"')
        lines.append('"FLExTransRuleGenerator.dtd">')
        lines.append("<FLExTransRuleGenerator>")
        lines.append("  <FLExTransRules>")

        for rule in self.rule_generator.rules:
            lines.append(f'    <FLExTransRule name="{rule.name}">')
            self._write_source(lines, rule.source, 6)
            self._write_target(lines, rule.target, 6)
            lines.append("    </FLExTransRule>")

        lines.append("  </FLExTransRules>")
        lines.append("</FLExTransRuleGenerator>")

        with open(file_name, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(lines))

    def _write_source(self, lines: list[str], source: Source, indent: int):
        pad = " " * indent
        lines.append(f"{pad}<Source>")
        self._write_phrase(lines, source.phrase, indent + 2)
        lines.append(f"{pad}</Source>")

    def _write_target(self, lines: list[str], target: Target, indent: int):
        pad = " " * indent
        lines.append(f"{pad}<Target>")
        self._write_phrase(lines, target.phrase, indent + 2)
        lines.append(f"{pad}</Target>")

    def _write_phrase(self, lines: list[str], phrase: Phrase, indent: int):
        pad = " " * indent
        lines.append(f"{pad}<Phrase>")
        lines.append(f"{pad}  <Words>")
        for word in phrase.words:
            self._write_word(lines, word, indent + 4)
        lines.append(f"{pad}  </Words>")
        lines.append(f"{pad}</Phrase>")

    def _write_word(self, lines: list[str], word: Word, indent: int):
        pad = " " * indent
        head_str = "yes" if word.head == HeadValue.YES else "no"
        cat_str = word.category if word.category else ""
        attrs = f'id="{word.id}" category="{cat_str}" head="{head_str}"'
        lines.append(f"{pad}<Word {attrs}>")
        self._write_features(lines, word.features, indent + 2)
        self._write_affixes(lines, word.affixes, indent + 2)
        lines.append(f"{pad}</Word>")

    def _write_features(self, lines: list[str], features: list, indent: int):
        pad = " " * indent
        if not features:
            lines.append(f"{pad}<Features />")
        else:
            lines.append(f"{pad}<Features>")
            for feat in features:
                lines.append(f'{pad}  <Feature match="{feat.match}" label="{feat.label}" />')
            lines.append(f"{pad}</Features>")

    def _write_affixes(self, lines: list[str], affixes: list, indent: int):
        pad = " " * indent
        if not affixes:
            lines.append(f"{pad}<Affixes />")
        else:
            lines.append(f"{pad}<Affixes>")
            for affix in affixes:
                self._write_affix(lines, affix, indent + 2)
            lines.append(f"{pad}</Affixes>")

    def _write_affix(self, lines: list[str], affix: Affix, indent: int):
        pad = " " * indent
        type_str = "prefix" if affix.type == AffixType.PREFIX else "suffix"
        lines.append(f'{pad}<Affix type="{type_str}">')
        self._write_features(lines, affix.features, indent + 2)
        lines.append(f"{pad}</Affix>")
