# Layer Painter Automated Test Suite (MP-1)

Quick reference for running tests.

## Quick Start

```bash
# Run all tests
cd tests
python test_runner.py

# Run specific quick win tests
python test_runner.py --qw1  # UID duplication
python test_runner.py --qw2  # Input validation
python test_runner.py --qw3  # Depsgraph optimization
python test_runner.py --qw4  # Image import errors

# With verbose output and coverage
python test_runner.py -v --coverage
```

## Test Files

| File | Tests | Coverage |
|------|-------|----------|
| `test_qw1_uid_duplication.py` | 35 | Material UID generation, duplication, sync |
| `test_qw2_input_validation.py` | 50 | Operator validation, error handling |
| `test_qw3_depsgraph_optimization.py` | 35 | Performance, caching, responsiveness |
| `test_qw4_image_import.py` | 40 | File validation, error handling, edge cases |
| **Total** | **150+** | All P0 quick wins |

## Key Test Categories

### QW-1: UID Duplication (test_qw1_uid_duplication.py)
- ✅ UID generation and format validation
- ✅ Duplicate material detection
- ✅ UID syncing across duplicates
- ✅ Layer preservation during duplication
- ✅ Undo/redo integrity
- ✅ Performance scaling

### QW-2: Input Validation (test_qw2_input_validation.py)
- ✅ Material lookup validation (6 layer operators)
- ✅ Channel lookup validation (4 channel operators)
- ✅ Paint operator validation (2 paint operators)
- ✅ Safe `.get()` pattern usage
- ✅ Error message quality
- ✅ Edge case handling (special chars, unicode, empty values)

### QW-3: Depsgraph Optimization (test_qw3_depsgraph_optimization.py)
- ✅ Depsgraph handler is now no-op
- ✅ No CPU overhead from high-frequency calls
- ✅ UID sync only at load/undo time
- ✅ Material integrity maintained
- ✅ UI responsiveness
- ✅ Cache invalidation still works

### QW-4: Image Import (test_qw4_image_import.py)
- ✅ Missing file handling
- ✅ Permission error handling
- ✅ Corrupted image handling
- ✅ Missing node handling
- ✅ Descriptive error messages
- ✅ Edge cases (long paths, special chars, unicode)

## Requirements

```bash
pip install pytest pytest-cov pytest-html Pillow numpy
```

## CI/CD

Automated tests run on:
- Every push to `main` or `develop`
- Every pull request

See `.github/workflows/tests.yml` for configuration.

## Full Documentation

See [TESTING.md](../TESTING.md) for complete documentation including:
- Detailed test description
- Fixture reference
- Adding new tests
- Troubleshooting
- Performance metrics
