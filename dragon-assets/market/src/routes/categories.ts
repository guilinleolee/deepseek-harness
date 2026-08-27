/**
 * 分类路由
 */

import { Router, Request, Response } from 'express';
import {
  getAllCategories,
  getCategoryById,
  getCategoryBySlug,
  createCategory,
  updateCategory,
  deleteCategory
} from '../services/category';

const router = Router();

/**
 * GET /api/categories
 * 获取所有分类
 */
router.get('/', (_, res) => {
  try {
    const categories = getAllCategories();
    res.json({ success: true, data: categories });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

/**
 * GET /api/categories/:id
 * 获取单个分类
 */
router.get('/:id', (req: Request, res) => {
  try {
    let category = getCategoryById(req.params.id);
    if (!category) {
      category = getCategoryBySlug(req.params.id);
    }

    if (!category) {
      res.status(404).json({ success: false, error: 'Category not found' });
      return;
    }

    res.json({ success: true, data: category });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

/**
 * POST /api/categories
 * 创建分类
 */
router.post('/', (req: Request, res) => {
  try {
    const { name, slug, description, icon, color } = req.body;

    if (!name || !slug) {
      res.status(400).json({ success: false, error: 'Missing required fields: name, slug' });
      return;
    }

    const category = createCategory({ name, slug, description, icon, color });
    res.status(201).json({ success: true, data: category });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

/**
 * PUT /api/categories/:id
 * 更新分类
 */
router.put('/:id', (req: Request, res) => {
  try {
    const category = updateCategory(req.params.id, req.body);

    if (!category) {
      res.status(404).json({ success: false, error: 'Category not found' });
      return;
    }

    res.json({ success: true, data: category });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

/**
 * DELETE /api/categories/:id
 * 删除分类
 */
router.delete('/:id', (req: Request, res) => {
  try {
    const deleted = deleteCategory(req.params.id);

    if (!deleted) {
      res.status(404).json({ success: false, error: 'Category not found' });
      return;
    }

    res.json({ success: true, data: { deleted: true } });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

export { router as categoryRoutes };
