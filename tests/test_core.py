"""Tests for tilde_path_expander.core."""

from __future__ import annotations

import os
import unittest

from tilde_path_expander.core import expand_path, collapse_path


class TestCollapsePath(unittest.TestCase):
    """Direct tests of the string-level collapsing logic."""

    def test_empty_returns_empty(self):
        self.assertEqual(collapse_path(""), "")

    def test_single_dot_unchanged(self):
        self.assertEqual(collapse_path("."), ".")

    def test_redundant_separators_collapsed(self):
        self.assertEqual(collapse_path("a//b///c"), "a/b/c")

    def test_current_dir_components_resolved(self):
        self.assertEqual(collapse_path("a/./b/./c"), "a/b/c")

    def test_parent_references_resolved(self):
        self.assertEqual(collapse_path("a/b/../c"), "a/c")

    def test_collapse_to_dot(self):
        self.assertEqual(collapse_path("a/.."), ".")

    def test_relative_leading_parent_preserved(self):
        self.assertEqual(collapse_path("a/../../b"), "../b")

    def test_absolute_root_unchanged(self):
        self.assertEqual(collapse_path("/"), "/")

    def test_absolute_climbs_above_root_clamped(self):
        self.assertEqual(collapse_path("/.."), "/")
        self.assertEqual(collapse_path("/a/../.."), "/")

    def test_trailing_slash_stripped(self):
        self.assertEqual(collapse_path("a/b/"), "a/b")

    def test_type_error_on_non_str(self):
        with self.assertRaises(TypeError):
            collapse_path(123)  # type: ignore[arg-type]


class TestExpandPath(unittest.TestCase):
    """Tests for the public expand_path entry point.

    Tilde expansion depends on the operating environment and the real home
    directory of the current user, so we cannot assert on ``~`` producing a
    fixed value. We instead assert on properties that are deterministic on
    every platform: that ``~`` is expanded, and that the result is further
    collapsed.
    """

    def test_plain_path_collapsed(self):
        self.assertEqual(expand_path("a//b/./c"), "a/b/c")

    def test_absolute_path_unchanged_in_structure(self):
        self.assertEqual(expand_path("/a/b/../c"), "/a/c")

    def test_tilde_expanded_on_posix(self):
        if os.name == "nt":
            self.skipTest("tilde expansion is a POSIX convention")
        home = os.path.expanduser("~")
        result = expand_path("~/foo//bar")
        self.assertTrue(result.startswith(home + "/"))
        self.assertEqual(result, os.path.join(home, "foo/bar"))

    def test_tilde_plus_user_expanded_on_posix(self):
        if os.name == "nt":
            self.skipTest("tilde expansion is a POSIX convention")
        user = os.environ.get("USER") or os.environ.get("LOGNAME") or ""
        if not user:
            self.skipTest("no USER/LOGNAME set in environment")
        # On POSIX ``~user`` expands via the password database. We assert
        # that the leading ``~`` has been replaced rather than asserting on
        # the specific home directory, which is environment-dependent.
        result = expand_path(f"~{user}/foo/../bar")
        self.assertFalse(result.startswith("~"))
        self.assertTrue(result.endswith("/bar"))

    def test_tilde_left_alone_on_windows(self):
        if os.name != "nt":
            self.skipTest("only relevant on Windows")
        # On Windows ``~`` is a literal directory name, not a home marker.
        self.assertEqual(expand_path("~/foo/./bar"), "~/foo/bar")

    def test_type_error_on_non_str(self):
        with self.assertRaises(TypeError):
            expand_path(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
