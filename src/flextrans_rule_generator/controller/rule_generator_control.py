from pathlib import Path
from typing import Optional
import sys
import os

# *** CRITICAL: Ensure we use system Python 3.11's packages ***
_sys_py311_site = r"C:\Program Files\Python311\Lib\site-packages"
if _sys_py311_site not in sys.path:
    sys.path.insert(0, _sys_py311_site)

# IMMEDIATE TEST: Confirm this module is being imported at all
try:
    with open(r"C:\Users\thoua\RuleGeneratorControl_IMPORTED.txt", 'w') as f:
        f.write("Module import started\n")
except Exception as e:
    pass

# NOTE: Qt.AA_ShareOpenGLContexts is already set in RuleAssistantPY.py
# before QApplication is created, so we don't set it here
from PyQt5.QtCore import Qt, QCoreApplication

# CRITICAL: Try to import WebEngine
QWebEngineView = None
QWebChannel = None
WEBENGINE_AVAILABLE = False

# Direct import attempt - report any real errors
_WEBENGINE_ERROR = None
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView as _TEST_QWE
    from PyQt5.QtWebChannel import QWebChannel as _TEST_QWC
    _WEBENGINE_WORKS = True
except ImportError as _imp_err:
    _WEBENGINE_WORKS = False
    _WEBENGINE_ERROR = str(_imp_err)
except Exception as _gen_err:
    _WEBENGINE_WORKS = False
    _WEBENGINE_ERROR = f"{type(_gen_err).__name__}: {str(_gen_err)}"

# CRITICAL: Write the import error to a file immediately so we can see what's failing
try:
    with open(r"C:\Users\thoua\RuleGeneratorControl_ERROR.txt", 'w') as _f:
        _f.write(f"WebEngine import works: {_WEBENGINE_WORKS}\n")
        if not _WEBENGINE_WORKS and _WEBENGINE_ERROR:
            _f.write(f"Error: {_WEBENGINE_ERROR}\n")
        else:
            _f.write("No error captured\n")
except Exception as _e:
    pass

# Set up error logging for WebEngine import debugging
# Use a dedicated log file to avoid file locking issues
_webengine_log_path = r"C:\Users\thoua\RuleGeneratorControl_WebEngine.log"
def _log_webengine_debug(msg):
    try:
        with open(_webengine_log_path, 'a') as f:
            f.write(f"{msg}\n")
    except Exception as _e:
        # If logging fails, just continue - don't crash
        pass

# Clear previous log and start fresh
try:
    with open(_webengine_log_path, 'w') as f:
        f.write("=== rule_generator_control.py WebEngine import logging ===\n")
except:
    pass

_log_webengine_debug(f"\n=== rule_generator_control.py import started ===")
_log_webengine_debug(f"sys.path[0:3]: {sys.path[0:3]}")

# First, check if imports were cached by RuleAssistantPY.py before flextoolslib was loaded
_webengine_cache = sys.modules.get('__webengine_cache__', {})

# DIRECT FILE WRITE - bypass any logging issues
try:
    with open(r"C:\Users\thoua\RuleGeneratorControl_CACHE.log", 'w') as _f:
        _f.write(f"Cache object exists: {_webengine_cache is not None}\n")
        _f.write(f"Cache bool: {bool(_webengine_cache)}\n")
        _f.write(f"Cache keys: {list(_webengine_cache.keys()) if _webengine_cache else 'NONE'}\n")
        _f.write(f"Has QWebEngineView: {'QWebEngineView' in _webengine_cache}\n")
        _f.write(f"Has QWebChannel: {'QWebChannel' in _webengine_cache}\n")
except Exception as _e:
    pass

_log_webengine_debug(f"Cache exists: {bool(_webengine_cache)}")
_log_webengine_debug(f"Cache keys: {list(_webengine_cache.keys()) if _webengine_cache else 'NONE'}")

if 'QWebEngineView' in _webengine_cache and 'QWebChannel' in _webengine_cache:
    QWebEngineView = _webengine_cache['QWebEngineView']
    QWebChannel = _webengine_cache['QWebChannel']
    WEBENGINE_AVAILABLE = True
    _log_webengine_debug("SUCCESS: Using cached WebEngine imports from RuleAssistantPY.py")
else:
    _log_webengine_debug("Cache not available, attempting normal import...")
    # Otherwise, try to import normally
    try:
        _log_webengine_debug("Attempting: from PyQt5.QtWebEngineWidgets import QWebEngineView")
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        _log_webengine_debug("Success: QWebEngineView imported")

        _log_webengine_debug("Attempting: from PyQt5.QtWebChannel import QWebChannel")
        from PyQt5.QtWebChannel import QWebChannel
        _log_webengine_debug("Success: QWebChannel imported")

        WEBENGINE_AVAILABLE = True
        _log_webengine_debug("SUCCESS: WebEngine imports successful (normal import)")
    except ImportError as e:
        _log_webengine_debug(f"ImportError: {type(e).__name__}: {e}")
        import traceback
        _log_webengine_debug(f"Traceback:\n{traceback.format_exc()}")
        QWebEngineView = None
        QWebChannel = None
        WEBENGINE_AVAILABLE = False
        _log_webengine_debug("FAILED: WebEngine import failed with ImportError")
    except Exception as e:
        _log_webengine_debug(f"Exception: {type(e).__name__}: {e}")
        import traceback
        _log_webengine_debug(f"Traceback:\n{traceback.format_exc()}")
        QWebEngineView = None
        QWebChannel = None
        WEBENGINE_AVAILABLE = False
        _log_webengine_debug("FAILED: WebEngine import failed with Exception")

_log_webengine_debug(f"Final WEBENGINE_AVAILABLE: {WEBENGINE_AVAILABLE}")
_log_webengine_debug("=== rule_generator_control.py import completed ===")

# NOW import the rest of PyQt5
from PyQt5.QtCore import QSettings, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow,
    QSplitter,
    QListWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QCheckBox,
    QMenu,
    QMessageBox,
    QDialog,
    QPushButton,
    QAction,
    QTextBrowser,
)

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

        # --- Integration with calling script ---
        self.from_lrt: bool = False
        self.exit_code: str = ""  # "1 <rule_number>" or "2"
        self.request_lrt: bool = False
        self._test_data_file: str = ""

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

        # Main 2-pane layout: left pane (rules) | right pane (form + tree)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # LEFT PANE: Rules list with checkbox and button
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.rules_list = QListWidget()
        self.rules_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.rules_list.customContextMenuRequested.connect(self._show_rule_context_menu)
        self.rules_list.currentRowChanged.connect(self._on_rule_selected)
        left_layout.addWidget(self.rules_list)

        # Checkbox and button at bottom of left pane
        bottom_layout = QHBoxLayout()
        self.overwrite_rules_check = QCheckBox(strings.OVERWRITE_RULES)
        bottom_layout.addWidget(self.overwrite_rules_check)
        self.btn_set_disjoint = QPushButton(strings.SET_DISJOINT_FEATURES)
        self.btn_set_disjoint.clicked.connect(self._on_set_disjoint_features)
        bottom_layout.addWidget(self.btn_set_disjoint)
        left_layout.addLayout(bottom_layout)

        main_splitter.addWidget(left_pane)

        # RIGHT PANE: Vertical splitter with form fields at top and tree at bottom
        right_pane = QSplitter(Qt.Orientation.Vertical)

        # Top section: form fields on left, source text on right
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Form fields (Rule name, Description, Create permutations)
        form_pane = QWidget()
        form_layout = QVBoxLayout(form_pane)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # Rule name row
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel(strings.RULE_NAME))
        self.rule_name_edit = QLineEdit()
        self.rule_name_edit.textEdited.connect(self._on_rule_name_changed)
        name_layout.addWidget(self.rule_name_edit)
        form_layout.addLayout(name_layout)

        # Description row
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel(strings.DESCRIPTION))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.textChanged.connect(self._on_description_changed)
        desc_layout.addWidget(self.description_edit)
        form_layout.addLayout(desc_layout)

        # Create permutations row
        perm_layout = QHBoxLayout()
        perm_layout.addWidget(QLabel(strings.CREATE_PERMUTATIONS))
        self.create_permutations_combo = QComboBox()
        self.create_permutations_combo.addItem(strings.NO)
        self.create_permutations_combo.addItem(strings.YES)
        self.create_permutations_combo.currentTextChanged.connect(self._on_create_permutations_changed)
        perm_layout.addWidget(self.create_permutations_combo)
        perm_layout.addStretch()
        form_layout.addLayout(perm_layout)

        form_layout.addStretch()
        top_splitter.addWidget(form_pane)

        # Source text display
        source_pane = QWidget()
        source_layout = QVBoxLayout(source_pane)
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.addWidget(QLabel(strings.SOURCE_TEXT))
        self.source_text_view = QWebEngineView()
        source_layout.addWidget(self.source_text_view)
        top_splitter.addWidget(source_pane)

        top_splitter.setStretchFactor(0, 1)
        top_splitter.setStretchFactor(1, 1)
        right_pane.addWidget(top_splitter)

        # Bottom section: tree diagram
        self.web_view = QWebEngineView()
        self.bridge = WebBridge()
        channel = QWebChannel(self.web_view.page())
        channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(channel)
        self.bridge.message_received.connect(self._process_web_message)
        right_pane.addWidget(self.web_view)

        right_pane.setStretchFactor(0, 1)
        right_pane.setStretchFactor(1, 1)

        main_splitter.addWidget(right_pane)

        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)
        main_layout.addWidget(main_splitter)

    # ------------------------------------------------------------------
    # Context menu definitions
    # ------------------------------------------------------------------

    def _build_context_menus(self):
        # --- Rule context menu (C# order: Duplicate, Insert Before, Insert After, -, Move Up, Move Down, -, Delete) ---
        self.rule_menu = QMenu(self)
        self.rule_act_duplicate = self._add_action(self.rule_menu, strings.CM_DUPLICATE, self._rule_duplicate)
        self.rule_act_insert_before = self._add_action(self.rule_menu, strings.CM_INSERT_BEFORE, self._rule_insert_before)
        self.rule_act_insert_after = self._add_action(self.rule_menu, strings.CM_INSERT_AFTER, self._rule_insert_after)
        self.rule_menu.addSeparator()
        self.rule_act_move_up = self._add_action(self.rule_menu, strings.CM_MOVE_UP, self._rule_move_up)
        self.rule_act_move_down = self._add_action(self.rule_menu, strings.CM_MOVE_DOWN, self._rule_move_down)
        self.rule_menu.addSeparator()
        self.rule_act_delete = self._add_action(self.rule_menu, strings.CM_DELETE, self._rule_delete)

        # --- Word context menu (C# order: Duplicate, Insert Before, Insert After, -, Move Left, Move Right, -, Delete, -, Insert Prefix, Insert Suffix, Insert Category, Insert Feature, Mark As Head, Remove Head Marking) ---
        self.word_menu = QMenu(self)
        self.word_act_duplicate = self._add_action(self.word_menu, strings.CM_DUPLICATE, self._word_duplicate)
        self.word_act_insert_before = self._add_action(self.word_menu, strings.CM_INSERT_BEFORE, self._word_insert_before)
        self.word_act_insert_after = self._add_action(self.word_menu, strings.CM_INSERT_AFTER, self._word_insert_after)
        self.word_menu.addSeparator()
        self.word_act_move_left = self._add_action(self.word_menu, strings.CM_MOVE_LEFT, self._word_move_left)
        self.word_act_move_right = self._add_action(self.word_menu, strings.CM_MOVE_RIGHT, self._word_move_right)
        self.word_menu.addSeparator()
        self.word_act_delete = self._add_action(self.word_menu, strings.CM_DELETE, self._word_delete)
        self.word_menu.addSeparator()
        self.word_act_insert_prefix = self._add_action(self.word_menu, strings.CM_INSERT_PREFIX, self._word_insert_prefix)
        self.word_act_insert_suffix = self._add_action(self.word_menu, strings.CM_INSERT_SUFFIX, self._word_insert_suffix)
        self.word_act_insert_category = self._add_action(self.word_menu, strings.CM_INSERT_CATEGORY, self._word_insert_category)
        self.word_act_insert_feature = self._add_action(self.word_menu, strings.CM_INSERT_FEATURE, self._word_insert_feature)
        self.word_act_mark_as_head = self._add_action(self.word_menu, strings.CM_MARK_AS_HEAD, self._word_mark_as_head)
        self.word_act_remove_head_marking = self._add_action(self.word_menu, strings.CM_REMOVE_HEAD_MARKING, self._word_remove_head_marking)

        # --- Category context menu (C# order: Edit, -, Delete) ---
        self.category_menu = QMenu(self)
        self._add_action(self.category_menu, strings.CM_EDIT, self._category_edit)
        self.category_menu.addSeparator()
        self._add_action(self.category_menu, strings.CM_DELETE, self._category_delete)

        # --- Feature context menu (C# order: Edit, -, Delete) ---
        self.feature_menu = QMenu(self)
        self._add_action(self.feature_menu, strings.CM_EDIT, self._feature_edit)
        self.feature_menu.addSeparator()
        self._add_action(self.feature_menu, strings.CM_DELETE, self._feature_delete)

        # --- Affix context menu (C# order: Duplicate, Insert Prefix Before, Insert Prefix After, Insert Suffix Before, Insert Suffix After, -, Move Left, Move Right, -, Delete, -, Insert Feature) ---
        self.affix_menu = QMenu(self)
        self._add_action(self.affix_menu, strings.CM_DUPLICATE, self._affix_duplicate)
        self._add_action(self.affix_menu, strings.CM_INSERT_PREFIX_BEFORE, self._affix_insert_prefix_before)
        self._add_action(self.affix_menu, strings.CM_INSERT_PREFIX_AFTER, self._affix_insert_prefix_after)
        self._add_action(self.affix_menu, strings.CM_INSERT_SUFFIX_BEFORE, self._affix_insert_suffix_before)
        self._add_action(self.affix_menu, strings.CM_INSERT_SUFFIX_AFTER, self._affix_insert_suffix_after)
        self.affix_menu.addSeparator()
        self.affix_act_move_left = self._add_action(self.affix_menu, strings.CM_MOVE_LEFT, self._affix_move_left)
        self.affix_act_move_right = self._add_action(self.affix_menu, strings.CM_MOVE_RIGHT, self._affix_move_right)
        self.affix_menu.addSeparator()
        self._add_action(self.affix_menu, strings.CM_DELETE, self._affix_delete)
        self.affix_menu.addSeparator()
        self._add_action(self.affix_menu, strings.CM_INSERT_FEATURE, self._affix_insert_feature)

    @staticmethod
    def _add_action(menu: QMenu, text: str, slot) -> QAction:
        action = menu.addAction(text)
        action.triggered.connect(slot)
        return action

    # ------------------------------------------------------------------
    # Populate rules list
    # ------------------------------------------------------------------

    def fill_rules_list(self):
        import sys
        print("[DEBUG] fill_rules_list: starting", file=sys.stderr, flush=True)
        self.rules_list.blockSignals(True)
        print("[DEBUG] fill_rules_list: signals blocked", file=sys.stderr, flush=True)
        self.rules_list.clear()
        print("[DEBUG] fill_rules_list: list cleared", file=sys.stderr, flush=True)
        if self.rule_generator:
            print(f"[DEBUG] fill_rules_list: adding {len(self.rule_generator.rules)} rules", file=sys.stderr, flush=True)
            for i, rule in enumerate(self.rule_generator.rules):
                print(f"[DEBUG] fill_rules_list: adding rule {i}: {str(rule)}", file=sys.stderr, flush=True)
                self.rules_list.addItem(str(rule))
                print(f"[DEBUG] fill_rules_list: added rule {i}", file=sys.stderr, flush=True)
        print("[DEBUG] fill_rules_list: unblocking signals", file=sys.stderr, flush=True)
        self.rules_list.blockSignals(False)
        print("[DEBUG] fill_rules_list: signals unblocked", file=sys.stderr, flush=True)
        if self.rule_generator and self.rule_generator.rules:
            print("[DEBUG] fill_rules_list: setting current row", file=sys.stderr, flush=True)
            index = min(self.last_selected_rule, len(self.rule_generator.rules) - 1)
            index = max(index, 0)
            print(f"[DEBUG] fill_rules_list: setting current row to {index}", file=sys.stderr, flush=True)
            self.rules_list.setCurrentRow(index)
            print("[DEBUG] fill_rules_list: current row set", file=sys.stderr, flush=True)
        print("[DEBUG] fill_rules_list: finished", file=sys.stderr, flush=True)

    # ------------------------------------------------------------------
    # Rule selection
    # ------------------------------------------------------------------

    def _on_rule_selected(self, row: int):
        import sys
        print(f"[DEBUG] _on_rule_selected called with row={row}", file=sys.stderr, flush=True)
        if row < 0 or not self.rule_generator or row >= len(self.rule_generator.rules):
            print(f"[DEBUG] _on_rule_selected: invalid row", file=sys.stderr, flush=True)
            self.selected_rule = None
            self.rule_name_edit.clear()
            return
        print(f"[DEBUG] _on_rule_selected: setting selected_rule", file=sys.stderr, flush=True)
        self.selected_rule = self.rule_generator.rules[row]
        self.last_selected_rule = row
        print(f"[DEBUG] _on_rule_selected: setting name text", file=sys.stderr, flush=True)
        self.rule_name_edit.setText(self.selected_rule.name)
        print(f"[DEBUG] _on_rule_selected: calling _show_rule_in_web_page", file=sys.stderr, flush=True)
        self._show_rule_in_web_page()
        print(f"[DEBUG] _on_rule_selected: finished", file=sys.stderr, flush=True)

    def _on_rule_name_changed(self, text: str):
        if self.selected_rule is None:
            return
        self.selected_rule.name = text
        row = self.rules_list.currentRow()
        if 0 <= row < self.rules_list.count():
            self.rules_list.item(row).setText(str(self.selected_rule))
        self._mark_dirty()

    def _on_description_changed(self):
        # TODO: Description field not yet mapped to rule model
        pass

    def _on_create_permutations_changed(self, text: str):
        # TODO: Create permutations field not yet mapped to rule model
        pass

    def _on_set_disjoint_features(self):
        # TODO: Implement set disjoint features
        pass

    # ------------------------------------------------------------------
    # Web page display
    # ------------------------------------------------------------------

    def _show_rule_in_web_page(self):
        import sys
        print(f"[DEBUG] _show_rule_in_web_page called", file=sys.stderr, flush=True)
        if self.selected_rule is None:
            print(f"[DEBUG] _show_rule_in_web_page: selected_rule is None", file=sys.stderr, flush=True)
            return
        print(f"[DEBUG] _show_rule_in_web_page: producing web page", file=sys.stderr, flush=True)
        html = self.producer.produce_web_page(self.selected_rule)
        print(f"[DEBUG] _show_rule_in_web_page: web page produced, length={len(html)}", file=sys.stderr, flush=True)

        if WEBENGINE_AVAILABLE:
            print(f"[DEBUG] _show_rule_in_web_page: WebEngine available", file=sys.stderr, flush=True)
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

        print(f"[DEBUG] _show_rule_in_web_page: calling setHtml", file=sys.stderr, flush=True)
        print(f"[DEBUG] _show_rule_in_web_page: web_view type={type(self.web_view).__name__}", file=sys.stderr, flush=True)

        try:
            if WEBENGINE_AVAILABLE:
                # QWebEngineView supports baseUrl parameter
                base_url = QUrl.fromLocalFile(
                    str(Path(__file__).parent.parent / "resources") + "/"
                )
                print(f"[DEBUG] _show_rule_in_web_page: calling setHtml with base_url", file=sys.stderr, flush=True)
                self.web_view.setHtml(html, base_url)
            else:
                # QTextBrowser may not handle baseUrl the same way
                print(f"[DEBUG] _show_rule_in_web_page: calling setHtml without base_url (QTextBrowser)", file=sys.stderr, flush=True)
                self.web_view.setHtml(html)
            print(f"[DEBUG] _show_rule_in_web_page: setHtml completed", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"[ERROR] setHtml failed: {str(e)}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)
            # Fallback: show plain text version
            try:
                plain = html.replace("<", "&lt;").replace(">", "&gt;")
                self.web_view.setHtml(f"<pre>{plain}</pre>")
                print(f"[DEBUG] Fallback setHtml succeeded", file=sys.stderr, flush=True)
            except Exception as e2:
                print(f"[ERROR] Fallback also failed: {str(e2)}", file=sys.stderr, flush=True)

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
                self._adjust_word_context_menu()
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
                self._adjust_affix_context_menu()
                self._show_menu_at_cursor(self.affix_menu)

    def _show_menu_at_cursor(self, menu: QMenu):
        from PyQt5.QtGui import QCursor

        menu.popup(QCursor.pos())

    # ------------------------------------------------------------------
    # Rule context menu (shown on QListWidget right-click)
    # ------------------------------------------------------------------

    def _show_rule_context_menu(self, pos):
        if not self.rule_generator:
            return
        index = self.rules_list.currentRow()
        self._adjust_rule_context_menu(index)
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
        phrase.insert_new_word_at(index + 1)
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
        dup.id = str(len(phrase.words) + 1)
        phrase.insert_word_at(dup, index + 1)
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
        self.word.insert_new_affix_at(AffixType.PREFIX, 0)
        self._mark_dirty()
        self._show_rule_in_web_page()

    def _word_insert_suffix(self):
        if self.word is None:
            return
        self.word.insert_new_affix_at(AffixType.SUFFIX, 0)
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
        word.insert_affix_at(dup, index)
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
        word.insert_new_affix_at(AffixType.PREFIX, index + 1)
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
        word.insert_new_affix_at(AffixType.SUFFIX, index + 1)
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
        if chooser.exec_() == QDialog.Accepted and chooser.selected_category:
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
        if chooser.exec_() != QDialog.Accepted:
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
        if value_chooser.exec_() == QDialog.Accepted and value_chooser.selected_feature_value:
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
    # Context menu enable/disable adjustment
    # ------------------------------------------------------------------

    def _adjust_rule_context_menu(self, index: int):
        """Enable/disable rule menu items based on current position."""
        if not self.rule_generator:
            return
        count = len(self.rule_generator.rules)
        index_last = count - 1
        self.rule_act_move_up.setEnabled(index > 0)
        self.rule_act_move_down.setEnabled(index < index_last)
        self.rule_act_delete.setEnabled(not (index == 0 and index_last == 0))

    def _adjust_word_context_menu(self):
        """Enable/disable word menu items based on current word state."""
        if self.word is None:
            return
        phrase = self._get_parent_phrase()
        if phrase is None:
            return
        index = self._word_index_in_phrase(phrase)
        if index < 0:
            return
        index_last = len(phrase.words) - 1
        self.word_act_move_left.setEnabled(index > 0)
        self.word_act_move_right.setEnabled(index < index_last)
        # Only allow insert prefix/suffix if no affixes yet
        has_affixes = len(self.word.affixes) > 0
        self.word_act_insert_prefix.setEnabled(not has_affixes)
        self.word_act_insert_suffix.setEnabled(not has_affixes)
        # Only allow insert category if no category yet
        self.word_act_insert_category.setEnabled(not self.word.category)
        # Only allow insert feature if no features yet
        self.word_act_insert_feature.setEnabled(len(self.word.features) == 0)
        # Head marking toggles
        self.word_act_mark_as_head.setEnabled(self.word.head == HeadValue.NO)
        self.word_act_remove_head_marking.setEnabled(self.word.head == HeadValue.YES)

    def _adjust_affix_context_menu(self):
        """Enable/disable affix menu items based on current affix position."""
        if self.affix is None:
            return
        word = self._get_parent_word_for_affix()
        if word is None:
            return
        index = self._affix_index_in_word(word)
        if index < 0:
            return
        index_last = len(word.affixes) - 1
        self.affix_act_move_left.setEnabled(index > 0)
        self.affix_act_move_right.setEnabled(index < index_last)

    # ------------------------------------------------------------------
    # Dirty tracking / save
    # ------------------------------------------------------------------

    def _mark_dirty(self):
        self._is_dirty = True
        self._show_change_status_on_form()

    def _show_change_status_on_form(self):
        title = strings.FORM_TITLE
        if self._is_dirty:
            title += "*"
        self.setWindowTitle(title)

    def _save(self):
        if self.provider and self.rule_file_path:
            self.provider.save_data_to_file(self.rule_file_path)
            self._is_dirty = False
            self._show_change_status_on_form()

    # ------------------------------------------------------------------
    # Toolbar button handlers
    # ------------------------------------------------------------------

    def _on_test_in_lrt(self):
        self.request_lrt = True
        self._save()
        self.close()

    def _on_save_clicked(self):
        self._save()

    def _on_save_and_write(self):
        self._save()
        rule_index = self._current_rule_index()
        if rule_index >= 0:
            self.exit_code = f"1 {rule_index}"
        self.close()

    def _on_save_and_write_all(self):
        self._save()
        self.exit_code = "2"
        self.close()

    def _on_help(self):
        QMessageBox.information(
            self,
            strings.BTN_HELP,
            "FLExTrans Rule Generator\n\n"
            "Right-click on rules or tree elements to edit them.\n\n"
            "Use the toolbar buttons to save and generate transfer rules.",
        )

    # ------------------------------------------------------------------
    # Test data (source text) display
    # ------------------------------------------------------------------

    def set_test_data_file(self, file_path: str):
        self._test_data_file = file_path
        if WEBENGINE_AVAILABLE:
            url = QUrl.fromLocalFile(file_path)
            self.source_text_view.setUrl(url)
        else:
            # For QTextBrowser, read file content and display as HTML
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.source_text_view.setHtml(f"<pre>{content}</pre>")
            except Exception:
                self.source_text_view.setHtml("")

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
