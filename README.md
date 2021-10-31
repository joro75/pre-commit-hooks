[![PyPI pyversions](https://img.shields.io/badge/python-3.7-blue.svg)]()
[![codecov](https://codecov.io/gh/joro75/pre-commit-hooks/branch/main/graph/badge.svg?token=TUIBLCE5CW)](https://codecov.io/gh/joro75/pre-commit-hooks)
[![GitHub Release](https://img.shields.io/github/release/joro75/pre-commit-hooks.svg)](https://github.com/joro75/pre-commit-hooks/releases)

pre-commit-hooks
================

A pre-commit to verify if a Microsoft MSBuild of a C/C++ project was successful

See also: https://github.com/pre-commit/pre-commit

### Using pre-commit-hooks with pre-commit

Add this to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/joro75/pre-commit-hooks
    rev: v0.4.0
    hooks:
    -   id: check-successful-c-msbuild
```

### Hooks available

#### `check-successfull-c-msbuild`
Check that the MSBuild of a C/C++ project was successful before the commit is performed.
