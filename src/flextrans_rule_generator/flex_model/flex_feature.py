from flextrans_rule_generator.flex_model.flex_feature_value import FLExFeatureValue

class FLExFeature:
    def __init__(self):
        self.name: str = ""
        self.values: list[FLExFeatureValue] = []
    def __str__(self) -> str:
        return self.name
