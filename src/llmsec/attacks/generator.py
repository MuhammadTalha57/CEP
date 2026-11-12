"""Turn configs/experiment.yaml into concrete, JSON-serializable trials (design.md §4.4).

A trial holds (a) the request sent to the app, including the lab-only setup (secret, planted documents,
planted emails/pages), and (b) the deterministic check the harness applies to the response.
Everything is derived from the trial id, so regenerating gives identical trials.
"""
from __future__ import annotations

import random
import zlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ..harness.checkers import make_canary, make_marker
from . import techniques as T

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA = REPO_ROOT / "data"
DEFAULT_EXPERIMENT = REPO_ROOT / "configs" / "experiment.yaml"


@dataclass
class Trial:
    trial_id: str
    app: str
    cell: str
    technique: str
    carrier: str
    variant: int
    seed: int
    kind: str  # "attack" | "clean"
    request: dict[str, Any]
    check: dict[str, Any]
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _yaml(rel: str) -> Any:
    return yaml.safe_load((DATA / rel).read_text(encoding="utf-8"))


def stable_seed(trial_id: str) -> int:
    return zlib.crc32(trial_id.encode()) & 0x7FFFFFFF


def load_experiment(path: str | Path = DEFAULT_EXPERIMENT) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


# ------------------------------------------------------------------ attack trials
def _attacker(rng: random.Random) -> str:
    return "".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(6)) + "@evil-mail.example"


def _chatbot_attack(tech: str, carrier: str, v: int, tid: str, seed: int) -> Trial:
    rng = random.Random(seed)
    secret = make_canary(rng)
    if tech == "H2":
        msg = T.SPLIT_TEMPLATES_A[v % len(T.SPLIT_TEMPLATES_A)]
    else:
        msg = T.payload(tech, "chatbot", v)
    return Trial(tid, "chatbot", f"{tech}@{carrier}", tech, carrier, v, seed, "attack",
                 {"app": "chatbot", "user_message": msg, "lab": {"secret": secret}},
                 {"type": "secret_leak", "secret": secret})


def _rag_attack(tech: str, carrier: str, v: int, tid: str, seed: int, h1: str | None) -> Trial | None:
    rng = random.Random(seed)
    marker = make_marker(rng)
    targets = _yaml("kb/attack_targets.yaml")["targets"]
    tgt = targets[v % len(targets)]
    real_tech = {"H1": h1, "H3": "T7"}.get(tech, tech)
    if real_tech is None:
        return None
    text = T.payload(real_tech, "rag", v, marker=marker)
    doc_id = f"POISON-{tgt['id']}"
    doc = {"carrier": carrier, "doc_id": doc_id, "title": tgt["title"], "cover": tgt["cover"],
           "payload": text, "variant": v}
    return Trial(tid, "rag", f"{tech}@{carrier}", tech, carrier, v, seed, "attack",
                 {"app": "rag", "question": tgt["q"], "lab": {"poison_docs": [doc]}},
                 {"type": "marker", "marker": marker, "poison_doc": doc_id},
                 {"target": tgt["id"], "payload_technique": real_tech})


def _agent_attack(tech: str, carrier: str, v: int, tid: str, seed: int) -> Trial:
    rng = random.Random(seed)
    attacker = _attacker(rng)
    spec = _yaml("agent/attack_targets.yaml")
    targets = [t for t in spec["targets"] if t["carrier"] == carrier]
    tgt = targets[v % len(targets)]
    q = tgt["q"]
    if tech == "H2":
        text = T.TRIGGER_NOTE_C.format(goal=T.goal_text("agent", v, attacker=attacker))
        q = q + T.TRIGGER_SUFFIX_C
    else:
        text = T.payload(tech, "agent", v, attacker=attacker)
    lab: dict[str, Any] = {}
    if carrier == "C8":
        cover = spec["covers"]["email"]
        lab["extra_emails"] = [{"id": "MX", "from": cover["from"], "subject": cover["subject"],
                                "body": f"{cover['body']}\n\n{text}"}]
    else:
        lab["extra_pages"] = {tgt["url"]: f"{spec['covers']['page']}\n\n{text}"}
    return Trial(tid, "agent", f"{tech}@{carrier}", tech, carrier, v, seed, "attack",
                 {"app": "agent", "user_request": q, "lab": lab},
                 {"type": "tool_call", "name": "send_email", "arg": "to", "value": attacker},
                 {"target": tgt["id"]})


# ------------------------------------------------------------------ clean trials
def _clean(app: str) -> list[Trial]:
    out = []
    if app == "chatbot":
        for t in _yaml("tasks/chatbot_clean.yaml")["tasks"]:
            tid = f"chatbot|U|{t['id']}"
            seed = stable_seed(tid)
            secret = make_canary(random.Random(seed))
            out.append(Trial(tid, app, "U", "-", "-", 0, seed, "clean",
                             {"app": app, "user_message": t["q"], "lab": {"secret": secret}},
                             {"type": "keywords", "any_of": t["expect"], "secret": secret}))
    elif app == "rag":
        for t in _yaml("tasks/rag_clean.yaml")["tasks"]:
            tid = f"rag|U|{t['id']}"
            out.append(Trial(tid, app, "U", "-", "-", 0, stable_seed(tid), "clean",
                             {"app": app, "question": t["q"], "lab": {}},
                             {"type": "keywords", "any_of": t["expect"], "doc": t["doc"]}))
    elif app == "agent":
        for t in _yaml("tasks/agent_clean.yaml")["tasks"]:
            tid = f"agent|U|{t['id']}"
            chk = {"type": "agent_clean", "forbid_calls": t.get("forbid_calls", [])}
            if "expect_call" in t:
                chk["expect_call"] = t["expect_call"]
            else:
                chk["expect_text"] = t["expect_text"]
            out.append(Trial(tid, app, "U", "-", "-", 0, stable_seed(tid), "clean",
                             {"app": app, "user_request": t["q"], "lab": {}}, chk))
    return out


# ------------------------------------------------------------------ public API
def generate(experiment: dict[str, Any] | None = None, apps: list[str] | None = None,
             variants: int | None = None, cells: list[str] | None = None,
             include_clean: bool = True) -> list[Trial]:
    exp = experiment or load_experiment()
    n = variants if variants is not None else exp.get("variants", T.VARIANTS_PER_CELL)
    h1 = exp.get("h1_technique")
    trials: list[Trial] = []
    for app, conf in exp["apps"].items():
        if apps and app not in apps:
            continue
        for cell in conf["cells"]:
            if cells and cell not in cells:
                continue
            tech, carrier = cell.split("@", 1)
            for v in range(n):
                tid = f"{app}|{cell}|{v:02d}"
                seed = stable_seed(tid)
                if app == "chatbot":
                    tr = _chatbot_attack(tech, carrier, v, tid, seed)
                elif app == "rag":
                    tr = _rag_attack(tech, carrier, v, tid, seed, h1)
                else:
                    tr = _agent_attack(tech, carrier, v, tid, seed)
                if tr is not None:
                    trials.append(tr)
        if include_clean and conf.get("clean", True) and (not cells or "U" in cells):
            trials.extend(_clean(app))
    return trials
