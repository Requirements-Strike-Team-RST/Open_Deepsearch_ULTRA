# Evaluation Table

> **Purpose:** ADD results: for each architectural question, 2–3 candidate solutions compared on pros, cons, complexity and testability, and the choice made.
> **Authoritative for:** option comparisons. The decision itself is recorded in the ADR named in the entry.
> **Maintained by:** each module owner adds the entries for their module; entries are integrated before SA Review (`Prompt.md` §4).
> **Last updated:** 2026-11-12

## How to Add an Entry

1. Copy the example below, take the next free `EVAL-NNN` number and keep the same fields.
2. **ASR:** list the requirements and the acceptance criteria (C-/M- IDs from `docs/req/requirements.yaml`) that shape the decision.
3. **Candidates:** describe 2–3 options; rate complexity and offline testability as Low, Medium or High.
4. **Choice:** name the chosen option and why it wins, say why each other option was rejected, then write the ADR.

## EVAL-NNN: <Question being decided>

- **Module:** <module from `architecture-blueprint.md` §4>
- **Owner:** <name>
- **Decision recorded in:** ADR-NNN
- **Status:** Open | Decided

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-NNN | C-NNN, M-NNN | e.g. correctness, testability, cost |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | | | | | Low / Medium / High | Low / Medium / High |
| B | | | | | | |
| C (optional) | | | | | | |

**Choice:** <option> — <why it wins>.

**Rejected and why:** <option>: <reason>.

## EVAL-002: Where the delegation contract and the research-loop exit decision live

- **Module:** orchestration
- **Owner:** Centay
- **Decision recorded in:** ADR-002
- **Status:** Open

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-001 | C-001, C-002, C-003, C-004, M-001 | Correctness, deterministic validation, offline testability |
| REQ-003 | C-001, C-002, C-003, C-004, C-005, C-006, M-001, M-002 | Determinism, boundedness, single exit reason |
| REQ-002 | C-005, C-007 (contributor only) | Failure isolation, no failure text in notes |
| REQ-005 | C-004 (contributor only) | A failed task is a typed result, not placeholder text |

**Critical drivers.** Each driver is rated weak (W), medium (M) or strong (S) against an observable runtime design property. A **fail** on any critical driver K1–K5 disqualifies the option; K6 is a secondary tradeoff. No numeric score is summed; the choice is justified qualitatively on the drivers that separate the options.

| # | Driver (observable property) | Fail means |
|---|---|---|
| K1 | **Deterministic status and exit.** Every exit produces exactly one `RunRecord`; code validates model-proposed findings and computes status/coverage/exit, without accepting a model's self-declared status or exit as authority. | A model's completion/status claim can bypass the deterministic selector or source validation. |
| K2 | **Single delta/override state protocol.** Per-turn results travel as plain list deltas that `override_reducer` appends, and the final write is one override envelope; a reader can reconstruct every task result exactly once. | Results are written twice, by two writers, or only as free text. |
| K3 | **Flag-off equivalence.** With `orchestration_enabled = False` the enabled-only code is unreachable and the baseline nodes, tools and state fields behave as at commit `827fd32`. | Enabled logic runs in the flag-off path. |
| K4 | **Scope and owner separation.** Orchestration introduces no REQ-002 dispatch/join logic and no REQ-004 outcome logic, so three owners can work in parallel on `supervisor_tools`. | One module must own another module's acceptance criteria. |
| K5 | **Reader validity.** Readers receive a validated object only, and `notes` are rendered from validated findings rather than model prose. | Failure or unverified prose can reach report generation or the outcome. |
| K6 | **Implementation and coordination cost**, a secondary tradeoff rather than an acceptance gate. | Assessed qualitatively; no schedule measurement is claimed. |

Rating anchors: **W** permits a documented bypass or violates a critical driver;
**M** covers only some paths or needs an additional manual control; **S** assigns
an explicit deterministic boundary to every specified path in the candidate's
declared support envelope. These are inspection-based design ratings, not test
verdicts. W on K1–K5 disqualifies; K6 compares cost among otherwise viable choices.
Native-search enablement, the shared reader contracts and the course input-token
policy remain explicit integration decisions; S does not claim they are approved.

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | **Prompt-only gating:** add must-answer questions and a completion rubric to `lead_researcher_prompt`; the supervisor model is asked to call `ResearchComplete` only when every question is answered; no new type or state field; `notes` stay as returned. | `prompts.py` only | Smallest diff; no new state; cannot break reducers | K1 **fail**: loop exit, status and coverage stay model decisions, so REQ-001 C-002/C-003 and REQ-003 C-001…C-005 cannot fail offline for the right reason; K2 **fail**: no typed result exists; K5 **fail**: notes remain model prose. | Low | Low |
| B | **Deterministic orchestration module over typed shared state (preferred):** `state.py` holds the types and the orchestration fields; `orchestration/` holds helpers (`contracts`, `budget`, `evidence`, `termination`) over one receipt that import those types; `supervisor_tools` keeps its baseline structure and calls the helpers at the existing boundaries; REQ-002 dispatch/join and REQ-005 trimming stay with their owners. | `state.py`, `orchestration/`, `configuration.py`, thin calls from `supervisor`, `supervisor_tools`, `researcher_tools`, `compress_research`, `prompts.py` (draft, Jeremy's approval) | K1–K5 all strong: the selector is one pure function over exact fractions; deltas use the existing append reducer; enabled-only code sits behind one flag; each owner keeps their own lines; every case is a fake-model offline test | Adds fields to four state classes (an honest change to those classes) and one subpackage; a coordinated hand-over inside `supervisor_tools` | Medium | High |
| C | **Whole-node takeover:** orchestration supplies a complete replacement `supervisor_tools` (and a matching `supervisor`) that performs dispatch, queuing, join, validation and the exit decision in one module. | `deep_researcher.py` node bodies replaced, `orchestration/` | K1, K2 and K5 can be strong: a single module holds one coherent loop | K4 **fail**: takes REQ-002 dispatch, queuing and join and REQ-004 outcome inputs away from their owners, so those owners cannot implement or test their own criteria in their own lines; K6 **weak**: largest coordination surface and highest merge-conflict risk for parallel module work | High | High (but the delivered tests would belong to the wrong module) |

**Choice:** **B**, provisionally. Within the declared support envelope it assigns boundaries for K1–K5: a pure exit selector over validated results, baseline append/final-override semantics, a disabled-path switch, scoped module ownership and findings-only notes. Its implementation/coordination cost is Medium (K6). Reader agreement and the listed course integration gaps must be resolved before acceptance; the design ratings are not proof of implemented behavior.

**Rejected and why:**

- **A:** fails K1, K2 and K5. Prompt text cannot make a task status or an exit reason deterministic, and REQ-003 explicitly rejects trusting the model's completion claim.
- **C:** rejected on owner scope and coordination cost (K4 fail, K6 weak), not on correctness — it could produce a correct loop, but it moves other owners' acceptance criteria into one module and maximises merge conflict in the one node three owners must edit.
