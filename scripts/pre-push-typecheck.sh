#!/bin/sh
# git pre-push feeds "<local-ref> <local-sha> <remote-ref> <remote-sha>" lines on stdin.
#
# The typecheck below validates THIS worktree's checkout, so it is a real gate for a
# pushed ref only when that ref is contained in HEAD (the checked-out commit). Pushing
# a branch that is not checked out would otherwise pass or fail on the wrong tree —
# refuse that push instead of validating silently. A deletion (all-zero sha) needs no
# check. When stdin carries no refs (a runner that does not forward it), fall through
# to the typecheck unchanged.
fail=0
while read -r localRef localSha remoteRef remoteSha; do
  [ -n "$localSha" ] || continue
  [ "$localSha" = "0000000000000000000000000000000000000000" ] && continue
  if ! git merge-base --is-ancestor "$localSha" HEAD 2>/dev/null; then
    echo "pre-push typecheck: $(git rev-parse --short "$localSha" 2>/dev/null || echo "$localSha") ($localRef) is not contained in the checked-out HEAD ($(git rev-parse --short HEAD))." >&2
    echo "This hook typechecks the checked-out tree; check out the branch being pushed first, or push with --no-verify if you really mean it." >&2
    fail=1
  fi
done
[ "$fail" -ne 0 ] && exit 1
exec pnpm run typecheck
