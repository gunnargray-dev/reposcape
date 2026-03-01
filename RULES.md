# Reposcape Development Rules

Rules governing autonomous development sessions.

## Session Protocol

1. **Read state first.** Every session starts by reading ROADMAP.md, SESSION_LOG.md, and the current source tree to understand what exists.
2. **Pick tasks from the roadmap.** Choose 2-4 items from the Active Sprint. If the sprint is empty, promote items from the next phase.
3. **Write code locally, test locally.** Clone all repo files into the sandbox, write new code, run `python -m pytest` until all tests pass.
4. **Push to feature branch.** Never push directly to main. Create a branch named `session-N-description`.
5. **Open a PR.** Include what was built, what was tested, and test results in the PR body.
6. **Merge the PR.** After confirming CI passes and tests are green, merge via squash.
7. **Update bookkeeping on main.** After merging, push updates to ROADMAP.md (check off items), SESSION_LOG.md (append entry), and README.md (update stats).
8. **Notify.** Send a push notification summarizing the session.

## Code Standards

- **Python 3.10+ compatible.** Use type hints. Use f-strings.
- **Pure stdlib where possible.** Minimize external dependencies for the analysis engine. FastAPI and D3.js are exceptions for the web layer.
- **Every module gets tests.** Aim for 80%+ coverage. Tests live in `tests/` mirroring `src/` structure.
- **Docstrings on all public functions.** Google-style.
- **No hardcoded paths.** Everything relative to project root.
- **Max function length: 50 lines.** Extract helpers aggressively.
- **Max file length: 400 lines.** Split into modules when approaching.

## Git Conventions

- Branch names: `session-N-short-description`
- Commit messages: `feat: ...`, `fix: ...`, `test: ...`, `docs: ...`, `refactor: ...`
- PR titles: `Session N: Feature Description`
- One PR per session (may contain multiple commits)

## Quality Gates

- All tests must pass before pushing
- No syntax errors (validated by `python -m py_compile`)
- Health score >= 80 (once health module exists)
- Coverage >= 80% (once coverage tracking exists)

## Architecture

```
reposcape/
  src/
    __init__.py
    clone.py          # Git clone + log parsing
    languages.py      # Language/LOC analysis
    heatmap.py        # Commit frequency data
    treemap.py        # File tree analysis
    contributors.py   # Author stats
    complexity.py     # Cyclomatic complexity
    dependencies.py   # Import graph
    techdebt.py       # Tech debt scoring
    server.py         # FastAPI web server
  tests/
    __init__.py
    test_clone.py
    test_languages.py
    ...
  frontend/
    index.html
    js/
    css/
  ROADMAP.md
  SESSION_LOG.md
  RULES.md
  README.md
  pyproject.toml
```

## Decision-Making

- **Bias toward shipping.** A working feature beats a perfect plan.
- **Bias toward visualization.** Every analysis should produce something visual and shareable.
- **Bias toward the demo.** The Nightshift repo is the default demo target. Build features that look impressive when run against it.
- **Human issues take priority.** If the repo owner opens a GitHub issue, address it in the next session before roadmap items.
