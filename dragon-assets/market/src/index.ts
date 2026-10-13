/**
 * PPT 模板市场后端 - 入口文件
 * 轻量级本地存储的模板管理系统
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { templateRoutes } from './routes/templates';
import { categoryRoutes } from './routes/categories';
import { uploadRoutes } from './routes/upload';
import { statsRoutes } from './routes/stats';
import { initStorage, getStoragePath } from './utils/storage';
import { errorHandler, notFoundHandler } from './middleware/error';
import { requestLogger } from './middleware/logger';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Logger
app.use(requestLogger);

// Routes
app.use('/api/templates', templateRoutes);
app.use('/api/categories', categoryRoutes);
app.use('/api/upload', uploadRoutes);
app.use('/api/stats', statsRoutes);

// Health check
app.get('/health', (_, res) => {
  res.json({
    status: 'ok',
    version: '1.0.0',
    storage: getStoragePath()
  });
});

// Error handling
app.use(notFoundHandler);
app.use(errorHandler);

// Initialize storage and start server
async function main() {
  await initStorage();

  app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════╗
║     🎯 PPT 模板市场后端已启动                      ║
╠═══════════════════════════════════════════════════╣
║  📡 API:      http://localhost:${PORT}              ║
║  📂 存储:     ${getStoragePath().padEnd(35)}║
║  📋 端点:                                           ║
║     GET  /api/templates     - 列表模板             ║
║     GET  /api/templates/:id  - 获取模板详情         ║
║     POST /api/templates      - 创建模板             ║
║     PUT  /api/templates/:id  - 更新模板             ║
║     DELETE /api/templates/:id - 删除模板             ║
║     GET  /api/categories     - 分类列表             ║
║     GET  /api/stats           - 统计数据             ║
╚═══════════════════════════════════════════════════╝
    `);
  });
}

main().catch(console.error);

export default app;
