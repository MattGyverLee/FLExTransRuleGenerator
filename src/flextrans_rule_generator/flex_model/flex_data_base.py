from flextrans_rule_generator.flex_model.flex_category import FLExCategory
from flextrans_rule_generator.flex_model.flex_feature import FLExFeature

class FLExDataBase:
    def __init__(self):
        self.name: str = ""
        self.categories: list[FLExCategory] = []
        self.features: list[FLExFeature] = []

    def set_feature_in_feature_values(self):
        for feat in self.features:
            for value in feat.values:
                value.feature = feat
