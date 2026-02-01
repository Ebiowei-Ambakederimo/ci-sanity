# ci-sanity

A CLI tool that tells you your CI will fail before you push.

Like ESLint, but for pipelines with trust issues.

## Install

```bash
npm install -g ci-sanity
```

## Usage

```bash
ci-sanity check
```

### Options

```bash
ci-sanity check --github          # Check GitHub Actions
ci-sanity check --gitlab          # Check GitLab CI
ci-sanity check --path ./project  # Specify directory
ci-sanity check --strict          # Warnings = errors
```

## What It Catches

**YAML syntax errors**
Bad indentation, missing colons, malformed structure.

**Invalid runners**
Unknown or unsupported runner names.

**Platform mismatches**
Docker on Windows runners. Linux commands on Windows.

**Unpinned action versions**
Actions using @master or @main instead of pinned versions.

**Missing secrets**
References to secrets not declared in config.

**Wrong step order**
Checkout after other steps. Cache after install.

## Configuration

Create `.ci-sanity.yml` in your project root:

```yaml
platform: github
secrets:
  - DATABASE_URL
  - STRIPE_KEY
strict: false
```

No config file needed. Defaults work fine.

## Exit Codes

- `0` = clean, no issues
- `1` = warnings found
- `2` = errors found (CI will fail)

## Examples

```bash
# Check current directory
ci-sanity check

# Check specific project
ci-sanity check --path ~/projects/my-app

# Strict mode (warnings = errors)
ci-sanity check --strict
```

## Features

Fast. Runs in under 1.5 seconds.
Offline. No network calls.
Zero setup. Works immediately.
Clear output. Shows exactly what's wrong.

## Supported Platforms

GitHub Actions: yes
GitLab CI: yes

More platforms coming if users ask.

## Why This Exists

CI configs fail for dumb reasons.
You only find out after pushing.
Red builds waste time.
This tool catches errors locally.

## Development

```bash
npm install
npm run build
npm link
ci-sanity check
```

## License

MIT
