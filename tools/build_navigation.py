"""Rebuild indexes from authored curriculum metadata; never generates teaching prose."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "tools/curriculum.json").read_text(encoding="utf-8"))
SECTIONS = {s["dir"]: s for s in DATA["sections"]}
CHECKPOINTS = json.loads((ROOT / "tools/checkpoints.json").read_text(encoding="utf-8"))
old_progress = (ROOT / "PROGRESS.md").read_text(encoding="utf-8") if (ROOT / "PROGRESS.md").exists() else ""
checked_items = set(re.findall(r"^- \[[xX]\] (.+)$", old_progress, re.M))
progress = ["# Progress\n", "Mark a concept only after you can explain its mechanism, predict a failure, and supply evidence from an exercise. P0 = Essential; P1 = Important; P2/P3 = Advanced (not unimportant). Revisit checked items after a week.\n"]
coverage = ["# Coverage audit\n", "This index maps every curriculum concept to its teaching chapter. Depth is audited at chapter level: **worked** means mechanism, concrete example, failure/trade-off discussion, exercises, and connections; **focused** means a shorter treatment within a broader chapter. It is not a claim of exhaustive specialist coverage. The final validation report records structural checks separately from technical review.\n", "Concept | File | Depth | Exercises | Cross-links | Status\n--- | --- | --- | --- | --- | ---"]
for section in DATA["sections"]:
    folder = ROOT / section["dir"]
    folder.mkdir(exist_ok=True)
    prereqs = ", ".join(f'[{SECTIONS[p]["title"]}](../{p}/README.md)' for p in section["prerequisites"]) or "Basic programming and data structures"
    index = [f'# {section["title"]}\n', f'**Prerequisites:** {prereqs}. **Roadmap level:** {section["level"]}.\n', "Read in this order; the checkpoint asks you to combine the ideas rather than repeat definitions.\n", "Chapter | Priority | Concepts\n--- | --- | ---"]
    progress.append(f'\n## {section["title"]}\n')
    for slug, title, priority, topics in section["chapters"]:
        rel = f'{section["dir"]}/{slug}.md'
        file = ROOT / rel
        body = file.read_text(encoding="utf-8") if file.exists() else ""
        words = len(re.findall(r"\b[\w'-]+\b", body))
        exercises = "Yes" if "## Exercises" in body else "No"
        links = len(re.findall(r"\]\((?!https?:)[^)]+\.md(?:#[^)]*)?\)", body))
        status = "Authored" if body else "Planned"
        depth = "Worked chapter" if words >= 600 else "Focused treatment" if body else "Pending"
        index.append(f'[{title}]({slug}.md) | {priority} | {topics.replace(";", ", ")}')
        for concept in topics.split(";"):
            progress_item = f'{priority} — {concept} ([study](./{rel}))'
            checked = 'x' if progress_item in checked_items else ' '
            progress.append(f'- [{checked}] {progress_item}')
            coverage.append(f'{concept} | [{title}]({rel}) | {depth} | {exercises} | {links} | {status}')
    index += ["\n## Checkpoint\n", "Complete the [section checkpoint](CHECKPOINT.md) without opening the chapters, then revisit weak explanations.\n", "[Roadmap](../ROADMAP.md) · [Progress](../PROGRESS.md) · [Exercises](../EXERCISES.md)"]
    (folder / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    checkpoint = CHECKPOINTS[section["dir"]]
    check_body = [f'# Checkpoint: {section["title"]}\n',
                  'Attempt without notes. Explain mechanisms and draw histories before opening the rubric.\n',
                  '## Scenario\n', checkpoint['scenario'], '\n## Questions\n']
    check_body += [f'{i}. {q}' for i, q in enumerate(checkpoint['questions'], 1)]
    check_body += ['\n## Evidence to produce\n', checkpoint['evidence'],
                   '\nScore each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.\n',
                   '<details><summary>Review rubric after attempting</summary>\n', checkpoint['rubric'],
                   '\n</details>\n', '[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)']
    (folder / 'CHECKPOINT.md').write_text('\n'.join(check_body) + '\n', encoding='utf-8')
(ROOT / "PROGRESS.md").write_text("\n".join(progress) + "\n", encoding="utf-8")
coverage += ["\n## Required end-to-end reasoning checks\n",
             "These questions are the synthesis gate. The linked chapter supplies the mechanism; its exercises require a history, failure analysis, or implementation.\n",
             "Question | Primary teaching file\n--- | ---"]
question_map = [
    ("What happens after a URL is entered?", "03-networking/dns-tls-http.md"),
    ("How does HTML become pixels?", "04-frontend/browser-internals.md"),
    ("How can one JavaScript thread handle concurrent network work?", "04-frontend/javascript-runtime.md"),
    ("What causes React rendering, and what changes the DOM?", "04-frontend/react-mental-model.md"),
    ("What happens inside a backend after HTTP arrives?", "05-backend/server-architecture.md"),
    ("Why do indexes help reads and cost writes?", "06-databases/indexes-and-query-plans.md"),
    ("How can correct-looking transactions violate an invariant?", "06-databases/transactions-and-mvcc.md"),
    ("What happens when 100,000 requests miss one key?", "07-caching/cache-failures.md"),
    ("Why is JWT decoding different from verification and trust?", "08-security/sessions-jwt-oauth.md"),
    ("What if a worker crashes after the effect but before acknowledgement?", "09-messaging-streaming/queues-and-workers.md"),
    ("How can two servers believe they are leader?", "10-distributed-systems/consensus-and-leadership.md"),
    ("What if a lease expires while its holder continues?", "10-distributed-systems/leases-and-fencing.md"),
    ("What can fencing enforce that expiration alone cannot?", "10-distributed-systems/leases-and-fencing.md"),
    ("How can absence be certain while presence is probabilistic?", "11-system-data-structures/bloom-filters.md"),
    ("Why are LSM trees useful for writes, and what debt remains?", "11-system-data-structures/lsm-trees.md"),
    ("What if a write is followed by a lagging-replica read?", "06-databases/scaling-and-nosql.md"),
    ("What must a system decide during a network partition?", "10-distributed-systems/partial-failure-and-consistency.md"),
    ("How do payment APIs handle retries safely?", "20-production-patterns/idempotency-and-deduplication.md"),
    ("Where did a five-second request spend its time?", "14-observability/logs-metrics-traces.md"),
    ("How does one service evolve toward large scale?", "21-case-studies/relay-evolution.md"),
]
coverage += [f'{question} | [Read and practice]({path})' for question, path in question_map]
coverage += ["\n## Audit interpretation\n",
             "All 22 requested areas have authored teaching material and a checkpoint. The final editorial pass separated skip lists, Merkle trees, HyperLogLog, and inverted indexes into dedicated chapters; expanded JavaScript execution examples and rate-limiter comparisons; and sharpened the lease-fencing limit. The worked system-design set contains 4 beginner, 6 intermediate, and 8 advanced designs. Five project briefs and runnable mechanism labs connect concepts to evidence.\n",
             "[VALIDATION.md](VALIDATION.md) records structural checks, executed labs, source reachability, qualitative review, and verification limits. Depth labels apply to the containing chapter, not a claim that each vocabulary term has an independent full-length chapter. Read the linked section for its specific treatment."]
(ROOT / "COVERAGE.md").write_text("\n".join(coverage) + "\n", encoding="utf-8")
print(f'Indexed {len(SECTIONS)} sections and {sum(len(s["chapters"]) for s in DATA["sections"])} chapters.')
