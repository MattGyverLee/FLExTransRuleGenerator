from flextrans_rule_generator.flex_model.source_flex_data import SourceFLExData
from flextrans_rule_generator.flex_model.target_flex_data import TargetFLExData

class FLExData:
    def __init__(self):
        self.source_data: SourceFLExData = SourceFLExData()
        self.target_data: TargetFLExData = TargetFLExData()

    def set_feature_in_feature_values(self):
        self.source_data.set_feature_in_feature_values()
        self.target_data.set_feature_in_feature_values()
