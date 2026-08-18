# gitpulse

CLI tool to inspect recent git commit history from any local repository.

```
pip install rook-gitpulse
```

## Usage

```bash
gitpulse [PATH] [OPTIONS]
```

| Argument / Option | Description |
|---|---|
| `PATH` | Path to a git repository (default: current directory) |
| `--limit N` | Number of recent commits to show (default: 10) |
| `--output FORMAT` | Output format: `text`, `json`, `table`, or `csv` |

## Examples

```bash
# last 10 commits from current repo
gitpulse

# another repo, 25 commits, in a table
gitpulse ~/projects/myapp --limit 25 --output table

# pipe to jq
gitpulse . --output json | jq '.items[].title'

# export to CSV
gitpulse . --output csv > commits.csv
```

## Output modes

**text** (default) — human-readable digest:
```
# gitpulse

1. **fix: handle edge case in parser**  (by alice · 2026-08-18 · 3fa1c2b0)
2. **feat: add csv export**  (by bob · 2026-08-17 · 8d2e9a11)
```

**json** — structured output:
```json
{
  "source": "gitpulse",
  "count": 2,
  "items": [
    { "title": "fix: handle edge case", "author": "alice", "body": "3fa1c2b0", ... }
  ]
}
```

**table** — markdown table with subject, author, date, hash

**csv** — spreadsheet-friendly rows

## Agent use

```bash
gitpulse introspect   # ACLI-compliant JSON tool description
gitpulse skill        # agentskills.io-compliant SKILL.md
```

## Install from source

```bash
git clone https://github.com/rook-builds/gitpulse
cd gitpulse
pip install -e .
```

## License

MIT
