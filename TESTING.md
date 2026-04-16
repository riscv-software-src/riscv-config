# Testing

Tests for the RISC-V ISA regex pattern.

## Quick Start

```bash
make help           # See all commands
make install-test   # Install dependencies
make test           # Run tests
```

## What's Tested

- Valid ISA strings: `RV32I`, `RV64IG`, `RV32I_Zicsr`
- Invalid patterns: `RV64G`, `rv32i`, `RV32IZicsr`
- Edge cases and real configs

## Running Tests

```bash
make test                      # Basic test run
make test-coverage            # Full coverage report  
make test-coverage-constants  # Coverage for regex only
```

## Adding Tests

Edit `tests/test_constants.py`:

```python
# Valid patterns
("RV32I_NewExt", True),

# Invalid patterns  
("RV32I_BadExt", False),
```

## CI Setup

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
    - run: make install-test
    - run: make test
```

## Troubleshooting

**Import errors?** Make sure you're in project root:
```bash
cd /workspaces/riscv-config
export PYTHONPATH=.
```

**Coverage report?** Open `htmlcov/index.html` after running coverage tests.
