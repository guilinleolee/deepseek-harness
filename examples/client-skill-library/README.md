# client-skill-library · 客户技能库 profile

> 用途：卡巴格私有部署的**每个 DSH 实例**用这个 profile 启动，技能只从打包库挂载。
> 对应卡巴格任务书 §6 前置 a："技能库（天龙 skills）作为服务器侧管理员统一维护的只读资产"。

## 部署流程

```bash
# 1. 按当前授权清单打库（每次发版跑一次）
python dragon-assets/runtime/scripts/pack-skill-library.py --out /srv/dsh/client-library
# → /srv/dsh/client-library/skills/<33 个资产> + ATTRIBUTIONS.md

# 2. 安装 profile 到实例的 DSH_HOME
cp examples/client-skill-library/cordis.patch.yml  $DSH_HOME/profiles/client-skill-library/cordis.patch.yml
cp examples/client-skill-library/package.json      $DSH_HOME/profiles/client-skill-library/

# 3. 启动实例时指向库目录
CLIENT_SKILL_LIBRARY_DIR=/srv/dsh/client-library/skills dsh --profile client-skill-library "任务"
```

## 安全属性

| 属性 | 实现 |
|---|---|
| **只挂打包库** | `skill-filesystem` 的 `includeDefaultRoots: false` 关掉项目根 / 用户根 / bundled 根，`customSkillDirs` 只留库目录 |
| **无库不降级** | `CLIENT_SKILL_LIBRARY_DIR` 未设置时挂载为零个技能 —— **不会**静默回退到本机未审查技能 |
| **授权边界在库内** | 库内容由 `DELIVERABLE_SKILLS.json` 决定，AGPL / NC / 专有资产物理上不在库里 |
| **致谢随包** | 库根有 `ATTRIBUTIONS.md`；Apache-2.0 资产目录内带 NOTICE |

## 管理员维护（卡巴格 §6 前置 a）

- 库目录对实例**只读**（文件系统权限控制，不由本 profile 实现）
- 版本升级 = 重跑 `pack-skill-library.py` + 替换库目录 + 重启实例
- 发版前 CI 会跑 `verify-dragon-deliverable-skills`，清单与注册表不一致即拦截

## 与 minimax-code-plan 的关系

本 profile 的模型段与 `examples/minimax-code-plan` 相同（MiniMax Code Plan，无 DeepSeek 依赖）。
区别只在技能挂载：那个例子挂本机默认技能根，适合开发者自用；本例子只挂打包库，适合交付。
