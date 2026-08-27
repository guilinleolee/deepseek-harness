/**
 * 上传路由
 */

import { Router, Request, Response } from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { PATHS } from '../utils/storage';

const router = Router();

// Multer 配置
const storage = multer.diskStorage({
  destination: (_, __, cb) => cb(null, PATHS.uploads),
  filename: (_, file, cb) => {
    const unique = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, `${unique}${path.extname(file.originalname)}`);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 100 * 1024 * 1024 }, // 100MB
  fileFilter: (_, file, cb) => {
    const allowed = ['.pptx', '.ppt', '.key', '.pdf', '.png', '.jpg', '.jpeg', '.webp'];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowed.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error(`不支持的文件类型: ${ext}`));
    }
  }
});

/**
 * POST /api/upload
 * 上传单个文件
 */
router.post('/', upload.single('file'), (req: Request, res) => {
  try {
    if (!req.file) {
      res.status(400).json({ success: false, error: 'No file uploaded' });
      return;
    }

    res.json({
      success: true,
      data: {
        filename: req.file.filename,
        originalName: req.file.originalname,
        size: req.file.size,
        mimeType: req.file.mimetype,
        url: `/uploads/${req.file.filename}`,
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

/**
 * POST /api/upload/multiple
 * 上传多个文件
 */
router.post('/multiple', upload.array('files', 10), (req: Request, res) => {
  try {
    const files = (req as any).files as Express.Multer.File[];

    if (!files || files.length === 0) {
      res.status(400).json({ success: false, error: 'No files uploaded' });
      return;
    }

    res.json({
      success: true,
      data: files.map(f => ({
        filename: f.filename,
        originalName: f.originalname,
        size: f.size,
        mimeType: f.mimetype,
        url: `/uploads/${f.filename}`,
      }))
    });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

/**
 * DELETE /api/upload/:filename
 * 删除上传的文件
 */
router.delete('/:filename', (req: Request, res) => {
  try {
    const filePath = path.join(PATHS.uploads, req.params.filename);

    if (!fs.existsSync(filePath)) {
      res.status(404).json({ success: false, error: 'File not found' });
      return;
    }

    fs.unlinkSync(filePath);
    res.json({ success: true, data: { deleted: true } });
  } catch (error) {
    res.status(500).json({ success: false, error: String(error) });
  }
});

export { router as uploadRoutes };
