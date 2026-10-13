---
name: dashboard-learning-integration
description: Dragon Dashboard 学习进度可视化集成
---

# 🐉 Dragon Dashboard 学习进度集成

将 Claudeception 学习进度可视化集成到 Dragon Dashboard。

## 新增 API 端点

```javascript
// 获取学习统计
GET /api/learning/stats
Response: {
  totalSkills: 24,
  recentSkills: 5,
  categories: { error: 8, pattern: 6, workaround: 5, debug: 5 },
  qualityScore: 4.2,
  knowledgeRetention: 85
}

// 获取技能列表
GET /api/learning/skills?category=error&sort=recent
Response: [{ id, name, category, qualityScore, createdAt, usageCount }]

// 获取知识图谱
GET /api/learning/graph
Response: { nodes: [], edges: [] }
```

## Dashboard 组件

```typescript
// components/LearningOverview.tsx
export function LearningOverview() {
  return (
    <div className="learning-dashboard">
      {/* 统计卡片 */}
      <StatCard title="总技能数" value={24} change="+3" />
      <StatCard title="质量评分" value={4.2} change="+0.3" />
      <StatCard title="知识留存率" value="85%" change="+15%" />
      <StatCard title="复用次数" value={142} change="+28" />

      {/* 学习趋势图 */}
      <LearningTrendChart data={learningData} />

      {/* 技能分类分布 */}
      <CategoryDistribution categories={categories} />

      {/* 最近技能 */}
      <RecentSkills skills={recentSkills} />
    </div>
  );
}
```

## 路由更新

```typescript
// app/dashboard/page.tsx
export default function DashboardPage() {
  return (
    <DashboardLayout>
      <Tabs>
        <TabsList>
          <Tab value="overview">总览</Tab>
          <Tab value="tasks">任务</Tab>
          <Tab value="learning">学习进度</Tab> {/* 新增 */}
          <Tab value="agents">代理</Tab>
        </TabsList>
        <TabsContent value="learning">
          <LearningOverview />
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
}
```

## 数据获取 Hook

```typescript
// hooks/useLearningData.ts
export function useLearningStats() {
  return useQuery({
    queryKey: ['learning', 'stats'],
    queryFn: () => fetch('/api/learning/stats').then(r => r.json()),
    refetchInterval: 60000, // 每分钟刷新
  });
}
```

## WebSocket 实时更新

```typescript
// lib/learning-websocket.ts
export function subscribeToLearningUpdates(callback: (update: LearningUpdate) => void) {
  const ws = new WebSocket('ws://localhost:3000/api/learning/stream');

  ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    callback(update);
  };

  return () => ws.close();
}
```

## 完整配置文件

```json
{
  "learningDashboard": {
    "enabled": true,
    "refreshInterval": 60000,
    "widgets": {
      "stats": { "enabled": true, "position": "top" },
      "trendChart": { "enabled": true, "position": "middle" },
      "categories": { "enabled": true, "position": "bottom-left" },
      "recentSkills": { "enabled": true, "position": "bottom-right" }
    }
  }
}
```
