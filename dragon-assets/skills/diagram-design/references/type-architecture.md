# 架构图设计参考

## 适用场景
软件架构、系统拓扑、网络架构、微服务架构、云架构

## 设计原则
- **目标密度**: 4/10（清晰组件）
- **组件数量**: 约8-12个，层级3-4层
- **accent使用**: 核心组件或关键路径用accent
- **布局**: 分层对齐，同层组件等高

## 组件类型

### 服务组件
```
外形: 圆角矩形 (rx=6)
尺寸: width=100-120, height=60
填充: var(--service) opacity="0.1"
边框: var(--service) stroke-width=2
文字: 中文名称 center, 英文 sublabel muted
```
- 适用于: API服务、微服务、业务逻辑

### 数据库组件
```
外形: 圆柱形 (上椭圆 + 矩形 + 下椭圆)
尺寸: width=80-100, height=50-70
填充: var(--database) opacity="0.1"
边框: var(--database) stroke-width=2
文字: center 居中
```
- 适用于: MySQL、PostgreSQL、MongoDB、Redis

### 外部系统
```
外形: 圆角矩形 (rx=6)
尺寸: width=100-120, height=60
填充: var(--external) opacity="0.1"
边框: var(--external) stroke-dasharray="4,4" stroke-width=1.5
文字: muted 灰色
```
- 适用于: 第三方API、CDN、用户浏览器

### 核心组件 (accent)
```
外形: 圆角矩形 (rx=6)
尺寸: width=100-120, height=60
填充: var(--accent) opacity="0.15"
边框: var(--accent) stroke-width=2
文字: var(--accent) font-weight=600
```
- 适用于: API Gateway、认证中心、核心调度

## 连接线规范

### 实线 (同步调用)
```svg
<path d="M X1 Y1 L X2 Y2"
      stroke="var(--link)" stroke-width="1.5" fill="none"
      marker-end="url(#arrow)"/>
```

### 虚线 (异步/可选)
```svg
<path d="M X1 Y1 L X2 Y2"
      stroke="var(--link)" stroke-width="1.5" fill="none"
      stroke-dasharray="4,2" marker-end="url(#arrow)"/>
```

### 数据库连接
```svg
<path d="M X1 Y1 L X2 Y2"
      stroke="var(--database)" stroke-width="1.5" fill="none"
      marker-end="url(#db-arrow)"/>
```

## 层级布局
```
┌─────────────────────────────────────┐
│           客户端层                   │  y=60, height=50
├─────────────────────────────────────┤
│           网关层                     │  y=130, height=50
├─────────────────────────────────────┤
│  服务A   服务B   服务C   服务D       │  y=210, height=60
├─────────────────────────────────────┤
│         消息队列                     │  y=310, height=40
├─────────────────────────────────────┤
│  数据库A  数据库B  数据库C           │  y=390, height=50
└─────────────────────────────────────┘
```

## 命名规范
| 组件类型 | 中文 | 英文 |
|---------|------|------|
| 网关 | API 网关 | API Gateway |
| 服务 | 用户服务/订单服务 | User Service / Order Service |
| 数据库 | 用户数据库 | User DB |
| 队列 | 消息队列 | Message Queue |
| 缓存 | 缓存层 | Cache Layer |

## 常见布局模式

### 单体架构
```
┌─────────────────────────────┐
│         客户端              │
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│      单体应用 (accent)     │
│  ┌─────────────────────┐   │
│  │ Controller/Svc/DAO │   │
│  └─────────────────────┘   │
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│          数据库             │
└─────────────────────────────┘
```

### 微服务架构
```
客户端 → API Gateway → 用户服务/订单服务/支付服务 → 消息队列 → 各数据库
```

### 三层架构
```
客户端层 → 业务逻辑层 → 数据访问层 → 数据库
```

## 箭头标记定义
```svg
<defs>
  <marker id="arrow" markerWidth="8" markerHeight="8"
           refX="7" refY="4" orient="auto">
    <path d="M 0 0 L 8 4 L 0 8 Z" fill="var(--ink)"/>
  </marker>
  <marker id="db-arrow" markerWidth="8" markerHeight="8"
           refX="7" refY="4" orient="auto">
    <path d="M 0 0 L 8 4 L 0 8 Z" fill="var(--database)"/>
  </marker>
</defs>
```

## 质量检查清单
- [ ] 组件数量 ≤ 12
- [ ] 层级清晰分离（视觉上等高）
- [ ] 连接线无交叉或重叠
- [ ] 数据库符号正确（圆柱形）
- [ ] 外部系统使用虚线边框
- [ ] WCAG AA 对比度（文字/背景 ≥ 4.5:1）
- [ ] 组件间距 ≥ 20px
- [ ] 图例完整（与图中元素一一对应）
