
    -- fingerprints 加 design 列
    ALTER TABLE fingerprints ADD COLUMN design_style TEXT;
    ALTER TABLE fingerprints ADD COLUMN design_consent_file TEXT;

    -- ip_profiles 加 design 列（V2 表存在时）
    -- 用 PRAGMA 检查表存在性
    
    -- 索引
    CREATE INDEX IF NOT EXISTS idx_design_style ON fingerprints(design_style);
  