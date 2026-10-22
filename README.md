# Tilde Path Expander

Expands leading tildes (`~`, `~user`) in paths and collapses redundant separators and parent references (`a//b/../c` -> `a/c`).

## Usage

```python
from tilde_path_expander import expand_path, collapse_path

expand_path("~/projects/tilde_path_expander//src/../tests")
# -> '/home/you/projects/tilde_path_expander/tests'

collapse_path("a//b/./c/../d")
# -> 'a/d'
```

## Why this exists

`os.path.expanduser` only handles the `~` prefix; it does not collapse `//`, `.`, or `..` that appear later in the string. `os.path.normpath` collapses structure but does not expand `~`. Glueing them together is a one-liner, except for the fact that `normpath` on Windows rewrites forward slashes to backslashes and lowercases drive letters, which is a filesystem concern you may not want leaking into a string operation.

This library makes one explicit trade-off: collapsing is purely lexical and always uses POSIX semantics (forward slashes, no drive-letter handling). Tilde expansion is dispatched to the native `expanduser` on POSIX and disabled on Windows, where `~` is a literal directory name. If you need Windows-style backslash normalisation, call `os.path.normpath` on the result yourself.

## Exported names

- `expand_path(path: str) -> str` — expand a leading `~`/`~user` and collapse the result.
- `collapse_path(path: str) -> str` — collapse redundant separators and `.`/`..` components only.

## Awkward edges

- `collapse_path("")` returns `""`, not `"."`. An empty path is degenerate; inventing a `.` would add content the caller did not supply. A path that collapses to nothing (e.g. `"a/.."`) does return `"."`, because that is the only usable filesystem path.
- For absolute paths, `..` that would climb above the root is clamped: `collapse_path("/..")` returns `"/"`. For relative paths, leading `..` components are preserved because they are the only signal about the intended directory level.
- Trailing slashes are stripped (`"a/b/"` -> `"a/b"`), except for the root itself (`"/"` stays `"/"`).

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

## Limitations

Values are coerced to floats, so very large integers lose precision. If you need
exact integer aggregates over a window, this is the wrong tool.

