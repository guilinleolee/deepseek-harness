/**
 * 分类服务
 */

import { Category } from '../types';
import { FILES, readJson, writeJson } from '../utils/storage';

/**
 * 获取所有分类
 */
export function getAllCategories(): Category[] {
  return readJson<Category[]>(FILES.categories);
}

/**
 * 获取单个分类
 */
export function getCategoryById(id: string): Category | null {
  const categories = getAllCategories();
  return categories.find(c => c.id === id) || null;
}

/**
 * 获取分类通过 slug
 */
export function getCategoryBySlug(slug: string): Category | null {
  const categories = getAllCategories();
  return categories.find(c => c.slug === slug) || null;
}

/**
 * 创建分类
 */
export function createCategory(input: Omit<Category, 'id' | 'order' | 'templateCount'>): Category {
  const categories = getAllCategories();

  const category: Category = {
    ...input,
    id: input.slug,
    order: categories.length + 1,
    templateCount: 0,
  };

  categories.push(category);
  writeJson(FILES.categories, categories);

  return category;
}

/**
 * 更新分类
 */
export function updateCategory(id: string, input: Partial<Category>): Category | null {
  const categories = getAllCategories();
  const index = categories.findIndex(c => c.id === id);

  if (index === -1) return null;

  categories[index] = {
    ...categories[index],
    ...input,
  };

  writeJson(FILES.categories, categories);

  return categories[index];
}

/**
 * 删除分类
 */
export function deleteCategory(id: string): boolean {
  const categories = getAllCategories();
  const index = categories.findIndex(c => c.id === id);

  if (index === -1) return false;

  categories.splice(index, 1);
  writeJson(FILES.categories, categories);

  return true;
}

/**
 * 获取分类下的模板数量
 */
export function getCategoryTemplateCount(categoryId: string): number {
  const templates = readJson<any[]>(FILES.templates.replace('categories', 'templates'));
  return templates.filter(t => t.category === categoryId).length;
}

/**
 * 更新所有分类的模板数量
 */
export function updateCategoryCounts(): void {
  const categories = getAllCategories();
  const templates = readJson<any[]>(FILES.templates);

  categories.forEach(cat => {
    cat.templateCount = templates.filter(t => t.category === cat.id).length;
  });

  writeJson(FILES.categories, categories);
}
