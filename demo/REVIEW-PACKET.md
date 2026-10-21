# Independent review packet for PR #1

This is a public, synthetic-key OpenEMR D05 component replay. It is not a production OpenEMR deployment. The PR was authored and corrected by `github-actions[bot]`. `stperic` is the requested independent reviewer of the current corrected head `3d04a6005fdee741b5f56c76fa5043232370f119`.

## What changed

The pinned vulnerable head `b86d9cf413e01cba27dccdf96c27aed66bfcf826` placed the Stripe `gateway_api_key` global in browser JavaScript. The corrected head removes that assignment from the Stripe branch. The synthetic PHP render check failed on the first head and passed on the corrected head. This check proves only the isolated Stripe client/server boundary and a payment stub. The Authorize.Net API Login ID classification and a full transaction are outside the oracle.

## Snyk Code

The raw Snyk Code CLI scans of the exact PR heads are in [vulnerable-head-snyk.sarif.json](evidence/vulnerable-head-snyk.sarif.json) and [fixed-head-snyk.sarif.json](evidence/fixed-head-snyk.sarif.json). Both completed with exit code 1 and 36 findings: 35 `php/XSS` and one `php/ServerLeak`. The deleted line shifts some locations in the corrected scan. The payment credential disclosure was not reported as such. Neither a matching count nor that miss proves the other findings are false positives.

The fixed scan file's SHA-256 is `fc00cfd3a839b99c98e3f6468cc9adea094abddc269d421a67bd47499db6ada5`. The protected workflow checks this digest and the count before it can consider a human disposition. Review the findings and decide which, if any, are blocking for this scoped derivative. If any concern remains blocking, request changes instead of approving.

## Jev, specialist and trace

The captured [Jev route](evidence/jev-routing.json) selected boundary, construction, data and SQL specialist actions. It also estimated insufficient context at 90%, so human triage is required. The [Sonnet 5.5 boundary review](evidence/specialist-boundary.txt) completed after an earlier output-limit attempt. Its three findings are model claims, not verified vulnerabilities. The decrypted versus stored Stripe value and Authorize.Net API Login ID semantics remain open review questions. Decide whether the other selected specialist actions need execution or can be closed for this narrowly scoped correction, with a reason.

The `trace.yaml` and `TRACE-REVIEW.md` link a demo-authored draft need, risk and `RC-PAYMENT-SECRET-SERVER` control to the PHP files and the synthetic boundary test. This is a retrospective what-if, not an upstream OpenEMR requirement. Accept or reject this proposed demo control and its links as part of review.

## How the gate uses your decision

GitHub branch protection requires the source-pinned `demo/policy-gate` status from GitHub Actions App 15368 and one current-head approval by someone other than the last pusher. The trusted workflow runs the payment oracle. It will continue to publish PENDING until the latest `stperic` review on the exact fixed head is APPROVED and contains all of these lines:

```text
D05-HEAD: 3d04a6005fdee741b5f56c76fa5043232370f119
D05-SNYK-SHA256: fc00cfd3a839b99c98e3f6468cc9adea094abddc269d421a67bd47499db6ada5
D05-SNYK-DISPOSITION: accepted-for-scoped-demo
D05-ROUTING-DISPOSITION: selected-work-reviewed
D05-TRACE-DISPOSITION: accepted-retrospective-demo-control
D05-SNYK-RATIONALE: <at least 20 characters explaining the finding disposition>
D05-ROUTING-RATIONALE: <at least 20 characters explaining the specialist scope decision>
```

These lines are an accountable human attestation, not a model output or a shortcut around review. Include them only if the linked evidence supports your decision. You can request changes, decline approval or leave the gate pending. A later PR commit requires a new scan, payment check and approval for that head. The protected workflow never accepts a review of an earlier head.
