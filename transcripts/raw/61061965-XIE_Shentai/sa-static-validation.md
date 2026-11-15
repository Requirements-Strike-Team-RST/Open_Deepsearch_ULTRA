# Static SA document validation

Generated: 2026-11-14T05:04:26.455691+08:00
Static verdict: **PASS**

This is an external document audit. No functional, regression, live-test or human-approval PASS is implied.

## Command

```text
/opt/homebrew/opt/python@3.15/bin/python3.15 /Users/e1bae/src/homework/5351/project/sa-evidence-2026-11-14/validate-sa-docs.py
```

## Checks

| Static check | Verdict |
|---|---|
| baseline_commit | PASS |
| git_visible_change_scope | PASS |
| shared_document_preservation | PASS |
| unassigned_trace_rows_unchanged | PASS |
| adr_template_and_proposed_status | PASS |
| actual_architecture_ids_unique | PASS |
| own_architecture_references_resolve | PASS |
| d1_yaml_and_existing_entries | PASS |
| acceptance_to_planned_case_traceability | PASS |
| markdown_table_column_counts | PASS |
| relative_markdown_links_exist | PASS |
| d5_raw_evidence_bundles | PASS |
| opencode_models_and_role | PASS |
| git_diff_check_and_new_document_whitespace | PASS |

## Findings

No static scope, structure, reference or evidence-file error was found by these checks.

## Later gates and tests

| Check | Verdict | Reason |
|---|---|---|
| product contract/behavior tests | NOT_RUN | SA only; no product/test code was written or executed by this tool. |
| offline regression tests | NOT_RUN | This tool invokes no pytest command and imports no project source. |
| live model/search tests | NOT_RUN | No network or model API invocation is performed. |
| human module review / Gate 1 / Gate 2 | NOT_RUN | An automated static audit cannot approve a human gate. |

The JSON report contains exact Git commands, exit codes, outputs, the changed-file inventory and detailed check results.
