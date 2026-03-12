# FLExTransRuleGenerator: C#/.NET → Python 3.13 / PyQt6 Conversion Plan

## Overview

**Source**: C# / .NET 4.6.1 / Windows Forms / WebView2 (46 C# files, ~5,000 lines)
**Target**: Python 3.13 / PyQt6 / QWebEngineView (est. ~2,500 lines)
**Verification**: Test-first — translate all 25 NUnit tests before implementing, verify against golden XML/HTML files

---

## Target Directory Structure

```
FLExTransRuleGenerator/
├── pyproject.toml
├── src/
│   └── flextrans_rule_generator/
│       ├── __init__.py
│       ├── main.py                        # Entry point (from FLExTransRuleGenerator.cs)
│       ├── model/
│       │   ├── __init__.py
│       │   ├── rule_constituent.py        # RuleConstituent base class
│       │   ├── constituent_with_features.py # ConstituentWithFeatures abstract class
│       │   ├── feature.py                 # Feature class
│       │   ├── category.py                # Category class
│       │   ├── affix.py                   # Affix class + AffixType enum
│       │   ├── word.py                    # Word class + HeadValue enum
│       │   ├── phrase.py                  # Phrase class + PhraseType enum
│       │   ├── source.py                  # Source class
│       │   ├── target.py                  # Target class
│       │   ├── rule.py                    # FLExTransRule class
│       │   ├── rule_generator.py          # FLExTransRuleGenerator root class
│       │   └── strings.py                 # Model string constants (from RuleGenModelStrings.resx)
│       ├── flex_model/
│       │   ├── __init__.py
│       │   ├── flex_category.py           # FLExCategory
│       │   ├── flex_categories.py         # FLExCategories
│       │   ├── flex_feature.py            # FLExFeature
│       │   ├── flex_feature_value.py      # FLExFeatureValue
│       │   ├── flex_feature_values.py     # FLExFeatureValues
│       │   ├── flex_data_base.py          # FLExDataBase abstract
│       │   ├── source_flex_data.py        # SourceFLExData
│       │   ├── target_flex_data.py        # TargetFLExData
│       │   └── flex_data.py               # FLExData root
│       ├── service/
│       │   ├── __init__.py
│       │   ├── xml_backend_provider.py          # XmlBackEndProvider
│       │   ├── xml_backend_provider_flex_data.py # XmlBackEndProviderFLExData
│       │   ├── web_page_producer.py             # WebPageProducer (singleton)
│       │   ├── constituent_finder.py            # ConstituentFinder (singleton)
│       │   └── rule_identifier_setter.py        # RuleIdentifierAndParentSetter (singleton)
│       ├── controller/
│       │   ├── __init__.py
│       │   ├── rule_generator_control.py  # Main window (QMainWindow + QWebEngineView)
│       │   ├── category_chooser.py        # Category dialog (QDialog)
│       │   ├── feature_value_chooser.py   # Feature value dialog (QDialog)
│       │   ├── web_bridge.py              # QWebChannel bridge object
│       │   └── strings.py                 # Controller string constants (from RuleGenStrings.resx)
│       └── resources/
│           ├── treeflex.css               # Copied as-is
│           └── rulegen.css                # Copied as-is
├── tests/
│   ├── conftest.py                        # Shared fixtures (from ServiceTestBase.cs)
│   ├── test_data/                         # Copied as-is from RuleGeneratorServiceTests/TestData/
│   │   ├── Ex1a_Def-Noun.xml
│   │   ├── Ex1a_Def-Noun.htm
│   │   ├── Ex4b_Indef-Adj-Noun.xml
│   │   ├── Ex4b_Indef-Adj-Noun.htm
│   │   ├── RuleGenExpected.xml
│   │   ├── FLExDataSpanFrench.xml
│   │   └── FLExTransRuleGenerator.dtd
│   ├── test_word.py                       # From WordTests.cs (7 tests)
│   ├── test_phrase.py                     # From PhraseTests.cs (4 tests)
│   ├── test_duplicate.py                  # From DuplicateTests.cs (3 tests)
│   ├── test_rule_generator.py             # From RuleGeneratorTests.cs (1 test)
│   ├── test_constituent_finder.py         # From ConstituentFinderTests.cs (2 tests)
│   ├── test_identifier_setter.py          # From RuleIdentifierAndParentSetterTests.cs (4 tests)
│   ├── test_xml_backend.py                # From XmlBackEndProviderTests.cs (3 tests)
│   ├── test_xml_backend_flex.py           # From XmlBackEndProviderFLExDataTests.cs (1 test)
│   └── test_web_page_producer.py          # From WebPageProducerTests.cs (2 tests)
└── TRACEABILITY.md                        # Method-level C#→Python mapping
```

---

## Phase 0: Project Scaffolding

**Agent**: scaffold-agent (general-purpose)
**Time gate**: None (first phase)

### Tasks
1. Create `pyproject.toml` with dependencies:
   ```toml
   [project]
   name = "flextrans-rule-generator"
   version = "1.0.0"
   requires-python = ">=3.13"
   dependencies = [
       "PyQt6>=6.6",
       "PyQt6-WebEngine>=6.6",
       "lxml>=5.0",
   ]

   [project.optional-dependencies]
   dev = [
       "pytest>=8.0",
       "pytest-qt>=4.3",
   ]

   [project.scripts]
   flextrans-rule-gen = "flextrans_rule_generator.main:main"
   ```
2. Create all `__init__.py` files
3. Create `src/` and `tests/` directory structure
4. Copy test data files as-is from `RuleGeneratorServiceTests/TestData/`
5. Copy CSS files as-is from `TestData/`
6. Create `tests/conftest.py` with shared fixtures (translated from `ServiceTestBase.cs`):
   - `test_data_dir` fixture returning path to `tests/test_data/`
   - `xml_provider` fixture returning loaded `XmlBackEndProvider`
   - Helper functions: `check_word_attributes()`, `check_feature_attributes()`,
     `make_word_attributes()`, `make_affix()`, `make_feature_attributes()`

### Deliverable
- `pip install -e ".[dev]"` succeeds
- `pytest --collect-only` finds 0 tests (files exist but are empty/skipped)

---

## Phase 1: Test Contracts (Write Tests First)

**Agent team**: 3 parallel agents

### Agent 1A: Model Test Translator
Translates 4 model test files from NUnit → pytest.

| Source File | Target File | Tests |
|-------------|-------------|-------|
| `WordTests.cs` | `test_word.py` | `test_delete_category`, `test_insert_category`, `test_delete_affix_at`, `test_insert_new_affix_at`, `test_insert_affix_at`, `test_delete_feature`, `test_swap_position_of_affixes` |
| `PhraseTests.cs` | `test_phrase.py` | `test_delete_word_at`, `test_insert_new_word_at`, `test_swap_position_of_words`, `test_mark_word_as_head` |
| `DuplicateTests.cs` | `test_duplicate.py` | `test_rule_duplicate`, `test_word_duplicate`, `test_affix_duplicate` |
| `RuleGeneratorTests.cs` | `test_rule_generator.py` | `test_new_operation` |

Translation rules:
- `[SetUp] public void Setup()` → `def setup_method(self):`
- `[Test]` → plain method name starting with `test_`
- `Assert.AreEqual(expected, actual)` → `assert actual == expected`
- `Assert.IsNotNull(x)` → `assert x is not None`
- `Assert.IsTrue(x)` → `assert x`
- `new Word()` → `Word()`
- `word.Category` → `word.category`
- `HeadValue.yes` → `HeadValue.YES`
- `AffixType.prefix` → `AffixType.PREFIX`
- `PhraseType.source` → `PhraseType.SOURCE`

### Agent 1B: Service Test Translator
Translates 5 service test files from NUnit → pytest.

| Source File | Target File | Tests |
|-------------|-------------|-------|
| `ConstituentFinderTests.cs` | `test_constituent_finder.py` | `test_set_for_ex1a_def_noun`, `test_set_for_ex4b_indef_adj_noun` |
| `RuleIdentifierAndParentSetterTests.cs` | `test_identifier_setter.py` | `test_identifiers_ex1a`, `test_identifiers_ex4b`, `test_parents_ex1a`, `test_parents_ex4b` |
| `XmlBackEndProviderTests.cs` | `test_xml_backend.py` | `test_load_ex1a_def_noun`, `test_load_ex4b_indef_adj_noun`, `test_save` |
| `WebPageProducerTests.cs` | `test_web_page_producer.py` | `test_produce_ex1a`, `test_produce_ex4b` |
| `XmlBackEndProviderFLExDataTests.cs` | `test_xml_backend_flex.py` | `test_load_flex_data` |

### Agent 1C: conftest.py + Test Infrastructure
- Translate `ServiceTestBase.cs` → `conftest.py` with pytest fixtures
- Ensure all test files have correct imports (even though implementations don't exist yet)
- All tests must be marked `@pytest.mark.skip(reason="implementation pending")` or use conditional imports

### Gate
- `pytest --collect-only` reports all 25 tests collected
- No import errors (use lazy imports or TYPE_CHECKING)

---

## Phase 2: Model Layer Implementation

**Agent team**: 3 parallel agents

### Agent 2A: Base Classes + Enums
Implements the foundation classes:

| C# File | Python File | Classes/Enums |
|---------|-------------|---------------|
| `RuleConstituent.cs` | `rule_constituent.py` | `RuleConstituent` |
| `ConstituentWithFeatures.cs` | `constituent_with_features.py` | `ConstituentWithFeatures` |

Methods to implement in `RuleConstituent`:
- `__init__(self)` — sets `identifier = 0`, `parent = None`
- `produce_span(self, s_class, s_type) -> str`
- `_produce_to_app(self, s_type) -> str`

Methods to implement in `ConstituentWithFeatures(RuleConstituent)`:
- `__init__(self)` — adds `features: list[Feature] = []`
- `delete_feature(self, feature)`
- `insert_new_feature(self, label, match) -> Feature`
- `_find_constituent_in_features(self, identifier) -> Optional[RuleConstituent]`
- `_produce_html_for_features(self) -> str`
- `_duplicate_features(self) -> list[Feature]`

### Agent 2B: Leaf Classes
Implements the leaf model classes:

| C# File | Python File | Classes |
|---------|-------------|---------|
| `Feature.cs` | `feature.py` | `Feature(RuleConstituent)` |
| `Category.cs` | `category.py` | `Category(RuleConstituent)` |
| `Affix.cs` | `affix.py` | `Affix(ConstituentWithFeatures)`, `AffixType(Enum)` |

Each class needs: `__init__`, `find_constituent`, `produce_html`, `duplicate`

### Agent 2C: Composite Classes
Implements the composite model classes:

| C# File | Python File | Classes |
|---------|-------------|---------|
| `Word.cs` | `word.py` | `Word(ConstituentWithFeatures)`, `HeadValue(Enum)` |
| `Phrase.cs` | `phrase.py` | `Phrase(RuleConstituent)`, `PhraseType(Enum)` |
| `Source.cs` | `source.py` | `Source` |
| `Target.cs` | `target.py` | `Target` |
| `FLExTransRule.cs` | `rule.py` | `FLExTransRule(RuleConstituent)` |
| `FLExTransRuleGenerator.cs` (model) | `rule_generator.py` | `FLExTransRuleGenerator` |

`Word` methods (12):
- `__init__`, `delete_category`, `insert_category`, `delete_affix_at`,
  `insert_affix_at`, `insert_new_affix_at`, `swap_position_of_affixes`,
  `find_constituent`, `produce_html`, `duplicate`

`Phrase` methods (10):
- `__init__`, `delete_word_at`, `insert_new_word_at`, `insert_word_at`,
  `swap_position_of_words`, `mark_word_as_head`, `produce_html`,
  `find_constituent`, `duplicate`

Also: `model/strings.py` with constants from `RuleGenModelStrings.resx`:
```python
CAT = "cat"
FEATURE_X = "FeatureX"
MATCH_X = "?"
PHRASE = "phrase"
PREFIX = "prefix"
SRC = "src"
SUFFIX = "suffix"
TGT = "tgt"
WORD = "word"
NAME_MISSING = "This rule needs a name"
HEAD = "head"
```

### Gate
- Remove `@pytest.mark.skip` from model tests
- Run: `pytest tests/test_word.py tests/test_phrase.py tests/test_duplicate.py tests/test_rule_generator.py`
- **All 15 model tests pass**

---

## Phase 3: FLEx Model Layer Implementation

**Agent**: Single agent (small layer)

### Agent 3A: FLEx Model Classes

| C# File | Python File | Class |
|---------|-------------|-------|
| `FLExCategory.cs` | `flex_category.py` | `FLExCategory` — `abbreviation: str`, `__str__` |
| `FLExCategories.cs` | `flex_categories.py` | `FLExCategories` — `categories: list[FLExCategory]` |
| `FLExFeature.cs` | `flex_feature.py` | `FLExFeature` — `name: str`, `values: list`, `__str__` |
| `FLExFeatureValue.cs` | `flex_feature_value.py` | `FLExFeatureValue` — `abbreviation: str`, `feature: Optional`, `__str__` |
| `FLExFeatureValues.cs` | `flex_feature_values.py` | `FLExFeatureValues` — `values: list` |
| `FLExDataBase.cs` | `flex_data_base.py` | `FLExDataBase` (abstract) — `name`, `categories`, `features`, `set_feature_in_feature_values()` |
| `SourceFLExData.cs` | `source_flex_data.py` | `SourceFLExData(FLExDataBase)` |
| `TargetFLExData.cs` | `target_flex_data.py` | `TargetFLExData(FLExDataBase)` |
| `FLExData.cs` | `flex_data.py` | `FLExData` — `source_data`, `target_data`, `set_feature_in_feature_values()` |

### Gate
- No dedicated tests for this layer alone, but needed by Phase 4

---

## Phase 4: XML Serialization (Highest Risk)

**Agent team**: 2 parallel agents

### Agent 4A: Rule XML Provider
Implements `xml_backend_provider.py` — the most critical file.

**`XmlBackEndProvider`**:
- `load_data_from_file(file_name: str)`:
  - Parse XML with `xml.etree.ElementTree`
  - Map `<FLExTransRuleGenerator>` → `FLExTransRuleGenerator` object
  - Map `<FLExTransRules>` → list of `FLExTransRule`
  - Map `<FLExTransRule name="...">` → `FLExTransRule` with `name` attribute
  - Map `<Source><Phrase><Words><Word id="..." category="..." head="...">` → nested objects
  - Map `<Features><Feature match="..." label="..."/>` → `Feature` objects
  - Map `<Affixes><Affix type="...">` → `Affix` objects with nested features
  - After loading: set `target.Phrase.Type = PhraseType.TARGET`
  - After loading: set `word.CategoryConstituent.Name = word.Category` for all words
- `save_data_to_file(file_name: str)`:
  - Build XML tree from Python objects
  - Insert DOCTYPE declaration (matching C# hack at position 165):
    ```
    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE FLExTransRuleGenerator PUBLIC " -//XMLmind//DTD FLExTransRuleGenerator//EN"
    "FLExTransRuleGenerator.dtd">
    <FLExTransRuleGenerator>
    ```
  - Write UTF-8 encoded output

**Verification**: Round-trip test:
1. Load `Ex4b_Indef-Adj-Noun.xml`
2. Save to temp file
3. Load saved file
4. Compare all object properties

### Agent 4B: FLEx Data XML Provider
Implements `xml_backend_provider_flex_data.py`.

**`XmlBackEndProviderFLExData`**:
- `load_data_from_file(file_name: str)`:
  - Parse `<FLExData>` root
  - Map `<SourceData name="...">` → `SourceFLExData`
  - Map `<TargetData name="...">` → `TargetFLExData`
  - Map `<Categories><FLExCategory abbr="..."/>` → list of `FLExCategory`
  - Map `<Features><FLExFeature name="..."><Values><FLExFeatureValue abbr="..."/>` → nested objects
  - Call `flex_data.set_feature_in_feature_values()` to link back-references

### Gate
- Remove `@pytest.mark.skip` from XML tests
- Run: `pytest tests/test_xml_backend.py tests/test_xml_backend_flex.py`
- **All 4 XML tests pass**
- **Specific verification**: `test_save` produces output matching `RuleGenExpected.xml`

---

## Phase 5: Service Layer

**Agent team**: 2 parallel agents

### Agent 5A: ConstituentFinder + RuleIdentifierAndParentSetter

**`RuleIdentifierAndParentSetter`** (singleton):
- `set_identifiers_and_parents(rule)` — traverses rule tree, assigns sequential IDs, sets parent refs
- `_set_phrase_identifiers(phrase)` — assigns IDs to phrase → words → categories → features → affixes
- `_set_feature_identifiers(features, parent)` — assigns IDs to feature list

**`ConstituentFinder`** (singleton):
- `find_constituent(rule, identifier)` — splits search by ID vs target phrase ID threshold

### Agent 5B: WebPageProducer

**`WebPageProducer`** (singleton):
- `produce_web_page(rule) -> str` — generates complete HTML document
- `_html_beginning() -> str` — DOCTYPE, head, CSS links, **JavaScript bridge**
- `_javascript_contents() -> str`:
  - **CRITICAL CHANGE**: Replace WebView2's `window.chrome.webview.postMessage(msg)` with QWebChannel:
    ```javascript
    function toApp(msg) {
        if (window.bridge) {
            window.bridge.receive_message(msg);
        }
        return false;
    }
    ```
  - Add QWebChannel initialization script
- `_html_body() -> str` — table with source/target phrases
- `_phrase_html(phrase) -> str` — TreeFlex tree structure
- `_html_ending() -> str` — closing tags

### Gate
- Remove `@pytest.mark.skip` from service tests
- Run: `pytest tests/test_constituent_finder.py tests/test_identifier_setter.py tests/test_web_page_producer.py`
- **All 8 service tests pass**
- **HTML golden file comparison**: generated HTML matches `Ex1a_Def-Noun.htm` and `Ex4b_Indef-Adj-Noun.htm`
  - Note: JS bridge code will differ from C# version — update `.htm` golden files to match new bridge, OR compare only the HTML body portion

---

## Phase 6: UI Layer (Dialogs)

**Agent team**: 2 parallel agents

### Agent 6A: CategoryChooser Dialog

**`category_chooser.py`** — `CategoryChooser(QDialog)`:

| C# Method | Python Method |
|-----------|---------------|
| `CategoryChooser()` | `__init__(self, categories, parent=None)` |
| `InitializeComponent()` | Build layout: `QVBoxLayout` → `QListWidget` + `QDialogButtonBox` |
| `FillCategoriesListBox()` | `fill_categories_list(self)` — populate `QListWidget` |
| `SelectCategory(index)` | `select_category(self, index)` — `QListWidget.setCurrentRow()` |
| `btnOK_Click` | Override `accept(self)` — set `self.selected_category` from selection |

UI specification:
- Window title: "Category Chooser"
- Size: 800x450
- ListBox: 764x364, items are `FLExCategory` objects (display via `__str__`)
- OK button (AcceptRole) + Cancel button (RejectRole)

### Agent 6B: FeatureValueChooser Dialog

**`feature_value_chooser.py`** — `FeatureValueChooser(QDialog)`:

| C# Method | Python Method |
|-----------|---------------|
| `FeatureValueChooser()` | `__init__(self, parent=None)` |
| `CreateVariableValues(feat)` | `create_variable_values(self, feat)` — using `["α","β","γ","δ","ε","ζ","η","θ","ι","κ","μ","ν"]` |
| `FillFeatureValuesListBox()` | `fill_feature_values_list(self)` |
| `FindAndSelectFeatureValuePair(label, match)` | `find_and_select_feature_value_pair(self, label, match)` |
| `SelectFeatureValue(index)` | `select_feature_value(self, index)` |
| `btnOK_Click` | Override `accept(self)` |

Properties to preserve:
- `feature_values: list[FLExFeatureValue]`
- `variable_feature_values: list[FLExFeatureValue]`
- `selected_feature_value: FLExFeatureValue`
- `match: str`
- `max_variables: int = 4`

### Gate
- Both dialogs instantiate without errors
- pytest-qt tests verify: list population, selection, OK/Cancel return values

---

## Phase 7: Main Window (QWebEngineView)

**Agent team**: 2 parallel agents

### Agent 7A: WebChannel Bridge + WebView Integration

**`web_bridge.py`** — `WebBridge(QObject)`:
```python
class WebBridge(QObject):
    message_received = pyqtSignal(str)  # Signal emitted when JS calls bridge

    @pyqtSlot(str)
    def receive_message(self, msg: str):
        self.message_received.emit(msg)
```

QWebChannel setup in main window:
```python
channel = QWebChannel(self.web_view.page())
self.bridge = WebBridge()
channel.registerObject("bridge", self.bridge)
self.web_view.page().setWebChannel(channel)
self.bridge.message_received.connect(self._process_web_message)
```

JavaScript injection (added to `WebPageProducer._html_beginning()`):
```html
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<script>
var bridge = null;
new QWebChannel(qt.webChannelTransport, function(channel) {
    bridge = channel.objects.bridge;
});
function toApp(msg) {
    if (bridge) { bridge.receive_message(msg); }
    return false;
}
</script>
```

### Agent 7B: RuleGeneratorControl Main Window

**`rule_generator_control.py`** — `RuleGeneratorControl(QMainWindow)`:

**Constructor & lifecycle** (6 methods):
| C# | Python |
|----|--------|
| `RuleGeneratorControl()` | `__init__(self)` — create UI, connect signals |
| `RuleGeneratorControl_Load` | Logic in `__init__` or `showEvent` |
| `InitFlexTransDir()` | `_init_flex_trans_dir(self)` — use `Path(__file__).parent / "resources"` |
| `RetrieveRegistrySettings()` | `_retrieve_settings(self)` — `QSettings("SIL", "FLExTransRuleGenerator")` |
| `SaveRegistrySettings()` | `_save_settings(self)` — `QSettings` |
| `RuleGeneratorControl_FormClosing` | `closeEvent(self, event)` |
| `SaveDataIfChanged()` | `_save_data_if_changed(self)` — `QMessageBox.question()` |

**UI layout**:
- `QSplitter` containing:
  - Left: `QListWidget` (rules list, 266px wide)
  - Right: `QVBoxLayout` with:
    - `QHBoxLayout`: `QLabel("Rule Name:")` + `QLineEdit`
    - `QWebEngineView` (rule display)

**WebView methods** (3):
| C# | Python |
|----|--------|
| `webView2_CoreWebView2InitializationCompleted` | Not needed |
| `wv2RuleEditor_WebMessageReceived` | `_process_web_message(self, msg)` connected via `WebBridge.message_received` signal |
| `ShowRuleInWebPage()` | `_show_rule_in_web_page(self)` — `self.web_view.setHtml(html, base_url)` |

**Rule list methods** (3):
| C# | Python |
|----|--------|
| `FillRulesListBox()` | `fill_rules_list(self)` |
| `lBoxRules_SelectedIndexChanged` | Connect `QListWidget.currentRowChanged` → `_on_rule_selected` |
| `lBoxRules_MouseUp` | Connect `QListWidget.customContextMenuRequested` → `_on_rules_context_menu` |

**Context menu builders** (5 methods):
| C# | Python |
|----|--------|
| `BuildRuleContextMenu()` | `_build_rule_context_menu(self) -> QMenu` |
| `BuildAffixContextMenu()` | `_build_affix_context_menu(self) -> QMenu` |
| `BuildCategoryContextMenu()` | `_build_category_context_menu(self) -> QMenu` |
| `BuildFeatureContextMenu()` | `_build_feature_context_menu(self) -> QMenu` |
| `BuildWordContextMenu()` | `_build_word_context_menu(self) -> QMenu` |

**Context menu adjusters** (3 methods):
| C# | Python |
|----|--------|
| `AdjustRuleContextMenuContent(lBoxSender, indexAtMouse)` | `_adjust_rule_context_menu(self, index)` |
| `AdjustWordContextMenuContent()` | `_adjust_word_context_menu(self)` |
| `AdjustAffixContextMenuContent()` | `_adjust_affix_context_menu(self)` |

**Context menu click handlers** (30 methods):
Rule handlers (6):
- `_on_rule_insert_before`, `_on_rule_insert_after`
- `_on_rule_duplicate`, `_on_rule_delete`
- `_on_rule_move_up`, `_on_rule_move_down`

Word handlers (12):
- `_on_word_insert_before`, `_on_word_insert_after`
- `_on_word_duplicate`, `_on_word_delete`
- `_on_word_move_left`, `_on_word_move_right`
- `_on_word_mark_as_head`, `_on_word_remove_head_marking`
- `_on_word_insert_category`, `_on_word_insert_feature`
- `_on_word_insert_prefix`, `_on_word_insert_suffix`

Category handlers (2): `_on_category_edit`, `_on_category_delete`
Feature handlers (2): `_on_feature_edit`, `_on_feature_delete`

Affix handlers (8):
- `_on_affix_insert_feature`, `_on_affix_delete`, `_on_affix_duplicate`
- `_on_affix_insert_prefix_before`, `_on_affix_insert_prefix_after`
- `_on_affix_insert_suffix_before`, `_on_affix_insert_suffix_after`
- `_on_affix_move_left`, `_on_affix_move_right`

**Helper methods** (7):
- `_do_rule_insert(index)`, `_do_rule_move(index, other_index)`
- `_do_word_insert(before: bool)`
- `_get_index_of_affix_in_word() -> int`
- `_get_index_of_word_in_phrase() -> int`
- `_get_phrase_from_feature(feature) -> Phrase`
- `_get_phrase_from_category(category) -> Phrase`

**Dialog launchers** (3):
- `_launch_category_chooser(categories)`
- `_launch_feature_chooser(features)`
- `_process_insert_feature()`, `_process_insert_category()`

**Text/state handlers** (3):
- `_on_name_changed(text)` — connected to `QLineEdit.textChanged`
- `_mark_as_changed(value: bool)`
- `_show_change_status_on_form()`

### Gate
- Application launches: `python -m flextrans_rule_generator.main <rule.xml> <flex_data.xml>`
- Loads rules, displays in list
- Selecting a rule shows tree visualization in QWebEngineView
- Clicking tree nodes triggers correct context menus
- All context menu actions modify model correctly
- Unsaved changes prompt on close

---

## Phase 8: Entry Point + Packaging

**Agent**: Single agent

### Agent 8A: Main Entry Point

**`main.py`**:
```python
def main():
    parser = argparse.ArgumentParser(description="FLExTrans Rule Generator")
    parser.add_argument("rule_file", help="FLExTrans transfer rule file")
    parser.add_argument("flex_data_file", help="XML file with source/target categories and features")
    parser.add_argument("max_vars", nargs="?", type=int, default=4,
                        help="Max number of variables (default: 4)")
    args = parser.parse_args()

    # Validate files exist
    # Load data via XmlBackEndProvider + XmlBackEndProviderFLExData
    # Create QApplication
    # Create RuleGeneratorControl, set properties
    # app.exec()
```

### Gate
- `python -m flextrans_rule_generator.main --help` shows usage
- `python -m flextrans_rule_generator.main <rule.xml> <flex.xml>` launches the GUI
- `python -m flextrans_rule_generator.main <rule.xml> <flex.xml> 6` sets max variables to 6

---

## Phase 9: Final Validation

**Agent team**: 3 parallel agents

### Agent 9A: Full Test Suite
- Run `pytest` — **all 25+ tests green**
- Run `pytest --tb=long -v` for full output
- Verify no skipped tests remain

### Agent 9B: Traceability Matrix
Create `TRACEABILITY.md` mapping every C# method → Python method:

```markdown
| C# File | C# Method | Python File | Python Method | Status |
|---------|-----------|-------------|---------------|--------|
| Word.cs:35 | DeleteCategory() | word.py | delete_category() | DONE |
| Word.cs:41 | InsertCategory(cat) | word.py | insert_category(cat) | DONE |
...
```

Verify: **zero gaps** — every C# public/protected method has a Python counterpart.

### Agent 9C: Golden File Verification
- Load each XML test file → save → diff against original (normalize whitespace)
- Generate HTML for each test rule → diff against `.htm` golden files
- Verify CSS files copied unchanged
- Verify DTD file copied unchanged

### Final Gate
- All tests pass
- Traceability matrix is complete with no gaps
- XML round-trip produces identical output
- HTML generation matches golden files (with JS bridge adjustment documented)
- Application launches and all UI interactions work

---

## Agent Team Summary

| Phase | Agents | Parallelism | Dependencies |
|-------|--------|-------------|--------------|
| 0: Scaffold | 1 general-purpose | — | None |
| 1: Test Contracts | 3 parallel | Full parallel | Phase 0 |
| 2: Model Layer | 3 parallel | Full parallel | Phase 1 |
| 3: FLEx Model | 1 agent | Sequential | Phase 2 |
| 4: XML Serialization | 2 parallel | Full parallel | Phase 3 |
| 5: Service Layer | 2 parallel | Full parallel | Phase 4 |
| 6: UI Dialogs | 2 parallel | Full parallel | Phase 5 |
| 7: Main Window | 2 parallel | Full parallel | Phase 6 |
| 8: Entry Point | 1 agent | Sequential | Phase 7 |
| 9: Validation | 3 parallel | Full parallel | Phase 8 |
| **Total** | **20 agent invocations** | | |

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| XML serialization mismatch | HIGH — FLExTrans can't read output | Golden file comparison in Phase 4 gate |
| QWebChannel JS bridge differs from WebView2 | MEDIUM — tree clicks don't work | Phase 7A dedicated agent for bridge |
| SIL.LCModel C# dependency | LOW — only used in controller import | Already optional; XML data path works without it |
| PyQt6-WebEngine unavailable on target platform | MEDIUM — no tree visualization | Fallback: QTextBrowser with static HTML |
| DOCTYPE hack position (char 165) mismatch | HIGH — corrupted XML output | Explicit byte-level test in Phase 4 |
| TreeFlex CSS rendering differences | LOW — cosmetic only | Copy CSS as-is, visual inspection |
