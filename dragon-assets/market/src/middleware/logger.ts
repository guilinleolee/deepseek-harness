/**
 * 请求日志中间件
 */

import { Request, Response, NextFunction } from 'express';

export function requestLogger(req: Request, res: Response, next: NextFunction) {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    const method = req.method.padEnd(6);
    const status = res.statusCode.toString().padStart(3);
    const path = req.path;

    const statusColor = res.statusCode >= 400 ? '\x1b[31m' : '\x1b[32m';
    const reset = '\x1b[0m';

    console.log(
      `${statusColor}${status}${reset} ${method} ${path} - ${duration}ms`
    );
  });

  next();
}
