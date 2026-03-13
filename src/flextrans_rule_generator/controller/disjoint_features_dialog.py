# Copyright (c) 2023 SIL International
# This software is licensed under the LGPL, version 2.1 or later
# (http://www.gnu.org/licenses/lgpl-2.1.html)

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt

from flextrans_rule_generator.model.disjoint_feature_set import DisjointFeatureSet
from flextrans_rule_generator.model.disjoint_feature_value_pairing import DisjointFeatureValuePairing
from flextrans_rule_generator.controller import strings


class DisjointFeaturesDialog(QDialog):
    """Dialog for managing disjoint feature sets.

    Allows users to:
    - View existing disjoint feature sets
    - Add new disjoint feature sets
    - Edit existing sets (name, language, pairings)
    - Remove sets
    """

    def __init__(self, parent=None, disjoint_sets: list[DisjointFeatureSet] = None):
        super().__init__(parent)
        self.disjoint_sets = disjoint_sets if disjoint_sets is not None else []
        self.current_set_index = -1
        self.init_ui()
        self.setWindowTitle("Set Disjoint Features")
        self.resize(700, 500)

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Feature Set Selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Disjoint Feature Set:"))
        self.set_combo = QComboBox()
        self.set_combo.currentIndexChanged.connect(self._on_set_selected)
        selection_layout.addWidget(self.set_combo)

        add_set_btn = QPushButton("Add New Set")
        add_set_btn.clicked.connect(self._on_add_set)
        selection_layout.addWidget(add_set_btn)

        delete_set_btn = QPushButton("Delete Set")
        delete_set_btn.clicked.connect(self._on_delete_set)
        selection_layout.addWidget(delete_set_btn)

        main_layout.addLayout(selection_layout)

        # Set Properties
        properties_group = QGroupBox("Set Properties")
        props_layout = QVBoxLayout()

        # Co-feature name
        co_feature_layout = QHBoxLayout()
        co_feature_layout.addWidget(QLabel("Co-feature Name:"))
        self.co_feature_input = QLineEdit()
        self.co_feature_input.textChanged.connect(self._on_properties_changed)
        co_feature_layout.addWidget(self.co_feature_input)
        props_layout.addLayout(co_feature_layout)

        # Language
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["target", "source"])
        self.language_combo.currentTextChanged.connect(self._on_properties_changed)
        lang_layout.addWidget(self.language_combo)
        props_layout.addLayout(lang_layout)

        # Disjoint name
        disjoint_layout = QHBoxLayout()
        disjoint_layout.addWidget(QLabel("Disjoint Feature Name:"))
        self.disjoint_name_input = QLineEdit()
        self.disjoint_name_input.textChanged.connect(self._on_properties_changed)
        disjoint_layout.addWidget(self.disjoint_name_input)
        props_layout.addLayout(disjoint_layout)

        properties_group.setLayout(props_layout)
        main_layout.addWidget(properties_group)

        # Feature Value Pairings
        pairings_group = QGroupBox("Feature Value Pairings")
        pairings_layout = QVBoxLayout()

        # Table for pairings
        self.pairings_table = QTableWidget()
        self.pairings_table.setColumnCount(2)
        self.pairings_table.setHorizontalHeaderLabels(["Co-feature Value", "FLEx Feature Name"])
        self.pairings_table.horizontalHeader().setStretchLastSection(True)
        pairings_layout.addWidget(self.pairings_table)

        # Buttons for pairings
        pairing_buttons_layout = QHBoxLayout()
        add_pairing_btn = QPushButton("Add Pairing")
        add_pairing_btn.clicked.connect(self._on_add_pairing)
        pairing_buttons_layout.addWidget(add_pairing_btn)

        delete_pairing_btn = QPushButton("Delete Pairing")
        delete_pairing_btn.clicked.connect(self._on_delete_pairing)
        pairing_buttons_layout.addWidget(delete_pairing_btn)

        pairings_layout.addLayout(pairing_buttons_layout)
        pairings_group.setLayout(pairings_layout)
        main_layout.addWidget(pairings_group)

        # Dialog buttons
        dialog_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        dialog_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        dialog_layout.addWidget(cancel_btn)

        main_layout.addLayout(dialog_layout)

        self.setLayout(main_layout)
        self._refresh_set_combo()

    def _refresh_set_combo(self):
        """Refresh the combo box with current sets."""
        self.set_combo.blockSignals(True)
        self.set_combo.clear()

        for i, dset in enumerate(self.disjoint_sets):
            label = dset.disjoint_name if dset.disjoint_name else f"Set {i + 1}"
            self.set_combo.addItem(label, i)

        self.set_combo.blockSignals(False)
        if self.disjoint_sets:
            self.set_combo.setCurrentIndex(0)
        else:
            self._clear_properties()

    def _on_set_selected(self, index: int):
        """Handle selection of a disjoint feature set."""
        if index < 0 or index >= len(self.disjoint_sets):
            self._clear_properties()
            return

        self.current_set_index = index
        dset = self.disjoint_sets[index]

        self.co_feature_input.blockSignals(True)
        self.language_combo.blockSignals(True)
        self.disjoint_name_input.blockSignals(True)

        self.co_feature_input.setText(dset.co_feature_name)
        self.language_combo.setCurrentText(dset.language)
        self.disjoint_name_input.setText(dset.disjoint_name)

        self.co_feature_input.blockSignals(False)
        self.language_combo.blockSignals(False)
        self.disjoint_name_input.blockSignals(False)

        self._refresh_pairings_table()

    def _clear_properties(self):
        """Clear all property fields."""
        self.co_feature_input.clear()
        self.language_combo.setCurrentIndex(0)
        self.disjoint_name_input.clear()
        self.pairings_table.setRowCount(0)
        self.current_set_index = -1

    def _refresh_pairings_table(self):
        """Refresh the pairings table for the current set."""
        self.pairings_table.setRowCount(0)

        if self.current_set_index < 0 or self.current_set_index >= len(self.disjoint_sets):
            return

        dset = self.disjoint_sets[self.current_set_index]

        for i, pairing in enumerate(dset.feature_value_pairings):
            self.pairings_table.insertRow(i)
            co_item = QTableWidgetItem(pairing.co_feature_value)
            flex_item = QTableWidgetItem(pairing.flex_feature_name)
            self.pairings_table.setItem(i, 0, co_item)
            self.pairings_table.setItem(i, 1, flex_item)

    def _on_properties_changed(self):
        """Handle changes to set properties."""
        if self.current_set_index < 0 or self.current_set_index >= len(self.disjoint_sets):
            return

        dset = self.disjoint_sets[self.current_set_index]
        dset.co_feature_name = self.co_feature_input.text()
        dset.language = self.language_combo.currentText()
        dset.disjoint_name = self.disjoint_name_input.text()

        # Refresh combo box label
        self._refresh_set_combo()

    def _on_add_set(self):
        """Add a new disjoint feature set."""
        new_set = DisjointFeatureSet()
        self.disjoint_sets.append(new_set)
        self._refresh_set_combo()
        self.set_combo.setCurrentIndex(len(self.disjoint_sets) - 1)

    def _on_delete_set(self):
        """Delete the current disjoint feature set."""
        if self.current_set_index < 0:
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
            self._refresh_set_combo()

    def _on_add_pairing(self):
        """Add a new feature value pairing."""
        if self.current_set_index < 0:
            return

        dset = self.disjoint_sets[self.current_set_index]
        pairing = DisjointFeatureValuePairing()
        dset.add_pairing(pairing)
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
            self._refresh_pairings_table()

    def get_disjoint_sets(self) -> list[DisjointFeatureSet]:
        """Return the modified list of disjoint feature sets."""
        return self.disjoint_sets
