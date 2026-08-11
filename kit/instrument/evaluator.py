import hashlib
import json
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError as e:
    raise SystemExit(
        "run_negative_tests requires the 'jsonschema' package for receipt schema validation: "
        "pip install -r requirements.txt"
    ) from e

ROOT = Path(__file__).parent
CATALOG = json.loads((ROOT / "question-catalog.json").read_text())
PATHS = tuple(q["input_path"] for q in CATALOG["questions"])
OUTPUTS = (
    "O01_agent_decision",
    "O02_outcome_baseline",
    "O03_workflow_action_map",
    "O04_reversibility_classification",
    "O05_risk_tier",
    "O06_control_plan",
    "O07_deployment_boundary",
    "O08_acceptance_plan",
    "O09_operating_owner",
    "O10_unresolved_risk_register",
)
Q_OUTPUTS = {q["question_id"]: q["output_ids"] for q in CATALOG["questions"]}
DECISION_ORDER = ("R-T0", "R-UNKNOWN", "R-CONVENTIONAL", "R-HUMAN", "R-QUALIFY")
MODULES = (
    "authority_human_oversight",
    "quality_verification",
    "evidence_traceability",
    "identity_security_data_legal",
    "integration_change_supply_chain",
    "reliability_continuity",
    "economics_value",
    "adoption_ownership",
)
DECISION_FINGERPRINT = "0874f0870bcd0186b7d8e16f378ccc9bbf14cf419fd4d30f46acab89f1c07410"
RISK_FINGERPRINT = "1e37c7917f685d9f4f0b0db98e5d6f810b071a6c39e3b2d1d0de9f730092c4ea"


def _load_contracts():
    return json.loads((ROOT / "decision-rules.json").read_text()), json.loads(
        (ROOT / "risk-rules.json").read_text()
    )


def _rules():
    return json.loads((ROOT / "decision-rules.json").read_text())


def _risk_contract():
    return json.loads((ROOT / "risk-rules.json").read_text())["proportionality_pass"]


def _unknown(v):
    return (
        v is None
        or (
            isinstance(v, str)
            and (not v.strip() or v.strip().casefold() in {"unknown", "unavailable", "null", "none", "n/a", "na"})
        )
        or v == []
    )


def _condition(p, a):
    op = p["operator"]
    qs = p.get("question_ids", [p.get("question_id")])
    vals = [a.get(q, "unknown") for q in qs]
    if op == "equals":
        return vals[0] == p["value"]
    if op == "in":
        return vals[0] in p["value"]
    if op == "known":
        return not _unknown(vals[0])
    if op == "any_unknown":
        return any(_unknown(v) for v in vals)
    if op == "all":
        return all(_condition(x, a) for x in p["conditions"])
    raise ValueError("unknown operator: " + op)


def _leaf(a, path, default="unknown"):
    if path in a:
        return a[path]
    v = a
    for part in path.split("."):
        if not isinstance(v, dict) or part not in v:
            return default
        v = v[part]
    return v


def _risk_detail(a, c=None):
    c = _risk_contract() if c is None else c
    evaluated = []
    uplift_evaluated = []

    def hit(x, governing_rule_id=None):
        op = x["operator"]
        if op in ("all", "any"):
            results = [hit(z, governing_rule_id or x.get("id")) for z in x["conditions"]]
            return all(results) if op == "all" else any(results)
        v = _leaf(a, x["question_id"])
        if op == "equals":
            result = v == x["value"]
        elif op == "in":
            result = v in x["value"]
        elif op == "not_in":
            result = v not in x["value"]
        elif op == "unknown":
            result = _unknown(v)
        elif op == "known":
            result = not _unknown(v)
        else:
            raise ValueError("unknown risk operator")
        evaluated.append(
            {
                "governing_rule_id": governing_rule_id or x.get("id"),
                "predicate_id": x.get("id"),
                "input_path": x.get("question_id"),
                "value": v,
                "operator": op,
                "result": result,
            }
        )
        return result

    fired = [x for x in c["trigger_rules"] if hit(x)]
    order = {t: i for i, t in enumerate(c["evaluation_order"])}
    tier = min((x["tier"] for x in fired), key=lambda x: order[x]) if fired else None
    selected = next((x for x in fired if x["tier"] == tier), None)
    reasons = [x["reason"] for x in fired if x["tier"] == tier]
    trigger_evaluated = list(evaluated)
    profile = c["base_profiles"][tier].copy() if tier else {}
    uplifts = []
    for u in c["uplift_rules"]:
        before = len(evaluated)
        fired_uplift = hit(u)
        uplift_evaluated.extend(evaluated[before:])
        if fired_uplift:
            if tier:
                for m in u["modules"]:
                    profile[m] = max(profile[m], u["minimum"])
            uplifts.append(
                {
                    "id": u["id"],
                    "modules": u["modules"],
                    "floor": u["minimum"],
                    "reason": u["reason"],
                }
            )
    if not fired:
        return {
            "tier": None,
            "reasons": ["no_proportionality_trigger"],
            "profile": profile,
            "uplifts": uplifts,
            "trigger": None,
            "fired": [],
            "evaluated": evaluated,
            "trigger_evaluated": trigger_evaluated,
            "uplift_evaluated": uplift_evaluated,
        }
    return {
        "tier": tier,
        "reasons": reasons,
        "profile": profile,
        "uplifts": uplifts,
        "trigger": selected,
        "fired": fired,
        "evaluated": evaluated,
        "trigger_evaluated": trigger_evaluated,
        "uplift_evaluated": uplift_evaluated,
    }


def _risk(a):
    _, doc = _load_contracts()
    _validate_risk_contract(doc)
    d = _risk_detail(a, doc["proportionality_pass"])
    # Preserve the historical four-value oracle shape while detailed outputs use schema field names.
    compat = [{**u, "trigger": u["id"], "minimum": u["floor"]} for u in d["uplifts"]]
    return d["tier"], d["reasons"], d["profile"], compat


def _authority(raw, tier, disposition):
 occ=raw["occurrence"]
 release=occ.get("human_release_mechanism_available") == "available"
 refs=("accepted_first_h_record_ref","observed_effect_ref","tested_recovery_ref","policy_ratification_ref")
 complete=all(not _unknown(occ.get(k)) for k in refs)
 tuple_known=not _unknown(occ.get("tuple_identity"))
 if tier=="T4": return {"required":"H2","actual":"D","h2_denial_reason":"h2_available=false"}
 if tier in ("T0",None) or disposition in ("defer","do_not_agentize","conventional_automation","human_process"):
  return {"required":"H","actual":"D","h2_denial_reason":None}
 if tier in ("T1","T2") and disposition=="qualify" and occ.get("state")=="subsequent" and tuple_known and complete:
  return {"required":"H","actual":"A","h2_denial_reason":None}
 return {"required":"H","actual":"H" if release else "D","h2_denial_reason":None}


def _handoff_disposition(raw, disposition, rule):
 handoff=raw.get("answers",{}).get("handoff") or {}
 if handoff.get("cross_principal_required")=="yes" and handoff.get("atr_required") in ("no","unknown"):
  return "human_process","R-HUMAN"
 return disposition,rule

def _o07(raw):
 out={"sources_targets_exceptions":_leaf(raw,"answers.sources_targets_exceptions")}
 ep=raw.get("classification_groups",{}).get("enforcement_point")
 if ep:
  out["enforcement_point"]=ep
  out["boundary_dependencies"]=ep.get("boundary_dependencies",[])
 handoff=raw.get("answers",{}).get("handoff")
 if handoff:
  out["handoff_plan"]=handoff
 return out

def _o05(detail, raw, disposition_unresolved=()):
 tier=detail["tier"]; tr=detail["trigger"]
 unresolved=[]
 if tier is None:
  unresolved.append({"fact":"no_proportionality_trigger","owner":_leaf(raw,"answers.named_operating_owner"),"resume_trigger":_leaf(raw,"answers.resume_trigger")})
 unresolved.extend(disposition_unresolved)
 highest=None if tr is None else {"trigger_id":tr["id"],"tier":tier,"reason":tr["reason"]}
 return {"assigned_tier":tier,"known_minimum":tier,"unresolved_facts":unresolved,"highest_trigger":highest}

def _o06(detail, raw, disposition, c, rules):
 tier=detail["tier"]
 if tier is None:
  base={m:None for m in rules["module_ids"]}; selected=None
 else:
  base=c["base_profiles"][tier]; tr=detail["trigger"]; selected={"tier":tier,"trigger_id":tr["id"],"reason":tr["reason"]}
 mods=[]
 for m in rules["module_ids"]:
  floor=None
  for u in detail["uplifts"]:
   if m in u["modules"] and (floor is None or u["floor"]>floor): floor=u["floor"]
  final=None if base[m] is None else (base[m] if floor is None else max(base[m],floor))
  mods.append({"module_id":m,"base_depth":base[m],"applied_uplift_floor":floor,"final_depth":final,"reasons":[u["reason"] for u in detail["uplifts"] if m in u["modules"]]})
 return {"authority":_authority(raw,tier,disposition),"selected_base_rule":selected,"modules":mods,"applied_uplifts":detail["uplifts"]}

def _validate_contract(rules=None):
 rules=_rules() if rules is None else rules
 if hashlib.sha256(json.dumps(rules,sort_keys=True,separators=(',',':')).encode()).hexdigest() != DECISION_FINGERPRINT: raise ValueError('decision semantic fingerprint drift')
 cat=json.loads((ROOT/'question-catalog.json').read_text()); qids={q['question_id'] for q in cat['questions']}; rs=rules['rules']; order=rules['disposition_pass']['evaluation_order']
 expected_rules=[('R-T0','do_not_agentize','any',['prohibited_purpose','unbounded_material_effect','no_target_readback_or_safe_state']),('R-UNKNOWN','defer','all',['acceptance_critical_unknown']),('R-CONVENTIONAL','conventional_automation','all',['fixed_schema','deterministic_transformation','no_ambiguous']),('R-HUMAN','human_process','any',['material_judgment']),('R-QUALIFY','qualify','all',['bounded_scope','named_owner','acceptance_criteria_known'])]
 if set(rules) != {'authority','disposition_pass','module_ids','rule_set_id','rules'}: raise ValueError('decision document keys')
 if set(rules['disposition_pass']) != {'evaluation_order'} or rules['disposition_pass']['evaluation_order'] != [x[0] for x in expected_rules]: raise ValueError('decision order')
 if rules['module_ids'] != list(MODULES): raise ValueError('module order')
 if len(rs)!=5: raise ValueError('rule count')
 for r,(rid,disp,match,pids) in zip(rs,expected_rules):
  if set(r)!={'rule_id','disposition','match','predicates'} or (r['rule_id'],r['disposition'],r['match'])!=(rid,disp,match): raise ValueError('rule shape')
  if [p.get('predicate_id') for p in r['predicates']] != pids: raise ValueError('predicate order')
  if len(r['predicates']) != len(pids): raise ValueError('predicate count')
 def exact_pred(p, nested=False):
  op=p.get('operator')
  if op in ('all','any'):
   if set(p)!={'operator','predicate_id','conditions'} or not p['conditions']: raise ValueError('compound shape')
   ids=[x.get('predicate_id') for x in p['conditions']]
   if len(ids)!=len(set(ids)): raise ValueError('nested IDs')
   if p.get('predicate_id')=='unbounded_material_effect' and ids != ['material_consequence','unrecoverable_effect']: raise ValueError('nested predicate order')
   for x in p['conditions']: exact_pred(x,True)
  elif op in ('equals','in','known'):
   if set(p)!={'operator','predicate_id','question_id','value'}: raise ValueError('leaf shape')
   if p['question_id'] not in qids: raise ValueError('leaf path')
  elif op=='any_unknown':
   if set(p)!={'operator','predicate_id','question_ids','value'} or p['question_ids'] != ['answers.mission','answers.intended_outcome','answers.named_operating_owner','answers.acceptance_criteria'] or p['value'] is not True: raise ValueError('unknown shape')
  else: raise ValueError('unsupported decision operator')
 for r in rs:
  for p in r['predicates']: exact_pred(p)
 schema=json.loads((ROOT/'intake-schema.json').read_text()); domains={}
 def walk(n,path=()):
  if not isinstance(n,dict): return
  if 'enum' in n: domains['.'.join(path)]=set(n['enum'])
  if 'const' in n: domains['.'.join(path)]={n['const']}
  for k,v in n.get('properties',{}).items(): walk(v,path+(k,))
 walk(schema)
 if [r['rule_id'] for r in rs]!=list(DECISION_ORDER) or order!=list(DECISION_ORDER) or set(Q_OUTPUTS)!=qids: raise ValueError('contract drift')
 if rules.get('module_ids')!=list(MODULES): raise ValueError('module contract drift')
 seen=set()
 for r in rs:
  if r.get('match') not in ('all','any') or 'disposition' not in r : raise ValueError('invalid rule')
  for p in r['predicates']:
   if p['predicate_id'] in seen: raise ValueError('duplicate predicate')
   seen.add(p['predicate_id'])
   deps=p.get('question_ids',[p.get('question_id')]) if p['operator']!='all' else [q for c in p['conditions'] for q in c.get('question_ids',[c.get('question_id')])]
   for q in deps:
    if q not in qids: raise ValueError('dangling question')
   if p['operator'] not in ('equals','in','known','any_unknown','all','any','not_in','unknown'): raise ValueError('unknown operator')
   if p['operator']=='all':
    for c in p['conditions']:
     if c['operator'] not in ('equals','in','known','any','not_in','unknown'): raise ValueError('invalid nested operator')
 def check(p, parent):
  op=p.get('operator')
  if op in ('all','any'):
   if not p.get('conditions'): raise ValueError('empty decision compound')
   ids=[x.get('predicate_id') for x in p['conditions']]
   if len(ids)!=len(set(ids)): raise ValueError('duplicate nested predicate')
   for x in p['conditions']: check(x,parent)
   return
  if op not in ('equals','in','known','any_unknown','not_in','unknown'): raise ValueError('invalid decision operator')
  for q in p.get('question_ids',[p.get('question_id')]):
   if q not in qids: raise ValueError('dangling question')
  if op in ('equals','in','not_in'):
   vals=p.get('value') if op!='equals' else [p.get('value')]
   if any(v not in domains.get(qids and p.get('question_id'),set()) for v in vals): raise ValueError('invalid decision literal')
 for r in rs:
  ids=[p.get('predicate_id') for p in r.get('predicates',[])]
  if len(ids)!=len(set(ids)): raise ValueError('duplicate predicate')
  for p in r.get('predicates',[]): check(p,r['rule_id'])

def _validate_risk_contract(risk=None, rules=None):
 risk=_risk_contract() if risk is None else risk
 if "proportionality_pass" in risk:
  if hashlib.sha256(json.dumps(risk,sort_keys=True,separators=(",",":" )).encode()).hexdigest() != RISK_FINGERPRINT: raise ValueError("risk semantic fingerprint drift")
  if set(risk) != {"schema_id","disposition_pass","proportionality_pass"}: raise ValueError("risk document keys")
  risk=risk["proportionality_pass"]
 rules=_rules() if rules is None else rules
 if risk.get('evaluation_order') != ['T0','T4','T3','T2','T1']: raise ValueError('risk evaluation order drift')
 expected={'T0':{'authority_human_oversight':'L0','quality_verification':'L0','evidence_traceability':'L1','identity_security_data_legal':'L1','integration_change_supply_chain':'L0','reliability_continuity':'L0','economics_value':'L1','adoption_ownership':'L1'},'T1':{m:'L1' for m in rules['module_ids']},'T2':{'authority_human_oversight':'L2','quality_verification':'L2','evidence_traceability':'L2','identity_security_data_legal':'L2','integration_change_supply_chain':'L2','reliability_continuity':'L2','economics_value':'L1','adoption_ownership':'L1'},'T3':{'authority_human_oversight':'L3','quality_verification':'L3','evidence_traceability':'L3','identity_security_data_legal':'L3','integration_change_supply_chain':'L3','reliability_continuity':'L2','economics_value':'L2','adoption_ownership':'L2'},'T4':{m:'L3' for m in rules['module_ids']}}
 if risk.get('base_profiles') != expected: raise ValueError('risk matrix drift')
 schema=json.loads((ROOT/'intake-schema.json').read_text())
 domains={}
 def walk(node,path=()):
  if not isinstance(node,dict): return
  if "enum" in node: domains[".".join(path)]=set(node["enum"])
  if "const" in node: domains[".".join(path)]={node["const"]}
  for k,v in node.get("properties",{}).items(): walk(v,path+(k,))
 walk(schema)
 paths=set(PATHS)
 seen=set()
 def check(x):
  op=x.get("operator")
  if op not in {"equals","in","not_in","unknown","known","all","any"}: raise ValueError("invalid risk operator")
  if op in {"all","any"}:
   if not x.get("conditions"): raise ValueError("empty risk conditions")
   for c in x["conditions"]: check(c)
   return
  q=x.get("question_id")
  if q not in paths: raise ValueError("dangling risk path")
  if op in {"equals","in","not_in"}:
   vals=x["value"] if op!="equals" else [x["value"]]
   if any(v not in domains.get(q,set()) for v in vals): raise ValueError("invalid risk literal")
 modules=list(MODULES)
 for section in (risk["trigger_rules"],risk["uplift_rules"]):
  for x in section:
   if x.get("id") in seen: raise ValueError("duplicate risk id")
   seen.add(x["id"]); check(x)
   if section is risk["trigger_rules"]:
    if x["tier"] not in {"T0","T1","T2","T3","T4"}: raise ValueError("trigger tier")
    if x["operator"] in {"all","any"}:
     if set(x) != {"id","operator","tier","reason","conditions"} or not x["conditions"]: raise ValueError("trigger shape")
    elif not set(x).issubset({"id","operator","tier","reason","question_id","value"}) or not {"question_id","reason"}.issubset(x): raise ValueError("trigger leaf shape")
   else:
    if not set(x).issubset({"id","operator","minimum","modules","reason","question_id","value","conditions"}) or "modules" not in x: raise ValueError("uplift shape")
    if x["minimum"] not in {"L0","L1","L2","L3"} or not x["modules"] or any(m not in modules for m in x["modules"]): raise ValueError("uplift module/floor")
 tiers=[x["tier"] for x in risk["trigger_rules"]]
 if set(tiers)!={"T0","T1","T2","T3","T4"}: raise ValueError("incomplete risk tiers")
 if len(risk["uplift_rules"])!=8: raise ValueError("uplift contract incomplete")
 if len(risk["trigger_rules"])!=22 or len(seen)!=30: raise ValueError("risk rule count drift")
 if len(modules)!=8 or len(set(modules))!=8: raise ValueError("module matrix drift")
 if set(risk["base_profiles"]) != {"T0","T1","T2","T3","T4"}: raise ValueError("base profile drift")
 if any(set(v)!=set(modules) for v in risk["base_profiles"].values()): raise ValueError("base module drift")

def _condition_detail(p, a, governing_rule_id, records):
 op=p['operator']
 if op in ('all','any'):
  results=[_condition_detail(x,a,governing_rule_id,records) for x in p['conditions']]
  return all(results) if op=='all' else any(results)
 qids=p.get('question_ids',[p.get('question_id')])
 results=[]
 for q in qids:
  value=a.get(q,'unknown')
  if op=='equals': result=value==p['value']
  elif op=='in': result=value in p['value']
  elif op=='known': result=not _unknown(value)
  elif op=='any_unknown': result=_unknown(value)
  elif op=='not_in': result=value not in p['value']
  elif op=='unknown': result=_unknown(value)
  else: raise ValueError('unknown operator: '+op)
  records.append({'governing_rule_id':governing_rule_id,'predicate_id':p.get('predicate_id'),'input_path':q,'value':value,'operator':op,'result':result})
  results.append(result)
 return any(results) if op=='any_unknown' else results[0]

def _select_detail(a, rules=None):
 rules=_rules() if rules is None else rules; by={r["rule_id"]:r for r in rules["rules"]}
 all_records=[]; unknown_rule=None
 for rid in rules["disposition_pass"]["evaluation_order"]:
  rule=by[rid]
  records=[]
  hits=[_condition_detail(p,a,rid,records) for p in rule["predicates"]]
  all_records.extend(records)
  if rid=="R-UNKNOWN": unknown_rule=rule
  matched=all(hits) if rule["match"]=="all" else any(hits)
  if matched: return rule, all_records
 if unknown_rule is not None: return unknown_rule, all_records
 raise ValueError("decision contract omitted R-UNKNOWN rule")

def _select(a):
 return _select_detail(a)[0]
def _construct_result(raw, rules, risk_doc):
 risk=risk_doc["proportionality_pass"]
 schema=json.loads((ROOT/'intake-schema.json').read_text())
 errors=sorted(Draft202012Validator(schema).iter_errors(raw), key=lambda e:list(e.path))
 if errors: raise ValueError("invalid complete raw intake: " + errors[0].message)
 a=dict(raw)
 flat={p:_leaf(a,p) for p in PATHS}
 r, disposition_detail=_select_detail(flat, rules); rule,disposition=r["rule_id"],r["disposition"]
 detail=_risk_detail(flat, risk); tier=detail["tier"]
 if tier in ("T0","T4") and disposition not in ("do_not_agentize","defer"): disposition="do_not_agentize"
 if tier is None and disposition != "human_process": disposition="defer"; rule="R-UNKNOWN"
 disposition,rule=_handoff_disposition(raw,disposition,rule)
 evidence="E-"+rule[2:]
 conf="unknown" if disposition=="defer" else ("high" if disposition=="qualify" else "medium")
 disposition_unresolved=[]
 seen_facts=set()
 if disposition=="defer":
  for fact in disposition_detail:
   if not fact["result"] or not _unknown(fact["value"]):
    continue
   path=fact["input_path"]
   if path in seen_facts:
    continue
   if path not in {"answers.mission","answers.intended_outcome","answers.named_operating_owner","answers.acceptance_criteria"}: continue
   seen_facts.add(path)
   disposition_unresolved.append({"fact":path,"owner":_leaf(raw,"answers.named_operating_owner"),"resume_trigger":_leaf(raw,"answers.resume_trigger")})
 o05=_o05(detail,raw,disposition_unresolved); o06=_o06(detail,raw,disposition,risk,rules)
 vals=[
  {"intervention_decision":"conventional_automation" if disposition=="conventional_automation" else disposition,"lifecycle_disposition":"do_not_agentize" if disposition=="conventional_automation" else disposition},
  {"outcome":_leaf(a,"answers.intended_outcome"),"baseline":_leaf(a,"answers.baseline")},
  {"workflow":_leaf(a,"answers.mission"),"actions":_leaf(a,"answers.workflow_actions"),"map":_leaf(a,"answers.sources_targets_exceptions")},
  _leaf(a,"classification_groups.reversibility.reversibility"), o05, o06,
  _o07(raw), _leaf(a,"answers.acceptance_criteria"),
  {"operating":_leaf(a,"answers.named_operating_owner"),"policy":_leaf(a,"answers.named_policy_owner")}, o05["unresolved_facts"]
 ]
 def trace_records(records, evaluation_pass):
  return [{"record_type":"predicate_evaluation","evaluation_pass":evaluation_pass,"rule_id":x["governing_rule_id"],"predicate_id":x["predicate_id"],"operator":x["operator"],"input_path":x["input_path"],"input_value":x["value"],"result":x["result"],"affected_output_ids":Q_OUTPUTS.get(x["input_path"],[])} for x in records]
 trace=trace_records(disposition_detail,"disposition")+trace_records(detail["trigger_evaluated"],"proportionality")+trace_records(detail["uplift_evaluated"],"uplift")
 evidence_ids={o:[f"{evidence}-{o}"] for o in OUTPUTS}
 trace += [{"record_type":"output_leaf","output_id":o,"json_path":f"/outputs/{i}/value","evidence_ids":evidence_ids[o]} for i,o in enumerate(OUTPUTS)]
 result={"instrument_id":"b03-scoping-instrument-v2","outputs":[{"output_id":o,"value":v,"confidence":conf,"evidence_ids":evidence_ids[o]} for o,v in zip(OUTPUTS,vals)],"trace":trace,"disposition":disposition,"rule_id":rule}
 out_schema=json.loads((ROOT/"compiled-output-schema.json").read_text())
 if o05["assigned_tier"] is None:
  if o05["known_minimum"] is not None or o05["highest_trigger"] is not None or not o05["unresolved_facts"] or o05["unresolved_facts"][0]["fact"]!="no_proportionality_trigger": raise ValueError("/outputs/4/value no-tier coherence")
 elif o05["assigned_tier"] != o05["known_minimum"] or o06["selected_base_rule"] != o05["highest_trigger"]: raise ValueError("/outputs/4/value and /outputs/5/value tier coherence")
 if len(o06["modules"]) != 8 or [m["module_id"] for m in o06["modules"]] != list(MODULES): raise ValueError("/outputs/5/value/modules order")
 for m in o06["modules"]:
  floors=[u["floor"] for u in o06["applied_uplifts"] if m["module_id"] in u["modules"]]
  expected_floor=max(floors) if floors else None
  if m["applied_uplift_floor"] != expected_floor: raise ValueError("/outputs/5/value/modules floor")
  expected_final=None if m["base_depth"] is None else max((m["base_depth"], expected_floor), key=lambda x: int(x[1:]) if x else -1)
  if m["final_depth"] != expected_final: raise ValueError("/outputs/5/value/modules final")
  expected_reasons=[u["reason"] for u in o06["applied_uplifts"] if m["module_id"] in u["modules"]]
  if m["reasons"] != expected_reasons: raise ValueError("/outputs/5/value/modules reasons")
 if o06["applied_uplifts"] != detail["uplifts"]: raise ValueError("/outputs/5/value/applied_uplifts order")
 if o06["authority"] != _authority(raw, detail["tier"], disposition): raise ValueError("/outputs/5/value/authority")
 pred_keys={"record_type","evaluation_pass","rule_id","predicate_id","operator","input_path","input_value","result","affected_output_ids"}
 if any(set(t) != pred_keys for t in trace if t["record_type"]=="predicate_evaluation"): raise ValueError("/trace predicate shape")
 if [t["output_id"] for t in trace if t["record_type"]=="output_leaf"] != list(OUTPUTS): raise ValueError("/trace output order")
 Draft202012Validator.check_schema(out_schema)
 tuples=[(t["rule_id"],t["predicate_id"],t["input_path"]) for t in trace if t["record_type"]=="predicate_evaluation"]
 if len(tuples) != len(set(tuples)): raise ValueError("/trace duplicate predicate lineage")
 leaves=[t for t in trace if t["record_type"]=="output_leaf"]
 if any(t["evidence_ids"] != evidence_ids[t["output_id"]] for t in leaves): raise ValueError("/trace output evidence")
 errors=sorted(Draft202012Validator(out_schema).iter_errors(result), key=lambda e:list(e.path))
 if errors: raise ValueError("compiled output invalid at /"+"/".join(map(str,errors[0].path))+": "+errors[0].message)
 if result["outputs"][9]["value"] != result["outputs"][4]["value"]["unresolved_facts"]: raise ValueError("O10/O05 unresolved facts mismatch")
 return result

def evaluate(raw):
    rules, risk_doc = _load_contracts()
    _validate_contract(rules)
    _validate_risk_contract(risk_doc, rules)
    result = _construct_result(raw, rules, risk_doc)
    _validate_result(result, raw, rules, risk_doc)
    return result


def _validate_result(result, raw, rules=None, risk_doc=None):
    if rules is None or risk_doc is None:
        rules, risk_doc = _load_contracts()
    _validate_contract(rules)
    _validate_risk_contract(risk_doc, rules)
    out_schema = json.loads((ROOT / "compiled-output-schema.json").read_text())
    errors = sorted(Draft202012Validator(out_schema).iter_errors(result), key=lambda e: list(e.path))
    if errors:
        raise ValueError(
            "compiled output invalid at /" + "/".join(map(str, errors[0].path)) + ": " + errors[0].message
        )
    expected = _construct_result(raw, rules, risk_doc)
    if result != expected:

        def first(a, b, path=""):
            if type(a) is not type(b) or a != b:
                if isinstance(a, dict) and isinstance(b, dict):
                    for k in sorted(set(a) | set(b)):
                        if k not in a or k not in b or a[k] != b[k]:
                            return first(a.get(k), b.get(k), path + "/" + str(k))
                if isinstance(a, list) and isinstance(b, list):
                    for i, (x, y) in enumerate(zip(a, b)):
                        if x != y:
                            return first(x, y, path + "/" + str(i))
                return path or "/"
            return None

        raise ValueError("runtime result mismatch at " + first(result, expected))
    return True


if __name__ == "__main__":
    raw = json.load(open(__import__("sys").argv[1]))
    print(json.dumps(evaluate(raw), sort_keys=True, separators=(",", ":")))
