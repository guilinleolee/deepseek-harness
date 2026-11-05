#!/bin/sh
# Staged whitespace check for the pre-commit hook.
#
# `dragon-assets/` is a verbatim mirror of the upstream engine tree: its
# markdown carries the source file's trailing spaces, and rewriting them would
# break mirror fidelity. Everything else in the tree keeps the one-trailing-
# newline and no-trailing-whitespace rules.
#
# The pathspec lives here rather than inline in lefthook.yml because a shell
# that re-parses the quoted `:(exclude)` literal loses the exclusion.

git diff --cached --check -- . ':(exclude)dragon-assets'
