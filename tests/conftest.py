import os
import pytest
from pathlib import Path

@pytest.fixture
def test_data_dir():
    return Path(__file__).parent / "test_data"

@pytest.fixture
def xml_provider(test_data_dir):
    from flextrans_rule_generator.service.xml_backend_provider import XmlBackEndProvider
    provider = XmlBackEndProvider()
    return provider

def check_word_attributes(word, expected_id, expected_category, expected_head):
    assert word.id == expected_id
    assert word.category == expected_category
    assert word.head == expected_head

def check_feature_attributes(feature, expected_label, expected_match):
    assert feature.label == expected_label
    assert feature.match == expected_match
