#
#   RuleAssistant
#
#   Ron Lockwood
#   SIL International
#   9/11/23
#
#   Version 4.0.0 - Updated to use the Python/PyQt6 Rule Generator in-process
#   instead of launching the C# exe as a subprocess.
#
#   Version 3.15.1 - 3/6/26 - Ron Lockwood
#    Upgraded to PyQt5 and Python 3.11.
#
#   Runs the Rule Assistant to create Apertium transfer rules.
#

import os
import subprocess
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

# CRITICAL: Set Qt attribute before ANY other imports that might create QCoreApplication
try:
    from PyQt6.QtCore import Qt, QCoreApplication
    from PyQt6.QtWidgets import QApplication
    # Try to set on both - one might work depending on when QApplication was created
    try:
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
    except RuntimeError:
        pass
    try:
        QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
    except RuntimeError:
        pass
except Exception:
    pass

from flextoolslib import *

from PyQt6.QtCore import QUrl

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
TRANSL_TS_NAME = "RuleAssistant"

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
    "RuleAssistant",
    """This module runs a tool which let's you create transfer rules.""",
)
docs = {
    FTM_Name: _translate("RuleAssistant", "Rule Assistant"),
    FTM_Version: "4.0.0",
    FTM_ModifiesDB: False,
    FTM_Synopsis: _translate(
        "RuleAssistant", "Runs a tool for creating transfer rules."
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
    try:
        from flextrans_rule_generator.service.xml_backend_provider import (
            XmlBackEndProvider,
        )
        from flextrans_rule_generator.service.xml_backend_provider_flex_data import (
            XmlBackEndProviderFLExData,
        )
        from flextrans_rule_generator.controller.rule_generator_control import (
            RuleGeneratorControl,
        )

        # Load rule data
        provider = XmlBackEndProvider()
        provider.load_data_from_file(ruleAssistantFile)

        # Load FLEx category/feature data
        flex_provider = XmlBackEndProviderFLExData()
        flex_provider.load_data_from_file(ruleAssistGUIinputfile)

        # Create and configure the GUI window
        window = RuleGeneratorControl()
        window.rule_generator = provider.rule_generator
        window.provider = provider
        window.rule_file_path = ruleAssistantFile
        window.flex_data = flex_provider.flex_data
        window.from_lrt = fromLRT

        # Load test data if available
        if testDataFile and os.path.isfile(testDataFile):
            window.set_test_data_file(testDataFile)

        # Capture results before the window is destroyed
        result_holder = {"exit_code": "", "request_lrt": False}

        def _on_close():
            result_holder["exit_code"] = window.exit_code
            result_holder["request_lrt"] = window.request_lrt

        window.fill_rules_list()

        # Run a local event loop so this function blocks until the window closes.
        from PyQt6.QtCore import QEventLoop

        loop = QEventLoop()
        # Connect close to capture results, then quit the local loop
        original_close = window.closeEvent

        def patched_close(event):
            _on_close()
            original_close(event)
            if event.isAccepted():
                loop.quit()

        window.closeEvent = patched_close
        window.show()
        loop.exec()

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

    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

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
    saved, rule, lrt = StartRuleAssistant(
        report, ruleAssistantFile, ruleAssistGUIinputfile, testData, fromLRT=fromLRT
    )

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
