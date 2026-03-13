# Copyright (c) 2023 SIL International
# This software is licensed under the LGPL, version 2.1 or later
# (http://www.gnu.org/licenses/lgpl-2.1.html)

from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTableWidget,
    QMessageBox, QSplitter, QListWidget, QListWidgetItem,
    QScrollArea, QSpinBox, QWidget
)
from PyQt6.QtCore import Qt

from flextrans_rule_generator.model.disjoint_feature_set import DisjointFeatureSet
from flextrans_rule_generator.model.disjoint_feature_value_pairing import DisjointFeatureValuePairing
from flextrans_rule_generator.flex_model.flex_data import FLExData
from flextrans_rule_generator.controller import strings


class DisjointFeaturesDialog(QDialog):
    """Dialog for managing disjoint feature sets with FLEx data integration.

    Allows users to:
    - View existing disjoint feature sets in left list panel
    - Add/delete disjoint feature sets
    - Edit set properties: name, language, feature to split
    - Dynamically manage feature value pairings via spinner (2-6 subfeatures)
    - Select pairings from FLEx-available features (dropdown validated)
    """

    # Morphological abbreviation mappings for common features
    MORPHOLOGICAL_ABBREVIATIONS = {
        'number': ['sg', 'pl', 'du'],
        'tense': ['pst', 'prs', 'fut'],
        'mood': ['ind', 'subj', 'imp'],
        'aspect': ['pfv', 'ipfv'],
        'person': ['1', '2', '3'],
        'gender': ['m', 'f', 'n'],
        'case': ['nom', 'acc', 'gen', 'dat', 'loc', 'ins'],
        'voice': ['act', 'pass'],
    }

    def __init__(
        self,
        parent=None,
        disjoint_sets: list[DisjointFeatureSet] = None,
        flex_data: Optional[FLExData] = None
    ):
        super().__init__(parent)
        self.disjoint_sets = disjoint_sets if disjoint_sets is not None else []
        self.flex_data = flex_data
        self.current_set_index = -1

        # Pre-calculate available features from both source and target
        self._available_features = self._extract_available_features()

        self.init_ui()
        self.setWindowTitle("Set Disjoint Features")
        self.resize(900, 600)

        # Warn if flex_data is missing
        if self.flex_data is None:
            QMessageBox.warning(
                self,
                "Warning",
                "FLEx data not available. Feature dropdowns will be empty.\n"
                "Features must be entered manually."
            )

    def _extract_available_features(self) -> dict[str, list[str]]:
        """Extract feature names from both source and target data."""
        result = {'source': [], 'target': []}

        if self.flex_data is None:
            return result

        try:
            if self.flex_data.source_data and hasattr(self.flex_data.source_data, 'features'):
                result['source'] = [
                    feat.name for feat in self.flex_data.source_data.features
                    if feat and hasattr(feat, 'name')
                ]
        except Exception as e:
            print(f"[ERROR] Failed to extract source features: {e}")

        try:
            if self.flex_data.target_data and hasattr(self.flex_data.target_data, 'features'):
                result['target'] = [
                    feat.name for feat in self.flex_data.target_data.features
                    if feat and hasattr(feat, 'name')
                ]
        except Exception as e:
            print(f"[ERROR] Failed to extract target features: {e}")

        return result

    def _get_available_features_for_language(self, language: str) -> list[str]:
        """Get available features for a specific language."""
        return self._available_features.get(language, [])

    def _get_suggested_subfeature_values(self, feature_name: str, count: int) -> list[str]:
        """Get suggested subfeature values based on feature name and count."""
        suggested = self.MORPHOLOGICAL_ABBREVIATIONS.get(feature_name.lower(), [])

        if suggested:
            return suggested[:count]

        # Fallback: Generate generic values
        return [f"val{i+1}" for i in range(count)]

    def _validate_flex_feature_exists(self, language: str, feature_name: str) -> bool:
        """Check if a FLEx feature exists, with graceful handling."""
        if not feature_name:
            return True

        if self.flex_data is None:
            # Can't validate without flex_data
            return True

        available = self._get_available_features_for_language(language)
        exists = feature_name in available

        if not exists and available:
            print(f"[WARNING] Feature '{feature_name}' not found in {language} data")

        return exists

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Main horizontal splitter: left (list) and right (properties)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # ===== LEFT PANE: List of disjoint sets =====
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # List widget for sets
        self.sets_list = QListWidget()
        self.sets_list.itemSelectionChanged.connect(self._on_set_list_selected)
        left_layout.addWidget(self.sets_list)

        # Add/Delete buttons
        button_layout = QHBoxLayout()
        add_set_btn = QPushButton("Add")
        add_set_btn.clicked.connect(self._on_add_set)
        delete_set_btn = QPushButton("Delete")
        delete_set_btn.clicked.connect(self._on_delete_set)
        button_layout.addWidget(add_set_btn)
        button_layout.addWidget(delete_set_btn)
        left_layout.addLayout(button_layout)

        main_splitter.addWidget(left_pane)
        main_splitter.setStretchFactor(0, 1)

        # ===== RIGHT PANE: Properties form with scroll area =====
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        right_layout.setContentsMargins(5, 5, 5, 5)

        # Create scroll area for properties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # PROPERTY 1: Disjoint Feature Name
        disjoint_layout = QHBoxLayout()
        disjoint_layout.addWidget(QLabel("Disjoint Feature Name:"))
        self.disjoint_name_input = QLineEdit()
        self.disjoint_name_input.textChanged.connect(self._on_properties_changed)
        disjoint_layout.addWidget(self.disjoint_name_input)
        scroll_layout.addLayout(disjoint_layout)

        # PROPERTY 2: Language dropdown
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["target", "source"])
        self.language_combo.currentTextChanged.connect(self._on_language_changed)
        lang_layout.addWidget(self.language_combo)
        scroll_layout.addLayout(lang_layout)

        # PROPERTY 3: Feature being split (dropdown instead of text field)
        feature_layout = QHBoxLayout()
        feature_layout.addWidget(QLabel("Feature to Split:"))
        self.co_feature_combo = QComboBox()
        self.co_feature_combo.currentTextChanged.connect(self._on_co_feature_changed)
        feature_layout.addWidget(self.co_feature_combo)
        scroll_layout.addLayout(feature_layout)

        # PROPERTY 4: Number of subfeatures (spinner)
        subfeatures_layout = QHBoxLayout()
        subfeatures_layout.addWidget(QLabel("Number of Subfeatures:"))
        self.subfeatures_spinner = QSpinBox()
        self.subfeatures_spinner.setMinimum(2)
        self.subfeatures_spinner.setMaximum(6)
        self.subfeatures_spinner.setValue(2)
        self.subfeatures_spinner.valueChanged.connect(self._on_subfeatures_changed)
        subfeatures_layout.addWidget(self.subfeatures_spinner)
        subfeatures_layout.addStretch()
        scroll_layout.addLayout(subfeatures_layout)

        # Separator
        scroll_layout.addSpacing(10)
        scroll_layout.addWidget(QLabel("Feature Value Pairings:"))

        # PAIRINGS TABLE
        self.pairings_table = QTableWidget()
        self.pairings_table.setColumnCount(2)
        self.pairings_table.setHorizontalHeaderLabels(["Subfeature Value", "FLEx Feature Name"])
        self.pairings_table.horizontalHeader().setStretchLastSection(True)
        self.pairings_table.setMinimumHeight(150)
        scroll_layout.addWidget(self.pairings_table)

        # Buttons for pairings
        pairing_buttons = QHBoxLayout()
        add_pairing_btn = QPushButton("Add Pairing")
        add_pairing_btn.clicked.connect(self._on_add_pairing)
        delete_pairing_btn = QPushButton("Delete Pairing")
        delete_pairing_btn.clicked.connect(self._on_delete_pairing)
        pairing_buttons.addWidget(add_pairing_btn)
        pairing_buttons.addWidget(delete_pairing_btn)
        pairing_buttons.addStretch()
        scroll_layout.addLayout(pairing_buttons)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        right_layout.addWidget(scroll)

        main_splitter.addWidget(right_pane)
        main_splitter.setStretchFactor(1, 2)

        main_layout.addWidget(main_splitter)

        # Dialog buttons at bottom
        dialog_layout = QHBoxLayout()
        dialog_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        dialog_layout.addWidget(ok_btn)
        dialog_layout.addWidget(cancel_btn)
        main_layout.addLayout(dialog_layout)

        self.setLayout(main_layout)
        self._refresh_sets_list()

    def _refresh_sets_list(self):
        """Refresh the list widget with current sets."""
        self.sets_list.blockSignals(True)
        self.sets_list.clear()

        for i, dset in enumerate(self.disjoint_sets):
            label = dset.disjoint_name if dset.disjoint_name else f"Set {i + 1}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, i)
            self.sets_list.addItem(item)

        self.sets_list.blockSignals(False)
        if self.disjoint_sets:
            self.sets_list.setCurrentRow(0)
        else:
            self._clear_properties()

    def _on_set_list_selected(self):
        """Handle list widget selection change."""
        selected_items = self.sets_list.selectedItems()
        if not selected_items:
            self._clear_properties()
            return

        index = self.sets_list.row(selected_items[0])
        self._on_set_selected(index)

    def _refresh_feature_combo(self, language: str):
        """Populate feature selector combo based on selected language."""
        self.co_feature_combo.blockSignals(True)
        current_text = self.co_feature_combo.currentText()

        self.co_feature_combo.clear()
        features = self._get_available_features_for_language(language)
        self.co_feature_combo.addItems(features)

        # Restore previous selection if still available
        index = self.co_feature_combo.findText(current_text)
        if index >= 0:
            self.co_feature_combo.setCurrentIndex(index)

        self.co_feature_combo.blockSignals(False)

    def _on_set_selected(self, index: int):
        """Handle selection of a disjoint feature set."""
        if index < 0 or index >= len(self.disjoint_sets):
            self._clear_properties()
            return

        self.current_set_index = index
        dset = self.disjoint_sets[index]

        # Block signals to prevent triggering change handlers
        self.disjoint_name_input.blockSignals(True)
        self.language_combo.blockSignals(True)
        self.co_feature_combo.blockSignals(True)
        self.subfeatures_spinner.blockSignals(True)

        # Load values
        self.disjoint_name_input.setText(dset.disjoint_name)
        self.language_combo.setCurrentText(dset.language)

        # Populate feature combo with appropriate language features
        self._refresh_feature_combo(dset.language)
        self.co_feature_combo.setCurrentText(dset.co_feature_name)

        # Set spinner to current number of pairings
        self.subfeatures_spinner.setValue(len(dset.feature_value_pairings))

        self.disjoint_name_input.blockSignals(False)
        self.language_combo.blockSignals(False)
        self.co_feature_combo.blockSignals(False)
        self.subfeatures_spinner.blockSignals(False)

        self._refresh_pairings_table()

    def _clear_properties(self):
        """Clear all property fields."""
        self.disjoint_name_input.clear()
        self.language_combo.setCurrentIndex(0)
        self.co_feature_combo.clear()
        self.subfeatures_spinner.setValue(2)
        self.pairings_table.setRowCount(0)
        self.current_set_index = -1

    def _refresh_pairings_table(self):
        """Refresh the pairings table for current set with combo boxes."""
        self.pairings_table.setRowCount(0)

        if self.current_set_index < 0 or self.current_set_index >= len(self.disjoint_sets):
            return

        dset = self.disjoint_sets[self.current_set_index]
        language = dset.language

        # Get available flex feature names for current language
        available_flex_features = self._get_available_features_for_language(language)

        for i, pairing in enumerate(dset.feature_value_pairings):
            self.pairings_table.insertRow(i)

            # Column 0: Co-feature value (combo)
            value_combo = QComboBox()
            suggested_values = self._get_suggested_subfeature_values(
                dset.co_feature_name,
                len(dset.feature_value_pairings)
            )
            value_combo.addItems(suggested_values)
            if pairing.co_feature_value:
                index = value_combo.findText(pairing.co_feature_value)
                if index >= 0:
                    value_combo.setCurrentIndex(index)
            value_combo.currentTextChanged.connect(
                lambda text, row=i: self._on_pairing_value_changed(row, text)
            )
            self.pairings_table.setCellWidget(i, 0, value_combo)

            # Column 1: FLEx feature name (dropdown)
            feature_combo = QComboBox()
            feature_combo.addItems(available_flex_features)
            if pairing.flex_feature_name:
                index = feature_combo.findText(pairing.flex_feature_name)
                if index >= 0:
                    feature_combo.setCurrentIndex(index)
            feature_combo.currentTextChanged.connect(
                lambda text, row=i: self._on_pairing_feature_changed(row, text)
            )
            self.pairings_table.setCellWidget(i, 1, feature_combo)

    def _on_properties_changed(self):
        """Handle changes to general properties."""
        if self.current_set_index < 0:
            return

        dset = self.disjoint_sets[self.current_set_index]
        dset.disjoint_name = self.disjoint_name_input.text()

        # Refresh list to show updated name
        self._refresh_sets_list()

    def _on_language_changed(self, language: str):
        """Handle language combo change - updates available features."""
        if self.current_set_index < 0:
            return

        dset = self.disjoint_sets[self.current_set_index]
        dset.language = language

        # Refresh feature combo for new language
        self.co_feature_combo.blockSignals(True)
        self.co_feature_combo.clear()
        features = self._get_available_features_for_language(language)
        self.co_feature_combo.addItems(features)
        self.co_feature_combo.blockSignals(False)

        self._refresh_sets_list()
        self._refresh_pairings_table()

    def _on_co_feature_changed(self, feature_name: str):
        """Handle feature selection change."""
        if self.current_set_index < 0:
            return

        dset = self.disjoint_sets[self.current_set_index]
        dset.co_feature_name = feature_name

        self._refresh_pairings_table()

    def _on_subfeatures_changed(self, count: int):
        """Handle spinner change - dynamically adjust pairing rows."""
        if self.current_set_index < 0:
            return

        dset = self.disjoint_sets[self.current_set_index]
        current_count = len(dset.feature_value_pairings)

        if count > current_count:
            # Add new rows
            suggested_values = self._get_suggested_subfeature_values(
                dset.co_feature_name,
                count
            )
            for i in range(current_count, count):
                pairing = DisjointFeatureValuePairing()
                if i < len(suggested_values):
                    pairing.co_feature_value = suggested_values[i]
                dset.add_pairing(pairing)
        elif count < current_count:
            # Remove rows
            while len(dset.feature_value_pairings) > count:
                dset.feature_value_pairings.pop()

        self._refresh_pairings_table()

    def _on_pairing_value_changed(self, row: int, value: str):
        """Handle co-feature value change in pairing."""
        if self.current_set_index < 0 or row < 0:
            return

        dset = self.disjoint_sets[self.current_set_index]
        if row < len(dset.feature_value_pairings):
            dset.feature_value_pairings[row].co_feature_value = value

    def _on_pairing_feature_changed(self, row: int, feature_name: str):
        """Handle flex feature name change in pairing."""
        if self.current_set_index < 0 or row < 0:
            return

        dset = self.disjoint_sets[self.current_set_index]
        if row < len(dset.feature_value_pairings):
            pairing = dset.feature_value_pairings[row]
            pairing.flex_feature_name = feature_name

            # Validate: check if feature exists
            if not self._validate_flex_feature_exists(dset.language, feature_name):
                pass  # Could show warning, but just store for now

    def _on_add_set(self):
        """Add a new disjoint feature set."""
        new_set = DisjointFeatureSet()
        new_set.language = self.language_combo.currentText()
        self.disjoint_sets.append(new_set)
        self._refresh_sets_list()
        self.sets_list.setCurrentRow(len(self.disjoint_sets) - 1)

    def _on_delete_set(self):
        """Delete the current disjoint feature set."""
        if self.current_set_index < 0:
            QMessageBox.warning(self, "Warning", "Please select a set to delete.")
            return

        if len(self.disjoint_sets) == 1:
            QMessageBox.warning(self, "Warning", "Cannot delete the last set.")
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this disjoint feature set?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.disjoint_sets.pop(self.current_set_index)
            self._refresh_sets_list()

    def _on_add_pairing(self):
        """Add a new feature value pairing."""
        if self.current_set_index < 0:
            QMessageBox.warning(self, "Warning", "Please select a set first.")
            return

        dset = self.disjoint_sets[self.current_set_index]
        pairing = DisjointFeatureValuePairing()
        dset.add_pairing(pairing)
        self.subfeatures_spinner.blockSignals(True)
        self.subfeatures_spinner.setValue(len(dset.feature_value_pairings))
        self.subfeatures_spinner.blockSignals(False)
        self._refresh_pairings_table()

    def _on_delete_pairing(self):
        """Delete the selected pairing."""
        if self.current_set_index < 0:
            return

        current_row = self.pairings_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a pairing to delete.")
            return

        dset = self.disjoint_sets[self.current_set_index]
        if current_row < len(dset.feature_value_pairings):
            dset.feature_value_pairings.pop(current_row)
            self.subfeatures_spinner.blockSignals(True)
            self.subfeatures_spinner.setValue(len(dset.feature_value_pairings))
            self.subfeatures_spinner.blockSignals(False)
            self._refresh_pairings_table()

    def get_disjoint_sets(self) -> list[DisjointFeatureSet]:
        """Return the modified list of disjoint feature sets."""
        return self.disjoint_sets
