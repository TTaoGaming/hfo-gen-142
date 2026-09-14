# Shared workload profiles — workshop R0

Consumer: the Hatchery G2/G3 implementer and operator selecting the first real
workload. These profiles share work/attempt identity, immutable input, finite
resources, adapter binding, artifact receipt and independent acceptance.
Only bootstrap.reduce.v1 is implemented in this bootstrap release.

| Profile | Input | Result for the human/consumer | Required acceptance |
|---|---|---|---|
| Evolution | pinned candidate, evaluator, dataset, search budget | measured candidates, diverse archive, selected successor, reproducible artifact | frozen evaluator plus independent replay; two generations and recovery |
| Research | question, scope, allowed sources, freshness, token/time budget | concise answer, cited claims, disagreements, unknowns, source dates | factual claims checked against retrieved sources; model prose alone is insufficient |
| Application preparation | user-approved resume facts, job criteria, maximum roles | deduplicated shortlist, matched evidence, tailored drafts, field-by-field review packet | no invented qualifications; human checks exact recipient, attachments and final answers |
| Other bounded task | explicit tool capabilities, input, output oracle, effect ceiling | immutable artifact with receipt | reject if capability, authority or success oracle is missing |

Kimi, Gemini, OpenRouter and Ollama are interchangeable only where the workload
accepts their measured capabilities and identity guarantees. Model/provider
selection does not alter permissions or the evaluator. Existing OpenClaw/n8n
tools can implement a step; neither is required on every host.

Default external-effect policy is PREPARE_ONLY. A submission requires separate
current authorization binding the exact recipient/action and artifact digest.
Editing a draft invalidates its prior send approval. Browser preparation may
itself transmit/save data: remote draft/autosave and document uploads must be
explicitly included in the workload's authority, not hidden under 'fill only'.
An ambiguous send is held for reconciliation, never blindly retried. Captcha,
attestations and human-only identity steps surface as named manual actions.

'One click send' is a target interaction, not a promise that every employer's
form supports it. Prefer a complete local review packet where remote staging is
unavailable. Personal resumes, answers and application records stay out of this
public repository and its public CI artifacts.

For arbitrary tasks, extend an existing native adapter with a specific admitted
capability; never turn a model-generated command into unrestricted host access.
Only one autonomous evolutionary cell is admitted after the Gen142 gates pass.
