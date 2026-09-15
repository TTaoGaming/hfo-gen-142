# READY TO SEND — Packomania csqv candidates

**Status: `READY_FOR_HUMAN_SEND`. External effect has not been performed.** Distinct post-edit verifier terminal `#13 issuecomment-5673864570` PASSed exact R2 head `52ca3e76892c2ea31c0440be8640cc4d1b81bc6f`; downstream ConsumerAck is bound to the unchanged attachment hashes below (PR #33 review `5204946829`).

R2 packaging-only change: each `.pck` author line was normalized to the keeper-requested single author name `Tommy Tai`; coordinates/radii were not intentionally changed.

Exact R2 attachment hashes:
- `csqv120.pck`: `5921e2ca32b2da8c8f908caaeaa9decc6498fd51b5e98006c96b1fe0571fa63a`
- `csqv122.pck`: `87af14334f54bb1c517e8e5d5cd36c38302f5b34bc0eca9a851641e59e73247f`

Immediately before sending, re-fetch `https://www.packomania.com/csqv/csqv.html` and confirm:
- N=120 incumbent remains below `5.7742848313038259`.
- N=122 incumbent remains below `5.8242710218195016`.
- the two attachment hashes above are unchanged.

Attach:
- `csqv120.pck`
- `csqv122.pck`
- optionally this repository URL / `README.md` verification packet

Public keeper contact shown by the current Packomania hints footer: `eckard.specht@physik.uni-magdeburg.de`.

Suggested subject: `Candidate improvements for Packomania csqv N=120 and N=122`

Draft body:

Dear Dr. Specht,

I have two candidate improvements for the Packomania csqv table, generated in an HFO Gen142 research run using the open-source Discovery Loop solver by Wes Sander. N=120 has Σr=5.7742848313038259 and N=122 has Σr=5.8242710218195016. The exact R2 attachment bytes were independently re-verified after packaging; the repository packet preserves solver/version provenance, live-record snapshot, exact attachment hashes, and verification results.

The final submission coordinates include a tiny safety shrink (~1e-10 per radius), leaving positive wall/pairwise slack while remaining clearly above the current published values. A bounded neighborhood breaker also found no local improvement in 400 attempts for N=120 and 395 attempts for N=122.

If they check out independently, I would be grateful if you would consider them for the table. For attribution, please credit Tommy Tai; the repository documents HFO Gen142 and the Discovery Loop solver provenance by Wes Sander.

Best regards,
Tommy Tai

## Human action boundary

The exact-byte verifier/ConsumerAck gate is satisfied for the hashes above. Sending the email/attachments remains the explicit human authority boundary. Perform one final live keeper read immediately before send. Do not claim `WORLD_RECORD` or `PACKOMANIA_ACCEPTED` until the keeper independently accepts/lists the construction.
