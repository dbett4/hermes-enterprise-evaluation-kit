# Vendor-policy recommendation profile

This is the Hermes profile for S1, the fictional vendor-policy review.

## Job

A user asks: *“Assess this vendor exception request and recommend approve, defer, or
deny with conditions.”*

Organization policy selects `bundle-s1-decide`; the user does not choose the model,
tools, or checking setup.

## Read-only source files

- `reference-suite/s1-decide/vendor-policy-corpus/org-policy-v3.2.md`
- `reference-suite/s1-decide/vendor-policy-corpus/exception-request-cloudsync.md`
- `reference-suite/s1-decide/questionnaire.json`

## Output

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

## Install on a Hermes host

```bash
hermes profile install "$(pwd)" --name decide-vendor-policy -y
```

From this directory (`packs/profiles/profile-decide-vendor-policy`).
