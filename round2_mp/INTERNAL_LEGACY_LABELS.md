# Internal legacy labels retained for provenance

Some frozen CSV/source-code field names predate the final reader-facing terminology. They are retained byte-for-byte where changing them would break provenance hashes.

- `recovery_fraction` in `core_p1_map_summary.csv` corresponds to the reader-facing **normalized fitness recovery** coordinate.
- `submitted_constant` in the expected marginal diagnostic script/table provenance denotes the historical **pre-softmax affinity-averaging comparator**. It is a secondary diagnostic comparator only and is not used for primary Round-2 causal estimates or conclusions.
- Historical Gate-8 validation output may contain earlier terminology such as `value_of_information`; those files belong to the preserved foundation, not the current Round-2 reader-facing evidence layer.

The final manuscript and Supplement terminology is controlled by the notation-closed publication objects and their terminology audit.
