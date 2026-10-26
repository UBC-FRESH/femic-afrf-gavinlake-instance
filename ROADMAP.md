# AFRF Gavin Lake Instance Roadmap

This roadmap is the plan of record and the issue tracker map for the AFRF Gavin
Lake ws4 instance. Keep it in step with the GitHub issues, `CHANGE_LOG.md`, and
`notes/`. `scripts/check_workflow.py` parses the phase headers, status lines,
and checkboxes below, so keep their format.

Every phase starts as `planned` with `Parent issue: TBD`. Activate a phase only
after its parent issue exists and the maintainer approves it.

## Issue Tracker Map

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P0 Bootstrap and structural parity | #1 | `feature/p0-bootstrap` | complete |
| P1 Scenario translation and baseline benchmark | #7 | `feature/p1-scenario-baseline` | active |
| P2 ws4 runtime packaging | TBD | `feature/p2-runtime-packaging` | planned |
| P3 Verification and QA | TBD | `feature/p3-verification` | planned |
| P4 Scenario analysis and optimization | TBD | `feature/p4-scenarios` | planned |
| P5 Release v0.1 | TBD | `feature/p5-release` | planned |
| P6 Maintain and merge readiness | TBD | `feature/p6-maintain` | planned |

## Lifecycle Map

| Stage | Phases | Exit criteria |
| --- | --- | --- |
| Scope and design | P0 | The instance contract, publication boundary, and legacy provenance are recorded |
| Build | P1, P2 | The legacy matrix is translated, the ws4 dataset compiles, and the run entrypoints are reproducible |
| Verify | P3 | Structural and scenario evidence is recorded against the acceptance criteria |
| Release and deploy | P5 | Tag, release notes, and a clean-checkout verification are approved |
| Operate and maintain | P6 | Review cadence holds and the merged-model contract is current |

## Conventions

- A phase is `P<n>`. A task is `P<n>.<m>`. A subtask is a checklist item inside
  the task's issue body. Three levels at most.
- Status values are `planned`, `active`, `pr-open`, `complete`, and `deferred`.
- A phase becomes `complete` only after its pull request merges to `main` and
  its parent issue closes.
- The legacy package is immutable. Derived tables live outside
  `data/legacy_gavinlake/` or are named as derived files with a provenance note.

## Phase 0: Bootstrap and structural parity

Parent issue: #1
Branch: `feature/p0-bootstrap`
Status: complete

Goal: adapt the workflow surfaces to this instance, ingest the legacy H matrix,
compile a validated ws4 dataset, and record the initial structural parity.

- [x] P0.1 Adapt `AGENTS.md`, `README.md`, and the roadmap to Gavin Lake (#2)
- [x] P0.2 Record the legacy archive provenance and publication boundary (#3)
- [x] P0.3 Ingest the legacy H matrix and compile the ws4 dataset (#4)
- [x] P0.4 Record the initial-growing-stock parity evidence (#5)
- [x] P0.5 Confirm the green dashboard and the docs build (#6)

Acceptance criteria:

- The legacy archive hash and file inventory are recorded.
- `ws4 validate` accepts the compiled dataset.
- The ws4 initial growing stock matches the value implied by the legacy
  scenario constraint to better than 1 × 10⁻⁵ relative error.
- `python scripts/dashboard.py` is green.

## Phase 1: Scenario translation and baseline benchmark

Parent issue: #7
Branch: `feature/p1-scenario-baseline`
Status: active

Goal: translate the legacy H scenario catalog into a ws4 target contract and
build a reproducible baseline schedule that can be compared with the legacy
matrix behaviour.

- [x] P1.1 Translate the legacy H scenario catalog into ws4 target files (#8)
- [x] P1.2 Build a reproducible baseline schedule (#9)
- [x] P1.3 Run the baseline and compare account trajectories (#10)
- [x] P1.4 Record accepted variances and defer the carbon scenarios explicitly (#11)

Findings:

- The only treatment in the compiled H matrix is clearcut at age 80 or more.
- A sustained 80-year rotation produces a mean of 188,677.89 m³ per ten-year
  period over 300 years, with a minimum of 177,070.07 and a maximum of
  197,806.62 m³.
- The legacy 500,000 m³ per period floor is not feasible on this matrix. The
  one-time age-80 pulse produces about 1.26 million m³ in the first decade and
  then no sustained harvest.
- The legacy 1,277,067 m³ growing-stock floor at period 30 is not met; the
  baseline ends at 495,510.56 m³.
- The baseline is flat in absolute volume but not within the legacy -1 to 1
  percent even-flow band when each period is compared with the final period.
- The eight carbon scenarios are deferred because the compiled matrix does not
  carry the runtime duplicate stock/flux accounts and the target units are
  unresolved.

Acceptance criteria:

- Every legacy H scenario has a translated, deferred, or rejected disposition.
- The baseline run is reproducible from a documented command.
- The comparison report states what matches and what does not.

## Phase 2: ws4 runtime packaging

Parent issue: TBD
Branch: `feature/p2-runtime-packaging`
Status: planned

Goal: make the Gavin Lake model runnable as a packaged ws4 instance rather than
a collection of ad hoc commands.

- [ ] P2.1 Add a stable ws4 dataset build entrypoint
- [ ] P2.2 Add baseline and optimize entrypoints
- [ ] P2.3 Add a report or web surface for the instance evidence
- [ ] P2.4 Document the runtime package boundary

Acceptance criteria:

- A new operator can build, validate, simulate, and report from the runbook.
- Generated runtime files stay out of Git.

## Phase 3: Verification and QA

Parent issue: TBD
Branch: `feature/p3-verification`
Status: planned

Goal: verify area, curves, accounts, topology, and patch reporting against the
legacy matrix and record the benchmark report.

- [ ] P3.1 Verify area and block coverage
- [ ] P3.2 Verify curve and account coverage
- [ ] P3.3 Verify topology and patch reporting
- [ ] P3.4 Write the verification report

Acceptance criteria:

- Every legacy account has a ws4 mapping or a documented gap.
- Every area and topology discrepancy has a recorded explanation.

## Phase 4: Scenario analysis and optimization

Parent issue: TBD
Branch: `feature/p4-scenarios`
Status: planned

Goal: run the translated timber and carbon scenarios in ws4 and record the
scenario comparison.

- [ ] P4.1 Run the timber harvest scenario
- [ ] P4.2 Run the carbon stock and sequestration scenarios
- [ ] P4.3 Record the scenario comparison evidence
- [ ] P4.4 Decide which scenarios become the public baseline

Acceptance criteria:

- Each scenario has a documented target set, seed, and runtime.
- The public baseline is named and reproducible.

## Phase 5: Release v0.1

Parent issue: TBD
Branch: `feature/p5-release`
Status: planned

Goal: tag and publish the Gavin Lake instance with release notes and a clean
checkout verification.

- [ ] P5.1 Write release notes and the known-gaps list
- [ ] P5.2 Tag and publish after maintainer approval
- [ ] P5.3 Verify the release from a clean checkout

Acceptance criteria:

- The release notes match the evidence.
- A clean checkout reproduces the structural parity check.

## Phase 6: Maintain and merge readiness

Parent issue: TBD
Branch: `feature/p6-maintain`
Status: planned

Goal: keep the instance current and define the contract for the future merged
AFRF model.

- [ ] P6.1 Set a review cadence and record the first review
- [ ] P6.2 Define the cross-block identifier and schema contract
- [ ] P6.3 Record the merged-model handoff and open questions

Acceptance criteria:

- The merge contract is specific enough to implement without re-reading this
  roadmap.
- The sibling Knife Creek instance can consume the contract.

## Detailed Next Steps Notes

1. Phase 0 is active under parent issue #1. The bootstrap commit is on `main`;
   the task issues #2-#6 record the completed surfaces.
2. Phase 1 is planned under parent issue #7. Activate it only after Phase 0 is
   approved and the Phase 0 pull request or bootstrap closeout is accepted.
3. Keep the legacy archive out of Git; commit the sanitized package and its
   hash.
