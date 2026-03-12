from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QSettings, QUrl
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QListWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QDialog,
    QPushButton,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

from flextrans_rule_generator.controller import strings
from flextrans_rule_generator.controller.web_bridge import WebBridge
from flextrans_rule_generator.controller.category_chooser import CategoryChooser
from flextrans_rule_generator.controller.feature_value_chooser import FeatureValueChooser
from flextrans_rule_generator.model.rule_generator import FLExTransRuleGenerator
from flextrans_rule_generator.model.rule import FLExTransRule
from flextrans_rule_generator.model.rule_constituent import RuleConstituent
from flextrans_rule_generator.model.phrase import Phrase, PhraseType
from flextrans_rule_generator.model.word import Word, HeadValue
from flextrans_rule_generator.model.category import Category
from flextrans_rule_generator.model.feature import Feature
from flextrans_rule_generator.model.affix import Affix, AffixType
from flextrans_rule_generator.flex_model.flex_data import FLExData
from flextrans_rule_generator.service.web_page_producer import WebPageProducer
from flextrans_rule_generator.service.constituent_finder import ConstituentFinder
from flextrans_rule_generator.service.rule_identifier_setter import RuleIdentifierAndParentSetter


class RuleGeneratorControl(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(strings.FORM_TITLE)

        # --- Model references (set externally after construction) ---
        self.rule_generator: Optional[FLExTransRuleGenerator] = None
        self.provider = None  # XmlBackEndProvider, kept for saving
        self.rule_file_path: str = ""
        self.flex_data: Optional[FLExData] = None
        self.max_variables: int = 4

        # --- Services ---
        self.producer: WebPageProducer = WebPageProducer()
        self.finder: ConstituentFinder = ConstituentFinder()
        self.setter: RuleIdentifierAndParentSetter = RuleIdentifierAndParentSetter()

        # --- Currently-selected constituents ---
        self.selected_rule: Optional[FLExTransRule] = None
        self.phrase: Optional[Phrase] = None
        self.word: Optional[Word] = None
        self.category: Optional[Category] = None
        self.feature: Optional[Feature] = None
        self.affix: Optional[Affix] = None

        # --- Tracking ---
        self.last_selected_rule: int = 0
        self._is_dirty: bool = False

        # --- Build UI ---
        self._build_ui()
        self._build_context_menus()
        self._retrieve_settings()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Toolbar row
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addStretch()

        self.btn_test_lrt = QPushButton(strings.BTN_TEST_IN_LRT)
        self.btn_test_lrt.clicked.connect(self._on_test_in_lrt)
        toolbar_layout.addWidget(self.btn_test_lrt)

        self.btn_save = QPushButton(strings.BTN_SAVE)
        self.btn_save.clicked.connect(self._on_save_clicked)
        toolbar_layout.addWidget(self.btn_save)

        self.btn_save_write = QPushButton(strings.BTN_SAVE_AND_WRITE)
        self.btn_save_write.clicked.connect(self._on_save_and_write)
        toolbar_layout.addWidget(self.btn_save_write)

        self.btn_save_write_all = QPushButton(strings.BTN_SAVE_AND_WRITE_ALL)
        self.btn_save_write_all.clicked.connect(self._on_save_and_write_all)
        toolbar_layout.addWidget(self.btn_save_write_all)

        self.btn_help = QPushButton(strings.BTN_HELP)
        self.btn_help.clicked.connect(self._on_help)
        toolbar_layout.addWidget(self.btn_help)

        main_layout.addLayout(toolbar_layout)

        # Rule name row
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel(strings.RULE_NAME))
        self.rule_name_edit = QLineEdit()
        self.rule_name_edit.textEdited.connect(self._on_rule_name_changed)
        name_layout.addWidget(self.rule_name_edit)
        main_layout.addLayout(name_layout)

        # Splitter: list on left, web view on right
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.rules_list = QListWidget()
        self.rules_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.rules_list.customContextMenuRequested.connect(self._show_rule_context_menu)
        self.rules_list.currentRowChanged.connect(self._on_rule_selected)
        self.splitter.addWidget(self.rules_list)

        self.web_view = QWebEngineView()
        self.bridge = WebBridge()
        channel = QWebChannel(self.web_view.page())
        channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(channel)
        self.bridge.message_received.connect(self._process_web_message)
        self.splitter.addWidget(self.web_view)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        main_layout.addWidget(self.splitter)

    # ------------------------------------------------------------------
    # Context menu definitions
    # ------------------------------------------------------------------

    def _build_context_menus(self):
        # --- Rule context menu ---
        self.rule_menu = QMenu(self)
        self._add_action(self.rule_menu, strings.CM_INSERT_BEFORE, self._rule_insert_before)
        self._add_action(self.rule_menu, strings.CM_INSERT_AFTER, self._rule_insert_after)
        self._add_action(self.rule_menu, strings.CM_DUPLICATE, self._rule_duplicate)
        self._add_action(self.rule_menu, strings.CM_DELETE, self._rule_delete)
        self.rule_menu.addSeparator()
        self._add_action(self.rule_menu, strings.CM_MOVE_UP, self._rule_move_up)
        self._add_action(self.rule_menu, strings.CM_MOVE_DOWN, self._rule_move_down)

        # --- Word context menu ---
        self.word_menu = QMenu(self)
        self._add_action(self.word_menu, strings.CM_INSERT_BEFORE, self._word_insert_before)
        self._add_action(self.word_menu, strings.CM_INSERT_AFTER, self._word_insert_after)
        self._add_action(self.word_menu, strings.CM_DUPLICATE, self._word_duplicate)
        self._add_action(self.word_menu, strings.CM_DELETE, self._word_delete)
        self.word_menu.addSeparator()
        self._add_action(self.word_menu, strings.CM_MOVE_LEFT, self._word_move_left)
        self._add_action(self.word_menu, strings.CM_MOVE_RIGHT, self._word_move_right)
        self.word_menu.addSeparator()
        self._add_action(self.word_menu, strings.CM_MARK_AS_HEAD, self._word_mark_as_head)
        self._add_action(self.word_menu, strings.CM_REMOVE_HEAD_MARKING, self._word_remove_head_marking)
        self.word_menu.addSeparator()
        self._add_action(self.word_menu, strings.CM_INSERT_CATEGORY, self._word_insert_category)
        self._add_action(self.word_menu, strings.CM_INSERT_FEATURE, self._word_insert_feature)
        self._add_action(self.word_menu, strings.CM_INSERT_PREFIX, self._word_insert_prefix)
        self._add_action(self.word_menu, strings.CM_INSERT_SUFFIX, self._word_insert_suffix)

        # --- Category context menu ---
        self.category_menu = QMenu(self)
        self._add_action(self.category_menu, strings.CM_EDIT, self._category_edit)
        self._add_action(self.category_menu, strings.CM_DELETE, self._category_delete)

        # --- Feature context menu ---
        self.feature_menu = QMenu(self)
        self._add_action(self.feature_menu, strings.CM_EDIT, self._feature_edit)
        self._add_action(self.feature_menu, strings.CM_DELETE, self._feature_delete)

        # --- Affix context menu ---
        self.affix_menu = QMenu(self)
        self._add_action(self.affix_menu, strings.CM_INSERT_FEATURE, self._affix_insert_feature)
        self._add_action(self.affix_menu, strings.CM_DELETE, self._affix_delete)
        self._add_action(self.affix_menu, strings.CM_DUPLICATE, self._affix_duplicate)
        self.affix_menu.addSeparator()
        self._add_action(self.affix_menu, strings.CM_INSERT_PREFIX_BEFORE, self._affix_insert_prefix_before)
        self._add_action(self.affix_menu, strings.CM_INSERT_PREFIX_AFTER, self._affix_insert_prefix_after)
        self._add_action(self.affix_menu, strings.CM_INSERT_SUFFIX_BEFORE, self._affix_insert_suffix_before)
        self._add_action(self.affix_menu, strings.CM_INSERT_SUFFIX_AFTER, self._affix_insert_suffix_after)
        self.affix_menu.addSeparator()
        self._add_action(self.affix_menu, strings.CM_MOVE_LEFT, self._affix_move_left)
        self._add_action(self.affix_menu, strings.CM_MOVE_RIGHT, self._affix_move_right)

    @staticmethod
    def _add_action(menu: QMenu, text: str, slot) -> QAction:
        action = menu.addAction(text)
        action.triggered.connect(slot)
        return action

    # ------------------------------------------------------------------
    # Populate rules list
    # ------------------------------------------------------------------

    def fill_rules_list(self):
        self.rules_list.blockSignals(True)
        self.rules_list.clear()
        if self.rule_generator:
            for rule in self.rule_generator.rules:
                self.rules_list.addItem(str(rule))
        self.rules_list.blockSignals(False)
        if self.rule_generator and self.rule_generator.rules:
            index = min(self.last_selected_rule, len(self.rule_generator.rules) - 1)
            index = max(index, 0)
            self.rules_list.setCurrentRow(index)

    # ------------------------------------------------------------------
    # Rule selection
    # ------------------------------------------------------------------

    def _on_rule_selected(self, row: int):
        if row < 0 or not self.rule_generator or row >= len(self.rule_generator.rules):
            self.selected_rule = None
            self.rule_name_edit.clear()
            return
        self.selected_rule = self.rule_generator.rules[row]
        self.last_selected_rule = row
        self.rule_name_edit.setText(self.selected_rule.name)
        self._show_rule_in_web_page()

    def _on_rule_name_changed(self, text: str):
        if self.selected_rule is None:
            return
        self.selected_rule.name = text
        row = self.rules_list.currentRow()
        if 0 <= row < self.rules_list.count():
            self.rules_list.item(row).setText(str(self.selected_rule))
        self._mark_dirty()

    # ------------------------------------------------------------------
    # Web page display
    # ------------------------------------------------------------------

    def _show_rule_in_web_page(self):
        if self.selected_rule is None:
            return
        html = self.producer.produce_web_page(self.selected_rule)
        # Inject QWebChannel bridge before </head>
        bridge_script = (
            '<script src="qrc:///qtwebchannel/qwebchannel.js"></script>\n'
            "<script>\n"
            "var bridge = null;\n"
            "new QWebChannel(qt.webChannelTransport, function(channel) {\n"
            "    bridge = channel.objects.bridge;\n"
            "});\n"
            "function toApp(msg) {\n"
            "    if (bridge) { bridge.receive_message(msg); }\n"
            "    return false;\n"
            "}\n"
            "</script>"
        )
        # Remove original toApp function produced by WebPageProducer
        html = html.replace(
            "function toApp(msg) {\n"
            "window.chrome.webview.postMessage(msg);\n"
            "return false;\n"
            "}",
            "",
        )
        html = html.replace("</head>", bridge_script + "\n</head>")
        base_url = QUrl.fromLocalFile(
            str(Path(__file__).parent.parent / "resources") + "/"
        )
        self.web_view.setHtml(html, base_url)

    # ------------------------------------------------------------------
    # Web message processing
    # ------------------------------------------------------------------

    def _process_web_message(self, msg: str):
        if not msg or "." not in msg:
            return
        parts = msg.split(".")
        if len(parts) != 2:
            return
        msg_type = parts[0]
        try:
            identifier = int(parts[1])
        except ValueError:
            return

        if self.selected_rule is None:
            return

        constituent = self.finder.find_constituent(self.selected_rule, identifier)
        if constituent is None:
            return

        if msg_type == "p":
            if isinstance(constituent, Phrase):
                self.phrase = constituent
        elif msg_type == "w":
            if isinstance(constituent, Word):
                self.word = constituent
                self._show_menu_at_cursor(self.word_menu)
        elif msg_type == "c":
            if isinstance(constituent, Category):
                self.category = constituent
                self._show_menu_at_cursor(self.category_menu)
        elif msg_type == "f":
            if isinstance(constituent, Feature):
                self.feature = constituent
                self._show_menu_at_cursor(self.feature_menu)
        elif msg_type == "a":
            if isinstance(constituent, Affix):
                self.affix = constituent
                self._show_menu_at_cursor(self.affix_menu)

    def _show_menu_at_cursor(self, menu: QMenu):
        from PyQt6.QtGui import QCursor

        menu.popup(QCursor.pos())

    # ------------------------------------------------------------------
    # Rule context menu (shown on QListWidget right-click)
    # ------------------------------------------------------------------

    def _show_rule_context_menu(self, pos):
        if not self.rule_generator:
            return
        self.rule_menu.popup(self.rules_list.mapToGlobal(pos))

    def _current_rule_index(self) -> int:
        return self.rules_list.currentRow()

    def _rule_insert_before(self):
        if not self.rule_generator:
            return
        index = self._current_rule_index()
        if index < 0:
            index = 0
        new_rule = FLExTransRule()
        new_rule.source.phrase.words.append(Word())
        new_rule.target.phrase.words.append(Word())
        self.rule_generator.rules.insert(index, new_rule)
        self._mark_dirty()
        self.fill_rules_list()
        self.rules_list.setCurrentRow(index)

    def _rule_insert_after(self):
        if not self.rule_generator:
            return
        index = self._current_rule_index() + 1
        if index <= 0:
            index = len(self.rule_generator.rules)
        new_rule = FLExTransRule()
        new_rule.source.phrase.words.append(Word())
        new_rule.target.phrase.words.append(Word())
        self.rule_generator.rules.insert(index, new_rule)
        self._mark_dirty()
        self.fill_rules_list()
        self.rules_list.setCurrentRow(index)

    def _rule_duplicate(self):
        if not self.rule_generator or self.selected_rule is None:
            return
        index = self._current_rule_index()
        if index < 0:
            return
        new_rule = self.selected_rule.duplicate()
        self.rule_generator.rules.insert(index + 1, new_rule)
        self._mark_dirty()
        self.fill_rules_list()
        self.rules_list.setCurrentRow(index + 1)

    def _rule_delete(self):
        if not self.rule_generator or self.selected_rule is None:
            return
        index = self._current_rule_index()
        if index < 0 or index >= len(self.rule_generator.rules):
            return
        del self.rule_generator.rules[index]
        self._mark_dirty()
        self.fill_rules_list()
        if self.rule_generator.rules:
            new_index = min(index, len(self.rule_generator.rules) - 1)
            self.rules_list.setCurrentRow(new_index)
        else:
            self.selected_rule = None
            self.web_view.setHtml("")

    def _rule_move_up(self):
        if not self.rule_generator:
            return
        index = self._current_rule_index()
        if index <= 0:
            return
        rules = self.rule_generator.rules
        rules[index], rules[index - 1] = rules[index - 1], rules[index]
        self._mark_dirty()
        self.fill_rules_list()
        self.rules_list.setCurrentRow(index - 1)

    def _rule_move_down(self):
        if not self.rule_generator:
            return
        index = self._current_rule_index()
        rules = self.rule_generator.rules
        if index < 0 or index >= len(rules) - 1:
            return
        rules[index], rules[index + 1] = rules[index + 1], rules[index]
        self._mark_dirty()
        self.fill_rules_list()
        self.rules_list.setCurrentRow(index + 1)

    # ------------------------------------------------------------------
    # Word context menu handlers
    # ------------------------------------------------------------------

    def _get_parent_phrase(self) -> Optional[Phrase]:
        """Return the Phrase that owns the currently-selected word."""
        if self.word is None:
            return None
        parent = self.word.parent
        if isinstance(parent, Phrase):
            return parent
        return None

    def _word_index_in_phrase(self, phrase: Phrase) -> int:
        try:
            return phrase.words.index(self.word)
        except ValueError:
            return -1

    def _word_insert_before(self):
        phrase = self._get_parent_phrase()
        if phrase is None or self.word is None:
            return
        index = self._word_index_in_phrase(phrase)
        if index < 0:
            return
        phrase.insert_new_word_at(index)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _word_insert_after(self):
        phrase = self._get_parent_phrase()
        if phrase is None or self.word is None:
            return
        index = self._word_index_in_phrase(phrase)
        if index < 0:
            return
        # insert_new_word_at inserts *before* the given index, so use index+1
        # but the model's insert_new_word_at checks index < len(words), so
        # we need to handle the boundary: if at end, append directly.
        new_word = Word()
        new_word.id = str(len(phrase.words) + 1)
        if index + 1 >= len(phrase.words):
            phrase.words.append(new_word)
        else:
            phrase.words.insert(index + 1, new_word)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _word_duplicate(self):
        phrase = self._get_parent_phrase()
        if phrase is None or self.word is None:
            return
        index = self._word_index_in_phrase(phrase)
        if index < 0:
            return
        dup = self.word.duplicate()
        if index + 1 >= len(phrase.words):
            phrase.words.append(dup)
        else:
            phrase.words.insert(index + 1, dup)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _word_delete(self):
        phrase = self._get_parent_phrase()
        if phrase is None or self.word is None:
            return
        index = self._word_index_in_phrase(phrase)
        if index < 0:
            return
        phrase.delete_word_at(index)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _word_move_left(self):
        phrase = self._get_parent_phrase()
        if phrase is None or self.word is None:
            return
        index = self._word_index_in_phrase(phrase)
        if index <= 0:
            return
        phrase.swap_position_of_words(index, index - 1)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _word_move_right(self):
        phrase = self._get_parent_phrase()
        if phrase is None or self.word is None:
            return
        index = self._word_index_in_phrase(phrase)
        if index < 0 or index >= len(phrase.words) - 1:
            return
        phrase.swap_position_of_words(index, index + 1)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _word_mark_as_head(self):
        phrase = self._get_parent_phrase()
        if phrase is None or self.word is None:
            return
        phrase.mark_word_as_head(self.word)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _word_remove_head_marking(self):
        if self.word is None:
            return
        self.word.head = HeadValue.NO
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _word_insert_category(self):
        if self.word is None or self.flex_data is None:
            return
        phrase = self._get_parent_phrase()
        if phrase is None:
            return
        categories = self._get_categories_for_phrase(phrase)
        chosen = self._launch_category_chooser(categories)
        if chosen is not None:
            self.word.insert_category(chosen.abbreviation)
            self._mark_dirty()
            self._show_rule_in_web_page()

    def _word_insert_feature(self):
        if self.word is None or self.flex_data is None:
            return
        phrase = self._get_parent_phrase()
        if phrase is None:
            return
        features = self._get_features_for_phrase(phrase)
        result = self._launch_feature_chooser(features)
        if result is not None:
            label, match = result
            self.word.insert_new_feature(label, match)
            self._mark_dirty()
            self._show_rule_in_web_page()

    def _word_insert_prefix(self):
        if self.word is None:
            return
        new_affix = Affix()
        new_affix.type = AffixType.PREFIX
        self.word.affixes.append(new_affix)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _word_insert_suffix(self):
        if self.word is None:
            return
        new_affix = Affix()
        new_affix.type = AffixType.SUFFIX
        self.word.affixes.append(new_affix)
        self._mark_dirty()
        self._show_rule_in_web_page()

    # ------------------------------------------------------------------
    # Category context menu handlers
    # ------------------------------------------------------------------

    def _category_edit(self):
        if self.category is None or self.flex_data is None:
            return
        # Determine which phrase this category belongs to
        word = self._find_word_for_category()
        if word is None:
            return
        phrase = self._find_phrase_for_word(word)
        if phrase is None:
            return
        categories = self._get_categories_for_phrase(phrase)
        chosen = self._launch_category_chooser(categories)
        if chosen is not None:
            self.category.name = chosen.abbreviation
            word.category = chosen.abbreviation
            self._mark_dirty()
            self._show_rule_in_web_page()

    def _category_delete(self):
        if self.category is None:
            return
        word = self._find_word_for_category()
        if word is None:
            return
        word.delete_category()
        self._mark_dirty()
        self._show_rule_in_web_page()

    # ------------------------------------------------------------------
    # Feature context menu handlers
    # ------------------------------------------------------------------

    def _feature_edit(self):
        if self.feature is None or self.flex_data is None:
            return
        parent = self.feature.parent
        if parent is None:
            return
        phrase = self._find_phrase_for_constituent(parent)
        if phrase is None:
            return
        features = self._get_features_for_phrase(phrase)
        result = self._launch_feature_chooser(features, self.feature.label, self.feature.match)
        if result is not None:
            label, match = result
            self.feature.label = label
            self.feature.match = match
            self._mark_dirty()
            self._show_rule_in_web_page()

    def _feature_delete(self):
        if self.feature is None:
            return
        parent = self.feature.parent
        if parent is None:
            return
        if hasattr(parent, "delete_feature"):
            parent.delete_feature(self.feature)
            self._mark_dirty()
            self._show_rule_in_web_page()

    # ------------------------------------------------------------------
    # Affix context menu handlers
    # ------------------------------------------------------------------

    def _get_parent_word_for_affix(self) -> Optional[Word]:
        """Return the Word that owns the currently-selected affix."""
        if self.affix is None:
            return None
        parent = self.affix.parent
        if isinstance(parent, Word):
            return parent
        return None

    def _affix_index_in_word(self, word: Word) -> int:
        try:
            return word.affixes.index(self.affix)
        except ValueError:
            return -1

    def _affix_insert_feature(self):
        if self.affix is None or self.flex_data is None:
            return
        word = self._get_parent_word_for_affix()
        if word is None:
            return
        phrase = self._find_phrase_for_word(word)
        if phrase is None:
            return
        features = self._get_features_for_phrase(phrase)
        result = self._launch_feature_chooser(features)
        if result is not None:
            label, match = result
            self.affix.insert_new_feature(label, match)
            self._mark_dirty()
            self._show_rule_in_web_page()

    def _affix_delete(self):
        word = self._get_parent_word_for_affix()
        if word is None or self.affix is None:
            return
        index = self._affix_index_in_word(word)
        if index < 0:
            return
        word.delete_affix_at(index)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _affix_duplicate(self):
        word = self._get_parent_word_for_affix()
        if word is None or self.affix is None:
            return
        index = self._affix_index_in_word(word)
        if index < 0:
            return
        dup = self.affix.duplicate()
        if index + 1 >= len(word.affixes):
            word.affixes.append(dup)
        else:
            word.affixes.insert(index + 1, dup)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _affix_insert_prefix_before(self):
        word = self._get_parent_word_for_affix()
        if word is None or self.affix is None:
            return
        index = self._affix_index_in_word(word)
        if index < 0:
            return
        word.insert_new_affix_at(AffixType.PREFIX, index)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _affix_insert_prefix_after(self):
        word = self._get_parent_word_for_affix()
        if word is None or self.affix is None:
            return
        index = self._affix_index_in_word(word)
        if index < 0:
            return
        new_affix = Affix()
        new_affix.type = AffixType.PREFIX
        if index + 1 >= len(word.affixes):
            word.affixes.append(new_affix)
        else:
            word.affixes.insert(index + 1, new_affix)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _affix_insert_suffix_before(self):
        word = self._get_parent_word_for_affix()
        if word is None or self.affix is None:
            return
        index = self._affix_index_in_word(word)
        if index < 0:
            return
        word.insert_new_affix_at(AffixType.SUFFIX, index)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _affix_insert_suffix_after(self):
        word = self._get_parent_word_for_affix()
        if word is None or self.affix is None:
            return
        index = self._affix_index_in_word(word)
        if index < 0:
            return
        new_affix = Affix()
        new_affix.type = AffixType.SUFFIX
        if index + 1 >= len(word.affixes):
            word.affixes.append(new_affix)
        else:
            word.affixes.insert(index + 1, new_affix)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _affix_move_left(self):
        word = self._get_parent_word_for_affix()
        if word is None or self.affix is None:
            return
        index = self._affix_index_in_word(word)
        if index <= 0:
            return
        word.swap_position_of_affixes(index, index - 1)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _affix_move_right(self):
        word = self._get_parent_word_for_affix()
        if word is None or self.affix is None:
            return
        index = self._affix_index_in_word(word)
        if index < 0 or index >= len(word.affixes) - 1:
            return
        word.swap_position_of_affixes(index, index + 1)
        self._mark_dirty()
        self._show_rule_in_web_page()

    # ------------------------------------------------------------------
    # Dialog launchers
    # ------------------------------------------------------------------

    def _launch_category_chooser(self, categories) -> Optional[object]:
        chooser = CategoryChooser(categories, self)
        if self.category and self.category.name:
            for i, cat in enumerate(categories):
                if cat.abbreviation == self.category.name:
                    chooser.select_category(i)
                    break
        if chooser.exec() == QDialog.DialogCode.Accepted and chooser.selected_category:
            return chooser.selected_category
        return None

    def _launch_feature_chooser(self, features, current_label: str = "", current_match: str = ""):
        """Show the two-step feature chooser: first pick a feature, then a value.

        Returns (label, match) tuple or None if cancelled.
        """
        if not features:
            return None

        # Step 1 -- choose the feature
        from flextrans_rule_generator.controller.feature_value_chooser import FeatureValueChooser

        chooser = FeatureValueChooser(self)
        chooser.setWindowTitle(strings.FEATURE_CHOOSER_TITLE)
        chooser.list_widget.clear()
        for feat in features:
            chooser.list_widget.addItem(str(feat))
        # pre-select current feature if editing
        if current_label:
            for i, feat in enumerate(features):
                if feat.name == current_label:
                    chooser.select_feature_value(i)
                    break
        if chooser.exec() != QDialog.DialogCode.Accepted:
            return None
        row = chooser.list_widget.currentRow()
        if row < 0 or row >= len(features):
            return None
        selected_feature = features[row]

        # Step 2 -- choose the value
        value_chooser = FeatureValueChooser(self)
        value_chooser.max_variables = self.max_variables
        value_chooser.feature_values = list(selected_feature.values)
        value_chooser.create_variable_values(selected_feature)
        value_chooser.fill_feature_values_list()
        if current_label and current_match:
            value_chooser.find_and_select_feature_value_pair(current_label, current_match)
        if value_chooser.exec() == QDialog.DialogCode.Accepted and value_chooser.selected_feature_value:
            return (selected_feature.name, value_chooser.match)
        return None

    # ------------------------------------------------------------------
    # Helpers: find phrase / categories / features for a constituent
    # ------------------------------------------------------------------

    def _find_word_for_category(self) -> Optional[Word]:
        """Walk up from category to its parent Word."""
        if self.category is None:
            return None
        parent = self.category.parent
        if isinstance(parent, Word):
            return parent
        return None

    def _find_phrase_for_word(self, word: Word) -> Optional[Phrase]:
        parent = word.parent
        if isinstance(parent, Phrase):
            return parent
        return None

    def _find_phrase_for_constituent(self, constituent: RuleConstituent) -> Optional[Phrase]:
        """Walk the parent chain until we reach a Phrase."""
        current = constituent
        while current is not None:
            if isinstance(current, Phrase):
                return current
            current = getattr(current, "parent", None)
        return None

    def _get_categories_for_phrase(self, phrase: Phrase):
        if self.flex_data is None:
            return []
        if phrase.type == PhraseType.SOURCE:
            return self.flex_data.source_data.categories
        return self.flex_data.target_data.categories

    def _get_features_for_phrase(self, phrase: Phrase):
        if self.flex_data is None:
            return []
        if phrase.type == PhraseType.SOURCE:
            return self.flex_data.source_data.features
        return self.flex_data.target_data.features

    # ------------------------------------------------------------------
    # Dirty tracking / save
    # ------------------------------------------------------------------

    def _mark_dirty(self):
        self._is_dirty = True

    def _save(self):
        if self.provider and self.rule_file_path:
            self.provider.save_data_to_file(self.rule_file_path)
            self._is_dirty = False

    # ------------------------------------------------------------------
    # Toolbar button handlers
    # ------------------------------------------------------------------

    def _on_test_in_lrt(self):
        QMessageBox.information(self, strings.FORM_TITLE, "Test in LRT is not yet implemented.")

    def _on_save_clicked(self):
        self._save()

    def _on_save_and_write(self):
        self._save()
        QMessageBox.information(self, strings.FORM_TITLE, "Save & Write is not yet implemented.")

    def _on_save_and_write_all(self):
        self._save()
        QMessageBox.information(self, strings.FORM_TITLE, "Save & Write All is not yet implemented.")

    def _on_help(self):
        QMessageBox.information(
            self,
            strings.BTN_HELP,
            "FLExTrans Rule Generator\n\n"
            "Right-click on rules or tree elements to edit them.",
        )

    # ------------------------------------------------------------------
    # Settings persistence
    # ------------------------------------------------------------------

    def _retrieve_settings(self):
        settings = QSettings("SIL", "FLExTransRuleGenerator")
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        self.last_selected_rule = int(settings.value("LastRule", 0))

    def _save_settings(self):
        settings = QSettings("SIL", "FLExTransRuleGenerator")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("LastRule", self.last_selected_rule)

    # ------------------------------------------------------------------
    # Close event
    # ------------------------------------------------------------------

    def closeEvent(self, event):
        if self._is_dirty:
            reply = QMessageBox.question(
                self,
                strings.FORM_TITLE,
                "Save changes before closing?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._save()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        self._save_settings()
        super().closeEvent(event)
