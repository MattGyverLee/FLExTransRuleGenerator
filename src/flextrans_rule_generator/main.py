#!/usr/bin/env python3
# Copyright (c) 2023 SIL International
# This software is licensed under the LGPL, version 2.1 or later
# (http://www.gnu.org/licenses/lgpl-2.1.html)

import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="FLExTrans Rule Generator - A tool to help write FLExTrans transfer rules."
    )
    parser.add_argument("rule_file", help="FLExTrans transfer rule file")
    parser.add_argument(
        "flex_data_file",
        help="XML file with source/target categories and features",
    )
    parser.add_argument(
        "test_data_file",
        nargs="?",
        default="",
        help="HTML file with test data to display",
    )
    parser.add_argument(
        "from_lrt",
        nargs="?",
        default="n",
        help="'y' if launched from Live Rule Tester, 'n' otherwise",
    )
    parser.add_argument(
        "lang_code",
        nargs="?",
        default="",
        help="Interface language code",
    )
    parser.add_argument(
        "--max-vars",
        type=int,
        default=4,
        help="Max number of variables to show in values (default: 4)",
    )
    args = parser.parse_args()

    rule_path = Path(args.rule_file)
    flex_data_path = Path(args.flex_data_file)

    if not rule_path.exists():
        print("The rule file could not be found.")
        return 1
    if not flex_data_path.exists():
        print(
            "The XML file with both source and target categories and features could not be found."
        )
        return 1

    from flextrans_rule_generator.service.xml_backend_provider import XmlBackEndProvider
    from flextrans_rule_generator.service.xml_backend_provider_flex_data import (
        XmlBackEndProviderFLExData,
    )

    provider = XmlBackEndProvider()
    provider.load_data_from_file(str(rule_path))

    flex_provider = XmlBackEndProviderFLExData()
    flex_provider.load_data_from_file(str(flex_data_path))

    from PyQt6.QtWidgets import QApplication
    from flextrans_rule_generator.controller.rule_generator_control import (
        RuleGeneratorControl,
    )

    app = QApplication(sys.argv)
    window = RuleGeneratorControl()
    window.max_variables = args.max_vars
    window.rule_generator = provider.rule_generator
    window.provider = provider
    window.rule_file_path = str(rule_path)
    window.flex_data = flex_provider.flex_data
    window.from_lrt = args.from_lrt.lower() == "y"

    # Load test data HTML if provided
    test_data_path = Path(args.test_data_file) if args.test_data_file else None
    if test_data_path and test_data_path.exists():
        window.set_test_data_file(str(test_data_path))

    window.fill_rules_list()
    window.show()
    app.exec()

    # Output result codes to stdout for the calling script
    output_parts = []
    if window.exit_code:
        output_parts.append(window.exit_code)
    if window.request_lrt:
        output_parts.append("LRT")
    if output_parts:
        print(" ".join(output_parts))

    return 0


if __name__ == "__main__":
    sys.exit(main())
