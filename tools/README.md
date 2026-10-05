# Repository maintenance

The JSON files describe authored curriculum structure and checkpoint questions. The Python scripts generate navigation and check evidence; they do not generate the teaching chapters.

Run from the repository root with Python 3.11+:

```text
python tools/build_navigation.py
python tools/validate.py
python labs/models.py
```

`build_navigation.py` rebuilds section indexes, checkpoints, the concept coverage table, and progress entries. It preserves checked progress items whose exact concept/priority/chapter identity remains unchanged. If renaming a concept or moving its chapter, migrate that progress identity deliberately. Checkpoint prose lives in `checkpoints.json`; chapter order, priorities, prerequisites, and coverage terms live in `curriculum.json`.

`validate.py` checks local file/anchor links, fenced-code and details balance, required documents, substantive chapter length, exercises, references, and concept connections. It writes machine-readable results to `validation-results.json`. Length and headings are structural signals, not proof of explanation quality or technical accuracy; retain editorial review.

Optionally run `python tools/check_external_links.py` to refresh source reachability. It performs bounded concurrent HTTP requests and writes `external-link-results.json`. A blocked request or certificate error is reported as unverified, not automatically classified as a nonexistent source. Review actual errors before replacing a reference. A successful response also does not prove a page supports every claim or is free of a soft-error page.

The publication snapshot and qualitative review are recorded in [VALIDATION.md](../VALIDATION.md). Update that report after meaningful curriculum changes. The [coverage index](../COVERAGE.md) explains what its chapter-level depth labels mean.
