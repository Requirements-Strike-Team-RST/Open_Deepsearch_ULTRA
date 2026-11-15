# CS5351 SA deliverable audit — 2026-11-14

Status: read-only audit of course source material. No course submission, project source/test edit, governance change, review approval or model/API invocation was performed by this audit.

## Sources and verification

- Current Canvas project specification: `CS5351-2026-2027-project-canvas.pdf`, downloaded by the supervising agent with GET from Canvas file 15805980. File size 364,844 bytes; SHA-256 `6af742d3cbc0973b056a084ba54ff413a5885b1bb4d6a97b0b08b93f64f2ef7e`. Ten pages, PDF 1.7, no JavaScript or form fields reported by `pdfinfo`.
- Text extraction: `course-project-canvas.txt`, produced with `pdftotext -layout`. Relevant project pages 5–7 were also rendered and visually checked, including the contribution table.
- SA lecture: `/Users/e1bae/src/homework/5351/course-materials/slides/CS5351-2026-2027-SA.txt`. Its embedded tables are absent from the text; the corresponding original `CS5351-2026-2027-SA.pdf` slides 77–82 were rendered and visually read. Rendered pages are in `course-audit-render/`.
- Canvas assignment records already retrieved by the supervising agent: Project Zip 324835 and Demo Video 327885 both have due time `2026-11-25T15:59:59Z`, i.e. 2026-11-25 23:59:59 UTC+8. Both currently show `points_possible: 0.0` and no rubric. This does not establish a zero-weight project or an assessment scale.

## What the course requires

### D1: requirements and AI-use evidence

Project specification pages 2, 5 and 9:

- Machine-readable requirements under `docs/req/requirements.yaml`, validated by `req-schema.json`; IDs, type, statement, machine-checkable fit criteria, MoSCoW priority and explicit tradeoffs. Nonfunctional requirements use metric + threshold + verification; requirements derived from existing systems link to their sources.
- The AI-use log is mandatory and up to date at submission. The required tree assigns `docs/ai-use-log.yaml` to D1, even though the D1 prose primarily describes the registry.
- For this approved-requirements SA phase, preserve the approved registry and add truthful evidence of the actual assistance. Do not invent model success, human intervention or approval.

### D2: architecture artifacts

Project specification page 5:

1. Blueprint: scope, drivers, system and authority boundaries, components, agent workflow, permissions, verification strategy, observability and change policy.
2. ADR: choice, alternatives, rationale, consequences, reopen conditions and the architectural design process. For the AI component, explicitly provide the layered context received on each turn, the assembly pipeline, token-budget cap and compaction threshold, and reinjection of critical constraints after compaction. These details are easy to omit when following only the short team announcement.
3. Invariants: statement, source RID, enforcing component, verification and a concrete operational fallback.
4. Trace matrix: every requirement to enforcing component, test/evidence and runtime monitor.
5. Memory/state: survival across sessions, interruptions and versions; write/retrieval policy, ownership, retention and privacy.
6. Permission model: role-specific file access, default no read/no write and explicit path whitelisting.
7. Runtime policy: response to each degraded/failure path.
8. Candidate evaluation table justifying the choice.
9. Evaluation logbook, risk list and option ledger are optional artifacts. An ADR still needs its own reopen conditions regardless of whether a risk list is written.

The module owner can complete proposed ADRs, comparisons, invariants, state/policy sections, tracing and an integration checklist now. The system-wide blueprint and reconciliation of the shared context/permission decisions belong to integration and SA Review. This audit does not assign implementation ownership to other modules.

### D4: verification governance and review evidence

Project specification page 6:

- Every fit criterion has at least one test; every invariant has a test that fails on its violation; tests name the requirement/invariant; subsequent rounds run all prior suites with zero regressions.
- Three verification layers: structural, regression and behavioral. A static document check does not prove behavioral fit criteria.
- A review memo per PR covers specification and architecture alignment, code/test quality, operational metadata, and security/efficiency throughout. The course's final review verdicts are APPROVE, CHANGES REQUIRED or REJECT. The repository's local template uses different words; report the difference rather than silently rewriting governance.
- Technical debt and significant bugs require records with their specified fields. Do not invent a bug reproduction or measurement for optional evidence.
- At this stage the module's case inventory can be written. Test code and baseline-failure evidence wait for Gate 1; test approval and implementation wait for their later gates. Automated self-review is not a teammate's review or an SA gate.

### D5: full raw sessions and marked interventions

Project specification pages 2, 6 and 9:

- Full raw coding-agent session transcripts are required, annotated with the student team members' actual interventions and the rationale for interrupting, redirecting, approving or rejecting output.
- Collectively the transcripts must demonstrate requirements classification, candidate generation/evaluation, plan approval before code, build, verification compliance and architectural revision caused by test evidence.
- Preserve actual prompt, model/role, tool events, output, errors and follow-up corrections. A polished summary alone is not the raw transcript. Redact credentials; describe redaction without reproducing secret values.
- This SA run can supply authentic evidence for classification, candidate evaluation, proposed execution plan and corrections. It cannot truthfully supply future human approvals, implementation, passing tests or test-driven architecture revision.
- Page 2's submission-model sentence says five annotated transcripts; page 9 uses per-student naming and the team currently has six members. The count should be reconciled by humans; do not omit a student's evidence based on that sentence.

### Execution plan and supervision

Project specification page 7, D9:

- `Prompt.md` must make the coding agent produce an execution plan with traceability, interface contract, scope boundaries, testing strategy and steps, then stop for human approval before code.
- Build and self-verification follow with human gates. The static prompt is explicitly not an instruction to run unattended through completion.
- The present six-hour autonomy is therefore preparation within the SA role; it is not approval of the plan or authority to cross the architecture/test/implementation gates.

## Architecture evaluation expected by the lecture

SA slides 74–83:

- Freeze the requirement baseline, generate 2–3 candidates using ADD, define observable evaluation/scoring rules, compare, trace the decision back to drivers, refine interfaces/responsibilities, create a bounded implementation plan, then define monitors and change triggers.
- ADD's seven steps are review inputs, select drivers, decompose an element, choose design concepts/tactics, instantiate elements/interfaces/authority boundaries, record decisions and evaluate against drivers.
- Slide 77 uses Weak/Medium/Strong: Weak means a critical requirement is violated or bypassable; Medium means only some paths satisfy it or manual recovery is needed; Strong means deterministic satisfaction on all execution paths. Ratings must come from something observable, not hoped-for implementation behavior.
- Its ten example dimensions are invariant protection, authority separation, explanation isolation, availability, state/review continuity, observability, testability, modifiability, implementation complexity and fit to the project. Tailor these to this module's approved drivers; the lecture's VHIS-specific thresholds are examples, not new requirements.
- Slides 78–79 make critical-driver failure disqualifying regardless of total score. Choose the smallest candidate that satisfies all critical drivers with acceptable complexity; a larger number of Strong scores does not automatically win.
- Slides 80–82 refine what crosses an authority boundary, surviving state, logged evidence and allowed agent changes. Every architectural driver should have a runtime signal, threshold/condition, action and review trigger. Do not claim a runtime monitor is implemented during SA.

## Marks and scoring: what is and is not stated

- The current ten-page project specification has no percentage/point allocation by D1, D2, D4 or D5, and no project marking rubric. Do not invent a mark breakdown.
- Project specification pages 4, 6–7 require relative contributions, normalized so the mean is 1.0, and show individual marks pro-rated by the contribution factor, with bounds for extremes. Evidence such as agreed productive hours or story points is suggested; no contribution claim was measured by this audit.
- The lecture's candidate scores are design-selection evidence, not student marks.
- D6 later needs a single Markdown report, at most 10,000 words excluding diagrams, more than 15 pages at 12-point single spacing, names/IDs, contribution ratios and roughly 300–500 words of reflection per member.

## Review/integration issues to keep explicit

| Issue | Source | Recommended handling in this SA run |
|---|---|---|
| Blueprint location differs between D2 prose (`docs/architecture/`) and the required tree (root). Current approved repository uses `docs/architecture/architecture-blueprint.md`. | Project pp.5,9; current repository | Follow current repository authority in module drafts, flag final packaging question for integrator. |
| Course permission prose calls for default deny + explicit whitelist, while current project permissions allow broad routine reads/SA edits. | Project p.5; project permission model | Do not change permissions. Flag for whole-system compliance review with evidence. |
| Full raw transcript and future supervised pipeline are not complete after SA alone. | Project p.6 | Mark the SA transcript as a partial-stage contribution; preserve raw event logs separately. |
| Human review records and gate approvals cannot be generated by an AI self-review. | Project pp.1,3,6–7; repository gates | Provide review checklists/findings and leave actual reviewer identities/decisions pending. |
| Candidate evidence cannot be invented. | SA slides 77–79 | Label inspection-based arguments as design analysis; record experiments only if actually performed. |
| Six CI blocking gates are course requirements, and several are still planned in main. | Project p.10; current verification constraints | Report current state without fixing global CI in a module-only SA change. |

## Audit command verdicts

- PASS: `pdfinfo` inspection; ten pages and metadata identified.
- PASS: full `pdftotext -layout` extraction.
- PASS: visual inspection of project pp.5–7 and SA slides 77–82. The SA PDF renderer emitted an optional-content-group warning but returned exit 0 and the selected page images were readable.
- N/A: no model calls, source/tests, online writes or course submission were needed for this read-only audit.
