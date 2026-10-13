---
license: UNKNOWN
name: openspace-community-bridge
description: OpenSpace云端技能社区桥接，连接本地天龙引擎与云端技能市场
github_repo: HKUDS/OpenSpace
github_hash: d1e367d0ed4722d67f1f3b95d816ba4a959288d2
last_updated: 2026-04-25
source_type: marketplace
triggers: ["openspace community bridge", "OpenSpace Community Bridge"]
---

# OpenSpace Community Bridge

## Overview

OpenSpace Community Bridge enables天龙引擎 skills to publish, share, and sync with the [OpenSpace Cloud Skill Community](https://open-space.cloud). This bridge supports Public, Private, and Team三级共享机制, allowing skills to be distributed through the OpenSpace marketplace while maintaining天龙引擎's existing skill architecture.

## Core Features

### 1. 三级共享机制

| Level | Visibility | Description |
|-------|------------|-------------|
| **Public** | Global marketplace | Skills published to open-space.cloud community |
| **Private** | Personal namespace | Skills only visible to the owner |
| **Team** | Organization scope | Skills shared within a team/organization |

### 2. Skill Publishing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ Skill Development → Validation → Versioning → Publishing   │
└─────────────────────────────────────────────────────────────┘
          │              │              │              │
          ▼              ▼              ▼              ▼
    Local Testing   Lint/Format    Git Tag v1.0   OpenSpace API
```

### 3. Community Sync

- Real-time sync with OpenSpace Cloud
- Version conflict detection and resolution
- Dependency resolution for shared skills
- Star/favorite tracking for popular skills

## Token Efficiency Integration

OpenSpace reports **4.2x performance improvement** and **46% token savings** through their skill optimization system. This bridge leverages those optimizations when importing community skills.

## Usage

```bash
# Publish a skill to OpenSpace
openspace publish <skill-name> --visibility public|private|team

# Sync community skills
openspace sync --source open-space.cloud --target ~/.claude/skills/

# Search community skills
openspace search "category:debugging" --sort stars

# Import a community skill
openspace import <skill-id> [--rename <new-name>]

# Check skill status
openspace status <skill-name>
```

## Integration with 天龙Skills Market

This bridge integrates with天龙引擎's existing skills infrastructure:

- **Skills Index**: Community skills appear in `SKILLS_INDEX.md`
- **Hook System**: Post-publish hooks for documentation updates
- **Validation**: Aligns with天龙skill quality standards (SKILL.md, scripts/, tests/)

## OpenSpace API Integration

```python
# Initialize OpenSpace client
from openspace_bridge import OpenSpaceClient

client = OpenSpaceClient(
    api_key=os.environ["OPENSPACE_API_KEY"],
    base_url="https://api.open-space.cloud/v1"
)

# Publish skill
result = client.skills.publish(
    name="openspace-fix-repair",
    version="1.0.0",
    visibility="public",
    files=["./SKILL.md", "./scripts/"]
)
```

## Skill Metadata Schema

```yaml
name: openspace-community-bridge
version: 1.0.0
visibility: public  # public | private | team
category: infrastructure
tags:
  - community
  - sync
  - marketplace
  - open-space
dependencies:
  - requests>=2.28.0
  - pydantic>=2.0.0
author:
  name: Dragon Engine Team
  github: https://github.com/HKUDS/OpenSpace
open_space:
  skill_id: os_skill_xxx
  marketplace_url: https://open-space.cloud/skills/xxx
  stars: 0
  downloads: 0
```

## File Structure

```
openspace-community-bridge/
├── SKILL.md                    # This file
├── scripts/
│   ├── community_sync.py       # Sync logic with OpenSpace Cloud
│   └── skill_publisher.py      # Publishing pipeline
└── README.md                   # Quick start guide
```

## Examples

### Publishing a天龙Skill to OpenSpace

```bash
# Authenticate
openspace auth --login

# Validate skill structure
openspace validate ./skills/my-skill/

# Publish with version bump
openspace publish my-skill --bump patch --visibility public

# Monitor stats
openspace stats my-skill --watch
```

### Importing Community Skills

```bash
# Search for debugging skills
openspace search "debugging" --filter "stars>100"

# Preview before import
openspace preview os_skill_12345

# Import and rename
openspace import os_skill_12345 --rename debug-helper
```

## 与天龙现有技能市场协同

| Feature | 天龙Skills Market | OpenSpace Bridge |
|---------|------------------|------------------|
| Scope | Local/CI | Cloud marketplace |
| Sharing | Manual | Automated sync |
| Discovery | SKILLS_INDEX.md | open-space.cloud search |
| Versioning | Git tags | OpenSpace version API |
| Stars | N/A | Marketplace rating |

## 参考资源

- OpenSpace Cloud: https://open-space.cloud
- API Documentation: https://api.open-space.cloud/docs
- Skill Marketplace: https://open-space.cloud/skills
- 165 Autonomous Evolution Skills: https://open-space.cloud/explore

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-02 | Initial release with Public/Private/Team visibility |
