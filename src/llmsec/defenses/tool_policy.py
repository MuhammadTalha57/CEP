"""D4: tool policy, a simplified CaMeL-style data-flow rule (design.md §5.1; P08 p1, p4).

P08 lets untrusted data never influence control flow, enforced by an interpreter with provenance tags.
Our lightweight version [OURS, simplified]: arguments of side-effect tools must come from the trusted
user request. send_email recipients and delete_file paths that do not appear in the user's own request
are blocked, so an instruction found in an email or page cannot pick a new recipient or file.
Read-only tools are always allowed.
"""
from __future__ import annotations

import re
from typing import Any

from .base import Defense, Verdict

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


class ToolPolicyMixin:
    def _policy(self, name: str, arguments: dict[str, Any], user_request: str) -> Verdict:
        req = user_request.lower()
        if name == "send_email":
            to = str(arguments.get("to", ""))
            addrs = _EMAIL.findall(to) or [to]
            bad = [a for a in addrs if not a or a.lower() not in req]
            if bad:
                return Verdict(blocked=True, reason=f"recipient not in user request: {bad}")
        elif name == "delete_file":
            path = str(arguments.get("path", ""))
            if not path or path.lower() not in req:
                return Verdict(blocked=True, reason=f"path not in user request: {path}")
        return Verdict()


class D4ToolPolicy(ToolPolicyMixin, Defense):
    name = "d4_toolpolicy"

    def check_tool_call(self, name, arguments, user_request):
        return self._policy(name, arguments, user_request)
