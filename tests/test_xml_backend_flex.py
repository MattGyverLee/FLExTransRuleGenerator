import pytest
from pathlib import Path

class TestXmlBackEndProviderFLExData:
    def setup_method(self):
        from flextrans_rule_generator.service.xml_backend_provider_flex_data import XmlBackEndProviderFLExData
        self.provider = XmlBackEndProviderFLExData()
        self.test_data = Path(__file__).parent / "test_data"

    def test_load_flex_data(self):
        self.provider.load_data_from_file(str(self.test_data / "FLExDataSpanFrench.xml"))
        data = self.provider.flex_data
        # Source
        assert data.source_data.name == "Spanish-FLExTrans-Exp4"
        src_cats = data.source_data.categories
        assert len(src_cats) == 14
        assert src_cats[0].abbreviation == "adj"
        assert src_cats[1].abbreviation == "adv"
        assert src_cats[7].abbreviation == "indf"
        assert src_cats[8].abbreviation == "n"
        assert src_cats[13].abbreviation == "v"
        # Target
        assert data.target_data.name == "French-FLExTrans-Exp4"
        tgt_cats = data.target_data.categories
        assert len(tgt_cats) == 15
        # Source features
        src_feats = data.source_data.features
        assert len(src_feats) == 5
        assert src_feats[0].name == "absolute tense"
        assert len(src_feats[0].values) == 4
        assert src_feats[0].values[0].abbreviation == "fut"
        assert src_feats[0].values[0].feature == src_feats[0]  # back-reference
        assert src_feats[2].name == "gender"
        assert len(src_feats[2].values) == 3
        assert src_feats[3].name == "number"
        assert len(src_feats[3].values) == 2
        assert src_feats[3].values[0].abbreviation == "pl"
        assert src_feats[3].values[1].abbreviation == "sg"
