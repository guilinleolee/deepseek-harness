# Dragon Brain 架构文档

## 1. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Dragon Brain                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │ init-brain │  │query-brain │  │  update-brain    │   │
│  │    .sh     │  │    .sh     │  │      .sh         │   │
│  └─────────────┘  └─────────────┘  └─────────────────┘   │
│         │                │                  │              │
│         └────────────────┼──────────────────┘              │
│                          ▼                                 │
│                 ┌─────────────────┐                         │
│                 │  ~/.dragon-     │                         │
│                 │  engine/       │                         │
│                 │  projects/     │                         │
│                 │  {project_id}/ │                         │
│                 │  brain.json    │                         │
│                 └─────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## 2. 数据流

```
用户请求
    │
    ▼
1. 查询 Brain ──────▶ query-brain.sh ──▶ brain.json
    │                                        │
    │                                        ▼
2. 更新 Brain ◀─────── update-brain.sh ◀─────┘
    │
    ▼
3. 注入上下文 ──▶ LLM/Skill 生成内容
```

## 3. 与 SlideSmith Brain 的对比

| 特性 | SlideSmith Brain | Dragon Brain |
|------|-----------------|--------------|
| 存储格式 | JSON | JSON |
| 模板支持 | 无 | 3种预设模板 |
| 多项目管理 | 无 | ✅ 完整多项目 |
| 平台配置 | 固定 | 可配置 |
| 合规管理 | 无 | ✅ License/规则 |

## 4. 调用示例

### 4.1 AI Agent 调用

```javascript
// 在 AI Agent 中调用 Brain
const brain = require('./dragon-brain/scripts/query-brain.sh');

// 获取当前项目上下文
const context = brain.query();
const { brand, style, platforms } = context;

// 生成内容时注入上下文
const prompt = `根据以下品牌上下文生成内容:
品牌: ${brand.name}
定位: ${brand.niche}
受众: ${brand.audience}
配色: ${style.colors.primary}
平台: ${Object.keys(platforms).filter(k => platforms[k].enabled).join(', ')}
`;
```

### 4.2 Skill 集成

```javascript
// 在其他 Skill 中集成 Brain
const fs = require('fs');
const path = require('path');

function getBrainContext(projectId) {
    const brainFile = path.join(
        process.env.HOME,
        '.dragon-engine',
        'projects',
        projectId,
        'brain.json'
    );

    if (!fs.existsSync(brainFile)) {
        return null;
    }

    return JSON.parse(fs.readFileSync(brainFile, 'utf8'));
}
```

## 5. 扩展点

### 5.1 自定义模板

创建新的模板文件：

```bash
# 模板目录
skills/dragon-brain/memory/
├── template-{template_id}.json
```

### 5.2 存储后端扩展

当前使用文件系统存储，未来可扩展：

- SQLite: 高并发场景
- Redis: 缓存层
- Cloudflare KV: 多设备同步
