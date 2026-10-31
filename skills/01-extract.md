# 01 Extract (one JSON per paper -> data/papers/<id>.json)

Input: PDF at my_papers/<file>. Output: JSON below. Then update data/ledger.csv row and data/verified.json.

```json
{
 "id":"P01","file":"","git_blob":"",
 "meta":{"title":"","authors":[],"year":null,"venue":"","doi":"","pages":null},
 "type":"attack | defense | benchmark | survey | system | other",
 "problem":{"v":"","p":0,"q":""},
 "main_idea":{"v":"","p":0,"q":""},
 "threat_model":{"v":"","p":0,"q":""},
 "injection_types_covered":[{"name":"","p":0,"q":""}],
 "models_tested":[{"name":"","size":"","open_source":null,"p":0}],
 "datasets_benchmarks":[{"name":"","size":"","url":"","p":0}],
 "metrics":[{"name":"","definition":"","p":0}],
 "results":[{"claim":"","number":"","setting":"","p":0,"q":""}],
 "baselines":[],
 "limitations_stated":[{"v":"","p":0,"q":""}],
 "limitations_inferred":["[INFERENCE] ..."],
 "artifacts":[{"kind":"code|data|other","url":"","p":0,"checked":null}],
 "reusable_for_our_project":{"v":"","why":"[INFERENCE]"},
 "confidence":"high|medium|low","flags":[]
}
```
Rules: `NOT FOUND` for absent fields. `q` = verbatim quote (<=15 words) so the user can Ctrl+F it. Report numbers exactly as printed, with units and the setting they apply to.
Artifacts: record URLs only; GitHub stats go in a later step (skills/02).
Dedupe: compare DOI, then normalized title; list suspected duplicates in STATE.md for the user to approve.