# Nimbus Widgets Inc. — Third-Party Vendor Data Handling Policy v3.2

**Status:** synthetic fixture for reference suite S1; not a real organization policy.

## Scope

This policy governs SaaS vendors that process Nimbus Widgets customer metadata in the **synthetic-internal** data zone.

## Retention requirements

| Data class | Maximum retention | Offboarding requirement |
|---|---|---|
| Customer contact records | 24 months | Delete within 30 days of contract termination |
| Usage telemetry (aggregated) | 12 months | Delete within 30 days |
| Support ticket content | 36 months | Export then delete within 60 days |

## Exception criteria

A vendor may request a retention exception only when **all** of the following hold:

1. **Business necessity:** the vendor documents a concrete operational need that cannot be met with export-and-delete.
2. **Data minimization:** the exception applies to the smallest data subset possible; no blanket retention extensions.
3. **Encryption at rest:** vendor confirms AES-256 or equivalent for stored data.
4. **Subprocessor disclosure:** all subprocessors are listed with data categories and regions.
5. **Contractual addendum:** Legal approves a time-bounded addendum with explicit expiry (maximum 12 months).
6. **No production credentials:** exception data must not include production API keys, payment instruments, or employee PII beyond ticket author email.

## Deny conditions (fail closed)

- Exception exceeds 12 months without executive waiver record.
- Vendor cannot confirm encryption at rest.
- Requested retention applies to payment card data (always denied).
- Vendor refuses subprocessor disclosure.

## Recommendation bounds for agent output

Agents may recommend **approve**, **approve-with-conditions**, **defer-pending-legal**, or **deny**. Agents may not execute contractual changes or contact the vendor directly.
