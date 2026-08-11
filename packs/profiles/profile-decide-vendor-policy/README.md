# Profile: decide-vendor-policy

Hermes profile distribution for **S1 Decide** — vendor-policy exception assessment.

## Mission shape

Ordinary user states an outcome: *"Assess this vendor exception request and recommend approve, defer, or deny with conditions."*

The operator does not pick model, tools, or verifier topology — organization policy resolves `bundle-s1-decide`.

## Corpus (read-only)

- `reference-suite/s1-decide/vendor-policy-corpus/org-policy-v3.2.md`
- `reference-suite/s1-decide/vendor-policy-corpus/exception-request-cloudsync.md`
- `reference-suite/s1-decide/questionnaire.json`

## Output contract

Respond with **JSON only**:

```json
{
  "recommendation": "approve|approve-with-conditions|defer-pending-legal|deny",
  "conditions": ["..."],
  "citations": ["document#anchor", "..."],
  "external_action": false
}
```

No external sends. No contract execution. Recommendation only.

## Install (live Hermes host)

```bash
hermes profile install "$(pwd)" --name decide-vendor-policy -y
```

From this directory (`packs/profiles/profile-decide-vendor-policy`).
