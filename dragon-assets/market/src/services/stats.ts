/**
 * 统计服务
 */

import { Stats, TemplateMeta } from '../types';
import { FILES, readJson } from '../utils/storage';

/**
 * 获取统计数据
 */
export function getStats(): Stats {
  const templates = readJson<TemplateMeta[]>(FILES.templates);

  // 按分类统计
  const byCategory: Record<string, number> = {};
  templates.forEach(t => {
    byCategory[t.category] = (byCategory[t.category] || 0) + 1;
  });

  // 按状态统计
  const byStatus: Record<string, number> = {};
  templates.forEach(t => {
    byStatus[t.status] = (byStatus[t.status] || 0) + 1;
  });

  // 最近模板
  const recentTemplates = [...templates]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 5);

  // 热门模板（按下载量）
  const topTemplates = [...templates]
    .sort((a, b) => b.downloads - a.downloads)
    .slice(0, 10);

  return {
    totalTemplates: templates.length,
    totalDownloads: templates.reduce((sum, t) => sum + t.downloads, 0),
    totalCategories: Object.keys(byCategory).length,
    byCategory,
    byStatus,
    recentTemplates,
    topTemplates,
  };
}

/**
 * 获取热门标签
 */
export function getPopularTags(limit = 20): Array<{ tag: string; count: number }> {
  const templates = readJson<TemplateMeta[]>(FILES.templates);
  const tagCount: Record<string, number> = {};

  templates.forEach(t => {
    t.tags.forEach(tag => {
      tagCount[tag] = (tagCount[tag] || 0) + 1;
    });
  });

  return Object.entries(tagCount)
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, limit);
}
