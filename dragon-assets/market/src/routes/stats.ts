/**
 * 统计路由
 */

import { Router } from 'express';
import { getStats, getPopularTags } from '../services/stats';

const router = Router();

/**
 * GET /api/stats
 * 获取统计数据
 */
router.get('/', (_, res) => {
  try {
    const stats = getStats();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

/**
 * GET /api/stats/tags
 * 获取热门标签
 */
router.get('/tags', (req, res) => {
  try {
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 20;
    const tags = getPopularTags(limit);
    res.json({ success: true, data: tags });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

export { router as statsRoutes };
