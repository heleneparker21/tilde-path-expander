"""Path expansion and collapsing logic."""

from __future__ import annotations

import os
import posixpath

__all__ = ["expand_path", "collapse_path"]


def expand_path(path: str) -> str:
    r"""Expand a leading ``~`` or ``~user`` in *path* and collapse it.

    Tilde expansion is a POSIX shell convention, not a filesystem property.
    On Windows a leading ``~`` is treated as a literal directory name, so we
    dispatch on the os path flavour rather than blindly calling
    :func:`os.path.expanduser` everywhere. This avoids surprising users on
    Windows by silently rewriting ``~foo`` to ``C:\Users\foo``.

    After expansion the result is passed through :func:`collapse_path` so that
    redundant separators (``a//b``) and parent references (``a/../b``) are
    normalised in one place rather than duplicated across functions.
    """
    if not isinstance(path, str):
        raise TypeError(f"path must be str, not {type(path).__name__}")

    if os.name == "nt":
        # Windows does not interpret ``~`` specially; leave it alone and only
        # collapse redundant structure.
        return collapse_path(path)

    expanded = os.path.expanduser(path)
    return collapse_path(expanded)


def collapse_path(path: str) -> str:
    """Collapse redundant separators and ``.`` / ``..`` components in *path*.

    Design decisions, stated plainly so the tests are not a moving target:

    * Empty input becomes ``""``, not ``.``. An empty string is a degenerate
      path and returning ``.`` would invent content the caller did not supply.
    * A path that collapses away to nothing (e.g. ``"a/.."``) returns
      ``.`` rather than the empty string, so the result is still a usable
      filesystem path.
    * ``..`` that would climb above the root is discarded for absolute paths
      (``/..`` -> ``/``) and preserved for relative paths
      (``a/../../b`` stays). Relative paths keep their leading ``..``
      components because they are the only signal the caller has about the
      intended directory level.
    * A trailing slash is stripped unless the path is the root directory
      (``/``). Input that explicitly ends in ``os.sep`` is normalised; callers
      who need to distinguish ``a/`` from ``a`` should check the input, not
      the collapsed output.
    """
    if not isinstance(path, str):
        raise TypeError(f"path must be str, not {type(path).__name__}")

    if path == "":
        return ""

    # posixpath works for both Unix semantics and for the purely lexical
    # collapsing we do here. On Windows ``os.path.normpath`` would flip
    # forward slashes to backslashes and lowercase drive letters, which is a
    # filesystem concern, not a string concern. We keep separators as the
    # caller wrote them (forward slash) and only collapse structure.
    normalised = posixpath.normpath(path)

    # ``normpath`` turns ``""`` into ``"."`` and ``"a/.."`` into ``"."``
    # but leaves ``"."`` alone. For an originally-empty input we preserve
    # the empty string; for a non-empty input that collapsed to ``.`` we keep
    # the ``.`` so the result is always usable as a path.
    if path != "" and normalised == ".":
        return "."
    return normalised
