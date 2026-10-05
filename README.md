# Software Engineering Guide

A connected curriculum for understanding how applications work, fail, and evolve. The starting point is basic programming and data structures. The destination is the ability to build, explain, operate, and debug a production system.

Start with the [roadmap](ROADMAP.md). Track demonstrated skills in [PROGRESS.md](PROGRESS.md), choose work from [EXERCISES.md](EXERCISES.md), and use [COVERAGE.md](COVERAGE.md) as the searchable concept index. [REFERENCES.md](REFERENCES.md) separates specifications, implementation documentation, papers, and books.

## How to study

Read one chapter, draw its mechanism from memory, predict a failure, and complete an exercise before moving on. Keep a lab notebook with your hypothesis, experiment, observation, and revised model. Reading alone does not satisfy a checkpoint. A chapter's priority measures learning order, not intellectual value.

- **P0 — Must know / Essential:** the foundation for building and explaining ordinary applications.
- **P1 — Strong engineer / Important:** production judgment, failure handling, and deeper interviews.
- **P2 — Advanced:** distributed coordination and infrastructure internals.
- **P3 — Specialist:** optional extensions, proofs, and specialized implementations.

Every section has a reading order and a checkpoint. Solutions and rubrics are folded away so that you can make a prediction first. Code blocks are focused teaching examples; pseudocode is explicitly labeled. The [projects](projects/README.md) supply acceptance criteria and failure experiments, rather than a ready-made application to copy.

## The running application

**Relay** is a team workspace: users belong to workspaces, create tasks, discuss them, upload attachments, and receive notifications. Start with a browser, one backend, and PostgreSQL. Add a component only when a measured bottleneck or a concrete guarantee justifies its operational cost. Its [evolution](21-case-studies/relay-evolution.md) connects the whole course; [the life of a request](12-fullstack/the-life-of-a-request.md) follows one click through the system and back to pixels.

The examples favor TypeScript, Node.js, React, PostgreSQL, and Redis. Concepts come first. Linux examples also work inside a Linux VM or WSL; commands that need additional packages or privileges are identified. Library defaults are version-sensitive: consult the linked official documentation before applying an example to a different version. Security examples teach boundaries, not homemade cryptography.

## Focused routes

- [Interview roadmap](INTERVIEW-ROADMAP.md): practice explaining mechanisms, diagnosing failures, and defending choices.
- [System design roadmap](SYSTEM-DESIGN-ROADMAP.md): progress from a single data path to coordination across machines.
- [Glossary](GLOSSARY.md): distinguish overloaded terms such as consistency, session, partition, and event.
- [Validation report](VALIDATION.md): coverage, links, and the limits of the repository audit.

All teaching material is local Markdown. External reading is optional enrichment and a way to inspect the exact claims of a specification or implementation. Architecture examples are educational scenarios, not claims about the private internals of named commercial products.
