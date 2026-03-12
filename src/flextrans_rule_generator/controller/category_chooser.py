from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox
from PyQt6.QtCore import Qt
from flextrans_rule_generator.flex_model.flex_category import FLExCategory
from flextrans_rule_generator.controller import strings

class CategoryChooser(QDialog):
    def __init__(self, categories=None, parent=None):
        super().__init__(parent)
        self.categories: list[FLExCategory] = categories or []
        self.selected_category: FLExCategory | None = None
        self.setWindowTitle(strings.CATEGORY_CHOOSER_TITLE)
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

        self.fill_categories_list()

    def fill_categories_list(self):
        self.list_widget.clear()
        for cat in self.categories:
            self.list_widget.addItem(str(cat))

    def select_category(self, index: int):
        if 0 <= index < self.list_widget.count():
            self.list_widget.setCurrentRow(index)

    def accept(self):
        row = self.list_widget.currentRow()
        if 0 <= row < len(self.categories):
            self.selected_category = self.categories[row]
        super().accept()
