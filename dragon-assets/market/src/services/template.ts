/**
 * 模板服务 - 核心业务逻辑
 */

import fs from 'fs';
import path from 'path';
import {
  TemplateMeta,
  TemplateCreateInput,
  TemplateUpdateInput,
  TemplateFilter
} from '../types';
import {
  FILES,
  PATHS,
  readJson,
  writeJson,
  generateId,
  generateSlug,
  getTemplatePath
} from './storage';

/**
 * 获取所有模板
 */
export function getAllTemplates(filter?: TemplateFilter): {
  templates: TemplateMeta[];
  total: number;
} {
  const allTemplates = readJson<TemplateMeta[]>(FILES.templates);

  let filtered = [...allTemplates];

  // 过滤
  if (filter) {
    if (filter.category) {
      filtered = filtered.filter(t => t.category === filter.category);
    }
    if (filter.tags && filter.tags.length > 0) {
      filtered = filtered.filter(t =>
        filter.tags!.some(tag => t.tags.includes(tag))
      );
    }
    if (filter.search) {
      const search = filter.search.toLowerCase();
      filtered = filtered.filter(t =>
        t.name.toLowerCase().includes(search) ||
        t.description.toLowerCase().includes(search) ||
        t.tags.some(tag => tag.toLowerCase().includes(search))
      );
    }
    if (filter.status) {
      filtered = filtered.filter(t => t.status === filter.status);
    }

    // 排序
    const sortBy = filter.sortBy || 'createdAt';
    const sortOrder = filter.sortOrder || 'desc';
    filtered.sort((a, b) => {
      let aVal: string | number = a[sortBy] as string | number;
      let bVal: string | number = b[sortBy] as string | number;

      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = (bVal as string).toLowerCase();
      }

      if (sortOrder === 'asc') {
        return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      } else {
        return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
      }
    });

    // 分页
    const page = filter.page || 1;
    const limit = filter.limit || 20;
    const start = (page - 1) * limit;
    filtered = filtered.slice(start, start + limit);
  }

  return {
    templates: filtered,
    total: allTemplates.length,
  };
}

/**
 * 获取单个模板
 */
export function getTemplateById(id: string): TemplateMeta | null {
  const templates = readJson<TemplateMeta[]>(FILES.templates);
  return templates.find(t => t.id === id) || null;
}

/**
 * 获取模板通过 slug
 */
export function getTemplateBySlug(slug: string): TemplateMeta | null {
  const templates = readJson<TemplateMeta[]>(FILES.templates);
  return templates.find(t => t.slug === slug) || null;
}

/**
 * 创建模板
 */
export function createTemplate(input: TemplateCreateInput, filePath?: string): TemplateMeta {
  const templates = readJson<TemplateMeta[]>(FILES.templates);

  const id = generateId();
  const slug = generateSlug(input.name);
  const now = new Date().toISOString();

  // 获取文件信息
  let fileName = '';
  let fileSize = 0;

  if (filePath && fs.existsSync(filePath)) {
    fileName = path.basename(filePath);
    fileSize = fs.statSync(filePath).size;

    // 移动文件到模板目录
    const templateDir = getTemplatePath(id);
    fs.mkdirSync(templateDir, { recursive: true });
    fs.copyFileSync(filePath, path.join(templateDir, fileName));
  }

  const template: TemplateMeta = {
    id,
    slug,
    name: input.name,
    description: input.description,
    category: input.category,
    tags: input.tags || [],
    author: input.author || 'Anonymous',
    version: '1.0.0',
    fileName,
    fileSize,
    fileType: input.fileType || 'pptx',
    slides: input.slides || 0,
    dimensions: input.dimensions,
    colorScheme: input.colorScheme,
    features: input.features,
    downloads: 0,
    views: 0,
    rating: 0,
    ratingCount: 0,
    createdAt: now,
    updatedAt: now,
    status: 'draft',
    license: input.license,
    source: input.source,
  };

  templates.push(template);
  writeJson(FILES.templates, templates);

  // 更新统计
  updateStats();

  return template;
}

/**
 * 更新模板
 */
export function updateTemplate(id: string, input: TemplateUpdateInput): TemplateMeta | null {
  const templates = readJson<TemplateMeta[]>(FILES.templates);
  const index = templates.findIndex(t => t.id === id);

  if (index === -1) return null;

  const template = templates[index];
  const updated: TemplateMeta = {
    ...template,
    ...input,
    updatedAt: new Date().toISOString(),
  };

  // 如果更新了名称，重新生成 slug
  if (input.name && input.name !== template.name) {
    updated.slug = generateSlug(input.name);
  }

  templates[index] = updated;
  writeJson(FILES.templates, templates);

  return updated;
}

/**
 * 删除模板
 */
export function deleteTemplate(id: string): boolean {
  const templates = readJson<TemplateMeta[]>(FILES.templates);
  const index = templates.findIndex(t => t.id === id);

  if (index === -1) return false;

  templates.splice(index, 1);
  writeJson(FILES.templates, templates);

  // 删除模板文件
  const templateDir = getTemplatePath(id);
  if (fs.existsSync(templateDir)) {
    fs.rmSync(templateDir, { recursive: true, force: true });
  }

  // 更新统计
  updateStats();

  return true;
}

/**
 * 记录下载
 */
export function recordDownload(id: string): boolean {
  const templates = readJson<TemplateMeta[]>(FILES.templates);
  const index = templates.findIndex(t => t.id === id);

  if (index === -1) return false;

  templates[index].downloads += 1;
  writeJson(FILES.templates, templates);

  // 更新统计
  updateStats();

  return true;
}

/**
 * 记录浏览
 */
export function recordView(id: string): boolean {
  const templates = readJson<TemplateMeta[]>(FILES.templates);
  const index = templates.findIndex(t => t.id === id);

  if (index === -1) return false;

  templates[index].views += 1;
  writeJson(FILES.templates, templates);

  return true;
}

/**
 * 获取模板文件路径
 */
export function getTemplateFilePath(id: string): string | null {
  const template = getTemplateById(id);
  if (!template) return null;

  const filePath = path.join(getTemplatePath(id), template.fileName);
  if (!fs.existsSync(filePath)) return null;

  return filePath;
}

/**
 * 更新统计数据
 */
function updateStats(): void {
  const templates = readJson<TemplateMeta[]>(FILES.templates);

  const stats = {
    totalTemplates: templates.length,
    totalDownloads: templates.reduce((sum, t) => sum + t.downloads, 0),
    lastUpdated: new Date().toISOString(),
  };

  writeJson(FILES.stats, stats);
}

/**
 * 搜索建议（用于自动补全）
 */
export function getSearchSuggestions(query: string, limit = 10): string[] {
  const templates = readJson<TemplateMeta[]>(FILES.templates);
  const suggestions = new Set<string>();

  const q = query.toLowerCase();

  templates.forEach(t => {
    if (t.name.toLowerCase().includes(q)) {
      suggestions.add(t.name);
    }
    t.tags.forEach(tag => {
      if (tag.toLowerCase().includes(q)) {
        suggestions.add(tag);
      }
    });
  });

  return Array.from(suggestions).slice(0, limit);
}
