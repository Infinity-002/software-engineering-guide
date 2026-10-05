"""Validate local Markdown navigation and curriculum structure (stdlib only)."""
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "tools/curriculum.json").read_text(encoding="utf-8"))
errors = []
files = sorted(ROOT.rglob("*.md"))
link_count = 0
external_urls = set()


def outside_fences(body):
    lines = []
    fence = None
    for line in body.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return "\n".join(lines), fence


def heading_ids(body):
    ids, seen = set(), Counter()
    for line in outside_fences(body)[0].splitlines():
        heading = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not heading:
            continue
        label = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", heading.group(1))
        slug = re.sub(r"[^\w\-\s]", "", label.lower()).replace(" ", "-")
        suffix = f"-{seen[slug]}" if seen[slug] else ""
        ids.add(slug + suffix)
        seen[slug] += 1
    ids.update(re.findall(r'<a\s+(?:id|name)="([^"]+)"', body))
    return ids


for file in files:
    body = file.read_text(encoding="utf-8")
    relative = file.relative_to(ROOT).as_posix()
    prose, open_fence = outside_fences(body)
    if open_fence:
        errors.append(f"{relative}: unclosed code fence")
    if body.count("<details>") != body.count("</details>"):
        errors.append(f"{relative}: unbalanced details blocks")
    if not body.strip() or not body.startswith("# "):
        errors.append(f"{relative}: missing content or top-level title")
    if re.search(r"\b(?:TODO|TBD|FIXME)\b|coming soon|content goes here", prose, re.I):
        errors.append(f"{relative}: possible placeholder")
    for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", prose):
        target = target.strip().strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme in ("http", "https"):
            external_urls.add(target)
            continue
        if parsed.scheme or target.startswith("mailto:"):
            continue
        link_count += 1
        destination = (file.parent / unquote(parsed.path)).resolve() if parsed.path else file
        if not destination.is_relative_to(ROOT):
            errors.append(f"{relative}: link escapes repository: {target}")
        elif not destination.exists():
            errors.append(f"{relative}: missing target: {target}")
        elif parsed.fragment and destination.suffix == ".md":
            if unquote(parsed.fragment) not in heading_ids(destination.read_text(encoding="utf-8")):
                errors.append(f"{relative}: missing anchor: {target}")

chapter_stats = []
critical_concepts = ["leases", "fencing tokens", "Bloom filters", "consistent hashing", "Merkle trees",
                     "LSM trees", "B+ trees", "WAL", "MVCC", "connection pooling", "backpressure",
                     "load shedding", "idempotency", "transactional outbox", "clock problems",
                     "replication lag", "cache stampede", "hot partitions", "retry storms", "jitter",
                     "DLQs", "poison messages", "schema evolution", "API compatibility",
                     "browser rendering", "JavaScript event loop", "hydration", "server state", "CORS",
                     "CSRF", "JWT verification", "trust boundaries", "WebSockets", "SSE",
                     "graceful shutdown", "distributed tracing", "SLI", "SLO", "SLA", "RPO", "RTO"]
catalog_concepts = {topic.lower() for s in DATA["sections"] for c in s["chapters"] for topic in c[3].split(";")}
for concept in critical_concepts:
    if concept.lower() not in catalog_concepts:
        errors.append(f"Missing critical coverage concept: {concept}")
for section in DATA["sections"]:
    for name in ("README.md", "CHECKPOINT.md"):
        if not (ROOT / section["dir"] / name).exists():
            errors.append(f'{section["dir"]}: missing {name}')
    for slug, title, priority, topics in section["chapters"]:
        path = ROOT / section["dir"] / f"{slug}.md"
        if not path.exists():
            errors.append(f"Missing chapter: {path.relative_to(ROOT)}")
            continue
        body = path.read_text(encoding="utf-8")
        prose = outside_fences(body)[0]
        words = len(re.findall(r"\b[\w'-]+\b", body))
        if words < 600:
            errors.append(f"{path.relative_to(ROOT)}: short teaching chapter ({words} words); review depth")
        if not re.search(r"^## Exercises", body, re.M):
            errors.append(f"{path.relative_to(ROOT)}: missing end-of-chapter exercises")
        if "## Further reading" not in body:
            errors.append(f"{path.relative_to(ROOT)}: missing further reading")
        if len(re.findall(r"\]\((?!https?:)[^)]+\.md(?:#[^)]*)?\)", prose)) < 2:
            errors.append(f"{path.relative_to(ROOT)}: insufficient local concept connections")
        chapter_stats.append({"file": path.relative_to(ROOT).as_posix(), "words": words})

required_roots = ["README.md", "ROADMAP.md", "GLOSSARY.md", "PROGRESS.md", "INTERVIEW-ROADMAP.md",
                  "SYSTEM-DESIGN-ROADMAP.md", "EXERCISES.md", "REFERENCES.md", "COVERAGE.md", "VALIDATION.md"]
for name in required_roots:
    if not (ROOT / name).exists():
        errors.append(f"Missing root document: {name}")

stats = {
    "markdown_files": len(files), "sections": len(DATA["sections"]),
    "chapters": len(chapter_stats), "chapter_words": sum(x["words"] for x in chapter_stats),
    "all_markdown_words": sum(len(re.findall(r"\b[\w'-]+\b", f.read_text(encoding="utf-8"))) for f in files),
    "local_links": link_count, "external_urls": len(external_urls),
    "concept_entries": sum(len(c[3].split(";")) for s in DATA["sections"] for c in s["chapters"]),
    "critical_concepts_checked": len(critical_concepts),
    "shortest_chapters": sorted(chapter_stats, key=lambda x: x["words"])[:8],
    "errors": errors,
}
(ROOT / "tools/validation-results.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
print(json.dumps(stats, indent=2))
sys.exit(bool(errors))
