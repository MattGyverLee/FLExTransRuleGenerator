import pytest
from pathlib import Path

class TestWebPageProducer:
    def setup_method(self):
        from flextrans_rule_generator.service.xml_backend_provider import XmlBackEndProvider
        from flextrans_rule_generator.service.web_page_producer import WebPageProducer
        self.provider = XmlBackEndProvider()
        self.producer = WebPageProducer()
        self.test_data = Path(__file__).parent / "test_data"

    def test_produce_ex1a(self):
        self.provider.load_data_from_file(str(self.test_data / "Ex1a_Def-Noun.xml"))
        rule = self.provider.rule_generator.rules[0]
        result = self.producer.produce_web_page(rule)
        expected = (self.test_data / "Ex1a_Def-Noun.htm").read_text()
        assert result.replace("\r", "") == expected.replace("\r", "")

    def test_produce_ex4b(self):
        self.provider.load_data_from_file(str(self.test_data / "Ex4b_Indef-Adj-Noun.xml"))
        rule = self.provider.rule_generator.rules[0]
        result = self.producer.produce_web_page(rule)
        expected = (self.test_data / "Ex4b_Indef-Adj-Noun.htm").read_text()
        assert result.replace("\r", "") == expected.replace("\r", "")
