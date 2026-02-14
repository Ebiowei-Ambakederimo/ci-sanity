# ci-sanity

A CLI tool that tells you your CI will fail before you push.

Like ESLint, but for pipelines with trust issues.

## Installation

```bash
pip install ci-sanity
```

## Usage

```bash
# Check current directory
ci-sanity check

# Check specific directory
ci-sanity check --path ./my-repo

# Strict mode (warnings become errors)
ci-sanity check --strict

# Custom config file
ci-sanity check --config custom-config.yml
```

## What It Checks

### YAML Validation
Catches syntax and structure errors before your CI does.

```
✗ job.build.steps[2] is invalid yaml (line 34)
  → fix yaml syntax
```

### Runner Compatibility
Validates runner names and detects common mistakes.

```
⚠ unknown runner: ubuntu-20.04-custom
  → use ubuntu-latest, windows-latest, or macos-latest

✗ uses docker but runner is windows. pick a side.
  → use ubuntu-latest for docker
```

### Action Version Checking
Flags unpinned or unstable action versions.

```
⚠ actions/checkout@master = chaos energy. pin a version.
  → use @v3 or a specific commit sha

✗ action actions/setup-node has no version
  → add @v3 or specific version
```

### Missing Secrets Detection
Finds undeclared secrets and suggests fixes.

```
⚠ secret STRIPE_KET not found. typo or optimism?
  → did you mean STRIPE_KEY? or add to .ci-sanity.yml
```

### Step Order Sanity
Catches illogical step ordering.

```
⚠ step runs before checkout
  → move actions/checkout to first step

⚠ install runs before cache
  → move cache step before install
```

## Configuration

Create `.ci-sanity.yml` in your project root:

```yaml
platform: github

secrets:
  - DATABASE_URL
  - STRIPE_KEY
  - AWS_ACCESS_KEY_ID

strict: false
```

No config file needed. Defaults work fine.

## Exit Codes

- `0` = No issues
- `1` = Warnings found
- `2` = Errors found (CI will probably fail)

## Supported Platforms

- GitHub Actions
- GitLab CI

## Performance

Runs in under 1 second on average.

Zero network calls. Works offline.

## Why This Exists

CI configs fail for dumb reasons:
- Bad YAML
- Missing secrets
- Wrong runners
- Ancient actions

You only find out after pushing. Red build. Rage. Coffee.

ci-sanity catches these before you push.

## Philosophy

Keep it boring. Boring pays.

- No auto-fixing
- No UI dashboard
- No AI
- No enterprise policy engine

Just fast, local validation.

## Development

```bash
# Clone repo
git clone https://github.com/yourusername/ci-sanity.git
cd ci-sanity

# Install in dev mode
pip install -e .

# Run tests
python -m pytest

# Run on example workflows
ci-sanity check --path examples/
```

## License

MIT