from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox
from PyQt5.QtCore import Qt
from flextrans_rule_generator.flex_model.flex_feature import FLExFeature
from flextrans_rule_generator.flex_model.flex_feature_value import FLExFeatureValue
from flextrans_rule_generator.controller import strings

VARIABLES = ["\u03b1", "\u03b2", "\u03b3", "\u03b4", "\u03b5", "\u03b6", "\u03b7", "\u03b8", "\u03b9", "\u03ba", "\u03bc", "\u03bd"]

class FeatureValueChooser(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.feature_values: list[FLExFeatureValue] = []
        self.variable_feature_values: list[FLExFeatureValue] = []
        self.selected_feature_value: FLExFeatureValue | None = None
        self.match: str = ""
        self.max_variables: int = 4

        self.setWindowTitle(strings.FEATURE_VALUE_CHOOSER_TITLE)
        self.resize(800, 450)

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.list_widget.setMinimumSize(764, 364)
        layout.addWidget(self.list_widget)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def create_variable_values(self, feat: FLExFeature):
        for i in range(min(self.max_variables, len(VARIABLES))):
            var = FLExFeatureValue()
            var.abbreviation = VARIABLES[i]
            var.feature = feat
            self.variable_feature_values.append(var)

    def fill_feature_values_list(self):
        self.list_widget.clear()
        self._all_values = []
        for val in self.feature_values:
            self.list_widget.addItem(str(val))
            self._all_values.append(val)
        for val in self.variable_feature_values:
            self.list_widget.addItem(str(val))
            self._all_values.append(val)

    def find_and_select_feature_value_pair(self, label: str, match: str):
        self.select_feature_value(0)
        for i, val in enumerate(self._all_values):
            if val.feature and val.feature.name == label and val.abbreviation == match:
                self.select_feature_value(i)
                break

    def select_feature_value(self, index: int):
        if 0 <= index < self.list_widget.count():
            self.list_widget.setCurrentRow(index)

    def accept(self):
        row = self.list_widget.currentRow()
        if 0 <= row < len(self._all_values):
            self.selected_feature_value = self._all_values[row]
            self.match = self.selected_feature_value.abbreviation
        super().accept()
