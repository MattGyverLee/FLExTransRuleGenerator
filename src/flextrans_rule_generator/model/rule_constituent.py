from __future__ import annotations
from typing import Optional

class RuleConstituent:
    def __init__(self):
        self.identifier: int = 0
        self.parent: Optional[RuleConstituent] = None

    def produce_span(self, s_class: str, s_type: str) -> str:
        # Generates: <span class="CLASS" id="TYPE.ID" onclick="toApp('TYPE.ID')" oncontextmenu="toApp('TYPE.ID')">
        return (
            f'<span class="{s_class}" id="{s_type}.{self.identifier}"'
            f' onclick={self._produce_to_app(s_type)}'
            f' oncontextmenu={self._produce_to_app(s_type)}">'
        )

    def _produce_to_app(self, s_type: str) -> str:
        return f"\"toApp('{s_type}.{self.identifier}')\""
