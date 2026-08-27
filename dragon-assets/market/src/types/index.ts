/**
 * 模板类型定义
 */

export interface TemplateMeta {
  id: string;
  name: string;
  slug: string;
  description: string;
  category: string;
  tags: string[];
  author: string;
  version: string;

  // 文件信息
  fileName: string;
  fileSize: number;
  fileType: 'pptx' | 'ppt' | 'key' | 'google-slides';

  // 预览
  previewUrl?: string;

  // 元数据
  slides: number;           // 幻灯片数量
  dimensions?: string;       // 尺寸规格
  colorScheme?: string[];    // 配色方案
  features?: string[];       // 特性标签

  // 统计
  downloads: number;
  views: number;
  rating: number;
  ratingCount: number;

  // 时间戳
  createdAt: string;
  updatedAt: string;
  publishedAt?: string;

  // 状态
  status: 'draft' | 'published' | 'archived';

  // 可选字段
  license?: string;
  source?: string;
  customFields?: Record<string, unknown>;
}

export interface TemplateCreateInput {
  name: string;
  description: string;
  category: string;
  tags?: string[];
  author?: string;
  fileType?: TemplateMeta['fileType'];
  slides?: number;
  dimensions?: string;
  colorScheme?: string[];
  features?: string[];
  license?: string;
  source?: string;
}

export interface TemplateUpdateInput {
  name?: string;
  description?: string;
  category?: string;
  tags?: string[];
  status?: TemplateMeta['status'];
  previewUrl?: string;
}

export interface TemplateFilter {
  category?: string;
  tags?: string[];
  search?: string;
  status?: TemplateMeta['status'];
  sortBy?: 'createdAt' | 'downloads' | 'rating' | 'name';
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string;
  icon: string;
  color: string;
  order: number;
  templateCount?: number;
  subcategories?: SubCategory[];
}

export interface SubCategory {
  id: string;
  name: string;
  slug: string;
  parentId: string;
}

export interface Stats {
  totalTemplates: number;
  totalDownloads: number;
  totalCategories: number;
  byCategory: Record<string, number>;
  byStatus: Record<string, number>;
  recentTemplates: TemplateMeta[];
  topTemplates: TemplateMeta[];
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  meta?: {
    total?: number;
    page?: number;
    limit?: number;
    totalPages?: number;
  };
}
