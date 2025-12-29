# Pre-commit Hooks Guide

This project uses **pre-commit hooks** to automatically check and format code before each commit.

## What are Pre-commit Hooks?

Pre-commit hooks are scripts that run automatically **before** you commit code to Git. They help maintain code quality by:

- ✅ Formatting code consistently (black, isort)
- ✅ Finding bugs and errors (flake8, mypy)
- ✅ Detecting security issues (bandit)
- ✅ Preventing common mistakes (trailing whitespace, large files)

## Installation

Pre-commit hooks are automatically installed when you run:

```bash
make install
```

Or manually:

```bash
pip install pre-commit
pre-commit install
```

## Usage

### Automatic (on commit)

Hooks run automatically when you commit:

```bash
git add .
git commit -m "Add feature"
# Pre-commit hooks run automatically here
```

If any hook fails, the commit is **blocked** and you must fix the issues.

### Manual (run on all files)

Run hooks on all files without committing:

```bash
make pre-commit
# or
pre-commit run --all-files
```

### Skip hooks (emergency only)

To skip hooks for a specific commit (not recommended):

```bash
git commit --no-verify -m "Emergency fix"
```

## Configured Hooks

### 1. **black** - Code Formatting
- Automatically formats Python code
- Line length: 100 characters
- Ensures consistent style across the project

### 2. **isort** - Import Sorting
- Sorts and organizes imports
- Groups imports by: stdlib, third-party, first-party
- Compatible with black

### 3. **flake8** - Linting
- Checks for Python errors and style issues
- Enforces PEP 8 style guide
- Detects unused imports, undefined variables, etc.

### 4. **mypy** - Type Checking
- Static type checking for Python
- Catches type-related bugs before runtime
- Improves code documentation

### 5. **bandit** - Security Checks
- Scans for common security issues
- Detects hardcoded passwords, SQL injection, etc.
- Helps maintain secure code

### 6. **General Checks**
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation
- Large file detection (>1MB)
- Private key detection

## Configuration

Configuration is stored in:

- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `pyproject.toml` - Tool-specific settings (black, isort, mypy, etc.)

## Troubleshooting

### Hook fails with "command not found"

Update pre-commit hooks:

```bash
pre-commit autoupdate
pre-commit install --install-hooks
```

### Want to skip a specific hook?

Edit `.pre-commit-config.yaml` and comment out the hook.

### Hooks are too slow?

Run only specific hooks:

```bash
pre-commit run black --all-files
pre-commit run flake8 --all-files
```

## Best Practices

1. **Run hooks before pushing** - Catch issues early
2. **Don't skip hooks** - They're there to help you
3. **Fix issues immediately** - Don't accumulate technical debt
4. **Update hooks regularly** - `pre-commit autoupdate`

## Examples

### Example 1: Formatting Code

```bash
# Before commit
$ git commit -m "Add feature"

black....................................................................Passed
isort....................................................................Passed
flake8...................................................................Passed
mypy.....................................................................Passed
bandit...................................................................Passed

[master abc1234] Add feature
 2 files changed, 50 insertions(+)
```

### Example 2: Hook Failure

```bash
# Before commit
$ git commit -m "Add feature"

black....................................................................Failed
- hook id: black
- files were modified by this hook

reformatted app/main.py
All done! ✨ 🍰 ✨
1 file reformatted.

# Fix and try again
$ git add app/main.py
$ git commit -m "Add feature"

black....................................................................Passed
[master abc1234] Add feature
 2 files changed, 50 insertions(+)
```

## Benefits

- ✅ **Consistent code style** - All developers follow the same standards
- ✅ **Fewer bugs** - Catch errors before they reach production
- ✅ **Better security** - Detect security issues early
- ✅ **Faster reviews** - No need to discuss formatting in PRs
- ✅ **Automated** - No manual work required

## Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
