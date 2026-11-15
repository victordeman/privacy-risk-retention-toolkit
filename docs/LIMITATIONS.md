# Limitations and cases that still need human review

- **Detection is not classification.** Patterns find values that look like personal data. They cannot tell whether a value identifies a real person, and they cannot see context.
- **Business categories can look like names.** `suppliers.category` ("Professional Services") is flagged at medium confidence and needs analyst rejection. Generic negative hints would also hide real names in columns with those words.
- **Column-level results.** Accuracy is measured per column, not per value. A column that is mostly personal data with a few exceptions is flagged as a whole.
- **Mixed columns.** `access_logs.user_id` holds employee IDs (personal) and external IDs (not matched). Its rate is 71%, so it is flagged but needs a human to decide how far it applies.
- **Free text is not inspected.** Personal data inside notes, ticket text or filenames is not found.
- **Format coverage.** Phone, ID and IPv4 formats are those in the synthetic data. IPv6, other national formats and non-Latin names need new rules.
- **Retention periods are test policies.** The `status_column`/`closed_statuses` extension is a modelling choice for the demo.
- **Holds are read from `on_hold`.** The toolkit cannot verify that a hold is still justified; legal owners must.
- **System rows in the inventory** (HRIS, CRM, ...) have no sample data, so their sensitivity is a heuristic.
- **Simulated people.** `--simulate` analyst and the demo reviewers are stand-ins so the demonstration is repeatable. A real run needs named humans.
- **Disposal is simulated.** There is deliberately no connection to a production deletion service.
