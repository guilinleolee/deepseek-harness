/**
 * 存储工具 - 本地文件存储
 */

import fs from 'fs';
import path from 'path';
import { app } from 'electron';

// 获取项目根目录
const getProjectRoot = (): string => {
  // 尝试从环境变量获取
  if (process.env.MARKET_ROOT) {
    return process.env.MARKET_ROOT;
  }

  // 默认到 dragon-engine/market
  const homePath = process.env.HOME || process.env.USERPROFILE || '';
  return path.join(homePath, '.claude', 'dragon-engine', 'market');
};

const ROOT = getProjectRoot();

// 存储路径
export const PATHS = {
  root: ROOT,
  data: path.join(ROOT, 'data'),
  templates: path.join(ROOT, 'templates'),
  uploads: path.join(ROOT, 'uploads'),
  temp: path.join(ROOT, 'temp'),
  backup: path.join(ROOT, 'backup'),
  logs: path.join(ROOT, 'logs'),
};

// 索引文件
export const FILES = {
  templates: path.join(PATHS.data, 'templates.json'),
  categories: path.join(PATHS.data, 'categories.json'),
  stats: path.join(PATHS.data, 'stats.json'),
  tags: path.join(PATHS.data, 'tags.json'),
};

/**
 * 初始化存储目录
 */
export async function initStorage(): Promise<void> {
  const dirs = Object.values(PATHS);

  for (const dir of dirs) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      console.log(`📁 Created: ${dir}`);
    }
  }

  // 初始化索引文件
  await initIndexFiles();
}

/**
 * 初始化索引文件
 */
async function initIndexFiles(): Promise<void> {
  const files = [
    { path: FILES.templates, defaultValue: [] },
    { path: FILES.categories, defaultValue: getDefaultCategories() },
    { path: FILES.stats, defaultValue: getDefaultStats() },
    { path: FILES.tags, defaultValue: [] },
  ];

  for (const file of files) {
    if (!fs.existsSync(file.path)) {
      fs.writeFileSync(file.path, JSON.stringify(file.defaultValue, null, 2));
      console.log(`📄 Created: ${file.path}`);
    }
  }
}

/**
 * 读取 JSON 文件
 */
export function readJson<T>(filePath: string): T {
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }
  const content = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(content) as T;
}

/**
 * 写入 JSON 文件
 */
export function writeJson<T>(filePath: string, data: T): void {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

/**
 * 获取存储路径
 */
export function getStoragePath(): string {
  return PATHS.root;
}

/**
 * 获取模板目录路径
 */
export function getTemplatePath(id: string): string {
  return path.join(PATHS.templates, id);
}

/**
 * 生成唯一 ID
 */
export function generateId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  return `${timestamp}-${random}`;
}

/**
 * 生成 slug
 */
export function generateSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// 默认分类
function getDefaultCategories() {
  return [
    {
      id: 'business',
      name: '商业办公',
      slug: 'business',
      description: '商业计划书、工作报告、会议演示等',
      icon: '💼',
      color: '#3B82F6',
      order: 1,
      subcategories: [
        { id: 'business-plan', name: '商业计划书', slug: 'business-plan', parentId: 'business' },
        { id: 'report', name: '工作报告', slug: 'report', parentId: 'business' },
        { id: 'meeting', name: '会议演示', slug: 'meeting', parentId: 'business' },
      ]
    },
    {
      id: 'marketing',
      name: '营销推广',
      slug: 'marketing',
      description: '产品介绍、活动策划、品牌宣传等',
      icon: '📣',
      color: '#10B981',
      order: 2,
      subcategories: [
        { id: 'product-intro', name: '产品介绍', slug: 'product-intro', parentId: 'marketing' },
        { id: 'campaign', name: '活动策划', slug: 'campaign', parentId: 'marketing' },
        { id: 'brand', name: '品牌宣传', slug: 'brand', parentId: 'marketing' },
      ]
    },
    {
      id: 'education',
      name: '教育培训',
      slug: 'education',
      description: '课程课件、培训资料、学术报告等',
      icon: '📚',
      color: '#8B5CF6',
      order: 3,
    },
    {
      id: 'personal',
      name: '个人简历',
      slug: 'personal',
      description: '简历、作品集、个人介绍等',
      icon: '👤',
      color: '#F59E0B',
      order: 4,
    },
    {
      id: 'social',
      name: '社交媒体',
      slug: 'social',
      description: '小红书、抖音、微博等社交平台内容',
      icon: '📱',
      color: '#EC4899',
      order: 5,
    },
  ];
}

// 默认统计
function getDefaultStats() {
  return {
    totalTemplates: 0,
    totalDownloads: 0,
    lastUpdated: new Date().toISOString(),
  };
}
