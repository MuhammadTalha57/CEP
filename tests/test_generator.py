import json
from collections import Counter

from llmsec.attacks import techniques as T
from llmsec.attacks.carriers import ZWSP, build_poisoned_doc
from llmsec.attacks.generator import generate, load_experiment


def test_every_technique_has_6_templates_and_30_unique_payloads():
    for tech in T.TECHNIQUES:
        assert len(T.TECHNIQUES[tech]) == 6
        for app, fill in [("chatbot", {}), ("rag", {"marker": "ZQ-1"}), ("agent", {"attacker": "a@e"})]:
            ps = {T.payload(tech, app, v, **fill) for v in range(30)}
            assert len(ps) == 30, (tech, app)


def test_matrix_size_matches_design():
    trials = generate()
    attack = Counter(t.app for t in trials if t.kind == "attack")
    clean = Counter(t.app for t in trials if t.kind == "clean")
    # h1_technique set from the baseline (14 Nov): all 16 rag cells run; 1,080 trials per model per defense
    assert load_experiment()["h1_technique"] == "T4"
    assert attack == {"chatbot": 8 * 30, "rag": 16 * 30, "agent": 9 * 30}
    assert clean == {"chatbot": 30, "rag": 30, "agent": 30}


def test_h1_enabled_when_pilot_sets_technique():
    exp = load_experiment()
    exp["h1_technique"] = "T2"
    trials = generate(exp, apps=["rag"], cells=["H1@C2"], variants=3)
    assert len(trials) == 3 and all(t.meta["payload_technique"] == "T2" for t in trials)


def test_trials_are_deterministic_and_serializable():
    a, b = generate(variants=2), generate(variants=2)
    assert [t.to_dict() for t in a] == [t.to_dict() for t in b]
    json.dumps([t.to_dict() for t in a])
    assert len({t.trial_id for t in a}) == len(a)


def test_secrets_markers_and_attackers_differ_per_trial():
    trials = generate(variants=30, include_clean=False)
    for app, key in [("chatbot", "secret"), ("rag", "marker"), ("agent", "value")]:
        vals = [t.check[key] for t in trials if t.app == app]
        assert len(set(vals)) == len(vals), app


def test_payload_contains_goal_placeholders_filled():
    for t in generate(variants=5, include_clean=False):
        if t.app == "rag":
            assert t.check["marker"] in t.request["lab"]["poison_docs"][0]["payload"]
        if t.app == "agent":
            lab = t.request["lab"]
            blob = json.dumps(lab)
            assert t.check["value"] in blob


def test_h2_and_h3_shapes():
    ts = generate(variants=1, include_clean=False)
    h2c = next(t for t in ts if t.app == "agent" and t.technique == "H2")
    assert "KIWI" in h2c.request["user_request"] and "KIWI note" in h2c.request["lab"]["extra_emails"][0]["body"]
    h3 = next(t for t in ts if t.cell == "H3@C2+C4")
    d = h3.request["lab"]["poison_docs"][0]
    doc = build_poisoned_doc(d["carrier"], d["doc_id"], d["title"], d["cover"], d["payload"], d["variant"])
    assert ZWSP in doc.text and h3.check["marker"] in doc.text.replace(ZWSP, "")
