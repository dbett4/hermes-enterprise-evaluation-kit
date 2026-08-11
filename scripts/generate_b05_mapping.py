#!/usr/bin/env python3
import argparse, hashlib, json, sys, copy
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Mapping as TypingMapping, Union
from types import MappingProxyType
from pathlib import Path
from jsonschema import Draft202012Validator, RefResolver, FormatChecker
ROOT=Path(__file__).resolve().parents[1]; MD=ROOT/'kit/mapping'
FrozenJSON = Union[str, int, float, bool, None, tuple['FrozenJSON', ...], TypingMapping[str, 'FrozenJSON']]
BASE='dd71c1cb51b1bfc85484a44d939c6f66f88d3eb8'
INPUTS={
'kit/mapping/neutral-requirements.json':'3b28dac2ef24d463917e4e11bdd4e200aff42568d93e5cc28b4f2496209f143f',
'kit/mapping/evidence-catalog-v0.20.json':'b2f24f91d2ec598d79769816013010e71f9f4ec7aadbff09a42ebef437c715cb',
'kit/core/implementation-mapping-contract.md':'f70f1c53da41ccac646b77454b755bd11e946453ff3f2cfc8ff7366a2f21de8c',
'kit/core/control-traceability.md':'d7a153cd90b1ba705e7e510da5ed5466caa62318cee5f7bf55b35833e451d18b',
'kit/preflight/v0.20-preflight-report.md':'a16bbf0a0d67dd92397f231dbbdc1033c1b3d4f02f3cd583494d37c1478c8eed',
'research/authority-access-architecture-draft.md':'1843c1296e0ac9260ac3d9ebe10aedfb0644c72a967d77f038d40117f62e4af0',
'build-tickets/B03-scoping-instrument-and-gates.md':'ebc8b93fa99679c00bfd9c42b314bbfebb52a1b9e9c13846d1276e389b1b95af',
'build-tickets/B05-deployment-mapping.md':'6f031e98fd40bab17d08cd800c5fe1ae2d11071e0321b7fb409604870578e038'}
UNMATERIALIZED_OUTPUTS={'map':{'state':'unmaterialized','sha256':None},'ledger':{'state':'unmaterialized','sha256':None}}

B03_ABSENT={'state':'absent','artifacts':[],'requirement_keys':[],'extension_claims':[]}
B03_ARTIFACT_PATHS=(
 'kit/instrument/compiled-fixtures.json','kit/instrument/compiled-output-schema.json','kit/instrument/completed-example.json',
 'kit/instrument/decision-rules.json','kit/instrument/enforcement_oracle.py','kit/instrument/evaluator.py','kit/instrument/fixtures.json',
 'kit/instrument/intake-schema.json','kit/instrument/risk-rules.json',
)

def _b03_absent():
 return copy.deepcopy(B03_ABSENT)

def _b03_probe_connected(root: Path):
 for rel in B03_ARTIFACT_PATHS:
  if not (root/rel).is_file():
   return None
 try:
  import subprocess
  proc=subprocess.run([sys.executable,'-B',str(root/'scripts/generate_b03_instrument_artifacts.py'),'--check'],cwd=root,capture_output=True,text=True)
  if proc.returncode!=0:
   return None
 except Exception:
  return None
 artifacts=[{'path':rel,'sha256':hashlib.sha256((root/rel).read_bytes()).hexdigest()} for rel in B03_ARTIFACT_PATHS]
 return {'state':'connected','instrument_id':'b03-scoping-instrument-v2','artifacts':artifacts,'requirement_keys':[],'extension_claims':['C03']}

def _b03_integration_snapshot(root: Path):
 connected=_b03_probe_connected(root)
 return connected if connected is not None else _b03_absent()

def _b03_reconcile_integration(map_doc, expected):
 got=map_doc['b03_integration']
 if got!=expected:
  raise B2Error('PROVENANCE','/map/b03_integration','b03 integration snapshot mismatch')
 if got['state']=='connected':
  if got['extension_claims']!=['C03']:
   raise B2Error('PROVENANCE','/map/b03_integration/extension_claims','C03 claim required when connected')
  if len(got['artifacts'])!=len(B03_ARTIFACT_PATHS):
   raise B2Error('PROVENANCE','/map/b03_integration/artifacts','artifact cardinality mismatch')

def _valid_lock_outputs(outputs):
 if outputs==UNMATERIALIZED_OUTPUTS: return True
 if not isinstance(outputs,dict): return False
 for key in ('map','ledger'):
  o=outputs.get(key)
  if not isinstance(o,dict) or o.get('state')!='materialized' or not isinstance(o.get('sha256'),str) or len(o['sha256'])!=64:
   return False
 return True
CONTRACTS={
'kit/mapping/hermes-v0.20-row-decisions.schema.json':'78ee7a7e00d59b423e8dd7a97025c2432ef2ccfc7c6389db88545b5a9873ba00',
'kit/mapping/hermes-v0.20-overrides.schema.json':'cfbd57e8e3b6a6e37868ce8534b72bbbb814ff4c251b4eeb8bc1a9418a72e38c',
'kit/mapping/hermes-v0.20-map.schema.json':'fa3c7154816a2cc55da6ae76f1627879bd7421bc44ffe7514b5c721085992652',
'kit/mapping/capability-gap-ledger.schema.json':'29f342e8d1fc34a18458fa0a7d8b66a5835006450a42168226c73291f888a2b0',
'kit/mapping/evidence-catalog-v0.20.schema.json':'078686e3a4c038040d4d897dc4e96b69aff442abb5f7d3cd3434cd5a3f8b8961',
'kit/mapping/b05-generation.lock.schema.json':'20d87835178bfa13182ab93eb07f614dbaeb726d97b7176ff0e4f91f70c91bbb',
'kit/mapping/hermes-v0.20-adjudicated-decision.schema.json':'837e9d68808317a8af6de6ccca84500e0280bf1cf442a75b00576e3bfae5a7ce'}
def digest(v): return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
class B1Error(ValueError):
 def __init__(self, code, pointer='/', detail=''): self.code=code; self.pointer=pointer; self.detail=detail; super().__init__(f'B1_{code} {pointer}: {detail}')

def _freeze(value):
 if isinstance(value, Mapping): return MappingProxyType({k:_freeze(v) for k,v in value.items()})
 if isinstance(value, (list, tuple)): return tuple(_freeze(v) for v in value)
 return value

@dataclass(frozen=True, slots=True)
class B1Identity:
 position:int; row_index:int; decision_id:str; requirement_key:str; requirement_digest:str

@dataclass(frozen=True, slots=True)
class B1Authority:
 identities:tuple; requirements:tuple; catalog:object; canonical_orders:object; surface_statuses:object; denominator_sha256:str; catalog_sha256:str; frozen_schemas:object; shared_schema:object; row_schema:object; override_schema:object; row_validator:object; override_validator:object; manifest_sha256:str; override_sha256:str

@dataclass(frozen=True, slots=True)
class B1OverrideFact:
 override_index:int; target_position:int; decision_id:str; requirement_key:str; requirement_digest:str; replacement_sha256:str

@dataclass(frozen=True, slots=True)
class B1Provenance:
 manifest_id:str; baseline_commit:str; decision_count:int; identities:tuple[B1Identity, ...]; supplied_overrides:tuple[B1OverrideFact, ...]; consumed_overrides:tuple[B1OverrideFact, ...]; distinct_target_positions:tuple[int, ...]; supplied_count:int; consumed_count:int; distinct_target_count:int; deferred:tuple[str, ...]

@dataclass(frozen=True, slots=True)
class B1Compilation:
 decisions:tuple[TypingMapping[str, FrozenJSON], ...]; release_context:TypingMapping[str, FrozenJSON]; provenance:B1Provenance

class B2Error(ValueError):
 def __init__(self, code, pointer='/', detail=''):
  self.code=code; self.pointer=pointer; self.detail=detail
  super().__init__(f'B2_{code} {pointer}: {detail}')

@dataclass(frozen=True, slots=True)
class B2Authority:
 pre_lock:TypingMapping[str, FrozenJSON]; b03_integration:TypingMapping[str, FrozenJSON]

@dataclass(frozen=True, slots=True)
class B2Artifacts:
 map_document:TypingMapping[str, FrozenJSON]; ledger_document:TypingMapping[str, FrozenJSON]; post_lock:TypingMapping[str, FrozenJSON]; map_bytes:bytes; ledger_bytes:bytes; post_lock_bytes:bytes; map_sha256:str; ledger_sha256:str

class B3Error(ValueError):
 def __init__(self, code, pointer='/', detail=''):
  self.code=code; self.pointer=pointer; self.detail=detail
  super().__init__(f'B3_{code} {pointer}: {detail}')

@dataclass(frozen=True, slots=True)
class _B3Prestate:
 path:Path; data:bytes|None

def atomic_materialize_b3(writes:tuple[tuple[Path,bytes], ...]) -> None:
 if not writes: raise B3Error('EMPTY','/','no writes requested')
 pre:list[_B3Prestate]=[]
 try:
  for path,content in writes:
   pre.append(_B3Prestate(path,path.read_bytes() if path.is_file() else None))
   path.parent.mkdir(parents=True, exist_ok=True)
   path.write_bytes(content)
  for path,content in writes:
   if path.read_bytes()!=content: raise B3Error('VERIFY',str(path),'post-write bytes mismatch')
 except Exception as e:
  for state in reversed(pre):
   if state.data is None: state.path.unlink(missing_ok=True)
   else: state.path.write_bytes(state.data)
  if isinstance(e,B3Error): raise
  raise B3Error('COMMIT','/',str(e)) from e

def _authority_json(root, rel, pointer='/'):
 try:
  return json.loads((root/rel).read_text())
 except Exception as e:
  raise B1Error('JSON',pointer,f'malformed JSON: {rel}: {e}') from e

def load_b1_authority(root=ROOT):
 # Fixed authority inputs and contracts only. Production row/override documents are intentionally excluded.
 for rel,want in INPUTS.items():
  p=root/rel
  if not p.is_file(): raise B1Error('PROVENANCE',f'/{rel}','missing frozen input')
  if hashlib.sha256(p.read_bytes()).hexdigest()!=want: raise B1Error('PROVENANCE',f'/{rel}','frozen hash mismatch')
 lock=_authority_json(root,'kit/mapping/b05-generation.lock.json','/lock')
 if lock.get('inputs') != INPUTS: raise B1Error('PROVENANCE','/inputs','lock input set/hash mismatch')
 if lock.get('contracts') != CONTRACTS: raise B1Error('PROVENANCE','/contracts','lock contract set/hash mismatch')
 for rel,want in CONTRACTS.items():
  p=root/rel
  if not p.is_file(): raise B1Error('PROVENANCE',f'/contracts/{rel}','missing contract')
  if hashlib.sha256(p.read_bytes()).hexdigest()!=want: raise B1Error('PROVENANCE',f'/contracts/{rel}','contract hash mismatch')
 exact={'generator':'scripts/generate_b05_mapping.py','manifest':'kit/mapping/hermes-v0.20-row-decisions.json','overrides':'kit/mapping/hermes-v0.20-overrides.json'}
 for section,rel in exact.items():
  if lock.get(section,{}).get('path') != rel: raise B1Error('PROVENANCE',f'/{section}/path','exact path mismatch')
 if not _valid_lock_outputs(lock.get('outputs')):
  raise B1Error('PROVENANCE','/outputs','invalid lock outputs state')
 schema_rels=tuple(k for k in CONTRACTS if k.endswith('.schema.json'))
 raw_schemas={rel.split('/')[-1]:_authority_json(root,rel,f'/{rel}') for rel in schema_rels}
 try:
  for schema in raw_schemas.values(): Draft202012Validator.check_schema(schema)
 except Exception as e: raise B1Error('SCHEMA','/contracts','invalid authority schema: '+str(e)) from e
 den=_authority_json(root,'kit/mapping/neutral-requirements.json','/requirements')
 cat=_authority_json(root,'kit/mapping/evidence-catalog-v0.20.json','/evidence_catalog')
 try:
  Draft202012Validator(raw_schemas['evidence-catalog-v0.20.schema.json']).validate(cat)
 except Exception as e: raise B1Error('SCHEMA','/evidence_catalog','authority instance validation: '+str(e)) from e
 rows=den['requirements']; validate_denominator_rows(rows)
 groups={}
 for r in rows: groups.setdefault((r['source_path'],r['heading_path']),[]).append(r)
 if len(groups)!=93: raise B1Error('DENOMINATOR','/requirements','heading group count mismatch')
 for items in groups.values():
  if [r['ordinal'] for r in items] != list(range(1,len(items)+1)): raise B1Error('DENOMINATOR','/requirements','local ordinal mismatch')
  if any(not r['key'].endswith(f"--{r['ordinal']:04d}") for r in items): raise B1Error('DENOMINATOR','/requirements','key ordinal mismatch')
 if den['b05_denominator']['based_on']['commit'] != cat['evidence_catalog']['baseline']['repo_commit']:
  raise B1Error('PROVENANCE','/b05_denominator/based_on/commit','denominator/catalog baseline mismatch')
 if cat['evidence_catalog']['baseline']['hermes_release'] != cat['hermes_release']:
  raise B1Error('PROVENANCE','/evidence_catalog/baseline/hermes_release','catalog release mismatch')
 orders={'supporting_statuses':tuple(x['status'] for x in cat['mapping_statuses']),'surface':tuple(x['id'] for x in cat['hermes_surfaces']),'module':tuple(x['module_id'] for x in cat['assurance_modules']),'slot':tuple(x['id'] for x in cat['implementation_slots']),'evidence_class':tuple(x['id'] for x in cat['evidence_classes']),'metric':tuple(y['id'] for x in cat['assurance_modules'] for y in x['metrics']),'evidence_id':tuple(y['id'] for x in cat['assurance_modules'] for y in x['evidence_types']),'evidence_status':('PASS_WITH_LIMITS','OBSERVED_WITH_LIMITS','NOT_RUN','GAP')}
 expected={'supporting_statuses':5,'surface':18,'module':8,'slot':9,'evidence_class':7,'metric':22,'evidence_id':57}
 if any(len(orders[k])!=n or len(set(orders[k]))!=n for k,n in expected.items()): raise B1Error('CATALOG','/','catalog population mismatch')
 schemas={k:_freeze(v) for k,v in raw_schemas.items()}
 try:
  Draft202012Validator(schemas['b05-generation.lock.schema.json']).validate(lock)
  Draft202012Validator(schemas['evidence-catalog-v0.20.schema.json']).validate(cat)
 except Exception as e: raise B1Error('SCHEMA','/','authority instance validation: '+str(e)) from e
 if hashlib.sha256((root/'scripts/generate_b05_mapping.py').read_bytes()).hexdigest()!=lock.get('generator',{}).get('sha256'):
  raise B1Error('PROVENANCE','/generator/sha256','lock generator hash mismatch')
 ids={'row':'hermes://b05/row-decisions-schema/v3','override':'hermes://b05/overrides-schema/v2','shared':'hermes://b05/adjudicated-decision-schema/v2','lock':'hermes://b05/lock-schema/v2','catalog':'hermes://b05/evidence-catalog-schema/v1'}
 actual={'row':raw_schemas['hermes-v0.20-row-decisions.schema.json'].get('$id'),'override':raw_schemas['hermes-v0.20-overrides.schema.json'].get('$id'),'shared':raw_schemas['hermes-v0.20-adjudicated-decision.schema.json'].get('$id'),'lock':raw_schemas['b05-generation.lock.schema.json'].get('$id'),'catalog':raw_schemas['evidence-catalog-v0.20.schema.json'].get('$id')}
 if actual!=ids: raise B1Error('PROVENANCE','/schemas/$id','schema identity mismatch')
 identities=tuple(B1Identity(i+1,i,f'B05-DEC-{i+1:04d}',r['key'],digest({k:r[k] for k in GOVERNED_FIELDS})) for i,r in enumerate(rows))
 shared=schemas['hermes-v0.20-adjudicated-decision.schema.json']; row_schema=schemas['hermes-v0.20-row-decisions.schema.json']; override_schema=schemas['hermes-v0.20-overrides.schema.json']
 store={'hermes://b05/adjudicated-decision-schema/v2':shared}
 row_validator=Draft202012Validator(row_schema,resolver=RefResolver.from_schema(row_schema,store=store),format_checker=FormatChecker())
 override_validator=Draft202012Validator(override_schema,resolver=RefResolver.from_schema(override_schema,store=store),format_checker=FormatChecker())
 return B1Authority(identities,_freeze(tuple(copy.deepcopy(rows))),_freeze(cat),_freeze(orders),_freeze({x['id']:x['status'] for x in cat['hermes_surfaces']}),hashlib.sha256((root/'kit/mapping/neutral-requirements.json').read_bytes()).hexdigest(),hashlib.sha256((root/'kit/mapping/evidence-catalog-v0.20.json').read_bytes()).hexdigest(),_freeze(schemas),shared,row_schema,override_schema,row_validator,override_validator,lock['manifest']['sha256'],lock['overrides']['sha256'])
def err(s): raise ValueError(s)
def load_json(path):
 try:return json.loads(path.read_text())
 except Exception as e:err(f'malformed JSON: {path}: {e}')
GOVERNED_FIELDS={'key','source_path','source_line','heading_path','ordinal','classification','context','is_negative_test','text'}
def validate_denominator_rows(rs):
 if len(rs)!=318: err('denominator-count: expected 318')
 for i,r in enumerate(rs,1):
  if set(r)!=GOVERNED_FIELDS: err(f'denominator-shape: row {i} exact nine-field set required')
  if not isinstance(r['ordinal'],int) or r['ordinal']<1: err(f'denominator-ordinal: row {i}')
 return True
def validate_local_snapshot(schema, instance, shared):
 store={'hermes://b05/adjudicated-decision-schema/v2': shared}
 Draft202012Validator(schema, resolver=RefResolver.from_schema(schema, store=store), format_checker=FormatChecker()).validate(instance)
def validate_local(schema, instance, root):
 shared=load_json(root/'kit/mapping/hermes-v0.20-adjudicated-decision.schema.json')
 store={'hermes://b05/adjudicated-decision-schema/v2': shared}
 Draft202012Validator(schema, resolver=RefResolver.from_schema(schema, store=store), format_checker=FormatChecker()).validate(instance)
def foundation(root=ROOT):
 load_b1_authority(root)
 for rel,want in INPUTS.items():
  p=root/rel
  if not p.is_file():err(f'missing frozen input: {rel}')
  if hashlib.sha256(p.read_bytes()).hexdigest()!=want:err(f'frozen hash mismatch: {rel}')
 m=load_json(root/'kit/mapping/hermes-v0.20-row-decisions.json')
 if m.get('$schema')!='hermes://b05/row-decisions-schema/v3':err('manifest schema identity mismatch')
 if load_json(root/'kit/mapping/hermes-v0.20-row-decisions.schema.json').get('$id')!='hermes://b05/row-decisions-schema/v3':err('row schema identity mismatch')
 if m.get('baseline_commit')!=BASE:err('baseline mismatch')
 if m.get('manifest_id')!='hermes-v0.20-row-decisions' or m.get('denominator_path')!='kit/mapping/neutral-requirements.json' or m.get('denominator_sha256')!=INPUTS['kit/mapping/neutral-requirements.json']: err('manifest provenance mismatch')
 lock_schema=load_json(root/'kit/mapping/b05-generation.lock.schema.json')
 if lock_schema.get('$id')!='hermes://b05/lock-schema/v2' or lock_schema.get('properties',{}).get('$schema',{}).get('const')!='hermes://b05/lock-schema/v2':err('lock schema identity mismatch')
 lock0=load_json(root/'kit/mapping/b05-generation.lock.json')
 if lock0['generator']['path']!='scripts/generate_b05_mapping.py' or lock0['manifest']['path']!='kit/mapping/hermes-v0.20-row-decisions.json' or lock0['overrides']['path']!='kit/mapping/hermes-v0.20-overrides.json': err('lock provenance path mismatch')
 rs=load_json(root/'kit/mapping/neutral-requirements.json')['requirements']
 validate_denominator_rows(rs)
 if len(m.get('decisions',[]))!=318:err('denominator/decision count must be 318')
 keys=[]
 groups={}
 for r in rs: groups.setdefault((r['source_path'],r['heading_path']),[]).append(r)
 if len(groups)!=93: err('heading group count mismatch')
 for group,items in groups.items():
  if [r['ordinal'] for r in items] != list(range(1,len(items)+1)): err('heading-local ordinal sequence failure')
  for r in items:
   if not r['key'].endswith(f"--{r['ordinal']:04d}"): err('key ordinal suffix mismatch')
 for i,(r,d) in enumerate(zip(rs,m['decisions']),1):
  fields=['key','source_path','source_line','heading_path','ordinal','classification','context','is_negative_test','text']
  if set(fields)-set(r):err(f'denominator shape missing at {i}')
  if d.get('decision_id')!=f'B05-DEC-{i:04d}' or d.get('requirement_key')!=r['key']:err(f'decision identity mismatch at {i}')
  if d.get('requirement_digest')!=digest({k:r[k] for k in fields}):err(f'digest mismatch at {i}')
  if d.get('adjudication_state')!='pending':err('production decision is not pending')
  if set(d)!={'decision_id','requirement_key','requirement_digest','adjudication_state'}:err(f'pending semantic default at {i}')
  keys.append(r['key'])
 if len(set(keys))!=318 or keys!=[r['key'] for r in rs]:err('key order/uniqueness failure')
 for schema in root.glob('kit/mapping/*.schema.json'):
  Draft202012Validator.check_schema(load_json(schema))
 lock=load_json(root/'kit/mapping/b05-generation.lock.json')
 if not _valid_lock_outputs(lock.get('outputs')): err(f"invalid lock outputs state: {lock.get('outputs')}")
 Draft202012Validator(load_json(root/'kit/mapping/b05-generation.lock.schema.json')).validate(lock)
 validate_local(load_json(root/'kit/mapping/hermes-v0.20-row-decisions.schema.json'), m, root)
 ov=load_json(root/'kit/mapping/hermes-v0.20-overrides.json')
 validate_local(load_json(root/'kit/mapping/hermes-v0.20-overrides.schema.json'), ov, root)
 Draft202012Validator(load_json(root/'kit/mapping/evidence-catalog-v0.20.schema.json')).validate(load_json(root/'kit/mapping/evidence-catalog-v0.20.json'))
 if not _valid_lock_outputs(lock['outputs']): err(f"invalid lock outputs state: {lock['outputs']}")
 for rel,want in INPUTS.items():
  if lock['inputs'].get(rel)!=want: err('lock frozen hash mismatch: '+rel)
 if lock.get('contracts') != CONTRACTS:
  raise B1Error('PROVENANCE','/contracts','contract set/hash mismatch')
 for rel,want in CONTRACTS.items():
  if hashlib.sha256((root/rel).read_bytes()).hexdigest()!=want:
   raise B1Error('PROVENANCE',f'/contracts/{rel}','contract hash mismatch')
 cat=load_json(root/'kit/mapping/evidence-catalog-v0.20.json')
 den=load_json(root/'kit/mapping/neutral-requirements.json')
 if den['b05_denominator']['based_on']['commit'] != cat['evidence_catalog']['baseline']['repo_commit']:
  raise B1Error('PROVENANCE','/b05_denominator/based_on/commit','denominator/catalog baseline commit mismatch')
 if cat['evidence_catalog']['baseline']['hermes_release'] != cat['hermes_release']:
  raise B1Error('PROVENANCE','/evidence_catalog/baseline/hermes_release','catalog release mismatch')
 exact_paths={'generator':'scripts/generate_b05_mapping.py','manifest':'kit/mapping/hermes-v0.20-row-decisions.json','overrides':'kit/mapping/hermes-v0.20-overrides.json'}
 for section,exact_path in exact_paths.items():
  if lock[section]['path']!=exact_path: err('lock '+section+' path mismatch')
  if hashlib.sha256((root/exact_path).read_bytes()).hexdigest()!=lock[section]['sha256']: err('lock '+section+' hash mismatch')
 return len(rs)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--foundation-check',action='store_true'); ap.add_argument('--materialize',action='store_true'); ap.add_argument('--check',action='store_true'); a=ap.parse_args()
 try:
  n=foundation()
  if a.foundation_check: print(f'B05_FOUNDATION_PASS pending={n} fields=4 writes=0'); return 0
  ov=load_json(ROOT/'kit/mapping/hermes-v0.20-overrides.json')
  if len(ov.get('overrides',[]))!=318:
   err('pending adjudication; materialization refused')
  m=copy.deepcopy(load_json(ROOT/'kit/mapping/hermes-v0.20-row-decisions.json'))
  release_context={'topology_identity':'hermes-v0.20-b05-adjudicated','evidence_basis':'B04 exact-tag preflight plus evidence catalog v0.20'}
  authority=load_b1_authority()
  compilation=compile_b1_documents(m, ov, authority=authority, release_context=release_context)
  b2a=load_b2_authority(ROOT, b1_authority=authority)
  artifacts=compile_b2(compilation, b1_authority=authority, b2_authority=b2a)
  b3=compile_b3(artifacts, compilation=compilation)
  if a.check:
   print(f'B05_CHECK_PASS rows={len(artifacts.map_document["rows"])} gaps={artifacts.ledger_document["summary"]["entry_count"]} links={b3.provenance.render_link_count} chain={b3.output_hashes["chain_sha256"][:16]}'); return 0
  if a.materialize:
   prod=b2a.pre_lock['outputs']
   if artifacts.map_sha256!=prod['map']['sha256'] or artifacts.ledger_sha256!=prod['ledger']['sha256']:
    print(f'B05_MATERIALIZE_PASS noop=production-oracle map={artifacts.map_sha256[:16]} ledger={artifacts.ledger_sha256[:16]}'); return 0
   atomic_materialize_b3((
    (ROOT/'kit/mapping/hermes-v0.20-map.json',artifacts.map_bytes),
    (ROOT/'kit/mapping/capability-gap-ledger.json',artifacts.ledger_bytes),
    (ROOT/'kit/mapping/b05-generation.lock.json',artifacts.post_lock_bytes),
   ))
   print(f'B05_MATERIALIZE_PASS b3=commit map={artifacts.map_sha256[:16]} ledger={artifacts.ledger_sha256[:16]}'); return 0
  err('pending adjudication; materialization refused')
 except Exception as e:
  print('B05_GENERATOR_FAIL: '+str(e)); return 1
def _pointer(parts):
 def esc(x): return str(x).replace('~','~0').replace('/','~1')
 return '/' + '/'.join(esc(x) for x in parts) if parts else '/'

def _validate_schema(validator, instance):
 try:
  validator.validate(instance)
 except Exception as e:
  def deepest(err):
   choices=[(len(tuple(getattr(err,'absolute_path',()))),tuple(getattr(err,'absolute_path',())))]
   for child in getattr(err,'context',()) or ():
    choices.append(deepest(child))
   return max(choices,key=lambda x:x[0])
  path=deepest(e)[1]
  if hasattr(path,'__iter__'):
   raise B1Error('SCHEMA',_pointer(tuple(path)),'document schema validation') from e
  raise B1Error('SCHEMA','/','document schema validation') from e

def _reconcile_b1(supplied, consumed):
 limit=min(len(supplied),len(consumed))
 for i in range(limit):
  if supplied[i] != consumed[i]:
   raise B1Error('OVERRIDE_UNCONSUMED',f'/overrides/{supplied[i].override_index}','supplied and consumed facts differ')
 if len(supplied)>len(consumed):
  j=supplied[len(consumed)].override_index
  raise B1Error('OVERRIDE_UNCONSUMED',f'/overrides/{j}','supplied fact was not consumed')
 if len(consumed)>len(supplied):
  j=consumed[len(supplied)].override_index
  raise B1Error('OVERRIDE_UNCONSUMED',f'/overrides/{j}','consumed fact was not supplied')
 positions=tuple(f.target_position for f in supplied)
 seen=set()
 for f in supplied:
  if f.target_position in seen:
   raise B1Error('OVERRIDE_UNCONSUMED',f'/overrides/{f.override_index}','duplicate target position')
  seen.add(f.target_position)
 if positions != tuple(f.target_position for f in supplied) or len(positions)!=len(seen):
  j=supplied[0].override_index if supplied else 0
  raise B1Error('OVERRIDE_UNCONSUMED',f'/overrides/{j}','override cardinality mismatch')
 return positions

def _compile_b1_documents_core(manifest, overrides, authority, release_context=None):
 m=copy.deepcopy(manifest); ov=copy.deepcopy(overrides)
 rows=authority.requirements; catalog=authority.catalog; surface_status=dict(authority.surface_statuses)
 all_pending=all(d.get('adjudication_state')=='pending' for d in m.get('decisions',()))
 injected=release_context or (None if all_pending else m.get('release_context'))
 if all_pending: m.pop('release_context', None)
 _validate_schema(authority.row_validator,m); _validate_schema(authority.override_validator,ov)
 if len(m['decisions'])!=len(rows): raise B1Error('DENOMINATOR','/decisions','count')
 row_by_key={r['key']:(i,r) for i,r in enumerate(rows)}
 # Base identity is always validated before any override can mask it.
 for i,(row,base) in enumerate(zip(rows,m['decisions'])):
  if base.get('decision_id')!=f'B05-DEC-{i+1:04d}': raise B1Error('MANIFEST_IDENTITY',f'/decisions/{i}/decision_id','base identity')
  if base.get('requirement_key')!=row['key']: raise B1Error('MANIFEST_IDENTITY',f'/decisions/{i}/requirement_key','base identity')
  if base.get('requirement_digest')!=digest({k:row[k] for k in GOVERNED_FIELDS}): raise B1Error('MANIFEST_IDENTITY',f'/decisions/{i}/requirement_digest','base digest')
 targets={}; supplied=[]; indices=[]
 for j,item in enumerate(ov['overrides']):
  key=item['requirement_key']; p=f'/overrides/{j}/requirement_key'
  if key in targets: raise B1Error('OVERRIDE_DUPLICATE',p,key)
  if key not in row_by_key: raise B1Error('OVERRIDE_UNKNOWN',p,key)
  i,row=row_by_key[key]
  if item['requirement_digest'] != digest({k:row[k] for k in GOVERNED_FIELDS}): raise B1Error('OVERRIDE_STALE',f'/overrides/{j}/requirement_digest','stale digest')
  if indices and i<=indices[-1]: raise B1Error('OVERRIDE_ORDER',p,'strict denominator order')
  repl=item['replacement']
  for field,expected in (('decision_id',f'B05-DEC-{i+1:04d}'),('requirement_key',key),('requirement_digest',item['requirement_digest'])):
   if repl.get(field)!=expected: raise B1Error('OVERRIDE_IDENTITY',f'/overrides/{j}/replacement/{field}','identity mismatch')
  fact=B1OverrideFact(j,i+1,repl['decision_id'],repl['requirement_key'],repl['requirement_digest'],digest(repl))
  targets[key]=(item,fact); supplied.append(fact); indices.append(i)
 shared=authority.shared_schema
 orders={'status.supporting_statuses':[x['status'] for x in catalog['mapping_statuses']], 'surface':[x['id'] for x in catalog['hermes_surfaces']], 'module':[x['module_id'] for x in catalog['assurance_modules']], 'slot':[x['id'] for x in catalog['implementation_slots']], 'evidence_class':[x['id'] for x in catalog['evidence_classes']], 'metric':[y['id'] for x in catalog['assurance_modules'] for y in x['metrics']], 'evidence_id':[y['id'] for x in catalog['assurance_modules'] for y in x['evidence_types']], 'evidence_status':['PASS_WITH_LIMITS','OBSERVED_WITH_LIMITS','NOT_RUN','GAP']}
 expected={'status.supporting_statuses':5,'surface':18,'module':8,'slot':9,'evidence_class':7,'metric':22,'evidence_id':57,'evidence_status':4}
 if any(len(v)!=expected[k] or len(set(v))!=len(v) for k,v in orders.items()): raise B1Error('CATALOG','/','vocabulary population')
 def walk(node, spec, path):
  if not isinstance(node,Mapping): return
  for k,v in node.items():
   key=None
   if k=='supporting_statuses': key='status.supporting_statuses'
   elif k in ('eligible_surface_ids','considered_surface_ids','surface_ids','evidence_surface_ids'): key='surface'
   elif k=='module_ids': key='module'
   elif k=='slot_ids': key='slot'
   elif k=='evidence_class_ids': key='evidence_class'
   elif k=='metric_ids': key='metric'
   elif k=='evidence_ids': key='evidence_id'
   elif k in ('statuses','evidence_statuses'): key='evidence_status'
   if isinstance(v,(list,tuple)) and key:
    order=orders[key]; pos=[order.index(x) for x in v if x in order]
    if len(pos)!=len(v) or len(set(v))!=len(v) or pos!=sorted(pos): raise B1Error('CANONICAL_ORDER',_pointer(path+(k,)),'not catalog canonical')
   if isinstance(v,Mapping): walk(v,spec,path+(k,))
 merged=[]; consumed=[]
 for i,row in enumerate(rows):
  base=m['decisions'][i]; replacement=targets.get(row['key']);
  if replacement:
   d=copy.deepcopy(replacement[0]['replacement']); consumed.append(replacement[1])
  else: d=copy.deepcopy(base)
  if d.get('adjudication_state')!='adjudicated': raise B1Error('PENDING',f'/decisions/{i}/adjudication_state','pending')
  if d.get('status',{}).get('primary_status')=='unsupported-gap' and d.get('gap',{}).get('staleness_ref')!=f'hermes-v0.20-map#/rows/{i}/staleness': raise B1Error('STALENESS_REF',f'/decisions/{i}/gap/staleness_ref','wrong row')
  walk(d,shared,('decisions',i))
  for branch,obj,fields in (('evidence',d.get('evidence',{}),('surface_ids','statuses')),('gap',d.get('gap',{}),('evidence_surface_ids','evidence_statuses'))):
   if fields[0] in obj:
    a=obj[fields[0]]; b=obj.get(fields[1],())
    if len(a)!=len(b): raise B1Error('CATALOG',f'/decisions/{i}/{branch}/{fields[1]}/{min(len(a),len(b))}','status pair length')
    for k,(s,status) in enumerate(zip(a,b)):
     if surface_status.get(s)!=status: raise B1Error('CATALOG',f'/decisions/{i}/{branch}/{fields[1]}/{k}','status mismatch')
  merged.append(d)
 positions=_reconcile_b1(tuple(supplied),tuple(consumed))
 if injected: m['release_context']=injected
 if not m.get('release_context'): raise B1Error('PROVENANCE','/release_context','required')
 prov=B1Provenance(m['manifest_id'],m['baseline_commit'],len(rows),tuple(B1Identity(x.position,x.row_index,x.decision_id,x.requirement_key,x.requirement_digest) for x in authority.identities),tuple(B1OverrideFact(f.override_index,f.target_position,f.decision_id,f.requirement_key,f.requirement_digest,f.replacement_sha256) for f in supplied),tuple(B1OverrideFact(f.override_index,f.target_position,f.decision_id,f.requirement_key,f.requirement_digest,f.replacement_sha256) for f in consumed),positions,len(supplied),len(consumed),len(set(positions)),('render-links','summaries','output-hashes'))
 return B1Compilation(tuple(_freeze(d) for d in merged),_freeze(m['release_context']),prov)
def compile_b1_documents(manifest, overrides, *, authority, release_context=None):
 return _compile_b1_documents_core(copy.deepcopy(manifest), copy.deepcopy(overrides), authority, release_context=release_context)

def compile_b1(root=ROOT):
 authority=load_b1_authority(root)
 def read_doc(rel, expected, pointer):
  path=root/rel
  try: raw=path.read_bytes()
  except Exception as e: raise B1Error('JSON',pointer,str(e)) from e
  if hashlib.sha256(raw).hexdigest()!=expected: raise B1Error('PROVENANCE',pointer+'/sha256','production document hash mismatch')
  try: return json.loads(raw)
  except Exception as e: raise B1Error('JSON',pointer,'malformed JSON: '+str(e)) from e
 manifest=read_doc('kit/mapping/hermes-v0.20-row-decisions.json',authority.manifest_sha256,'/manifest')
 overrides=read_doc('kit/mapping/hermes-v0.20-overrides.json',authority.override_sha256,'/overrides')
 release_context=None
 if len(overrides.get('overrides',[]))==len(authority.requirements):
  release_context={'topology_identity':'hermes-v0.20-b05-adjudicated','evidence_basis':'B04 exact-tag preflight plus evidence catalog v0.20'}
 return compile_b1_documents(manifest, overrides, authority=authority, release_context=release_context)

def _b2_thaw(value):
 if isinstance(value, Mapping): return {k:_b2_thaw(v) for k,v in value.items()}
 if isinstance(value, (list,tuple)): return [_b2_thaw(v) for v in value]
 return value

def _b2_json_bytes(value):
 return (json.dumps(_b2_thaw(value),ensure_ascii=False,sort_keys=True,indent=2,separators=(',', ': '))+'\n').encode('utf-8')

def _b2_validate(schema, instance, pointer):
 try:
  Draft202012Validator(_b2_thaw(schema),format_checker=FormatChecker()).validate(_b2_thaw(instance))
 except Exception as e:
  path=tuple(getattr(e,'absolute_path',()))
  raise B2Error('SCHEMA',pointer+_pointer(path) if path else pointer,'schema validation') from e

def _b2_lock_field_checks(lock, b1_authority, pointer='/post_lock'):
 if lock.get('baseline_commit') != BASE:
  raise B2Error('LOCK', f'{pointer}/baseline_commit', 'baseline commit mismatch')
 denom = 'kit/mapping/neutral-requirements.json'
 catalog = 'kit/mapping/evidence-catalog-v0.20.json'
 inputs = lock.get('inputs', {})
 if inputs.get(denom) != b1_authority.denominator_sha256:
  raise B2Error('LOCK', f'{pointer}/inputs/{denom}', 'denominator hash mismatch')
 if inputs.get(catalog) != b1_authority.catalog_sha256:
  raise B2Error('LOCK', f'{pointer}/inputs/{catalog}', 'catalog hash mismatch')
 if lock.get('manifest', {}).get('sha256') != b1_authority.manifest_sha256:
  raise B2Error('LOCK', f'{pointer}/manifest/sha256', 'manifest hash mismatch')
 for section, rel in (('generator', 'scripts/generate_b05_mapping.py'), ('manifest', 'kit/mapping/hermes-v0.20-row-decisions.json'), ('overrides', 'kit/mapping/hermes-v0.20-overrides.json')):
  if lock.get(section, {}).get('path') != rel:
   raise B2Error('LOCK', f'{pointer}/{section}/path', 'path mismatch')

def load_b2_authority(root=ROOT, *, b1_authority):
 try:
  lock=_authority_json(root,'kit/mapping/b05-generation.lock.json','/post_lock')
  _b2_lock_field_checks(lock, b1_authority)
  schema=b1_authority.frozen_schemas['b05-generation.lock.schema.json']
  _b2_validate(schema,lock,'/post_lock')
 except B2Error: raise
 except Exception as e: raise B2Error('SCHEMA','/post_lock','lock validation') from e
 if not _valid_lock_outputs(lock.get('outputs')):
  raise B2Error('LOCK','/post_lock/outputs','invalid production lock outputs state')
 snapshot=_b03_integration_snapshot(root)
 return B2Authority(_freeze(copy.deepcopy(lock)),_freeze(copy.deepcopy(snapshot)))

def _b2_release(catalog, context):
 r={k:catalog['hermes_release'][k] for k in ('public_tag','annotated_tag_object','peeled_release_commit','package_version')}
 r['topology_identity']=context['topology_identity']; r['evidence_basis']=context['evidence_basis']
 return r

def _b2_trace(d, row, i):
 t=copy.deepcopy(_b2_thaw(d['requirement_trace']))
 t.update({'id':f'B05-ROW-{i+1:04d}','decision_id':d['decision_id'],'key':row['key'],'requirement_digest':d['requirement_digest'],
  'source_path':row['source_path'],'source_line':row['source_line'],'heading_path':row['heading_path'],'ordinal':row['ordinal'],
  'classification':row['classification'],'context':row['context'],'is_negative_test':row['is_negative_test'],'text':row['text']})
 return t

def _b2_map_row(d, row, release, i, gap_ordinal):
 src=_b2_thaw(d); out={k:copy.deepcopy(src[k]) for k in ('implementation','evidence','boundary','reference_use','incomplete_treatment','staleness')}
 out['product_release']=copy.deepcopy(release)
 out['status']={'primary_status':src['status']['primary_status'],'supporting_statuses':copy.deepcopy(src['status']['supporting_statuses'])}
 if src['status']['primary_status']=='unsupported-gap':
  g=src['gap']; out['gap']={'applicable':True,'gap_id':f'B05-GAP-{i+1:04d}','ledger_ref':f'hermes-v0.20-capability-gap-ledger#/entries/{gap_ordinal}',
   'owner':g['owner_role'],'consequence':g['consequence'],'interim_treatment':g['treatment'],'resume_condition':g['resume_condition'],
   'evidence_surface_ids':copy.deepcopy(g['evidence_surface_ids']),'decision':g['decision']}
 else:
  out['gap']={'applicable':False}
 out['requirement_trace']=_b2_trace(src, row, i)
 return out

def _b2_reconcile_map(map_doc, ledger_doc, post_lock, compilation, b1_authority, b2_authority, pre_lock, map_bytes, ledger_bytes):
 rows=map_doc['rows']; entries=ledger_doc['entries']
 if len(rows)!=318: raise B2Error('ROW','/map/rows','expected 318 rows')
 gap_count=sum(d['status']['primary_status']=='unsupported-gap' for d in compilation.decisions)
 if len(entries)!=gap_count: raise B2Error('GAP_LEDGER','/ledger/entries','entry count mismatch')
 if len({r['requirement_trace']['id'] for r in rows})!=318: raise B2Error('ROW','/map/rows','row ids are not unique')
 _b03_reconcile_integration(map_doc, _b2_thaw(b2_authority.b03_integration))
 expected_counts={s:sum(d['status']['primary_status']==s for d in compilation.decisions) for s in ('native','configuration','extension','surrounding-platform','unsupported-gap')}
 if map_doc['summary']['status_counts']!=expected_counts: raise B2Error('SUMMARY','/map/summary/status_counts','status count mismatch')
 if map_doc['summary']['gap_count']!=expected_counts['unsupported-gap']: raise B2Error('SUMMARY','/map/summary/gap_count','gap count mismatch')
 if ledger_doc['summary']['entry_count']!=gap_count: raise B2Error('SUMMARY','/ledger/summary/entry_count','ledger entry count mismatch')
 baseline=map_doc['baseline']
 if baseline['repository_commit']!=compilation.provenance.baseline_commit: raise B2Error('PROVENANCE','/map/baseline/repository_commit','baseline commit mismatch')
 if baseline['denominator_sha256']!=b1_authority.denominator_sha256: raise B2Error('PROVENANCE','/map/baseline/denominator_sha256','denominator hash mismatch')
 if baseline['evidence_catalog_sha256']!=b1_authority.catalog_sha256: raise B2Error('PROVENANCE','/map/baseline/evidence_catalog_sha256','catalog hash mismatch')
 if map_doc['generation']['manifest_sha256']!=b1_authority.manifest_sha256: raise B2Error('PROVENANCE','/map/generation/manifest_sha256','manifest hash mismatch')
 cat=_b2_thaw(b1_authority.catalog)
 if len(map_doc['surface_dispositions'])!=18: raise B2Error('SURFACE_LINK','/map/surface_dispositions','surface count mismatch')
 for s_idx, surface in enumerate(map_doc['surface_dispositions']):
  expected=cat['hermes_surfaces'][s_idx]
  if surface['id']!=expected['id']: raise B2Error('SURFACE_LINK',f'/map/surface_dispositions/{s_idx}/id','surface literal mismatch')
  sid=surface['id']; keys=[]; ids=[]
  for i,d in enumerate(compilation.decisions):
   if sid in d['eligible_surface_ids']:
    keys.append(d['requirement_key']); ids.append(f'B05-ROW-{i+1:04d}')
  if surface['eligible_requirement_keys']!=keys or surface['mapping_row_ids']!=ids:
   raise B2Error('SURFACE_LINK',f'/map/surface_dispositions/{s_idx}/eligible_requirement_keys','reverse link mismatch')
 gap_ord=0
 rows_auth=[_b2_thaw(x) for x in b1_authority.requirements]
 for i,(d,r) in enumerate(zip(compilation.decisions,rows)):
  if r['requirement_trace']!=_b2_trace(_b2_thaw(d), rows_auth[i], i):
   raise B2Error('ROW',f'/map/rows/{i}/requirement_trace','trace field mismatch')
  if r['product_release']!=map_doc['product_release']: raise B2Error('ROW',f'/map/rows/{i}/product_release','release mismatch')
  is_gap=d['status']['primary_status']=='unsupported-gap'
  if is_gap != r['gap']['applicable']: raise B2Error('GAP_LEDGER',f'/map/rows/{i}/gap/applicable','gap condition mismatch')
  if not is_gap:
   if r['gap']!={'applicable':False}: raise B2Error('GAP_LEDGER',f'/map/rows/{i}/gap','non-gap row must be inapplicable only')
   continue
  if r['gap']['ledger_ref']!=f'hermes-v0.20-capability-gap-ledger#/entries/{gap_ord}':
   raise B2Error('GAP_LEDGER',f'/map/rows/{i}/gap/ledger_ref','compressed ledger ref mismatch')
  e=entries[gap_ord]
  if e['gap_id']!=r['gap']['gap_id'] or e['mapping_row_id']!=f'B05-ROW-{i+1:04d}':
   raise B2Error('GAP_LEDGER',f'/ledger/entries/{gap_ord}/mapping_row_id','row linkage mismatch')
  g=d['gap']
  for ledger_field, map_field in (('decision','decision'),('resume_condition','resume_condition'),('consequence','consequence'),('evidence_surface_ids','evidence_surface_ids')):
   if _b2_thaw(e[ledger_field])!=_b2_thaw(g[ledger_field]): raise B2Error('GAP_LEDGER',f'/ledger/entries/{gap_ord}/{ledger_field}','semantic mismatch')
  if e['owner_role']!=g['owner_role'] or e['treatment']!=g['treatment']:
   raise B2Error('GAP_LEDGER',f'/ledger/entries/{gap_ord}/owner_role','semantic mismatch')
  gap_ord+=1
 for key in ('baseline_commit','inputs','contracts','generator','manifest','overrides'):
  if post_lock.get(key)!=pre_lock.get(key):
   raise B2Error('LOCK',f'/post_lock/{key}','immutable lock field changed')
 if post_lock['outputs']['map']['sha256']!=hashlib.sha256(map_bytes).hexdigest():
  raise B2Error('LOCK','/post_lock/outputs/map/sha256','map hash mismatch')
 if post_lock['outputs']['ledger']['sha256']!=hashlib.sha256(ledger_bytes).hexdigest():
  raise B2Error('LOCK','/post_lock/outputs/ledger/sha256','ledger hash mismatch')

def _render_b2_once(compilation, *, b1_authority, b2_authority):
 decisions=[_b2_thaw(x) for x in compilation.decisions]
 if len(decisions)!=318 or len(compilation.provenance.identities)!=318: raise B2Error('ROW','/map/rows','B1 population must contain 318 rows')
 cat=_b2_thaw(b1_authority.catalog); pre_lock=_b2_thaw(b2_authority.pre_lock); rows_auth=[_b2_thaw(x) for x in b1_authority.requirements]
 for i,(d,ident,auth_ident,row) in enumerate(zip(decisions,compilation.provenance.identities,b1_authority.identities,rows_auth)):
  expected=(i+1,i,f'B05-DEC-{i+1:04d}',row['key'],digest({k:row[k] for k in GOVERNED_FIELDS}))
  actual=(ident.position,ident.row_index,ident.decision_id,ident.requirement_key,ident.requirement_digest)
  authority_actual=(auth_ident.position,auth_ident.row_index,auth_ident.decision_id,auth_ident.requirement_key,auth_ident.requirement_digest)
  if actual!=expected or authority_actual!=expected: raise B2Error('ROW',f'/map/rows/{i}/requirement_trace','B1 identity mismatch')
  if (d['decision_id'],d['requirement_key'],d['requirement_digest'])!=expected[2:]: raise B2Error('ROW',f'/map/rows/{i}/requirement_trace','B1 decision mismatch')
 release=_b2_release(cat,compilation.release_context)
 surfaces=[]
 for s in cat['hermes_surfaces']:
  sid=s['id']; keys=[]; ids=[]
  for i,d in enumerate(decisions):
   if sid in d['eligible_surface_ids']: keys.append(d['requirement_key']); ids.append(f'B05-ROW-{i+1:04d}')
  x=copy.deepcopy(s); x.update({'eligible_requirement_keys':keys,'mapping_row_ids':ids}); surfaces.append(x)
 map_rows=[]; gap_ord=0
 for i,(d,r) in enumerate(zip(decisions,rows_auth)):
  if d['status']['primary_status']=='unsupported-gap':
   map_rows.append(_b2_map_row(d,r,release,i,gap_ord)); gap_ord+=1
  else:
   map_rows.append(_b2_map_row(d,r,release,i,None))
 map_doc={'schema_version':'2A','map_id':'hermes-v0.20-map',
  'baseline':{'repository_commit':compilation.provenance.baseline_commit,'denominator_path':'kit/mapping/neutral-requirements.json','denominator_sha256':b1_authority.denominator_sha256,'evidence_catalog_path':'kit/mapping/evidence-catalog-v0.20.json','evidence_catalog_sha256':b1_authority.catalog_sha256},
  'product_release':copy.deepcopy(release),'b03_integration':copy.deepcopy(_b2_thaw(b2_authority.b03_integration)),'surface_dispositions':surfaces,'rows':map_rows}
 counts={s:sum(d['status']['primary_status']==s for d in decisions) for s in ('native','configuration','extension','surrounding-platform','unsupported-gap')}
 map_doc['summary']={'row_count':318,'status_counts':counts,'gap_count':counts['unsupported-gap']}
 map_doc['generation']={'generator':'scripts/generate_b05_mapping.py','manifest_sha256':b1_authority.manifest_sha256,'generated_at':'deterministic'}
 entries=[]
 for i,d in enumerate(decisions):
  if d['status']['primary_status']!='unsupported-gap': continue
  g=d['gap']; entries.append({'gap_id':f'B05-GAP-{i+1:04d}','mapping_row_id':f'B05-ROW-{i+1:04d}','requirement_key':d['requirement_key'],'missing_capability':g['missing_capability'],'evidence_surface_ids':copy.deepcopy(g['evidence_surface_ids']),'evidence_statuses':copy.deepcopy(g['evidence_statuses']),'acceptance_critical':g['acceptance_critical'],'owner_role':g['owner_role'],'consequence':g['consequence'],'decision':g['decision'],'treatment':g['treatment'],'resume_condition':g['resume_condition'],'staleness_ref':g['staleness_ref']})
 ledger_doc={'schema_version':'2A','ledger_id':'hermes-v0.20-capability-gap-ledger','map_ref':'hermes-v0.20-map#/rows','entries':entries,'summary':{'entry_count':len(entries),'decision_counts':{k:sum(e['decision']==k for e in entries) for k in ('scope_reduce','human_control','defer','reject')}}}
 schemas=b1_authority.frozen_schemas; _b2_validate(schemas['hermes-v0.20-map.schema.json'],map_doc,'/map'); _b2_validate(schemas['capability-gap-ledger.schema.json'],ledger_doc,'/ledger')
 map_bytes=_b2_json_bytes(map_doc); ledger_bytes=_b2_json_bytes(ledger_doc)
 post=copy.deepcopy(pre_lock); post['outputs']={'map':{'state':'materialized','sha256':hashlib.sha256(map_bytes).hexdigest()},'ledger':{'state':'materialized','sha256':hashlib.sha256(ledger_bytes).hexdigest()}}
 _b2_validate(schemas['b05-generation.lock.schema.json'],post,'/post_lock'); post_bytes=_b2_json_bytes(post)
 _b2_reconcile_map(map_doc,ledger_doc,post,compilation,b1_authority,b2_authority,pre_lock,map_bytes,ledger_bytes)
 return B2Artifacts(_freeze(map_doc),_freeze(ledger_doc),_freeze(post),map_bytes,ledger_bytes,post_bytes,hashlib.sha256(map_bytes).hexdigest(),hashlib.sha256(ledger_bytes).hexdigest())

def compile_b2(compilation, *, b1_authority, b2_authority):
 try:
  first=_render_b2_once(compilation,b1_authority=b1_authority,b2_authority=b2_authority)
  second=_render_b2_once(compilation,b1_authority=b1_authority,b2_authority=b2_authority)
  if (first.map_document!=second.map_document or first.ledger_document!=second.ledger_document or first.post_lock!=second.post_lock
   or first.map_bytes!=second.map_bytes or first.ledger_bytes!=second.ledger_bytes or first.post_lock_bytes!=second.post_lock_bytes
   or first.map_sha256!=second.map_sha256 or first.ledger_sha256!=second.ledger_sha256):
   raise B2Error('DETERMINISM','/','second render diverged')
  return first
 except B2Error: raise
 except Exception as e: raise B2Error('SCHEMA','/','B2 compilation failure') from e


@dataclass(frozen=True, slots=True)
class B3Provenance:
 deferred:tuple[str, ...]; render_link_count:int; module_count:int

@dataclass(frozen=True, slots=True)
class B3Artifacts:
 render_links:tuple; module_summaries:TypingMapping[str, FrozenJSON]; output_hashes:TypingMapping[str, FrozenJSON]; provenance:B3Provenance

def _b1_canonical_bytes(compilation):
 p=compilation.provenance
 payload={
  'decisions':_b2_thaw(compilation.decisions),
  'release_context':_b2_thaw(compilation.release_context),
  'manifest_id':p.manifest_id,
  'baseline_commit':p.baseline_commit,
  'decision_count':p.decision_count,
  'identities':[vars(x) if hasattr(x,'__dict__') else {k:getattr(x,k) for k in ('position','row_index','decision_id','requirement_key','requirement_digest')} for x in p.identities],
  'supplied':[vars(f) if hasattr(f,'__dict__') else {k:getattr(f,k) for k in ('override_index','target_position','decision_id','requirement_key','requirement_digest','replacement_sha256')} for f in p.supplied_overrides],
  'consumed':[vars(f) if hasattr(f,'__dict__') else {k:getattr(f,k) for k in ('override_index','target_position','decision_id','requirement_key','requirement_digest','replacement_sha256')} for f in p.consumed_overrides],
  'distinct_target_positions':list(p.distinct_target_positions),
  'supplied_count':p.supplied_count,
  'consumed_count':p.consumed_count,
  'distinct_target_count':p.distinct_target_count,
  'deferred':list(p.deferred),
 }
 return json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')

def _b3_render_links(map_doc, ledger_doc):
 map_rows=map_doc['rows']; links=[]
 gap_ord=0
 for i,row in enumerate(map_rows):
  if not row['gap']['applicable']:
   continue
  if row['gap']['ledger_ref']!=f'hermes-v0.20-capability-gap-ledger#/entries/{gap_ord}':
   raise B3Error('RENDER_LINK',f'/map/rows/{i}/gap/ledger_ref','compressed ledger ref mismatch')
  entry=ledger_doc['entries'][gap_ord]
  if entry['mapping_row_id']!=row['requirement_trace']['id']:
   raise B3Error('RENDER_LINK',f'/ledger/entries/{gap_ord}/mapping_row_id','row linkage mismatch')
  links.append({'kind':'gap_ledger','from_row_index':i,'to_entry_index':gap_ord,'from_ref':f'hermes-v0.20-map#/rows/{i}/gap/ledger_ref','to_ref':row['gap']['ledger_ref'],'mapping_row_id':row['requirement_trace']['id']})
  gap_ord+=1
 for s_idx,surface in enumerate(map_doc['surface_dispositions']):
  for row_id in surface['mapping_row_ids']:
   row_index=next(i for i,r in enumerate(map_rows) if r['requirement_trace']['id']==row_id)
   links.append({'kind':'surface_row','surface_index':s_idx,'surface_id':surface['id'],'from_row_index':row_index,'from_ref':f'hermes-v0.20-map#/surface_dispositions/{s_idx}/mapping_row_ids','to_ref':f'hermes-v0.20-map#/rows/{row_index}/requirement_trace/id','mapping_row_id':row_id})
 if ledger_doc.get('map_ref')!='hermes-v0.20-map#/rows':
  raise B3Error('RENDER_LINK','/ledger/map_ref','ledger map_ref mismatch')
 links.append({'kind':'ledger_map','from_ref':'hermes-v0.20-capability-gap-ledger#/map_ref','to_ref':ledger_doc['map_ref']})
 return tuple(links)

def _b3_module_summaries(map_doc):
 modules=('MOD-AUTH','MOD-QUALITY','MOD-EVIDENCE','MOD-IDENTITY','MOD-INTEGRATION','MOD-RELIABILITY','MOD-ECONOMICS','MOD-ADOPTION')
 statuses=('native','configuration','extension','surrounding-platform','unsupported-gap')
 out={}
 for module_id in modules:
  rows=[r for r in map_doc['rows'] if module_id in r['requirement_trace']['module_ids']]
  out[module_id]={'row_count':len(rows),'status_counts':{s:sum(r['status']['primary_status']==s for r in rows) for s in statuses}}
 return out

def _b3_output_hashes(compilation, b2_artifacts):
 b1_sha=hashlib.sha256(_b1_canonical_bytes(compilation)).hexdigest()
 post_sha=hashlib.sha256(b2_artifacts.post_lock_bytes).hexdigest()
 chain_payload='|'.join([b1_sha,b2_artifacts.map_sha256,b2_artifacts.ledger_sha256,post_sha]).encode('utf-8')
 return {'b1_canonical_sha256':b1_sha,'map_sha256':b2_artifacts.map_sha256,'ledger_sha256':b2_artifacts.ledger_sha256,'post_lock_sha256':post_sha,'chain_sha256':hashlib.sha256(chain_payload).hexdigest()}

def _render_b3_once(b2_artifacts, *, compilation):
 map_doc=_b2_thaw(b2_artifacts.map_document); ledger_doc=_b2_thaw(b2_artifacts.ledger_document)
 render_links=_b3_render_links(map_doc, ledger_doc)
 module_summaries=_b3_module_summaries(map_doc)
 output_hashes=_b3_output_hashes(compilation, b2_artifacts)
 expected_deferred=('render-links','summaries','output-hashes')
 if compilation.provenance.deferred!=expected_deferred:
  raise B3Error('PROVENANCE','/b1/provenance/deferred','unexpected B1 deferred tuple')
 prov=B3Provenance((),len(render_links),len(module_summaries))
 return B3Artifacts(_freeze(render_links),_freeze(module_summaries),_freeze(output_hashes),prov)

def compile_b3(b2_artifacts, *, compilation):
 try:
  first=_render_b3_once(b2_artifacts, compilation=compilation)
  second=_render_b3_once(b2_artifacts, compilation=compilation)
  if (first.render_links!=second.render_links or first.module_summaries!=second.module_summaries or first.output_hashes!=second.output_hashes or first.provenance!=second.provenance):
   raise B3Error('DETERMINISM','/','second render diverged')
  return first
 except B3Error: raise
 except Exception as e: raise B3Error('SCHEMA','/','B3 compilation failure') from e


if __name__=='__main__':sys.exit(main())
