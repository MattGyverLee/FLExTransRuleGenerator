from flextrans_rule_generator.model.rule import FLExTransRule
from flextrans_rule_generator.model.phrase import Phrase
from flextrans_rule_generator.service.rule_identifier_setter import RuleIdentifierAndParentSetter


class WebPageProducer:
    def __init__(self):
        self._setter = RuleIdentifierAndParentSetter()

    def produce_web_page(self, rule: FLExTransRule) -> str:
        self._setter.set_identifiers_and_parents(rule)
        parts = []
        parts.append(self._html_beginning(rule))
        parts.append(self._html_body(rule))
        parts.append(self._html_ending())
        return "".join(parts)

    def _html_beginning(self, rule: FLExTransRule) -> str:
        parts = []
        parts.append(
            '<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
        )
        parts.append('<html xmlns="http://www.w3.org/1999/xhtml">\n')
        parts.append(f"<head><title>{rule.name}</title>\n")
        parts.append('<meta charset="utf-8"/>\n')
        parts.append(
            '<link rel="stylesheet" href="treeflex.css"/>\n'
        )
        parts.append('<link rel="stylesheet" href="rulegen.css"/>\n')
        parts.append("<script>\n")
        parts.append(self._javascript_contents())
        parts.append("</script>\n")
        parts.append("</head>\n")
        return "".join(parts)

    def _javascript_contents(self) -> str:
        return (
            "function toApp(msg) {\n"
            "window.chrome.webview.postMessage(msg);\n"
            "return false;\n"
            "}\n"
        )

    def _html_body(self, rule: FLExTransRule) -> str:
        parts = []
        parts.append("<body>\n")
        parts.append("<table>\n")
        parts.append("<tr>\n")
        parts.append(self._phrase_html(rule.source.phrase))
        parts.append("<td>\n")
        parts.append('<span class="arrow"/>\n')
        parts.append("</td>\n")
        parts.append(self._phrase_html(rule.target.phrase))
        parts.append("</tr>\n")
        parts.append("</table>\n")
        return "".join(parts)

    def _phrase_html(self, phrase: Phrase) -> str:
        parts = []
        parts.append('<td valign="top">\n')
        parts.append('<div class="tf-tree tf-gap-sm">\n')
        parts.append("<ul>\n")
        parts.append(phrase.produce_html())
        parts.append("</ul>\n")
        parts.append("</div>\n")
        parts.append("</td>\n")
        return "".join(parts)

    def _html_ending(self) -> str:
        return "</body>\n</html>\n"
