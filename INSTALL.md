# Installation Guide

## Directory Structure

Create this structure:

```
ci-sanity/
├── src/
│   └── ci_sanity/
│       ├── __init__.py
│       ├── cli.py
│       ├── checker.py
│       ├── config.py
│       ├── models.py
│       └── rules/
│           ├── __init__.py
│           ├── yaml_syntax.py
│           ├── runner_compat.py
│           ├── action_version.py
│           ├── secrets.py
│           └── step_order.py
├── setup.py
├── README.md
└── .ci-sanity.yml (example)
```

## Step-by-Step Setup

### 1. Create Directory

```bash
mkdir ci-sanity
cd ci-sanity
```

### 2. Create Source Structure

```bash
mkdir -p src/ci_sanity/rules
```

### 3. Copy Files

Copy each artifact file to its location:

- `setup.py` → root
- `README.md` → root
- `.ci-sanity.yml` → root (example)
- `models.py` → `src/ci_sanity/`
- `config.py` → `src/ci_sanity/`
- `checker.py` → `src/ci_sanity/`
- `cli.py` → `src/ci_sanity/`
- Package `__init__.py` files → respective directories
- Rule files → `src/ci_sanity/rules/`

### 4. Install Dependencies

```bash
pip install pyyaml
```

### 5. Install Package

Development mode (editable):
```bash
pip install -e .
```

Production install:
```bash
pip install .
```

### 6. Verify Installation

```bash
ci-sanity check --help
```

You should see the help text.

## Quick Test

Create a test workflow:

```bash
mkdir -p test-repo/.github/workflows
cat > test-repo/.github/workflows/test.yml << 'EOF'
name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@master
      - run: npm install
EOF
```

Run ci-sanity:

```bash
ci-sanity check --path test-repo
```

Expected output:
```
test-repo/.github/workflows/test.yml
  test
    ⚠ actions/checkout@master = chaos energy. pin a version.
      → use @v3 or a specific commit sha

1 warning(s)
```

## Distribution

### PyPI Package

For distribution via pip:

```bash
# Build
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

### Single Binary

For standalone binary:

```bash
pip install pyinstaller
pyinstaller --onefile src/ci_sanity/cli.py --name ci-sanity
```

Binary will be in `dist/ci-sanity`.

## Troubleshooting

### Import errors

Make sure you installed in the correct directory:
```bash
pip install -e .
```

### Command not found

Check your PATH includes pip's bin directory:
```bash
python -m ci_sanity.cli check
```

### No workflows found

Verify you have workflows in:
- `.github/workflows/*.yml`
- `.gitlab-ci.yml`

## Next Steps

1. Test on real projects
2. Add more rules
3. Submit to PyPI
4. Build binary releases