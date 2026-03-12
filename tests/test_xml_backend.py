import pytest
from pathlib import Path
from flextrans_rule_generator.model.word import Word, HeadValue
from flextrans_rule_generator.model.affix import Affix, AffixType
from flextrans_rule_generator.model.feature import Feature
from flextrans_rule_generator.model.phrase import PhraseType

class TestXmlBackEndProvider:
    def setup_method(self):
        from flextrans_rule_generator.service.xml_backend_provider import XmlBackEndProvider
        self.provider = XmlBackEndProvider()
        self.test_data = Path(__file__).parent / "test_data"

    def test_load_ex1a_def_noun(self):
        self.provider.load_data_from_file(str(self.test_data / "Ex1a_Def-Noun.xml"))
        gen = self.provider.rule_generator
        assert len(gen.rules) == 1
        rule = gen.rules[0]
        assert rule.name == "Definite - Noun"
        # Source
        src_words = rule.source.phrase.words
        assert len(src_words) == 2
        assert src_words[0].id == "1"
        assert src_words[0].category == "def"
        assert src_words[0].head == HeadValue.NO
        assert len(src_words[0].features) == 0
        assert len(src_words[0].affixes) == 0
        assert src_words[1].id == "2"
        assert src_words[1].category == "n"
        assert src_words[1].head == HeadValue.NO
        # Target
        tgt_words = rule.target.phrase.words
        assert len(tgt_words) == 2
        assert tgt_words[0].id == "1"
        assert tgt_words[0].category == ""
        assert tgt_words[0].head == HeadValue.NO
        assert len(tgt_words[0].features) == 1
        assert tgt_words[0].features[0].label == "gender"
        assert tgt_words[0].features[0].match == "α"
        assert tgt_words[1].id == "2"
        assert tgt_words[1].head == HeadValue.YES
        assert len(tgt_words[1].features) == 1
        assert tgt_words[1].features[0].label == "gender"
        assert tgt_words[1].features[0].match == "α"

    def test_load_ex4b_indef_adj_noun(self):
        self.provider.load_data_from_file(str(self.test_data / "Ex4b_Indef-Adj-Noun.xml"))
        gen = self.provider.rule_generator
        assert len(gen.rules) == 1
        rule = gen.rules[0]
        assert rule.name == "Indefinite - Adjective - Noun"
        src_words = rule.source.phrase.words
        assert len(src_words) == 3
        assert src_words[0].category == "indef"
        assert src_words[1].category == "adj"
        assert src_words[2].category == "n"
        tgt_words = rule.target.phrase.words
        assert len(tgt_words) == 3
        # Target word 1: 2 suffixes
        assert len(tgt_words[0].affixes) == 2
        assert tgt_words[0].affixes[0].type == AffixType.SUFFIX
        assert len(tgt_words[0].affixes[0].features) == 1
        assert tgt_words[0].affixes[0].features[0].label == "gender"
        assert tgt_words[0].affixes[0].features[0].match == "α"
        assert tgt_words[0].affixes[1].type == AffixType.SUFFIX
        assert len(tgt_words[0].affixes[1].features) == 1
        assert tgt_words[0].affixes[1].features[0].label == "number"
        assert tgt_words[0].affixes[1].features[0].match == "β"
        # Target word 2: head=yes, features, 1 suffix
        assert tgt_words[1].head == HeadValue.YES
        assert len(tgt_words[1].features) == 1
        assert tgt_words[1].features[0].label == "gender"
        assert tgt_words[1].features[0].match == "α"
        assert len(tgt_words[1].affixes) == 1
        assert tgt_words[1].affixes[0].features[0].label == "number"
        # Target word 3: 1 suffix + 1 prefix
        assert len(tgt_words[2].affixes) == 2
        assert tgt_words[2].affixes[0].type == AffixType.SUFFIX
        assert tgt_words[2].affixes[1].type == AffixType.PREFIX

    def test_save(self):
        import tempfile
        from flextrans_rule_generator.model.rule_generator import FLExTransRuleGenerator
        from flextrans_rule_generator.model.rule import FLExTransRule
        from flextrans_rule_generator.model.source import Source
        from flextrans_rule_generator.model.target import Target

        gen = FLExTransRuleGenerator()
        rule = FLExTransRule()
        rule.name = "Indefinite - Adjective - Noun"
        # Build source: 3 words
        src_word1 = Word(); src_word1.id = "1"; src_word1.category = "indef"
        src_word2 = Word(); src_word2.id = "2"; src_word2.category = "adj"
        src_word3 = Word(); src_word3.id = "3"; src_word3.category = "n"
        rule.source.phrase.words.extend([src_word1, src_word2, src_word3])
        # Build target: 3 words with affixes and features
        tgt_word1 = Word(); tgt_word1.id = "1"
        suffix1a = Affix(); suffix1a.type = AffixType.SUFFIX
        suffix1a.insert_new_feature("gender", "α")
        suffix1b = Affix(); suffix1b.type = AffixType.SUFFIX
        suffix1b.insert_new_feature("number", "β")
        tgt_word1.affixes.extend([suffix1a, suffix1b])

        tgt_word2 = Word(); tgt_word2.id = "3"; tgt_word2.head = HeadValue.YES
        tgt_word2.insert_new_feature("gender", "α")
        suffix2 = Affix(); suffix2.type = AffixType.SUFFIX
        suffix2.insert_new_feature("number", "β")
        tgt_word2.affixes.append(suffix2)

        tgt_word3 = Word(); tgt_word3.id = "2"
        suffix3 = Affix(); suffix3.type = AffixType.SUFFIX
        suffix3.insert_new_feature("gender", "α")
        suffix3b = Affix(); suffix3b.type = AffixType.SUFFIX
        suffix3b.insert_new_feature("number", "β")
        tgt_word3.affixes.extend([suffix3, suffix3b])

        rule.target.phrase.words.extend([tgt_word1, tgt_word2, tgt_word3])
        gen.rules.append(rule)

        self.provider.rule_generator = gen
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False, mode='w') as f:
            tmp_path = f.name
        self.provider.save_data_to_file(tmp_path)

        expected = (self.test_data / "RuleGenExpected.xml").read_text()
        actual = Path(tmp_path).read_text()
        # Normalize line endings
        # Normalize line endings and BOM (C# StreamReader strips BOM)
        expected = expected.replace("\r", "").lstrip("\ufeff")
        actual = actual.replace("\r", "").lstrip("\ufeff")
        assert actual == expected
        Path(tmp_path).unlink()
