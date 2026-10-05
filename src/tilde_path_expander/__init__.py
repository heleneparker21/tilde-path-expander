"""Tilde Path Expander.

A focused library for expanding leading tildes in paths and collapsing
redundant separators and parent references.
"""

from .core import expand_path, collapse_path

__all__ = ["expand_path", "collapse_path"]
