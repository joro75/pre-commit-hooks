
pre-commit-hooks
================

A pre-commit to verify if a Microsoft MSBuild of a C/C++ project was successful

See also: https://github.com/pre-commit/pre-commit

### Using pre-commit-hooks with pre-commit

Add this to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/joro75/pre-commit-hooks
    rev: v0.9.0  # Use the ref you want to point at
    hooks:
    -   id: check-successful-msbuild
```

### Hooks available

#### `check-successfull-msbuild`
Check that the MSBuild was successful.
