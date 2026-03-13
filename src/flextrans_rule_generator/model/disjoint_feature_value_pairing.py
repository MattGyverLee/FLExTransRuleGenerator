# Copyright (c) 2023 SIL International
# This software is licensed under the LGPL, version 2.1 or later
# (http://www.gnu.org/licenses/lgpl-2.1.html)


class DisjointFeatureValuePairing:
    """Maps a co-feature value to a FLEx feature.

    Example: co_feature_value="sg" maps to flex_feature_name="BantuSG"
    """

    def __init__(self, co_feature_value: str = "", flex_feature_name: str = ""):
        self.co_feature_value: str = co_feature_value
        self.flex_feature_name: str = flex_feature_name

    def __repr__(self) -> str:
        return f"DisjointFeatureValuePairing(co_feature_value='{self.co_feature_value}', flex_feature_name='{self.flex_feature_name}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, DisjointFeatureValuePairing):
            return False
        return (self.co_feature_value == other.co_feature_value and
                self.flex_feature_name == other.flex_feature_name)
