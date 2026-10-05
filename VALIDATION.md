# Validation and editorial review

Review date: 2026-10-05. The repository is a self-contained Markdown curriculum with 22 major areas, 68 substantive teaching chapters, 22 checkpoints, 18 worked system designs, five practical project briefs, and runnable mechanism labs. Chapter text is distinct from indexes, glossary entries, coverage rows, and assessment material; file count alone is not used as evidence of depth.

## Automated checks

Run these commands from the repository root with Python 3.11+:

```text
python tools/build_navigation.py
python tools/validate.py
python labs/models.py
```

The navigation generator produces the per-section reading order, prerequisites, priorities, checkpoints, concept coverage table, and progress entries. It preserves existing checked items with unchanged identity. The validator checks local file and heading targets, repository-contained paths, balanced code fences/details, required root documents, all chapter files, end-of-chapter exercises, further reading, and cross-links. It also checks the 41 explicitly listed often-missed coverage concepts.

The final structural pass checked 131 Markdown files and 2,144 local links with zero errors. The 68 teaching chapters contain approximately 67,000 words, excluding the generated indexes, progress/coverage tables, glossary, projects, and checkpoints. The detailed machine-readable result is [validation-results.json](tools/validation-results.json). Every teaching chapter exceeds the structural 600-word review threshold; this is a guard against empty or definition-only files, not a claim that length proves quality. No unfinished teaching files are part of the delivery.

Eight deterministic lab tests passed. They check inserted Bloom membership, duplicate insert behavior, measured false positives, token-bucket burst/refill/capacity/backward-time behavior, lease takeover, stale-owner renewal/release, and the difference between observed-epoch fencing and immediate lease-expiry enforcement. The Bloom experiment used 9,586 bits and seven hash positions for 1,000 inserted keys, observing 105 false positives among 10,000 disjoint test keys. That observation is not a probabilistic bound or benchmark.

## Coverage and depth review

Review dimension | Evidence and result
--- | ---
Coverage | [COVERAGE.md](COVERAGE.md) maps 677 concept entries to authored files, exercise availability, and connections; all requested major areas are present.
Progression | [ROADMAP.md](ROADMAP.md) provides Levels 0–6, dependency graph, prerequisites, priorities, exit evidence, and specialist extensions.
Frontend depth | Nine chapters cover semantics/accessibility, JavaScript, TypeScript, browser internals, React, state, rendering architectures, performance, and tests.
Database depth | Dedicated chapters cover relational modeling, indexes/plans, transactions/MVCC, WAL/recovery, and replication/partitioning/data models; storage structures have separate explanations.
Distributed reasoning | CAP is explained through a partition history; quorum intersection is distinguished from a complete protocol; leases, stale holders, fencing limits, clocks, and consensus have worked reasoning.
Data structures | Bloom filters, consistent hashing, B+ trees, LSM trees, skip lists, Merkle trees, HyperLogLog, and inverted indexes each have a dedicated chapter.
Connections | The click-to-pixels request chapter, authentication/data flows, uploads/chat, and Relay evolution connect browser, network, API, data, and infrastructure.
Failure reasoning | Chapters contain concrete races/crash windows, bounded-resource policies, rejected alternatives, and folded exercise guidance; the incident lab provides three complete investigations.
Production patterns | Pattern chapters identify problem, naive failure, mechanism/example, failure modes, trade-offs, and use/non-use conditions, including cross-system atomicity limits.
System design | Four beginner, six intermediate, and eight advanced walkthroughs cover all fourteen methodology steps, grouped into readable stages.
Practice | Five project briefs define contracts, milestones, failure experiments, acceptance criteria, and evidence; every section has an assessment checkpoint.
Interviews | Cross-domain reasoning questions and four timed mock sessions test explanation, diagnosis, design, and response to new evidence.
Navigation | All teaching material is linked through section indexes, roadmaps, concept coverage, progress, and local connections; the validator checks internal targets.

## Corrections made during review

The depth review split previously grouped system structures into dedicated skip-list, Merkle-tree, HLL, and inverted-index chapters. It added concrete JavaScript binding/receiver/prototype/error examples, compared rate-limit algorithms against the same burst history, and added a two-session PostgreSQL concurrency lab. The fencing explanation now explicitly distinguishes installing a newer epoch from rejecting every old operation immediately at expiry.

The source audit corrected a moved Zustand documentation URL. It retained authentic references when automated retrieval was blocked rather than substituting invented sources. Of 198 unique external URLs, 196 were reachable and two remained unverified. The final external reachability snapshot is [external-link-results.json](tools/external-link-results.json). The ACM Bloom-paper page returned HTTP 403, and the author-hosted Pugh skip-list PDF failed this environment's certificate-chain verification; both are recorded as unverified by that fetch. The chapters also link accessible implementation documentation and related primary material.

## Verification limits

The eight Python model tests were executed. They are single-process deterministic teaching models, not production-ready distributed implementations or formal proofs. The PostgreSQL concurrency lab provides exact session instructions but was not executed against a live PostgreSQL instance during repository creation. Framework snippets are focused explanatory fragments with stated context; the five projects are learner implementation briefs, not prebuilt deployed applications.

External HTTP reachability does not prove technical correctness or guarantee a URL will remain available. Primary sources were inspected for selected subtle/version-sensitive claims; the report does not claim an independent formal verification of every sentence. Mermaid/ASCII diagrams were reviewed as source, and Markdown structure/links were checked programmatically; no universal renderer compatibility claim is made.

To maintain the repository, follow [tools/README.md](tools/README.md), rerun checks after changes, and update this review when guarantees, library versions, or learning scope change.
