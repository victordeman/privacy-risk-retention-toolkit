# Test results

Run: 2026-11-14 with Python 3.13.18, pytest. Command: `./run.sh test`

```
tests/test_discovery.py::test_detects_email_phone_ip_name_id PASSED
tests/test_discovery.py::test_phone_formats[+1-448-685-9537] PASSED
tests/test_discovery.py::test_phone_formats[607-426-5775] PASSED
tests/test_discovery.py::test_phone_formats[8265834251] PASSED
tests/test_discovery.py::test_phone_formats[+44 9499 685098] PASSED
tests/test_discovery.py::test_phone_formats[(247) 201-8529] PASSED
tests/test_discovery.py::test_placeholders_and_blanks_do_not_match PASSED
tests/test_discovery.py::test_operational_ids_not_flagged PASSED
tests/test_discovery.py::test_company_name_is_low_confidence PASSED
tests/test_discovery.py::test_single_word_needs_name_column PASSED
tests/test_discovery.py::test_examples_are_masked PASSED
tests/test_discovery.py::test_mask_value_all_categories PASSED
tests/test_discovery.py::test_real_data_accuracy_against_answer_sheet PASSED
tests/test_discovery.py::test_review_resolves_false_positives PASSED
tests/test_discovery.py::test_record_decision_validation PASSED
tests/test_discovery.py::test_unreadable_files_are_skipped_not_fatal PASSED
tests/test_discovery.py::test_ragged_rows_warned_and_skipped PASSED
tests/test_discovery.py::test_missing_folder_raises PASSED
tests/test_discovery.py::test_read_csv_missing_file PASSED
tests/test_disposal.py::test_proposal_only_contains_eligible_non_held PASSED
tests/test_disposal.py::test_no_disposal_without_approval PASSED
tests/test_disposal.py::test_rejected_or_unnamed_reviewer_cannot_dispose PASSED
tests/test_disposal.py::test_proposal_tampering_after_approval_is_detected PASSED
tests/test_disposal.py::test_simulation_inside_source_folder_refused PASSED
tests/test_disposal.py::test_execution_only_touches_the_copy PASSED
tests/test_disposal.py::test_held_records_survive_simulation PASSED
tests/test_disposal.py::test_defence_in_depth_blocks_held_record_even_if_proposed PASSED
tests/test_disposal.py::test_rejected_record_ids_are_not_deleted PASSED
tests/test_disposal.py::test_log_has_decision_reviewer_date_result_and_no_personal_data PASSED
tests/test_disposal.py::test_recovery_restores_identical_copy PASSED
tests/test_disposal.py::test_recovery_detects_damage PASSED
tests/test_disposal.py::test_recover_without_copy_fails PASSED
tests/test_disposal.py::test_proposal_filter_blocks_holds_independently_of_retention_engine PASSED
tests/test_end_to_end.py::test_demo_pipeline_and_report_masking PASSED
tests/test_end_to_end.py::test_no_raw_personal_data_in_reports_or_logs PASSED
tests/test_end_to_end.py::test_cli_reports_errors_cleanly PASSED
tests/test_retention.py::test_date_parsing PASSED
tests/test_retention.py::test_leap_day_rolls_to_28_feb PASSED
tests/test_retention.py::test_boundary_exactly_expired_is_eligible PASSED
tests/test_retention.py::test_review_due_date_is_explained PASSED
tests/test_retention.py::test_hold_excludes_even_when_expired PASSED
tests/test_retention.py::test_hold_flag_case_insensitive_and_blank_means_not_held PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[invalid] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[N/A] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[unknown] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[TBD] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[pending] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[NULL] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[0000-00-00] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[malformed] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[ongoing] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[TBC] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[open] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[invalid-date] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[2023-13-45] PASSED
tests/test_retention.py::test_invalid_trigger_on_closed_record_is_investigate_not_delete[garbage] PASSED
tests/test_retention.py::test_invalid_trigger_on_open_record_is_not_eligible[] PASSED
tests/test_retention.py::test_invalid_trigger_on_open_record_is_not_eligible[N/A] PASSED
tests/test_retention.py::test_invalid_trigger_on_open_record_is_not_eligible[TBD] PASSED
tests/test_retention.py::test_invalid_trigger_on_open_record_is_not_eligible[unknown] PASSED
tests/test_retention.py::test_invalid_trigger_on_open_record_is_not_eligible[pending] PASSED
tests/test_retention.py::test_placeholder_on_open_record_gets_quality_flag_blank_does_not PASSED
tests/test_retention.py::test_dataset_without_status_column_always_expects_trigger PASSED
tests/test_retention.py::test_held_record_with_missing_date_is_still_not_eligible PASSED
tests/test_retention.py::test_real_data_matches_corrected_answer_sheet PASSED
tests/test_retention.py::test_every_record_in_exactly_one_category_and_totals PASSED
tests/test_retention.py::test_no_closed_record_is_silently_active PASSED
tests/test_retention.py::test_as_of_override_changes_outcome PASSED
tests/test_retention.py::test_missing_required_column_reported_not_crash PASSED
tests/test_retention.py::test_config_is_separate_from_logic PASSED
tests/test_risk_register_inventory.py::test_band_boundaries[1-Low] PASSED
tests/test_risk_register_inventory.py::test_band_boundaries[4-Low] PASSED
tests/test_risk_register_inventory.py::test_band_boundaries[5-Medium] PASSED
tests/test_risk_register_inventory.py::test_band_boundaries[9-Medium] PASSED
tests/test_risk_register_inventory.py::test_band_boundaries[10-High] PASSED
tests/test_risk_register_inventory.py::test_band_boundaries[15-High] PASSED
tests/test_risk_register_inventory.py::test_band_boundaries[16-Critical] PASSED
tests/test_risk_register_inventory.py::test_band_boundaries[25-Critical] PASSED
tests/test_risk_register_inventory.py::test_score_validation PASSED
tests/test_risk_register_inventory.py::test_supplied_assessments_are_consistent PASSED
tests/test_risk_register_inventory.py::test_validation_catches_errors PASSED
tests/test_risk_register_inventory.py::test_new_assessment_scores_and_requires_mitigation PASSED
tests/test_risk_register_inventory.py::test_summary_overdue_and_due_soon PASSED
tests/test_risk_register_inventory.py::test_register_review_keeps_history PASSED
tests/test_risk_register_inventory.py::test_register_rejects_bad_edits PASSED
tests/test_risk_register_inventory.py::test_register_source_file_never_modified PASSED
tests/test_risk_register_inventory.py::test_inventory_links_files_to_activity_owner_rule_and_assessments PASSED
```

## Coverage by area
- Discovery accuracy (28/28 labelled columns found, 0 missed; 2 false positives raw, 1 at medium/high, 0 after review), masking, placeholders, unreadable inputs
- Date calculations (leap day, due-date boundary, invalid formats), holds, invalid/missing triggers, answer-sheet match of all 30 retention cells
- Disposal: approval required, tamper detection, copy-only execution, holds preserved, log content, recovery and damaged-recovery detection
- Risk scoring/bands/validation, register history, inventory linkage, end-to-end run, no raw personal data in outputs

Mutation checks done by hand: treating holds as eligible, treating blank closed dates as eligible, removing the proposal hold filter, and an off-by-one on the due date each cause test failures.
