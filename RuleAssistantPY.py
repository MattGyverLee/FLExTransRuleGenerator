#
#   RuleAssistantPY
#
#   Ron Lockwood
#   SIL International
#   9/11/23
#
#   Version 4.0.0 - Updated to use the Python/PyQt6 Rule Generator in-process
#   instead of launching the C# exe as a subprocess.
#
#   Version 3.15.1 - 3/6/26 - Ron Lockwood
#    Upgraded to PyQt6 and Python 3.13.
#
#   Version 3.15 - 2/6/26 - Ron Lockwood
#    Bumped to 3.15.
#
#   Version 3.14.5 - 11/28/25 - Ron Lockwood
#    Fixed #1062. When generating test data, if there is no compiled bilingual dictionary,
#    compile it.
#
#   Version 3.14.4 - 10/10/25 - Ron Lockwood
#    Better error messages when the Rule Assistant returns an error.
#
#   Version 3.14.3 - 8/19/25 - Ron Lockwood
#    Fixes #1045. When creating a test data file that has an error message. Create it as utf-8
#    because the error message may contain non-ASCII characters when translated.
#
#   Version 3.14.2 - 8/13/25 - Ron Lockwood
#    Translate module name.
#
#   Version 3.14.1 - 7/28/25 - Ron Lockwood
#    Reference module names by docs variable.
#
#   Version 3.14 - 5/21/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.1 - 3/24/25 - Ron Lockwood
#    Reorganized to thin out Utils code.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.1 - 1/6/25 - Ron Lockwood
#    Fixes #835. Don't crash when Apertium data is missing as Rule Assistant test data. Just don't show test data.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.3 - 10/9/24 - Ron Lockwood
#    Handle fixed up category names.
#
#   Version 3.11.2 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11.1 - 6/21/24 - Ron Lockwood
#    Use Setting for location and name of the Rule Assistant rules file.
#
#   Version 3.11 - 5/14/24 - Ron Lockwood
#    Connect to the now functioning CreateRules routine.
#    Rearrange the logic for the return code from the GUI program. Pretty print the GUIinput xml.
#
#   2023 version history removed
#
#   Runs the Rule Assistant to create Apertium transfer rules.
#

import sys
import os
import subprocess
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
import traceback

from PyQt6.QtCore import QCoreApplication, Qt, QUrl
from PyQt6.QtWidgets import QApplication

# *** CRITICAL: Set Qt.AA_ShareOpenGLContexts BEFORE any WebEngine import ***
# This MUST happen before ANY attempt to import QtWebEngineWidgets
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)

# Set up debug logging
_debug_log = open(os.path.join(os.path.expanduser("~"), "RuleAssistantPY_debug.log"), "w", buffering=1)

# DIAGNOSTICS: Log Python executable and paths
_diag_log = os.path.join(os.path.expanduser("~"), "RuleAssistantPY_diagnostics.log")
with open(_diag_log, "w") as f:
    f.write(f"Python executable: {sys.executable}\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"sys.path:\n")
    for p in sys.path:
        f.write(f"  {p}\n")
    # Check which PyQt6 is being used
    import PyQt6
    f.write(f"PyQt6 location: {PyQt6.__file__}\n")
try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        f.write(f"QtWebEngineWidgets: AVAILABLE\n")
    except:
        f.write(f"QtWebEngineWidgets: NOT AVAILABLE\n")

# CRITICAL: Import QtWebEngineWidgets BEFORE flextoolslib to avoid interference
import sys as _sys
_webengine_imports = {}
_webengine_log = os.path.expanduser(r"~\RuleAssistantWebEngineDebug.log")

def _cache_log(msg):
    try:
        with open(_webengine_log, 'a') as f:
            f.write(msg + '\n')
    except:
        pass

_cache_log("=== RuleAssistantPY.py: Creating WebEngine cache ===")
_cache_log(f"sys.path[0]: {sys.path[0] if sys.path else 'EMPTY'}")

    try:
    _cache_log("Attempting: from PyQt6.QtWebEngineWidgets import QWebEngineView")
    from PyQt6.QtWebEngineWidgets import QWebEngineView as _QWE
    _cache_log("Success: QWebEngineView imported")

    _cache_log("Attempting: from PyQt6.QtWebChannel import QWebChannel")
    from PyQt6.QtWebChannel import QWebChannel as _QWC
    _cache_log("Success: QWebChannel imported")

    _webengine_imports['QWebEngineView'] = _QWE
    _webengine_imports['QWebChannel'] = _QWC
    _sys.modules['__webengine_cache__'] = _webengine_imports
    _cache_log("SUCCESS: WebEngine cache created and stored in sys.modules['__webengine_cache__']")
    print(f"[DEBUG] WebEngine cache created before flextoolslib", file=_debug_log, flush=True)
except ImportError as _e:
    _cache_log(f"ImportError creating cache: {_e}")
    import traceback as _tb
    _cache_log(_tb.format_exc())
    print(f"[DEBUG] WebEngine cache creation failed: {_e}", file=_debug_log, flush=True)
except Exception as _e:
    _cache_log(f"Exception creating cache: {type(_e).__name__}: {_e}")
    import traceback as _tb
    _cache_log(_tb.format_exc())
    print(f"[DEBUG] WebEngine cache creation failed: {_e}", file=_debug_log, flush=True)

_cache_log("Before flextoolslib import")
_cache_log(f"Cache in sys.modules: {bool(sys.modules.get('__webengine_cache__'))}")
_cache_log(f"Cache content: {sys.modules.get('__webengine_cache__', {}).keys()}")

from flextoolslib import *

_cache_log("After flextoolslib import")
_cache_log(f"Cache in sys.modules: {bool(sys.modules.get('__webengine_cache__'))}")
_cache_log(f"Cache content: {sys.modules.get('__webengine_cache__', {}).keys()}")

import Mixpanel
import InterlinData
import Utils
import ReadConfig
import CreateApertiumRules
import FTPaths
from RunApertium import docs as RunApertDocs

from SIL.LCModel import (  # type: ignore
    IFsClosedFeatureRepository,
    ITextRepository,
)

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = "RuleAssistantPY"

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = [
    "ReadConfig",
    "Utils",
    "Mixpanel",
    "CreateApertiumRules",
    "TextClasses",
    "InterlinData",
]

# ----------------------------------------------------------------
# Documentation that the user sees:
descr = _translate(
    "RuleAssistantPY",
    """This module runs a tool which let's you create transfer rules.""",
)
docs = {
    FTM_Name: _translate("RuleAssistantPY", "Rule AssistantPY"),
    FTM_Version: "4.0.0",
    FTM_ModifiesDB: False,
    FTM_Synopsis: _translate(
        "RuleAssistantPY", "Runs a tool for creating transfer rules."
    ),
    FTM_Help: "",
    FTM_Description: descr,
}

# Element names in the rule assistant gui input file
FLEXDATA = "FLExData"
SOURCEDATA = "SourceData"
TARGETDATA = "TargetData"
CATEGORIES = "Categories"
FLEXCATEGORY = "FLExCategory"
FEATURES = "Features"
FLEXFEATURE = "FLExFeature"
VALUES = "Values"
FLEXFEATUREVALUE = "FLExFeatureValue"

# Attribute names in the rule assistant gui input file
NAME = "name"
ABBREV = "abbr"


@dataclass
class DBStartData:

    projectName: str
    categoryList: list
    featureList: list
    categoryFeatures: dict

    def toXml(self, root, tag):

        parent = ET.SubElement(root, tag, {NAME: self.projectName})

        catsEl = ET.SubElement(parent, CATEGORIES)

        for cat in self.categoryList:

            elem = ET.SubElement(catsEl, FLEXCATEGORY, {ABBREV: cat})
            dct = self.categoryFeatures.get(cat)

            if not dct:
                continue

            group = ET.SubElement(elem, "ValidFeatures")

            for feat, types in sorted(dct.items()):

                ET.SubElement(
                    group, "ValidFeature", name=feat, type="|".join(sorted(types))
                )

        if not self.featureList:
            return

        featsEl = ET.SubElement(parent, FEATURES)

        for name, values in self.featureList:

            featEl = ET.SubElement(featsEl, FLEXFEATURE, {NAME: name})
            group = ET.SubElement(featEl, VALUES)

            for val in values:

                ET.SubElement(group, FLEXFEATUREVALUE, {ABBREV: val})


@dataclass
class StartData:

    src: DBStartData
    tgt: DBStartData

    def write(self, fileName):

        root = ET.Element(FLEXDATA)
        self.src.toXml(root, SOURCEDATA)
        self.tgt.toXml(root, TARGETDATA)

        tree = ET.ElementTree(root)
        ET.indent(tree)
        tree.write(fileName, encoding="utf-8", xml_declaration=True)


def getFeatureData(DB):

    myFeatureList = []

    for feature in DB.ObjectsIn(IFsClosedFeatureRepository):

        featName = Utils.as_string(feature.Name)
        featValueList = sorted([Utils.as_tag(val) for val in feature.ValuesOC])
        myFeatureList.append((featName, featValueList))

    myFeatureList.sort()
    return myFeatureList


def GetStartData(report, DB, configMap):

    posMap = {}

    Utils.get_categories(
        DB,
        report,
        posMap,
        TargetDB=None,
        numCatErrorsToShow=1,
        addInflectionClasses=False,
    )
    catList = sorted(posMap.keys())

    featureList = getFeatureData(DB)

    inflFeatures = Utils.getAllInflectableFeatures(DB)
    stemFeatures = Utils.getAllStemFeatures(DB, report, configMap)

    catFeatures = {}

    for pos in DB.lp.AllPartsOfSpeech:

        flexCat = Utils.as_string(pos.Abbreviation)
        cat = Utils.convertProblemChars(flexCat, Utils.catProbData)
        catFeatures[cat] = {feat: {"stem"} for feat in stemFeatures[flexCat]}
        templates = Utils.getAffixTemplates(DB, flexCat)

        for tmpl in templates:

            for feat, side in tmpl:

                if feat not in catFeatures[cat]:

                    catFeatures[cat][feat] = set()

                catFeatures[cat][feat].add(side)

        for feat in inflFeatures[flexCat]:

            if feat not in catFeatures[cat]:

                catFeatures[cat][feat] = set()

            catFeatures[cat][feat].add("prefix")
            catFeatures[cat][feat].add("suffix")

    return DBStartData(DB.ProjectName(), catList, featureList, catFeatures)


def GetRuleAssistantStartData(report, DB, TargetDB, configMap):

    return StartData(
        GetStartData(report, DB, configMap), GetStartData(report, TargetDB, configMap)
    )


def ProcessLine(line):

    readings = []
    loc = "blank"
    esc = False
    cur_reading = []
    cur_string = ""

    for c in line:

        if esc:

            esc = False

            if loc != "blank":

                cur_string += c

        elif c == "\\":

            esc = True

        elif loc == "blank" and c == "^" and not esc:

            loc = "lu"

        elif loc == "lu" and c == "$" and not esc:

            loc = "blank"
            cur_reading.append(cur_string)
            cur_string = ""
            readings.append(cur_reading)
            cur_reading = []

            if len(readings) >= 2:

                yield (
                    [p for p in readings[0] if p],
                    [p for p in readings[1] if p],
                )
            readings = []

        elif loc == "lu" and c == "/" and not esc:

            cur_reading.append(cur_string)
            cur_string = ""
            readings.append(cur_reading)
            cur_reading = []

        elif loc == "lu":

            if c == "<":

                loc = "tag"
                cur_reading.append(cur_string)
                cur_string = ""
            else:
                cur_string += c

        elif loc == "tag":

            if c == ">":

                loc = "lu"
                cur_reading.append(cur_string)
                cur_string = ""
            else:
                cur_string += c


readingNumberRegex = re.compile(r"(\d+\.\d+)$")


def ReadingToHTML(reading):

    pieces = [
        readingNumberRegex.sub(r'<span class="num">\1</span>', reading[0]),
        '<span class="pos">' + reading[1] + "</span>",
    ] + ['<span class="tag">' + tag + "</span>" for tag in reading[2:]]

    return '<span class="lu">' + "".join(pieces) + "</span>"


def GenerateTestDataFile(report, DB, configMap, fhtml):

    sourceText = ReadConfig.getConfigVal(
        configMap, ReadConfig.SOURCE_TEXT_NAME, report
    )
    bidixDix = ReadConfig.getConfigVal(
        configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report
    )
    bidixBin = os.path.join(FTPaths.BUILD_DIR, "bilingual.bin")

    if not (sourceText or bidixDix):
        return False

    if not os.path.isfile(bidixDix):

        report.Warning(
            _translate(
                "RuleAssistant",
                "Bilingual dictionary not found. Build the bilingual dictionary to see test data in the {ruleAssistant}.",
            ).format(ruleAssistant=docs[FTM_Name])
        )
        return False

    content = None

    for text in DB.ObjectsIn(ITextRepository):

        if Utils.as_string(text.Name).strip() == sourceText:

            content = text.ContentsOA
            break
    else:
        report.Error(
            _translate("RuleAssistant", "The text named '%s' was not found.")
            % sourceText
        )
        return False

    params = InterlinData.initInterlinParams(configMap, report, content)

    if params is None:
        return False

    text = InterlinData.getInterlinData(DB, report, params)

    fsrc = os.path.join(
        FTPaths.BUILD_DIR, Utils.RULE_ASSISTANT_SOURCE_TEST_DATA_FILE
    )

    with open(fsrc, "w", encoding="utf-8") as fout:
        text.write(fout)

    # Compile the bilingual dictionary
    subprocess.run(
        [os.path.join(FTPaths.TOOLS_DIR, "lt-comp.exe"), "lr", bidixDix, bidixBin],
        capture_output=True,
    )

    if not os.path.isfile(bidixBin):

        report.Warning(
            _translate(
                "RuleAssistant",
                "Compiled bilingual dictionary not found. There was an error compiling the bilingual dictionary.",
            )
        )
        return False

    ftgt = os.path.join(
        FTPaths.BUILD_DIR, Utils.RULE_ASSISTANT_TARGET_TEST_DATA_FILE
    )
    subprocess.run(
        [
            os.path.join(FTPaths.TOOLS_DIR, "lt-proc.exe"),
            "-b",
            bidixBin,
            fsrc,
            ftgt,
        ],
        capture_output=True,
    )

    try:
        with open(ftgt, encoding="utf-8") as fin, open(
            fhtml, "w", encoding="utf-8"
        ) as fout:

            fout.write(
                """<html><head><style>
.lu { margin-left: 5px; font-size: 75%; }
.pos { color: blue; margin-left: 5px; }
.tag { color: green; margin-left: 5px; }
.num { vertical-align: sub; font-size: 50%; }
</style></head><body>
"""
            )
            fout.write(
                _translate("RuleAssistant", "<p><b>Source Text:</b> ")
                + sourceText
                + "</p>\n"
            )
            line_count = 0

            for line in fin:

                if not line.strip():
                    continue

                srcLine = ""
                tgtLine = ""

                for src, tgt in ProcessLine(line):

                    if len(src) > 1 and len(tgt) > 1:

                        srcLine += ReadingToHTML(src)
                        tgtLine += ReadingToHTML(tgt)

                fout.write(f"<p>{srcLine} → {tgtLine}</p>\n")
                line_count += 1

                if line_count >= 30:
                    break

            fout.write("</body></html>\n")

    except Exception:
        return False

    return True


def GetTestDataFile(report, DB, configMap):

    fhtml = os.path.join(
        FTPaths.BUILD_DIR, Utils.RULE_ASSISTANT_DISPLAY_DATA_FILE
    )

    if not GenerateTestDataFile(report, DB, configMap, fhtml):

        with open(fhtml, "w", encoding="utf-8") as fout:

            fout.write(
                _translate(
                    "RuleAssistant",
                    "<html><body><p>No test data available.</body></html>\n",
                )
            )

    return fhtml


def StartRuleAssistant(report, ruleAssistantFile, ruleAssistGUIinputfile,
                       testDataFile, fromLRT=False):
    """Launch the Rule Generator GUI in-process using the Python/PyQt6 version.

    Returns (saved, rule_index_or_None, request_lrt).
    """
    print(f"[DEBUG] StartRuleAssistant called", file=_debug_log, flush=True)
    try:
        print(f"[DEBUG] Importing rule generator modules...", file=_debug_log, flush=True)
        from flextrans_rule_generator.service.xml_backend_provider import (
            XmlBackEndProvider,
        )
        from flextrans_rule_generator.service.xml_backend_provider_flex_data import (
            XmlBackEndProviderFLExData,
        )
        print(f"[DEBUG] About to import RuleGeneratorControl...", file=_debug_log, flush=True)
        from flextrans_rule_generator.controller.rule_generator_control import (
            RuleGeneratorControl,
            WEBENGINE_AVAILABLE,
        )
        import flextrans_rule_generator.controller.rule_generator_control as rgc_module
        print(f"[DEBUG] rule_generator_control module location: {rgc_module.__file__}", file=_debug_log, flush=True)
        print(f"[DEBUG] Rule generator modules imported successfully", file=_debug_log, flush=True)
        print(f"[DEBUG] WEBENGINE_AVAILABLE = {WEBENGINE_AVAILABLE}", file=_debug_log, flush=True)
        # Try to get diagnostic status if available
        _import_status = getattr(rgc_module, '_WEBENGINE_IMPORT_STATUS', 'unknown')
        print(f"[DEBUG] WEBENGINE_IMPORT_STATUS = {_import_status}", file=_debug_log, flush=True)

        # Load rule data
        print(f"[DEBUG] Loading rule data from {ruleAssistantFile}", file=_debug_log, flush=True)
        provider = XmlBackEndProvider()
        provider.load_data_from_file(ruleAssistantFile)
        print(f"[DEBUG] Rule data loaded", file=_debug_log, flush=True)

        # Load FLEx category/feature data
        print(f"[DEBUG] Loading FLEx data from {ruleAssistGUIinputfile}", file=_debug_log, flush=True)
        flex_provider = XmlBackEndProviderFLExData()
        flex_provider.load_data_from_file(ruleAssistGUIinputfile)
        print(f"[DEBUG] FLEx data loaded", file=_debug_log, flush=True)

        # Create and configure the GUI window
        print(f"[DEBUG] Creating RuleGeneratorControl window...", file=_debug_log, flush=True)
        window = RuleGeneratorControl()
        print(f"[DEBUG] Window created, configuring...", file=_debug_log, flush=True)
        window.rule_generator = provider.rule_generator
        window.provider = provider
        window.rule_file_path = ruleAssistantFile
        window.flex_data = flex_provider.flex_data
        window.from_lrt = fromLRT
        # Set interface language code to match FlexTools
        try:
            window.interface_lang_code = Utils.getInterfaceLangCode()
            print(f"[DEBUG] Interface language code set: {window.interface_lang_code}", file=_debug_log, flush=True)
        except AttributeError:
            # If window doesn't support interface_lang_code, that's ok - it will use system default
            print(f"[DEBUG] Window does not have interface_lang_code attribute, using default", file=_debug_log, flush=True)
        print(f"[DEBUG] Window configured", file=_debug_log, flush=True)

        # Load test data if available
        if testDataFile and os.path.isfile(testDataFile):
            print(f"[DEBUG] Loading test data from {testDataFile}", file=_debug_log, flush=True)
            window.set_test_data_file(testDataFile)
            print(f"[DEBUG] Test data loaded", file=_debug_log, flush=True)

        # Capture results before the window is destroyed
        result_holder = {"exit_code": "", "request_lrt": False}

        def _on_close():
            result_holder["exit_code"] = window.exit_code
            result_holder["request_lrt"] = window.request_lrt

        print(f"[DEBUG] Filling rules list...", file=_debug_log, flush=True)
        window.fill_rules_list()
        print(f"[DEBUG] Rules list filled", file=_debug_log, flush=True)

        # Run a local event loop so this function blocks until the window closes.
        print(f"[DEBUG] Setting up event loop...", file=_debug_log, flush=True)
        from PyQt6.QtCore import QEventLoop

        loop = QEventLoop()
        # Connect close to capture results, then quit the local loop
        original_close = window.closeEvent

        def patched_close(event):
            print(f"[DEBUG] Window close event triggered", file=_debug_log, flush=True)
            _on_close()
            original_close(event)
            if event.isAccepted():
                loop.quit()

        window.closeEvent = patched_close
        print(f"[DEBUG] Showing window...", file=_debug_log, flush=True)
        window.show()
        print(f"[DEBUG] Window shown, entering event loop...", file=_debug_log, flush=True)
        loop.exec()
        print(f"[DEBUG] Event loop exited", file=_debug_log, flush=True)

        # Read captured results
        lrt = (not fromLRT) and result_holder["request_lrt"]
        exit_code = result_holder["exit_code"]

        if not exit_code:
            return (False, None, lrt)

        parts = exit_code.split()

        if parts[0] == "1" and len(parts) > 1:
            return (True, int(parts[1]), lrt)  # create single rule
        elif parts[0] == "2":
            return (True, None, lrt)  # create all rules
        else:
            return (False, None, lrt)

    except Exception as e:
        print(f"[ERROR] Exception in StartRuleAssistant: {str(e)}", file=_debug_log, flush=True)
        traceback.print_exc(file=_debug_log)
        _debug_log.flush()
        report.Error(
            _translate(
                "RuleAssistant",
                "An error happened when running the {ruleAssistant} tool: {error}",
            ).format(error=str(e), ruleAssistant=docs[FTM_Name])
        )
        return (False, None, False)


# ----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True, fromLRT=False):
    print(f"[DEBUG] MainFunction called", file=_debug_log, flush=True)

    translators = []
    app = QApplication.instance()

    if app is None:
        print(f"[DEBUG] Creating new QApplication instance", file=_debug_log, flush=True)
        app = QApplication([])
    print(f"[DEBUG] QApplication ready", file=_debug_log, flush=True)

    Utils.loadTranslations(
        librariesToTranslate + [TRANSL_TS_NAME], translators, loadBase=True
    )

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Get the path to the rule assistant rules file
    ruleAssistantFile = ReadConfig.getConfigVal(
        configMap, ReadConfig.RULE_ASSISTANT_FILE, report, giveError=False
    )

    if not ruleAssistantFile:

        buildFolder = FTPaths.BUILD_DIR
        ruleAssistantFile = os.path.join(buildFolder, "RuleAssistantRules.xml")

    # Get the path to the transfer rules file
    tranferRulePath = ReadConfig.getConfigVal(
        configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=False
    )

    if not tranferRulePath:
        return

    TargetDB = Utils.openTargetProject(configMap, report)

    # Get the FLEx info. for source & target projects that the Rule Assistant needs
    startData = GetRuleAssistantStartData(report, DB, TargetDB, configMap)

    # Write the data to an XML file
    ruleAssistGUIinputfile = os.path.join(
        FTPaths.BUILD_DIR, Utils.RA_GUI_INPUT_FILE
    )
    startData.write(ruleAssistGUIinputfile)

    testData = GetTestDataFile(report, DB, configMap)

    # Start the Rule Assistant GUI (now runs in-process via PyQt6)
    print(f"[DEBUG] About to call StartRuleAssistant", file=_debug_log, flush=True)
    print(f"[DEBUG]   ruleAssistantFile: {ruleAssistantFile}", file=_debug_log, flush=True)
    print(f"[DEBUG]   ruleAssistGUIinputfile: {ruleAssistGUIinputfile}", file=_debug_log, flush=True)
    print(f"[DEBUG]   testData: {testData}", file=_debug_log, flush=True)

    # TEST: Check WebEngine availability BEFORE importing rule_generator_control
    print(f"[DEBUG] PRE-IMPORT TEST: Checking QtWebEngineWidgets...", file=_debug_log, flush=True)
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView as TestQWebEngineView
        print(f"[DEBUG] PRE-IMPORT TEST: QtWebEngineWidgets import SUCCEEDED", file=_debug_log, flush=True)
    except Exception as e:
        print(f"[DEBUG] PRE-IMPORT TEST: QtWebEngineWidgets import FAILED: {type(e).__name__}: {str(e)}", file=_debug_log, flush=True)
    saved, rule, lrt = StartRuleAssistant(
        report, ruleAssistantFile, ruleAssistGUIinputfile, testData, fromLRT=fromLRT
    )
    print(f"[DEBUG] StartRuleAssistant returned: saved={saved}, rule={rule}, lrt={lrt}", file=_debug_log, flush=True)

    ruleCount = None

    if saved:
        ruleCount = CreateApertiumRules.CreateRules(
            DB, TargetDB, report, configMap, ruleAssistantFile, tranferRulePath, rule
        )
    else:
        report.Info(_translate("RuleAssistant", "No rules created."))

    if lrt:
        from LiveRuleTesterTool import MainFunction as LRT

        LRT(DB, report, modify, ruleCount=ruleCount)

    return ruleCount


# ----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction, docs=docs)

# ----------------------------------------------------------------
if __name__ == "__main__":
    FlexToolsModule.Help()
