/**
 * 模板路由
 */

import { Router, Request, Response } from 'express';
import multer from 'multer';
import path from 'path';
import {
  getAllTemplates,
  getTemplateById,
  getTemplateBySlug,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  recordDownload,
  recordView,
  getTemplateFilePath,
  getSearchSuggestions
} from '../services/template';
import { TemplateFilter } from '../types';

const router = Router();

// Multer 配置
const storage = multer.diskStorage({
  destination: (_, __, cb) => {
    cb(null, path.join(process.env.MARKET_ROOT || '', 'uploads'));
  },
  filename: (_, file, cb) => {
    const unique = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, `${unique}${path.extname(file.originalname)}`);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 100 * 1024 * 1024 }, // 100MB
  fileFilter: (_, file, cb) => {
    const allowed = ['.pptx', '.ppt', '.key', '.pdf', '.png', '.jpg'];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowed.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error(`不支持的文件类型: ${ext}`));
    }
  }
});

/**
 * GET /api/templates
 * 列出所有模板
 */
router.get('/', (req: Request, res) => {
  try {
    const filter: TemplateFilter = {
      category: req.query.category as string,
      tags: req.query.tags ? (req.query.tags as string).split(',') : undefined,
      search: req.query.search as string,
      status: req.query.status as TemplateFilter['status'],
      sortBy: req.query.sortBy as TemplateFilter['sortBy'],
      sortOrder: req.query.sortOrder as 'asc' | 'desc',
      page: req.query.page ? parseInt(req.query.page as string) : 1,
      limit: req.query.limit ? parseInt(req.query.limit as string) : 20,
    };

    const { templates, total } = getAllTemplates(filter);

    res.json({
      success: true,
      data: templates,
      meta: {
        total,
        page: filter.page,
        limit: filter.limit,
        totalPages: Math.ceil(total / (filter.limit || 20)),
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

/**
 * GET /api/templates/suggestions
 * 获取搜索建议
 */
router.get('/suggestions', (req: Request, res) => {
  try {
    const query = req.query.q as string || '';
    const suggestions = getSearchSuggestions(query);
    res.json({ success: true, data: suggestions });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

/**
 * GET /api/templates/:id
 * 获取单个模板
 */
router.get('/:id', (req: Request, res) => {
  try {
    // 支持 ID 或 slug
    let template = getTemplateById(req.params.id);
    if (!template) {
      template = getTemplateBySlug(req.params.id);
    }

    if (!template) {
      res.status(404).json({ success: false, error: 'Template not found' });
      return;
    }

    // 记录浏览
    recordView(template.id);

    res.json({ success: true, data: template });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

/**
 * GET /api/templates/:id/download
 * 下载模板文件
 */
router.get('/:id/download', (req: Request, res) => {
  try {
    const filePath = getTemplateFilePath(req.params.id);

    if (!filePath) {
      res.status(404).json({ success: false, error: 'Template file not found' });
      return;
    }

    // 记录下载
    recordDownload(req.params.id);

    res.download(filePath);
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

/**
 * POST /api/templates
 * 创建模板
 */
router.post('/', upload.single('file'), (req: Request, res) => {
  try {
    const { name, description, category, tags, author, fileType, slides, dimensions, colorScheme, features } = req.body;

    if (!name || !description || !category) {
      res.status(400).json({
        success: false,
        error: 'Missing required fields: name, description, category'
      });
      return;
    }

    const input = {
      name,
      description,
      category,
      tags: tags ? JSON.parse(tags) : [],
      author,
      fileType: fileType as any,
      slides: slides ? parseInt(slides) : 0,
      dimensions,
      colorScheme: colorScheme ? JSON.parse(colorScheme) : [],
      features: features ? JSON.parse(features) : [],
    };

    const template = createTemplate(input, req.file?.path);

    res.status(201).json({ success: true, data: template });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

/**
 * PUT /api/templates/:id
 * 更新模板
 */
router.put('/:id', (req: Request, res) => {
  try {
    const template = updateTemplate(req.params.id, req.body);

    if (!template) {
      res.status(404).json({ success: false, error: 'Template not found' });
      return;
    }

    res.json({ success: true, data: template });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

/**
 * DELETE /api/templates/:id
 * 删除模板
 */
router.delete('/:id', (req: Request, res) => {
  try {
    const deleted = deleteTemplate(req.params.id);

    if (!deleted) {
      res.status(404).json({ success: false, error: 'Template not found' });
      return;
    }

    res.json({ success: true, data: { deleted: true } });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

export { router as templateRoutes };
