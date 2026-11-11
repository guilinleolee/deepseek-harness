# client-skill-library · the client skill-library profile

English | [中文](README.zh.md)

> Purpose: **every DSH instance** of the Kabage private deployment starts with this profile, so skills mount from the packed library only.
> This implements Kabage task-brief §6 prerequisite a: "the skill library (Dragon skills) as a read-only asset maintained centrally by the server-side administrator".

## Deployment

```bash
# 1. Pack the library from the current license list (once per release)
python dragon-assets/runtime/scripts/pack-skill-library.py --out /srv/dsh/client-library
# → /srv/dsh/client-library/skills/<33 assets> + ATTRIBUTIONS.md

# 2. Install the profile into the instance's DSH_HOME
cp examples/client-skill-library/cordis.patch.yml  $DSH_HOME/profiles/client-skill-library/cordis.patch.yml
cp examples/client-skill-library/package.json      $DSH_HOME/profiles/client-skill-library/

# 3. Point the instance at the library directory on start
CLIENT_SKILL_LIBRARY_DIR=/srv/dsh/client-library/skills dsh --profile client-skill-library "task"
```

## Security properties

| Property | Implementation |
|---|---|
| **Packed library only** | `skill-filesystem`'s `includeDefaultRoots: false` turns off the project root, the user root, and the bundled root; `customSkillDirs` keeps only the library directory |
| **No silent fallback** | when `CLIENT_SKILL_LIBRARY_DIR` is unset the profile mounts zero skills — it **never** falls back silently to unreviewed local skills |
| **License boundary inside the library** | the library content is decided by `DELIVERABLE_SKILLS.json`; AGPL / NC / proprietary assets are physically absent from the library |
| **Attribution ships with the pack** | the library root carries `ATTRIBUTIONS.md`; Apache-2.0 assets carry a NOTICE in their directories |

## Administrator maintenance (Kabage §6 prerequisite a)

- The library directory is **read-only** to instances (enforced by file-system permissions, not by this profile)
- A version upgrade = rerun `pack-skill-library.py` + replace the library directory + restart the instance
- Before a release, CI runs `verify-dragon-deliverable-skills` and blocks when the manifest and the registry disagree

## Relationship to minimax-code-plan

The model section of this profile is identical to `examples/minimax-code-plan` (MiniMax Code Plan, no DeepSeek dependency).
The difference is only skill mounting: that example mounts the local default skill roots for developer use; this one mounts the packed library only, for delivery.
