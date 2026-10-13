/**
 * 错误处理中间件
 */

import { Request, Response, NextFunction } from 'express';

/**
 * 404 处理
 */
export function notFoundHandler(req: Request, res: Response) {
  res.status(404).json({
    success: false,
    error: `Route not found: ${req.method} ${req.path}`
  });
}

/**
 * 全局错误处理
 */
export function errorHandler(err: Error, req: Request, res: Response, next: NextFunction) {
  console.error('Error:', err);

  // Multer 错误
  if (err.name === 'MulterError') {
    if (err.message.includes('File too large')) {
      res.status(413).json({ success: false, error: '文件过大，最大支持 100MB' });
      return;
    }
    res.status(400).json({ success: false, error: err.message });
    return;
  }

  // 其他错误
  res.status(500).json({
    success: false,
    error: process.env.NODE_ENV === 'production' ? 'Internal server error' : err.message
  });
}
