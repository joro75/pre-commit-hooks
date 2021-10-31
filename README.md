[![PyPI pyversions](https://img.shields.io/badge/python-3.7-blue.svg)]()
[![GitHub Release](https://img.shields.io/github/release/joro75/pre-commit-hooks.svg)](https://github.com/joro75/pre-commit-hooks/releases)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![codecov](https://codecov.io/gh/joro75/pre-commit-hooks/branch/main/graph/badge.svg?token=TUIBLCE5CW)](https://codecov.io/gh/joro75/pre-commit-hooks)

pre-commit-hooks
================

A [pre-commit](https://pre-commit.com/) hook to verify if a Microsoft MSBuild of a C/C++ project was successfully build, before the code changes are actually committed.

See also: https://github.com/pre-commit/pre-commit

### Using pre-commit-hooks with pre-commit

Add this to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/joro75/pre-commit-hooks
    rev: v0.5.0
    hooks:
    -   id: check-successful-c-msbuild
```

### Hooks available

#### `check-successful-c-msbuild`
Check that the Microsoft C/C++ project file project was successfully build, before the code changes are actually committed.

* `--buildtype` - specifies the build type (or 'Solution Configuration' as it is called by Microsoft) that should be checked. Can be specified multiple times, and defaults to 'Release' if not specified at all.

For each modified file, it is checked which Microsoft C/C++ project files (\*.vcxproj) are present in the same or one of its parent directories. If the modified file is indeed included in one or more of the Microsoft C/C++ project files, a check is done if the build was successful, and is more recent than the change time of the modified file.
